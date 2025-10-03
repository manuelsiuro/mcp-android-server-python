# MCP Android Web Interface

Web-based interface for interacting with Android devices through the MCP Android server. Features include:

- 📱 Real-time device screen viewing with auto-refresh
- 🤖 Claude AI assistant integration for natural language device control
- 📊 Action history tracking for all MCP tool executions
- 🎯 Click-to-coordinate device interaction
- 🔄 WebSocket-based communication with Claude

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser (port 3000)                  │
│                                                              │
│  ┌──────────────────┐        ┌─────────────────────────┐   │
│  │   React Frontend │        │   Action History Panel   │   │
│  │   - Device View  │        │   - Real-time updates    │   │
│  │   - Claude Chat  │        │   - 3s auto-refresh      │   │
│  └──────────────────┘        └─────────────────────────┘   │
└──────────────┬───────────────────────┬──────────────────────┘
               │                       │
               ▼                       ▼
┌──────────────────────────────────────────────────────────────┐
│            FastAPI Backend (port 3001)                       │
│  - WebSocket /ws (Claude streaming)                          │
│  - REST API /api/* (device operations)                       │
│  - Action recording & history                                │
└──────────────┬────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│         MCP REST Adapter (port 8000) ⭐ NEW                  │
│  - Bridges web interface to MCP server                       │
│  - Exposes HTTP REST endpoints                               │
│  - Direct Python function calls to server.py                 │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│            MCP Server (server.py)                            │
│  - 63 Android automation tools                               │
│  - uiautomator2 integration                                  │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
         Android Device
```

## Quick Start

### Prerequisites

1. **Python 3.10+** with virtual environment
2. **Node.js 16+** and npm
3. **Android device** connected via ADB
4. **Claude API key** (for AI assistant features)

### 1. Install Dependencies

**Backend:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

**MCP REST Adapter:**
```bash
cd ..  # Return to project root
source .venv/bin/activate
pip install fastapi uvicorn  # Should already be installed
```

### 2. Configure Environment

**Backend (.env):**
```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```env
ANTHROPIC_API_KEY=your_claude_api_key_here
MCP_SERVER_URL=http://localhost:8000
```

### 3. Start the Services

You need to start **three services** in separate terminals:

**Terminal 1: MCP REST Adapter (port 8000)**
```bash
cd /path/to/mcp-android-server-python
./start-rest-adapter.sh
```

**Terminal 2: Backend Server (port 3001)**
```bash
cd /path/to/mcp-android-server-python/web-interface/backend
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 3001
```

**Terminal 3: Frontend Dev Server (port 3000)**
```bash
cd /path/to/mcp-android-server-python/web-interface/frontend
npm run dev
```

### 4. Access the Interface

Open your browser to:
```
http://localhost:3000
```

## Features

### 1. Device Screen Viewer

- Real-time screenshot display
- Auto-refresh every 2 seconds (configurable)
- Click-to-coordinate interaction
- Manual capture button
- Download screenshots

### 2. Claude AI Assistant

- Natural language device control
- WebSocket streaming responses
- Automatic MCP tool selection and execution
- Context-aware conversations

Example prompts:
- "Take a screenshot of the home screen"
- "Open the contacts app and search for John"
- "Click the login button"
- "What apps are installed on this device?"

### 3. Action History Panel

- Tracks all MCP tool executions
- Real-time updates (3-second polling)
- Shows tool names, timestamps, and success/failure
- Expandable parameters and results
- Auto-scrolling to latest actions
- Clear history button

## API Documentation

### REST Endpoints

**Device Operations:**
- `GET /api/devices` - List connected devices
- `POST /api/screenshot` - Capture device screenshot
- `GET /api/screenshots/:filename` - Retrieve screenshot file

**MCP Tool Execution:**
- `POST /api/mcp/tool` - Execute any MCP tool
  ```json
  {
    "tool_name": "check_adb",
    "parameters": {}
  }
  ```

**Action History:**
- `GET /api/actions/history` - Get recorded action history
- `DELETE /api/actions/history` - Clear action history (if implemented)

**Health Check:**
- `GET /api/health` - Server health status

### WebSocket

**Claude Streaming:**
- `WS /ws` - WebSocket connection for Claude chat
  - Send: `{"type": "message", "content": "your prompt"}`
  - Receive: Streaming JSON responses with Claude's output

## Development

### Backend Development

```bash
cd backend
source .venv/bin/activate

# Run with auto-reload
uvicorn main:app --reload --port 3001

# Run tests
pytest

# Format code
black .
ruff check .
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

### MCP REST Adapter Development

```bash
# Edit mcp_rest_adapter.py
cd /path/to/mcp-android-server-python

# Restart adapter
pkill -f mcp_rest_adapter.py
./start-rest-adapter.sh
```

## Troubleshooting

### REST Adapter Issues

**Problem:** Actions not recording / 404 errors

**Solution:**
1. Ensure REST adapter is running on port 8000:
   ```bash
   curl http://localhost:8000/
   # Should return: {"service":"MCP Android REST Adapter"...}
   ```

2. Check for port conflicts:
   ```bash
   lsof -i :8000
   # Kill any conflicting processes
   ```

3. Verify tool name mapping:
   ```bash
   curl http://localhost:8000/tools
   ```

See [ACTION_HISTORY_SOLUTION.md](./ACTION_HISTORY_SOLUTION.md) for detailed troubleshooting.

### Backend Issues

**Problem:** WebSocket connection fails

**Solution:**
- Check backend is running: `curl http://localhost:3001/api/health`
- Verify ANTHROPIC_API_KEY in `.env`
- Check browser console for error messages

**Problem:** Screenshots not loading

**Solution:**
- Ensure device is connected: `adb devices`
- Check MCP server is accessible
- Verify screenshots directory exists and is writable

### Frontend Issues

**Problem:** Frontend won't start

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Problem:** API calls fail with CORS errors

**Solution:**
- Backend CORS is configured to allow all origins in development
- Check backend logs for actual error
- Verify backend is running on port 3001

## Production Deployment

### Backend

```bash
# Use production ASGI server
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3001
```

### Frontend

```bash
# Build optimized production bundle
npm run build

# Serve with nginx or your preferred static file server
# Output is in: frontend/dist/
```

### MCP REST Adapter

```bash
# Run as systemd service (example)
sudo systemctl enable mcp-rest-adapter
sudo systemctl start mcp-rest-adapter
```

## File Structure

```
web-interface/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment template
│   └── screenshots/         # Captured device screenshots
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── ActionHistory.tsx
│   │   │   ├── ClaudeChat.tsx
│   │   │   └── DeviceViewer.tsx
│   │   ├── services/        # API clients
│   │   │   └── api.ts
│   │   ├── types/           # TypeScript definitions
│   │   └── App.tsx          # Main app component
│   ├── package.json
│   └── vite.config.ts       # Vite configuration
│
├── ACTION_HISTORY_SOLUTION.md  # Architecture fix documentation
├── TESTING_ACTION_HISTORY.md   # Testing guide
└── README.md                    # This file
```

## Technology Stack

**Backend:**
- FastAPI (async Python web framework)
- WebSockets (Claude streaming)
- Anthropic Claude API
- uiautomator2 (Android automation)

**Frontend:**
- React 18 with TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- WebSocket client

**Bridge:**
- MCP REST Adapter (FastAPI)
- Direct Python function calls

## Contributing

1. Follow the code style (Black for Python, ESLint for TypeScript)
2. Add tests for new features
3. Update documentation
4. Test with multiple Android devices/versions

## License

[Add your license here]

## Support

For issues and questions:
1. Check [ACTION_HISTORY_SOLUTION.md](./ACTION_HISTORY_SOLUTION.md) for common problems
2. Review [TESTING_ACTION_HISTORY.md](./TESTING_ACTION_HISTORY.md) for testing procedures
3. Open an issue on GitHub

## Acknowledgments

- Built with [MCP Android Server](https://github.com/yourusername/mcp-android-server-python)
- Powered by [Anthropic Claude](https://www.anthropic.com)
- Uses [uiautomator2](https://github.com/openatx/uiautomator2) for Android automation
