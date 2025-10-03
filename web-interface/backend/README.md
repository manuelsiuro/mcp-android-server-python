# MCP Android Web Interface - Backend

FastAPI server providing WebSocket and REST API for the MCP Android web interface.

## Features

- 🔌 **WebSocket Server** - Real-time Claude Code streaming via `/ws/claude`
- 🔄 **MCP Proxy** - Forward requests to MCP Android Server
- 📸 **Screenshot Management** - Capture and serve device screenshots
- 📊 **Action History** - Track all automation actions
- 🤖 **Claude SDK Integration** - Uses OAuth (no API keys required!)

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Install Claude SDK
pip install claude-agent-sdk
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit if needed (defaults work for local dev)
nano .env
```

### 3. Start Server

```bash
# Development mode (with auto-reload)
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 3001

# With Gunicorn (production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:3001
```

Server runs at: **http://localhost:3001**

## API Endpoints

### Health Check

```bash
# Basic health check
curl http://localhost:3001/

# Detailed health (includes MCP server status)
curl http://localhost:3001/health
```

### Device Management

```bash
# List connected devices
curl http://localhost:3001/api/devices

# Take screenshot
curl -X POST http://localhost:3001/api/screenshot \
  -H "Content-Type: application/json" \
  -d '{"device_id": "device123"}'

# Get screenshot
curl http://localhost:3001/api/screenshot/screenshot_1234567890.png \
  -o screen.png
```

### MCP Tools

```bash
# Call any MCP tool
curl -X POST http://localhost:3001/api/mcp/tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "click_xpath",
    "parameters": {
      "xpath": "//*[@text=\"Login\"]",
      "device_id": "device123"
    }
  }'

# Get UI hierarchy
curl -X POST http://localhost:3001/api/device/hierarchy \
  -H "Content-Type: application/json" \
  -d '{"device_id": "device123"}'
```

### Action History

```bash
# Get history
curl http://localhost:3001/api/actions/history

# Record action
curl -X POST http://localhost:3001/api/actions/record \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "click",
    "parameters": {"selector": "Login"},
    "result": {"success": true}
  }'

# Clear history
curl -X DELETE http://localhost:3001/api/actions/history
```

### WebSocket (Claude Integration)

```bash
# Using wscat
wscat -c ws://localhost:3001/ws/claude

# Send message
{"prompt": "Click the login button", "device_id": "device123"}

# Receive messages
{"type": "status", "content": "Processing request..."}
{"type": "claude_response", "content": "..."}
{"type": "complete", "content": "Request completed"}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_URL` | `http://localhost:8000` | MCP Android Server URL |
| `SCREENSHOTS_DIR` | `/tmp` | Directory for screenshots |
| `HOST` | `0.0.0.0` | Backend host |
| `PORT` | `3001` | Backend port |

### CORS Configuration

Default: Allows all origins (`allow_origins=["*"]`)

For production, restrict to your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Development

### Code Structure

```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .env                 # Local config (gitignored)
└── README.md            # This file
```

### Adding New Endpoints

```python
@app.get("/api/your-endpoint")
async def your_endpoint():
    """Your endpoint description"""
    return {"message": "Hello"}
```

### Adding New MCP Tools

```python
@app.post("/api/mcp/your-tool")
async def your_tool(params: YourToolParams):
    response = await http_client.post(
        f"{MCP_SERVER_URL}/tools/your_tool",
        json=params.dict()
    )
    return response.json()
```

## Troubleshooting

### Claude SDK Not Found

```bash
pip install claude-agent-sdk

# Or upgrade
pip install --upgrade claude-agent-sdk
```

### Cannot Connect to MCP Server

1. Verify MCP server is running:
   ```bash
   curl http://localhost:8000/
   ```

2. Check environment variable:
   ```bash
   echo $MCP_SERVER_URL
   ```

3. Check firewall rules

### Screenshot Permission Denied

```bash
mkdir -p /tmp/android-screenshots
chmod 755 /tmp/android-screenshots
```

### WebSocket Connection Issues

1. Check if port 3001 is available:
   ```bash
   lsof -i :3001
   ```

2. Verify WebSocket endpoint:
   ```bash
   curl http://localhost:3001/
   ```

3. Check browser console for errors

## Testing

### Manual Testing

```bash
# Terminal 1: Start server with logs
python main.py

# Terminal 2: Test endpoints
curl http://localhost:3001/health

# Terminal 3: Test WebSocket
wscat -c ws://localhost:3001/ws/claude
```

### Unit Tests (Coming Soon)

```bash
pytest tests/
```

## Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn[uvicorn]

# Run with 4 workers
gunicorn -w 4 \
  -k uvicorn.workers.UvicornWorker \
  main:app \
  --bind 0.0.0.0:3001 \
  --log-level info
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"]
```

### Using Systemd

```ini
# /etc/systemd/system/mcp-web-backend.service
[Unit]
Description=MCP Android Web Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/.venv/bin"
ExecStart=/path/to/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 3001

[Install]
WantedBy=multi-user.target
```

## Security Considerations

### Development

- CORS allows all origins
- No authentication
- Debug mode enabled
- Suitable for localhost only

### Production Checklist

- [ ] Enable authentication (JWT/OAuth)
- [ ] Restrict CORS to specific domains
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Rate limiting
- [ ] Input validation
- [ ] Logging and monitoring
- [ ] Environment secrets management
- [ ] Disable debug mode

## Performance

- **Startup Time:** ~2 seconds
- **Memory Usage:** ~100 MB
- **Request Latency:** < 100ms (REST), < 50ms (WebSocket)
- **Concurrent Connections:** 100+ (adjust with workers)

## Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **websockets** - WebSocket support
- **httpx** - Async HTTP client
- **pydantic** - Data validation
- **claude-agent-sdk** - Claude Code integration

## License

Same as parent project

## Support

- GitHub Issues
- Documentation: ../README.md
- Quick Start: ../QUICKSTART.md
