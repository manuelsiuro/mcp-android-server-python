# MCP Android Agent

This project provides an **MCP (Model Context Protocol)** server for automating Android devices using [uiautomator2](https://github.com/openatx/uiautomator2). It's designed to be easily plugged into AI agents like GitHub Copilot Chat, Claude, or Open Interpreter to control Android devices through natural language.

## Requirements

- Python 3.10 or higher (tested on 3.10, 3.11, 3.12, 3.13)
- Android Debug Bridge (adb) installed and in PATH
- Connected Android device with USB debugging enabled
- [uiautomator2](https://github.com/openatx/uiautomator2) compatible Android device

## Features

### 🚀 63 Total Tools Available

#### App Management
- Install/uninstall apps from APK files or URLs
- Start, stop, and manage apps by package name
- Retrieve installed apps, current foreground app, and detailed app info
- Clear app data and wait for activities

#### UI Interaction
- **Standard Selectors**: Click, long-click, double-click by text/resourceId/description
- **XPath Support**: Complex UI queries with XPath selectors
- **Coordinate-based**: Direct click/double-click at specific coordinates
- Send text, swipe, drag, scroll interactions

#### Advanced Scrolling & Gestures
- Scroll forward/backward, to beginning/end
- Fast fling gestures
- Pinch-in/pinch-out (zoom) gestures

#### Screen & Orientation Control
- Programmatically unlock, wake, or sleep the screen
- Set/get screen orientation (portrait, landscape, etc.)
- Lock/unlock screen rotation

#### System Operations
- Execute ADB shell commands
- Push/pull files to/from device
- Clipboard operations (get/set)

#### Notifications & Popups
- Open notification drawer and quick settings
- Auto-dismiss system popups

#### Watchers
- Start/stop/remove UI watchers for automatic popup handling

#### Device Management
- Get device info, screen resolution, battery status, WiFi IP
- Health check and UIAutomator service reset
- ADB diagnostic tools

#### UI Inspection
- Dump UI hierarchy (XML)
- Get element information and properties
- Capture screenshots and toast messages

## Use Cases

Perfect for:

- AI agents that need to interact with real devices
- Remote device control setups
- Automated QA tools
- Android bot frameworks
- UI testing and automation
- Device management and monitoring

## Running the Server

### Quick Start (Recommended)

**MCP stdio mode** (for Claude Desktop, VS Code agent mode):
```bash
./start.sh
```

**HTTP mode** (for development/testing):
```bash
./start-http.sh
```

### Manual Start

**Option 1: MCP stdio mode** (For AI agent integration)

```bash
source .venv/bin/activate
python3 server.py
```

**Option 2: HTTP mode with uvicorn** (For development/testing)

```bash
source .venv/bin/activate
uvicorn server:app --factory --host 0.0.0.0 --port 8000
```

## Usage

An MCP client is needed to use this server. The Claude Desktop app is an example of an MCP client. To use this server with Claude Desktop:

### Locate your Claude Desktop configuration file

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Add the Android MCP server configuration to the mcpServers section

```json
{
  "mcpServers": {
    "mcp-android": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/mcp-adb && source .venv/bin/activate && python -m server"
      ]
    }
  }
}
```

Replace `/path/to/mcp-adb` with the absolute path to where you cloned this repository. For example: `/Users/username/Projects/mcp-adb`

### Using with Claude Code CLI

**Quick Setup** - The server is pre-configured for Claude Code in this repository:

1. The configuration exists in `.claude/mcp-servers.json`
2. Start Claude Code in this directory - it will auto-detect the server
3. See [CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md) for global configuration and troubleshooting

### Using with VS Code

You can also use this MCP server with VS Code's agent mode (requires VS Code 1.99 or newer). To set up:

1. Create a `.vscode/mcp.json` file in your workspace:

```json
{
  "servers": {
    "mcp-android": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/mcp-adb && source .venv/bin/activate && python -m server"
      ]
    }
  }
}
```

## Available MCP Tools

| Tool Name             | Description                                                              |
|-----------------------|--------------------------------------------------------------------------|
| `mcp_health`          | Check if the MCP server is running properly                              |
| `connect_device`      | Connect to an Android device and get basic info                          |
| `get_installed_apps`  | List all installed apps with version and package info                    |
| `get_current_app`     | Get info about the app currently in the foreground                       |
| `start_app`           | Start an app by its package name                                         |
| `stop_app`            | Stop an app by its package name                                          |
| `stop_all_apps`       | Stop all currently running apps                                          |
| `screen_on`           | Turn on the screen                                                       |
| `screen_off`          | Turn off the screen                                                      |
| `get_device_info`     | Get detailed device info: serial, resolution, battery, etc.              |
| `press_key`           | Simulate hardware key press (e.g. `home`, `back`, `menu`, etc.)          |
| `unlock_screen`       | Unlock the screen (turn on and swipe if necessary)                       |
| `check_adb`           | Check if ADB is installed and list connected devices                     |
| `wait_for_screen_on`  | Wait asynchronously until the screen is turned on                        |
| `click`               | Tap on an element by `text`, `resourceId`, or `description`              |
| `long_click`          | Perform a long click on an element                                       |
| `send_text`           | Input text into currently focused field (optionally clearing before)     |
| `get_element_info`    | Get info on UI elements (text, bounds, clickable, etc.)                  |
| `swipe`               | Swipe from one coordinate to another                                     |
| `wait_for_element`    | Wait for an element to appear on screen                                  |
| `screenshot`          | Take and save a screenshot from the device                               |
| `scroll_to`           | Scroll until a given element becomes visible                             |
| `drag`                | Drag an element to a specific screen location                            |
| `get_toast`           | Get the last toast message shown on screen                               |
| `clear_app_data`      | Clear user data/cache of a specified app                                 |
| `wait_activity`       | Wait until a specific activity appears                                   |
| `dump_hierarchy`      | Dump the UI hierarchy of the current screen as XML                       |

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
