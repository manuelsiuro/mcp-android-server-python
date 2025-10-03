#!/bin/bash

# Start script for MCP Android Web Interface Backend
# Usage: ./start.sh

set -e

echo "🚀 Starting MCP Android Web Interface Backend..."

# Find compatible Python version (3.10-3.12)
PYTHON_CMD=""
for py_version in python3.12 python3.11 python3.10 python3; do
    if command -v $py_version &> /dev/null; then
        PY_VER=$($py_version --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        if [[ "$PY_VER" =~ ^3\.(10|11|12)$ ]]; then
            PYTHON_CMD=$py_version
            echo "✅ Using $PYTHON_CMD (version $PY_VER)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Compatible Python version not found (need 3.10, 3.11, or 3.12)"
    echo "Python 3.13 is not yet supported by all dependencies"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Run: $PYTHON_CMD -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed"
    echo "Run: pip install -r requirements.txt"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found, using defaults"
    cp .env.example .env
fi

# Load environment variables from project root's .env (for ANDROID_HOME)
PROJECT_ROOT_ENV="../../.env"
if [ -f "$PROJECT_ROOT_ENV" ]; then
    echo "✅ Loading ANDROID_HOME from project root .env"
    export $(grep -v '^#' "$PROJECT_ROOT_ENV" | xargs)
fi

# Start server
echo "✅ Starting FastAPI server on http://localhost:3001"
echo "📝 Logs will appear below..."
echo ""

python main.py
