"""
API endpoint tests for the RAG system.

Uses the lightweight test app defined in conftest.py to avoid the static-file
mount that the production app.py performs at import time.
"""

import pytest


class TestRootEndpoint:
    def test_root_returns_200(self, test_client):
        response = test_client.get("/")
        assert response.status_code == 200

    def test_root_returns_json(self, test_client):
        response = test_client.get("/")
        assert response.headers["content-type"].startswith("application/json")

    def test_root_response_body(self, test_client):
        response = test_client.get("/")
        assert "message" in response.json()


class TestQueryEndpoint:
    # --- happy-path ---

    def test_query_returns_200(self, test_client, sample_query_payload):
        response = test_client.post("/api/query", json=sample_query_payload)
        assert response.status_code == 200

    def test_query_response_has_required_fields(self, test_client, sample_query_payload):
        response = test_client.post("/api/query", json=sample_query_payload)
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data

    def test_query_answer_is_string(self, test_client, sample_query_payload):
        data = test_client.post("/api/query", json=sample_query_payload).json()
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0

    def test_query_sources_is_list(self, test_client, sample_query_payload):
        data = test_client.post("/api/query", json=sample_query_payload).json()
        assert isinstance(data["sources"], list)

    def test_query_returns_mocked_answer(self, test_client, sample_query_payload):
        data = test_client.post("/api/query", json=sample_query_payload).json()
        assert data["answer"] == "Test answer about machine learning."

    def test_query_returns_mocked_sources(self, test_client, sample_query_payload):
        data = test_client.post("/api/query", json=sample_query_payload).json()
        assert data["sources"] == ["Course A - Lesson 1"]

    # --- session handling ---

    def test_query_creates_session_when_none_provided(
        self, test_client, mock_rag_system, sample_query_payload
    ):
        test_client.post("/api/query", json=sample_query_payload)
        mock_rag_system.session_manager.create_session.assert_called_once()

    def test_query_returns_generated_session_id(
        self, test_client, sample_query_payload
    ):
        data = test_client.post("/api/query", json=sample_query_payload).json()
        assert data["session_id"] == "session_1"

    def test_query_uses_existing_session_id(
        self, test_client, mock_rag_system, sample_query_with_session
    ):
        data = test_client.post("/api/query", json=sample_query_with_session).json()
        assert data["session_id"] == "existing_session"
        mock_rag_system.session_manager.create_session.assert_not_called()

    def test_query_passes_session_id_to_rag(
        self, test_client, mock_rag_system, sample_query_with_session
    ):
        test_client.post("/api/query", json=sample_query_with_session)
        mock_rag_system.query.assert_called_once_with(
            "Explain transformers", "existing_session"
        )

    # --- validation errors ---

    def test_query_missing_query_field_returns_422(self, test_client):
        response = test_client.post("/api/query", json={})
        assert response.status_code == 422

    def test_query_empty_body_returns_422(self, test_client):
        response = test_client.post("/api/query", json=None)
        assert response.status_code == 422

    def test_query_wrong_content_type_returns_422(self, test_client):
        response = test_client.post(
            "/api/query",
            data="plain text",
            headers={"content-type": "text/plain"},
        )
        assert response.status_code in (415, 422)

    # --- error propagation ---

    def test_query_rag_exception_returns_500(self, test_client, mock_rag_system):
        mock_rag_system.query.side_effect = RuntimeError("RAG pipeline failure")
        response = test_client.post("/api/query", json={"query": "test"})
        assert response.status_code == 500

    def test_query_500_detail_contains_error_message(self, test_client, mock_rag_system):
        mock_rag_system.query.side_effect = RuntimeError("RAG pipeline failure")
        response = test_client.post("/api/query", json={"query": "test"})
        assert "RAG pipeline failure" in response.json()["detail"]

    def test_query_session_creation_failure_returns_500(
        self, test_client, mock_rag_system
    ):
        mock_rag_system.session_manager.create_session.side_effect = RuntimeError(
            "Session store unavailable"
        )
        response = test_client.post("/api/query", json={"query": "test"})
        assert response.status_code == 500


class TestCoursesEndpoint:
    # --- happy-path ---

    def test_courses_returns_200(self, test_client):
        response = test_client.get("/api/courses")
        assert response.status_code == 200

    def test_courses_response_has_required_fields(self, test_client):
        data = test_client.get("/api/courses").json()
        assert "total_courses" in data
        assert "course_titles" in data

    def test_courses_total_count(self, test_client):
        data = test_client.get("/api/courses").json()
        assert data["total_courses"] == 2

    def test_courses_titles_list(self, test_client):
        data = test_client.get("/api/courses").json()
        assert data["course_titles"] == ["Course A", "Course B"]

    def test_courses_titles_is_list(self, test_client):
        data = test_client.get("/api/courses").json()
        assert isinstance(data["course_titles"], list)

    def test_courses_count_matches_titles_length(self, test_client):
        data = test_client.get("/api/courses").json()
        assert data["total_courses"] == len(data["course_titles"])

    # --- empty catalog ---

    def test_courses_empty_catalog(self, test_client, mock_rag_system):
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": [],
        }
        data = test_client.get("/api/courses").json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    # --- error propagation ---

    def test_courses_analytics_exception_returns_500(self, test_client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = RuntimeError("DB unavailable")
        response = test_client.get("/api/courses")
        assert response.status_code == 500

    def test_courses_500_detail_contains_error_message(self, test_client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = RuntimeError("DB unavailable")
        response = test_client.get("/api/courses")
        assert "DB unavailable" in response.json()["detail"]
