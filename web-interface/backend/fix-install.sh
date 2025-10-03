#!/bin/bash

# Fix installation script for Python 3.13 compatibility issues
# This script recreates the virtual environment with Python 3.12

set -e

cd "$(dirname "$0")"

echo "🔧 Fixing Backend Installation..."
echo ""

# Remove old virtual environment
if [ -d ".venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf .venv
fi

# Find Python 3.12
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 not found"
    echo ""
    echo "Please install Python 3.12:"
    echo "  brew install python@3.12"
    exit 1
fi

echo "✅ Found Python 3.12"
python3.12 --version
echo ""

# Create new virtual environment with Python 3.12
echo "📦 Creating virtual environment with Python 3.12..."
python3.12 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install Claude SDK
echo ""
echo "🤖 Installing claude-agent-sdk..."
pip install claude-agent-sdk

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To start the server:"
echo "   source .venv/bin/activate"
echo "   python main.py"
echo ""
echo "Or simply run:"
echo "   ./start.sh"
