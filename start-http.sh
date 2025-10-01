#!/bin/bash
# MCP Android Agent - HTTP Server Startup Script
# This script starts the server in HTTP mode using uvicorn (for development/testing)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default host and port
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "🚀 Starting MCP Android Agent Server (HTTP Mode)"
echo "================================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Please run ./install.sh first to set up the environment"
    exit 1
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source .venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   ADB path will be detected from system PATH only"
    echo "   To configure custom ADB path: cp .env.example .env"
    echo ""
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "✓ Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Using Python $PYTHON_VERSION"
echo ""

# Start the server with SSE transport
echo "🌐 Starting MCP server with SSE transport on http://${HOST}:${PORT}/sse"
echo "   MCP clients can connect to: http://${HOST}:${PORT}/sse"
echo "   Press Ctrl+C to stop"
echo ""

python3 server.py --sse
