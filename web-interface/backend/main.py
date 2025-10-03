"""
Web Interface Backend for MCP Android Server
FastAPI server with WebSocket support for Claude Code integration
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import asyncio
import json
import os
from pathlib import Path

# Check if claude CLI is available
import subprocess
import shutil

def check_claude_cli():
    """Check if claude CLI is available in PATH"""
    return shutil.which("claude") is not None

CLAUDE_CLI_AVAILABLE = check_claude_cli()
if not CLAUDE_CLI_AVAILABLE:
    print("⚠️  Warning: 'claude' CLI not found in PATH. Claude integration will be disabled.")
    print("   Install with: npm install -g @anthropic-ai/claude-code")
else:
    print("✅ Claude CLI found and ready")

app = FastAPI(
    title="MCP Android Web Interface",
    description="Web interface for Android device automation with Claude Code integration",
    version="1.0.0"
)

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
SCREENSHOTS_DIR = Path(os.getenv("SCREENSHOTS_DIR", "/tmp"))
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Project root directory (where .claude/mcp-servers.json is located)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
CLAUDE_CONFIG_DIR = PROJECT_ROOT / ".claude"
MCP_CONFIG_FILE = CLAUDE_CONFIG_DIR / "mcp-servers.json"

# Validate MCP configuration exists
if not MCP_CONFIG_FILE.exists():
    print(f"⚠️  Warning: MCP configuration not found at {MCP_CONFIG_FILE}")
    print(f"   Claude CLI will not have access to MCP Android tools!")
else:
    print(f"✅ Found MCP config: {MCP_CONFIG_FILE}")

# HTTP client for MCP server communication
http_client = httpx.AsyncClient(timeout=30.0)


# ================== Pydantic Models ==================

class ClaudePromptRequest(BaseModel):
    prompt: str
    project_path: Optional[str] = "."
    device_id: Optional[str] = None


class MCPToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]


class ScreenshotRequest(BaseModel):
    device_id: Optional[str] = None


# ================== Health Check ==================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "MCP Android Web Interface",
        "claude_cli_available": CLAUDE_CLI_AVAILABLE,
        "mcp_server_url": MCP_SERVER_URL
    }


@app.get("/health")
async def health_check():
    """Detailed health check including MCP server connectivity"""
    health_status = {
        "api": "healthy",
        "claude_cli": "available" if CLAUDE_CLI_AVAILABLE else "not_installed",
        "mcp_server": "unknown"
    }

    # Check MCP server connectivity
    try:
        response = await http_client.get(f"{MCP_SERVER_URL}/", timeout=5.0)
        health_status["mcp_server"] = "connected" if response.status_code == 200 else "error"
    except Exception as e:
        health_status["mcp_server"] = f"unreachable: {str(e)}"

    return health_status


# ================== Claude Code Integration ==================

def _diagnose_claude_error(error_msg: str, return_code: int) -> str:
    """
    Diagnose Claude CLI errors and provide helpful error messages.
    """
    error_lower = error_msg.lower()

    # Check for common errors
    if "not found" in error_lower and "mcp" in error_lower:
        return (
            f"❌ MCP Configuration Error\n\n"
            f"Claude CLI couldn't find or load the MCP server configuration.\n\n"
            f"**Expected config location**: {MCP_CONFIG_FILE}\n"
            f"**Config exists**: {MCP_CONFIG_FILE.exists()}\n\n"
            f"**Solution**: Ensure the MCP Android server is configured in .claude/mcp-servers.json"
        )

    elif "permission" in error_lower or "denied" in error_lower:
        return (
            f"❌ Permission Error\n\n"
            f"Claude CLI lacks permissions to execute or access required files.\n\n"
            f"**Check**:\n"
            f"- File permissions on {PROJECT_ROOT}\n"
            f"- Python executable permissions\n"
            f"- MCP server script permissions"
        )

    elif "python" in error_lower and ("not found" in error_lower or "no such" in error_lower):
        return (
            f"❌ Python Not Found\n\n"
            f"The MCP server requires Python but it wasn't found.\n\n"
            f"**Solution**: Ensure Python 3.10+ is installed and in PATH"
        )

    elif "connection" in error_lower or "econnrefused" in error_lower:
        return (
            f"❌ MCP Server Connection Failed\n\n"
            f"Claude couldn't connect to the MCP Android server.\n\n"
            f"**Check**:\n"
            f"- Is the MCP server running?\n"
            f"- Is the server.py file accessible at: {PROJECT_ROOT}/server.py"
        )

    else:
        # Generic error message
        return (
            f"❌ Claude CLI Error (exit code {return_code})\n\n"
            f"{error_msg}\n\n"
            f"**Debug Info**:\n"
            f"- Project root: {PROJECT_ROOT}\n"
            f"- MCP config: {MCP_CONFIG_FILE} (exists: {MCP_CONFIG_FILE.exists()})"
        )


def _build_mcp_aware_prompt(user_prompt: str, device_id: Optional[str]) -> str:
    """
    Build an enhanced prompt that informs Claude about available MCP tools.

    This ensures Claude knows it can use MCP Android tools to interact with the device.
    """
    context_parts = []

    # Add device context
    if device_id:
        context_parts.append(f"**Device ID**: {device_id}")
        context_parts.append(f"Use this device_id parameter when calling MCP Android tools.")

    # Add MCP tool awareness
    context_parts.append(
        "**Available Tools**: You have access to MCP Android tools for device automation. "
        "These tools are prefixed with `mcp__mcp-android__` and include:\n"
        "- Device control: start_app, stop_app, press_key, screenshot\n"
        "- UI interaction: click, click_xpath, send_text, swipe, dump_hierarchy\n"
        "- UI inspection: get_element_info, wait_for_element\n"
        "- And many more (63 total tools)\n\n"
        f"Use these tools to accomplish the user's request."
    )

    # Build final prompt
    context_block = "\n".join(context_parts)
    enhanced_prompt = f"{context_block}\n\n---\n\n**User Request**:\n{user_prompt}"

    return enhanced_prompt


async def _execute_claude_query(prompt: str, device_id: Optional[str], websocket: WebSocket):
    """
    Execute Claude CLI query and stream responses back via WebSocket.

    Key fixes:
    1. Sets working directory (cwd) to project root so Claude finds .claude/mcp-servers.json
    2. Enhances prompt with MCP tool awareness
    3. Comprehensive error handling and diagnostics
    """
    process = None
    message_count = 0

    try:
        # Build enhanced prompt with MCP context and device_id
        enhanced_prompt = _build_mcp_aware_prompt(prompt, device_id)

        # Build command (Claude CLI will find .claude/mcp-servers.json via cwd)
        cmd = [
            "claude",
            "-p", enhanced_prompt,
            "--output-format", "stream-json",
            "--verbose"
        ]

        print(f"🔨 Executing Claude CLI command...")
        print(f"   Working Directory: {PROJECT_ROOT}")
        print(f"   MCP Config: {MCP_CONFIG_FILE}")
        print(f"   Config Exists: {MCP_CONFIG_FILE.exists()}")
        print(f"   Device ID: {device_id or 'Not specified'}")
        print(f"   Prompt: {prompt[:100]}...")

        # Start subprocess from project root directory
        # This allows Claude CLI to find .claude/mcp-servers.json automatically
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(PROJECT_ROOT)  # ✅ KEY FIX: Claude finds .claude/ from this directory
        )

        print(f"✅ Claude CLI process started (PID: {process.pid})")
        print(f"🔄 Streaming Claude responses...")

        # Read stdout line by line (stream-json outputs NDJSON)
        while True:
            line = await process.stdout.readline()

            if not line:
                # Process has finished
                break

            try:
                # Parse JSON line
                line_str = line.decode('utf-8').strip()
                if not line_str:
                    continue

                message_count += 1
                print(f"📤 [{message_count}] Received from Claude: {line_str[:200]}...")

                # Parse the JSON message
                message_data = json.loads(line_str)

                # Forward to WebSocket
                await websocket.send_json({
                    "type": "content",
                    "data": message_data
                })

            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse JSON: {e}")
                print(f"   Line: {line_str[:200]}")
                continue
            except Exception as send_error:
                print(f"❌ Failed to send message: {send_error}")
                break

        # Wait for process to complete
        await process.wait()

        # Check if there were any errors
        if process.returncode != 0:
            stderr = await process.stderr.read()
            error_msg = stderr.decode('utf-8')
            print(f"❌ Claude CLI exited with code {process.returncode}")
            print(f"   Error output:\n{error_msg}")

            # Provide helpful error messages
            error_details = _diagnose_claude_error(error_msg, process.returncode)

            await websocket.send_json({
                "type": "error",
                "data": error_details
            })
        else:
            print(f"✅ Claude query completed successfully. Total messages: {message_count}")

    except asyncio.CancelledError:
        print("⚠️  Claude query cancelled - terminating process")
        if process and process.returncode is None:
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                process.kill()
        raise

    except Exception as e:
        print(f"❌ Claude query error: {str(e)}")
        import traceback
        traceback.print_exc()

        try:
            await websocket.send_json({
                "type": "error",
                "data": f"Claude query error: {str(e)}"
            })
        except:
            pass

    finally:
        # Ensure process is cleaned up
        if process and process.returncode is None:
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except:
                try:
                    process.kill()
                except:
                    pass


@app.websocket("/ws/claude")
async def claude_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for Claude Code integration
    Receives prompts from frontend and streams Claude's responses back
    """
    await websocket.accept()

    if not CLAUDE_CLI_AVAILABLE:
        print("❌ Claude CLI not available")
        await websocket.send_json({
            "type": "error",
            "data": "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
        })
        await websocket.close()
        return

    print("✅ Claude WebSocket connected")

    query_task = None

    try:
        while True:
            # Receive prompt from frontend
            data = await websocket.receive_json()
            print(f"📥 Received from WebSocket: {data}")

            prompt = data.get("prompt")
            project_path = data.get("project_path", ".")
            device_id = data.get("device_id")

            if not prompt:
                print("❌ No prompt provided in request")
                await websocket.send_json({
                    "type": "error",
                    "data": "No prompt provided"
                })
                continue

            print(f"✅ Processing prompt: {prompt[:100]}...")
            print(f"   Device ID: {device_id}")
            print(f"   Project path: {project_path}")

            # Send acknowledgment
            await websocket.send_json({
                "type": "start",
                "data": "Processing request with Claude Code..."
            })

            print(f"🚀 Starting Claude CLI execution...")

            # Execute Claude CLI in a separate task with proper cancellation handling
            query_task = asyncio.create_task(
                _execute_claude_query(prompt, device_id, websocket)
            )

            try:
                await query_task
            except asyncio.CancelledError:
                # Task was cancelled, likely due to WebSocket disconnect
                print("Query task cancelled")
                break
            except Exception as e:
                print(f"❌ Query task error: {str(e)}")
                import traceback
                traceback.print_exc()
                await websocket.send_json({
                    "type": "error",
                    "data": f"Query execution error: {str(e)}"
                })
            finally:
                query_task = None

            # Send completion signal
            print("✅ Request completed")
            await websocket.send_json({
                "type": "end",
                "data": "Request completed"
            })

    except WebSocketDisconnect:
        print("👋 Claude WebSocket client disconnected")
        # Cancel any running query
        if query_task and not query_task.done():
            query_task.cancel()
            try:
                await query_task
            except asyncio.CancelledError:
                pass
    except Exception as e:
        print(f"❌ Claude WebSocket error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Cancel any running query
        if query_task and not query_task.done():
            query_task.cancel()
            try:
                await query_task
            except asyncio.CancelledError:
                pass
        try:
            await websocket.send_json({
                "type": "error",
                "data": f"WebSocket error: {str(e)}"
            })
        except:
            pass


# ================== MCP Server Proxy Endpoints ==================

@app.post("/api/mcp/tool")
async def call_mcp_tool(request: MCPToolRequest):
    """
    Proxy endpoint to call MCP Android tools directly
    This allows the frontend to invoke tools without going through Claude
    """
    try:
        # Forward request to MCP server
        response = await http_client.post(
            f"{MCP_SERVER_URL}/tools/{request.tool_name}",
            json=request.parameters
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"MCP tool call failed: {response.text}"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to MCP server: {str(e)}"
        )


@app.get("/api/devices")
async def get_devices():
    """Get list of connected Android devices via ADB"""
    try:
        # Find adb command
        adb_cmd = "adb"

        # Check if ANDROID_HOME is set
        android_home = os.getenv("ANDROID_HOME")
        if android_home:
            adb_path = os.path.join(android_home, "platform-tools", "adb")
            if os.path.exists(adb_path):
                adb_cmd = adb_path

        print(f"🔍 Looking for ADB at: {adb_cmd}")

        # Check if adb exists
        if not shutil.which(adb_cmd) and not os.path.exists(adb_cmd):
            print(f"❌ ADB not found at: {adb_cmd}")
            raise HTTPException(
                status_code=503,
                detail=f"ADB not found. Please set ANDROID_HOME environment variable or install Android SDK Platform Tools."
            )

        print(f"✅ ADB found, running: {adb_cmd} devices -l")

        # Run adb devices command asynchronously
        process = await asyncio.create_subprocess_exec(
            adb_cmd, "devices", "-l",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=5.0
        )

        result_code = process.returncode

        if result_code != 0:
            error_msg = stderr.decode('utf-8')
            print(f"❌ ADB command failed: {error_msg}")
            raise HTTPException(
                status_code=503,
                detail=f"ADB command failed: {error_msg}"
            )

        # Parse output
        output = stdout.decode('utf-8')
        print(f"📱 ADB output:\n{output}")

        devices = []
        lines = output.strip().split('\n')[1:]  # Skip "List of devices attached"

        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2 and parts[1] != "offline":
                    device_id = parts[0]
                    status = parts[1]

                    # Extract model/product if available
                    model = "Unknown"
                    product = "Unknown"
                    for part in parts[2:]:
                        if part.startswith("model:"):
                            model = part.split(":")[1]
                        elif part.startswith("product:"):
                            product = part.split(":")[1]

                    devices.append({
                        "device_id": device_id,
                        "status": status,
                        "model": model,
                        "product": product
                    })

        print(f"✅ Found {len(devices)} device(s): {[d['device_id'] for d in devices]}")
        return {"devices": devices, "count": len(devices)}

    except asyncio.TimeoutError:
        print(f"❌ ADB command timed out")
        raise HTTPException(
            status_code=503,
            detail="ADB command timed out (5 seconds)"
        )
    except FileNotFoundError as e:
        print(f"❌ ADB binary not found: {e}")
        raise HTTPException(
            status_code=503,
            detail="ADB not found. Please install Android SDK Platform Tools."
        )
    except Exception as e:
        print(f"❌ Error fetching devices: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=503,
            detail=f"Cannot fetch devices: {str(e)}"
        )


@app.post("/api/screenshot")
async def take_screenshot(request: ScreenshotRequest):
    """
    Take screenshot from device via ADB and return file path
    """
    try:
        import subprocess
        import time

        timestamp = int(time.time() * 1000)
        filename = f"screenshot_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename

        # Find adb command
        adb_cmd = "adb"
        android_home = os.getenv("ANDROID_HOME")
        if android_home:
            adb_path = os.path.join(android_home, "platform-tools", "adb")
            if os.path.exists(adb_path):
                adb_cmd = adb_path

        # Build adb command
        adb_args = [adb_cmd]
        if request.device_id:
            adb_args.extend(["-s", request.device_id])

        # Take screenshot on device and pull it
        device_path = "/sdcard/screenshot_temp.png"

        # Capture screenshot on device
        result = subprocess.run(
            adb_args + ["shell", "screencap", "-p", device_path],
            capture_output=True,
            timeout=10
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Screenshot capture failed: {result.stderr.decode()}"
            )

        # Pull screenshot from device
        result = subprocess.run(
            adb_args + ["pull", device_path, str(filepath)],
            capture_output=True,
            timeout=10
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Screenshot pull failed: {result.stderr.decode()}"
            )

        # Clean up device screenshot
        subprocess.run(
            adb_args + ["shell", "rm", device_path],
            capture_output=True,
            timeout=5
        )

        return {
            "success": True,
            "filename": filename,
            "path": str(filepath),
            "url": f"/api/screenshot/{filename}"
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="Screenshot operation timed out"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="ADB not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Screenshot error: {str(e)}"
        )


@app.get("/api/screenshot/{filename}")
async def get_screenshot(filename: str):
    """Serve screenshot file"""
    filepath = SCREENSHOTS_DIR / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Screenshot not found")

    return FileResponse(filepath, media_type="image/png")


@app.get("/api/screenshot/latest")
async def get_latest_screenshot():
    """Get the most recent screenshot"""
    try:
        screenshots = sorted(SCREENSHOTS_DIR.glob("screenshot_*.png"))
        if not screenshots:
            raise HTTPException(status_code=404, detail="No screenshots found")

        latest = screenshots[-1]
        return FileResponse(latest, media_type="image/png")
    except IndexError:
        raise HTTPException(status_code=404, detail="No screenshots found")


@app.post("/api/device/hierarchy")
async def get_ui_hierarchy(device_id: Optional[str] = None):
    """Get UI hierarchy from device"""
    try:
        response = await http_client.post(
            f"{MCP_SERVER_URL}/tools/dump_hierarchy",
            json={"device_id": device_id, "pretty": True, "max_depth": 15}
        )
        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot fetch UI hierarchy: {str(e)}"
        )


