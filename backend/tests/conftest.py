"""
Shared fixtures for the RAG system test suite.

The production app.py mounts static files from ../frontend at startup, which
won't exist in CI or isolated test runs. To avoid that import-time failure we
build a lightweight test app here that exposes the same API routes without the
StaticFiles mount.
"""

import pytest
from typing import List, Optional
from unittest.mock import MagicMock

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Pydantic models (mirrors app.py – kept here so the test app is self-contained)
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: str


class CourseStats(BaseModel):
    total_courses: int
    course_titles: List[str]


# ---------------------------------------------------------------------------
# Test-app factory
# ---------------------------------------------------------------------------

def create_test_app(rag_system) -> FastAPI:
    """
    Build a FastAPI app that mirrors the production routes but does NOT mount
    static files, so it can be instantiated without a frontend build present.
    """
    app = FastAPI(title="Course Materials RAG System - Test")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {"message": "RAG System API"}

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = rag_system.session_manager.create_session()
            answer, sources = rag_system.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_rag_system():
    """
    A MagicMock that stands in for RAGSystem with sensible default return values.
    Individual tests can override attributes/return values as needed.
    """
    mock = MagicMock()
    mock.session_manager.create_session.return_value = "session_1"
    mock.query.return_value = ("Test answer about machine learning.", ["Course A - Lesson 1"])
    mock.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Course A", "Course B"],
    }
    return mock


@pytest.fixture
def test_client(mock_rag_system) -> TestClient:
    """A Starlette TestClient wired to the lightweight test app."""
    app = create_test_app(mock_rag_system)
    return TestClient(app)


@pytest.fixture
def sample_query_payload() -> dict:
    """A valid /api/query request body."""
    return {"query": "What is machine learning?"}


@pytest.fixture
def sample_query_with_session() -> dict:
    """A valid /api/query request body that includes a pre-existing session."""
    return {"query": "Explain transformers", "session_id": "existing_session"}
