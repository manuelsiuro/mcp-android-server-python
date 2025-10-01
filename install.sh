#!/bin/bash
# MCP Android Agent Installation Script
# This script automates the setup process for the MCP Android server

set -e  # Exit on error

echo "🚀 MCP Android Agent Setup"
echo "=========================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.10 or higher is required (found: $PYTHON_VERSION)"
    exit 1
fi
echo "  Found Python $PYTHON_VERSION"
echo ""

# Check for uv, install if missing
echo "✓ Checking for uv package manager..."
if ! command -v uv &> /dev/null; then
    echo "  uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "  Found uv $(uv --version)"
fi
echo ""

# Create virtual environment
echo "✓ Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "  Virtual environment already exists, skipping..."
else
    uv venv
    echo "  Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "✓ Activating virtual environment..."
source .venv/bin/activate
echo ""

# Install dependencies
echo "✓ Installing dependencies..."
uv pip install -e .
echo ""

# Check for ADB
echo "✓ Checking for ADB..."
if ! command -v adb &> /dev/null; then
    echo "⚠️  Warning: ADB not found in PATH"
    echo "   Please install Android Debug Bridge (adb) to use this tool"
    echo "   - macOS: brew install android-platform-tools"
    echo "   - Linux: sudo apt-get install android-tools-adb"
    echo "   - Windows: Download from https://developer.android.com/studio/releases/platform-tools"
else
    echo "  Found adb $(adb version | head -n 1)"
fi
echo ""

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Connect your Android device with USB debugging enabled"
echo "  3. Run the server: python server.py"
echo ""
echo "For MCP integration with Claude Desktop or VS Code, see README.md"