# ================== Action History ==================

# In-memory action history (consider using Redis for production)
action_history: List[Dict[str, Any]] = []

@app.get("/api/actions/history")
async def get_action_history():
    """Get recorded action history"""
    return {"actions": action_history}


@app.post("/api/actions/record")
async def record_action(action: Dict[str, Any]):
    """Record an action to history"""
    import time
    action["timestamp"] = time.time()
    action_history.append(action)

    # Keep only last 100 actions
    if len(action_history) > 100:
        action_history.pop(0)

    return {"success": True, "action": action}


@app.delete("/api/actions/history")
async def clear_action_history():
    """Clear action history"""
    action_history.clear()
    return {"success": True, "message": "Action history cleared"}


# ================== Lifecycle ==================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print(f"\n{'='*60}")
    print(f"🚀 MCP Android Web Interface Starting")
    print(f"{'='*60}")
    print(f"📂 Project Root: {PROJECT_ROOT}")
    print(f"📋 MCP Config: {MCP_CONFIG_FILE}")
    print(f"   Config Exists: {'✅ YES' if MCP_CONFIG_FILE.exists() else '❌ NO'}")
    print(f"📡 MCP Server URL: {MCP_SERVER_URL}")
    print(f"🤖 Claude CLI: {'✅ Available' if CLAUDE_CLI_AVAILABLE else '❌ Not Found'}")
    print(f"📸 Screenshots Dir: {SCREENSHOTS_DIR}")
    print(f"{'='*60}\n")

    # Validate configuration
    if CLAUDE_CLI_AVAILABLE and not MCP_CONFIG_FILE.exists():
        print("⚠️  WARNING: Claude CLI is installed but MCP config not found!")
        print(f"   Expected location: {MCP_CONFIG_FILE}")
        print(f"   Claude will not be able to access MCP Android tools.")

    if not CLAUDE_CLI_AVAILABLE:
        print("⚠️  WARNING: Claude CLI not installed!")
        print(f"   Install with: npm install -g @anthropic-ai/claude-code")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await http_client.aclose()
    print("👋 MCP Android Web Interface shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3001,
        reload=True,
        log_level="info"
    )
