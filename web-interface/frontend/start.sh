#!/bin/bash

# Start script for Frontend
# Usage: ./start.sh

set -e

echo "🎨 Starting MCP Android Web Interface - Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "🚀 Starting Vite development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
