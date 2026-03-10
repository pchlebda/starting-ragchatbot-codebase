#!/usr/bin/env bash
# Frontend code quality auto-fix script
# Runs Prettier formatter and ESLint with --fix

set -e

FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Frontend Quality Auto-Fix ==="
echo ""

# Check if node_modules exists
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Installing dependencies..."
  cd "$FRONTEND_DIR" && npm install
fi

cd "$FRONTEND_DIR"

echo "1. Formatting code (Prettier)..."
npm run format
echo "   Formatting applied"
echo ""

echo "2. Auto-fixing lint issues (ESLint)..."
npm run lint:fix
echo "   Lint fixes applied"
echo ""

echo "=== Auto-fix complete ==="
