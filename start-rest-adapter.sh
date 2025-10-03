#!/bin/bash

# Start the MCP REST Adapter on port 8000
# This bridges the web interface to the MCP server

cd "$(dirname "$0")"

echo "🚀 Starting MCP Android REST Adapter..."

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./install.sh first."
    exit 1
fi

# Start the REST adapter
python3 mcp_rest_adapter.py
