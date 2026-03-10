#!/usr/bin/env bash
# Frontend code quality check script
# Runs Prettier format check and ESLint

set -e

FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Frontend Quality Checks ==="
echo ""

# Check if node_modules exists
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Installing dependencies..."
  cd "$FRONTEND_DIR" && npm install
fi

cd "$FRONTEND_DIR"

echo "1. Checking code formatting (Prettier)..."
npm run format:check
echo "   Formatting OK"
echo ""

echo "2. Running linter (ESLint)..."
npm run lint
echo "   Linting OK"
echo ""

echo "=== All checks passed ==="
