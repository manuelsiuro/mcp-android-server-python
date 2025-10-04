# server.py
from mcp.server.fastmcp import FastMCP
import uiautomator2 as u2
from typing import List, Optional, Dict, Any
import shutil
import subprocess
import asyncio
import os
from pathlib import Path
from typing import TypedDict
from dotenv import load_dotenv
from datetime import datetime
import json
import time

# Load environment variables from .env file
load_dotenv()

# Create an MCP server
mcp = FastMCP("MCP Server Android")

# ============================================================================
# RECORDING MECHANISM - POC
# ============================================================================

# Global recording state
_recording_state = {
    "active": False,
    "session_name": None,
    "actions": [],
    "screenshots_dir": None,
    "start_time": None,
    "action_counter": 0,
    "device_id": None,
    "last_action_time": None
}

def _record_action(tool_name: str, params: dict, result: Any) -> None:
    """Log an action if recording is active."""
    global _recording_state

    if not _recording_state["active"]:
        return

    _recording_state["action_counter"] += 1
    action_id = _recording_state["action_counter"]

    current_time = datetime.now()
    timestamp = current_time.isoformat()

    # Calculate delays
    delay_before_ms = 0
    if _recording_state["last_action_time"]:
        delay_before_ms = int((current_time - _recording_state["last_action_time"]).total_seconds() * 1000)

    action_data = {
        "id": action_id,
        "timestamp": timestamp,
        "tool": tool_name,
        "params": params,
        "result": result,
        "delay_before_ms": delay_before_ms,
        "delay_after_ms": 1000  # Default, can be adjusted
    }

    # Capture screenshot if enabled
    if _recording_state["screenshots_dir"]:
        screenshot_file = f"{_recording_state['screenshots_dir']}/{action_id:03d}_{tool_name}.png"
        try:
            # Use the screenshot function
            d = u2.connect(_recording_state["device_id"])
            d.screenshot(screenshot_file)
            action_data["screenshot"] = screenshot_file
        except Exception as e:
            print(f"Screenshot failed for action {action_id}: {e}")
            action_data["screenshot"] = None

    _recording_state["actions"].append(action_data)
    _recording_state["last_action_time"] = current_time

# ============================================================================
# Type definitions for better type hints
class DeviceInfo(TypedDict):
    manufacturer: str
    model: str
    serial: str
    version: str
    sdk: int
    display: str
    product: str


class AppInfo(TypedDict):
    package_name: str
    version_name: str
    version_code: int
    first_install_time: str
    last_update_time: str


class ElementInfo(TypedDict):
    text: str
    resourceId: str
    description: str
    className: str
    enabled: bool
    clickable: bool
    bounds: Dict[str, Any]
    selected: bool
    focused: bool


@mcp.tool(name="mcp_health", description="Simple mcp health tool")
def mcp_health() -> str:
    return "Hello, world!"


# ============================================================================
# RECORDING TOOLS - POC
# ============================================================================

@mcp.tool(
    name="start_recording",
    description="Start recording Android UI interactions as a test scenario"
)
def start_recording(
    session_name: str,
    description: Optional[str] = None,
    capture_screenshots: bool = True,
    device_id: Optional[str] = None
) -> Dict[str, Any]:
    """Start recording mode for capturing UI interactions.

    Args:
        session_name: Name for this test scenario
        description: Optional description of what this scenario tests
        capture_screenshots: Whether to capture screenshots at each step
        device_id: Optional specific device to record from

    Returns:
        recording_id: Unique ID for this recording session
        start_time: Timestamp when recording started
        status: Recording status
    """
    global _recording_state

    if _recording_state["active"]:
        return {
            "error": "Recording already in progress",
            "current_session": _recording_state["session_name"]
        }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"{session_name}_{timestamp}"

    # Create directories
    scenarios_dir = Path("scenarios") / session_id
    scenarios_dir.mkdir(parents=True, exist_ok=True)

    screenshots_dir = None
    if capture_screenshots:
        screenshots_dir = scenarios_dir / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        screenshots_dir = str(screenshots_dir)

    _recording_state = {
        "active": True,
        "session_name": session_id,
        "description": description,
        "actions": [],
        "screenshots_dir": screenshots_dir,
        "start_time": datetime.now(),
        "action_counter": 0,
        "device_id": device_id,
        "last_action_time": None
    }

    return {
        "recording_id": session_id,
        "status": "active",
        "start_time": _recording_state["start_time"].isoformat(),
        "capture_screenshots": capture_screenshots
    }


@mcp.tool(
    name="stop_recording",
    description="Stop recording and save the scenario"
)
def stop_recording() -> Dict[str, Any]:
    """Stop recording and save the scenario to JSON file.

    Returns:
        scenario_file: Path to saved scenario JSON
        screenshot_folder: Path to screenshots
        action_count: Number of actions recorded
        duration_ms: Total recording duration
    """
    global _recording_state

    if not _recording_state["active"]:
        return {
            "error": "No active recording session"
        }

    # Calculate duration
    duration_ms = int((datetime.now() - _recording_state["start_time"]).total_seconds() * 1000)

    # Get device info
    device_info = {}
    try:
        d = u2.connect(_recording_state["device_id"])
        info = d.info
        device_info = {
            "manufacturer": info.get("manufacturer", ""),
            "model": info.get("model", ""),
            "android_version": info.get("version", {}).get("release", ""),
            "sdk": info.get("version", {}).get("sdk", 0)
        }
    except Exception as e:
        print(f"Failed to get device info: {e}")

    # Build scenario JSON
    scenario = {
        "schema_version": "1.0",
        "metadata": {
            "name": _recording_state["session_name"],
            "description": _recording_state.get("description", ""),
            "created_at": _recording_state["start_time"].isoformat(),
            "device": device_info,
            "duration_ms": duration_ms
        },
        "actions": _recording_state["actions"]
    }

    # Save to file
    scenario_file = Path("scenarios") / _recording_state["session_name"] / "scenario.json"
    with open(scenario_file, 'w') as f:
        json.dump(scenario, f, indent=2)

    result = {
        "scenario_file": str(scenario_file),
        "screenshot_folder": _recording_state["screenshots_dir"],
        "action_count": len(_recording_state["actions"]),
        "duration_ms": duration_ms,
        "status": "saved"
    }

    # Reset recording state
    _recording_state["active"] = False

    return result


@mcp.tool(
    name="get_recording_status",
    description="Get current recording status"
)
def get_recording_status() -> Dict[str, Any]:
    """Get the current recording status and statistics.

    Returns:
        Status information about current recording session including:
        - action_count: Number of recorded actions
        - screenshot_count: Number of captured screenshots
        - last_action: String representation of the most recent action
    """
    global _recording_state

    if not _recording_state["active"]:
        return {
            "active": False,
            "message": "No recording in progress"
        }

    duration_ms = int((datetime.now() - _recording_state["start_time"]).total_seconds() * 1000)

    # Count screenshots in the screenshots directory
    screenshot_count = 0
    if _recording_state["screenshots_dir"]:
        screenshots_path = Path(_recording_state["screenshots_dir"])
        if screenshots_path.exists():
            screenshot_count = len(list(screenshots_path.glob("*.png")))

    # Get the last action as a formatted string
    last_action = None
    if _recording_state["actions"]:
        last_action_data = _recording_state["actions"][-1]
        # Format: "tool_name(param1, param2, ...)"
        tool_name = last_action_data.get("tool", "unknown")
        params = last_action_data.get("parameters", {})

        # Create a readable representation
        if tool_name == "click_at":
            x = params.get("x", "?")
            y = params.get("y", "?")
            last_action = f"click_at({x}, {y})"
        elif tool_name in ["click", "click_xpath"]:
            selector = params.get("selector") or params.get("xpath", "?")
            last_action = f"{tool_name}('{selector}')"
        elif tool_name == "send_text":
            text = params.get("text", "")
            text_preview = text[:20] + "..." if len(text) > 20 else text
            last_action = f"send_text('{text_preview}')"
        elif tool_name == "swipe":
            last_action = f"swipe({params.get('start_x')},{params.get('start_y')} → {params.get('end_x')},{params.get('end_y')})"
        else:
            # Generic format for other tools
            param_str = ", ".join(f"{k}={v}" for k, v in list(params.items())[:2])
            if len(params) > 2:
                param_str += ", ..."
            last_action = f"{tool_name}({param_str})"

    return {
        "active": True,
        "session_name": _recording_state["session_name"],
        "action_count": len(_recording_state["actions"]),
        "screenshot_count": screenshot_count,
        "last_action": last_action,
        "duration_ms": duration_ms,
        "capture_screenshots": _recording_state["screenshots_dir"] is not None
    }


@mcp.tool(
    name="replay_scenario",
    description="Replay a recorded scenario from JSON file with enhanced resilience"
)
def replay_scenario(
    scenario_file: str,
    device_id: Optional[str] = None,
    speed_multiplier: float = 1.0,
    retry_attempts: int = 3,
    capture_screenshots: bool = False,
    stop_on_error: bool = False
) -> Dict[str, Any]:
    """Replay a previously recorded scenario with comprehensive error handling.

    Feature 3: Enhanced Scenario Replay Engine
    - Supports all 48 action tools from Feature 1
    - Automatic retry with exponential backoff
    - Optional screenshot capture for debugging
    - Detailed execution reports

    Args:
        scenario_file: Path to scenario JSON file
        device_id: Optional specific device (default: first available device)
        speed_multiplier: Playback speed multiplier (1.0 = normal, 2.0 = 2x faster)
        retry_attempts: Number of retry attempts for failed actions (default: 3)
        capture_screenshots: Capture before/after screenshots for each action (default: False)
        stop_on_error: Stop replay on first error (default: False, continue despite failures)

    Returns:
        Comprehensive execution report with:
        - success: bool (overall success)
        - scenario: metadata (session name, device ID, etc.)
        - execution: statistics (total actions, success rate, duration, etc.)
        - action_results: detailed per-action results with timing and errors
        - errors: list of global errors
        - failed_actions: list of actions that failed
    """
    try:
        from replay import ReplayEngine, ReplayConfig

        # Build configuration from parameters
        config = ReplayConfig(
            retry_attempts=retry_attempts,
            capture_screenshots=capture_screenshots,
            speed_multiplier=speed_multiplier,
            stop_on_error=stop_on_error,
            screenshot_on_error=True,  # Always capture on error for debugging
            wait_for_screen_on=True
        )

        # Create engine and execute replay
        engine = ReplayEngine(device_id=device_id, config=config)
        report = engine.replay(scenario_file)

        return report

    except Exception as e:
        return {
            "success": False,
            "status": "ERROR",
            "error": str(e),
            "execution": {
                "total_actions": 0,
                "successful_actions": 0,
                "failed_actions": 0,
                "duration_seconds": 0
            }
        }


@mcp.tool(
    name="generate_espresso_code",
    description="Generate Espresso test code from a recorded scenario"
)
def generate_espresso_code(
    scenario_file: str,
    language: str = "kotlin",
    package_name: Optional[str] = None,
    class_name: Optional[str] = None
) -> Dict[str, Any]:
    """Generate Espresso test code from a recorded scenario.

    Args:
        scenario_file: Path to scenario JSON file
        language: "kotlin" or "java" (default: kotlin)
        package_name: Target package name (default: extracted from scenario or com.example.app)
        class_name: Test class name (default: generated from scenario name)

    Returns:
        code: Generated test code as string
        file_path: Path where code was saved
        imports: List of required imports
        warnings: List of manual adjustments needed
        ui_framework: Detected UI framework (xml/compose/hybrid)
    """
    try:
        # Import the code generator agent
        from agents.codegen.espresso_generator import EspressoCodeGeneratorAgent

        # Initialize the code generator
        generator = EspressoCodeGeneratorAgent()

        # Prepare inputs
        inputs = {
            "scenario_file": scenario_file,
            "language": language,
            "package_name": package_name or "com.example.app",
            "class_name": class_name,
            "options": {
                "include_comments": True,
                "use_idling_resources": False,
                "generate_custom_actions": True,
            }
        }

        # Execute code generation
        result = generator.execute(inputs)

        if result["status"] == "success":
            generated_code = result["data"]
            return {
                "code": generated_code.code,
                "file_path": generated_code.file_path,
                "imports": generated_code.imports,
                "warnings": generated_code.warnings,
                "ui_framework": generated_code.ui_framework.value,
                "custom_actions": generated_code.custom_actions,
                "status": "success"
            }
        else:
            return {
                "error": "Code generation failed",
                "details": result.get("errors", []),
                "status": "failed"
            }

    except FileNotFoundError:
        return {
            "error": f"Scenario file not found: {scenario_file}",
            "status": "failed"
        }
    except Exception as e:
        return {
            "error": f"Failed to generate Espresso code: {str(e)}",
            "status": "failed"
        }


# ============================================================================
# END RECORDING TOOLS
# ============================================================================

@mcp.tool(
    name="connect_device",
    description="Connect to an Android device and return device info with uiautomator2",
)
def connect_device(device_id: Optional[str] = None) -> DeviceInfo:
    """Connect to an Android device and get its information.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        Device information including manufacturer, model, etc.
    """
    try:
        d = u2.connect(device_id)
        info = d.info
        return {
            "manufacturer": info.get("manufacturer", ""),
            "model": info.get("model", ""),
            "serial": info.get("serial", ""),
            "version": info.get("version", {}).get("release", ""),
            "sdk": info.get("version", {}).get("sdk", 0),
            "display": info.get("display", {}).get("density", ""),
            "product": info.get("productName", ""),
        }
    except Exception as e:
        raise ConnectionError(
            f"Failed to connect to device with ID '{device_id}': {str(e)}"
        )


@mcp.tool(name="get_installed_apps", description="List installed apps")
def get_installed_apps(device_id: Optional[str] = None) -> List[AppInfo]:
    """Get a list of all installed applications on the device.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        List of application information including package names and versions
    """
    d = u2.connect(device_id)
    return d.app_list()


@mcp.tool(name="get_current_app", description="Get info about the foreground app")
def get_current_app(device_id: Optional[str] = None) -> AppInfo:
    """Get information about the currently active application.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        Information about the current foreground application
    """
    d = u2.connect(device_id)
    return d.app_current()


@mcp.tool(name="start_app", description="Start an app by package name")
def start_app(
    package_name: str, device_id: Optional[str] = None, wait: bool = True
) -> bool:
    """Start an application by its package name.

    Args:
        package_name: The package name of the application to start
        device_id: Optional device ID to connect to
        wait: Whether to wait for the app to come to the foreground

    Returns:
        True if the app was started successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.app_start(package_name)
        if wait:
            pid = d.app_wait(package_name, front=True)
            result = pid is not None
        else:
            result = True

        # RECORDING: Log this action if recording is active
        _record_action("start_app", {
            "package_name": package_name,
            "device_id": device_id,
            "wait": wait
        }, result)

        return result
    except Exception as e:
        print(f"Failed to start app {package_name}: {str(e)}")
        return False


@mcp.tool(name="stop_app", description="Stop an app by package name")
def stop_app(package_name: str, device_id: Optional[str] = None) -> bool:
    """Stop an application by its package name.

    Args:
        package_name: The package name of the application to stop
        device_id: Optional device ID to connect to

    Returns:
        True if the app was stopped successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.app_stop(package_name)

        # RECORDING: Log this action if recording is active
        _record_action("stop_app", {
            "package_name": package_name,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to stop app {package_name}: {str(e)}")
        return False


@mcp.tool(name="stop_all_apps", description="Stop all running apps")
def stop_all_apps(device_id: Optional[str] = None) -> bool:
    """Stop all running applications on the device.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if all apps were stopped successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.app_stop_all()

        # RECORDING: Log this action if recording is active
        _record_action("stop_all_apps", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to stop all apps: {str(e)}")
        return False


@mcp.tool(name="screen_on", description="Turn screen on")
def screen_on(device_id: Optional[str] = None) -> bool:
    """Turn the device screen on.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if the screen was turned on successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.screen_on()

        # RECORDING: Log this action if recording is active
        _record_action("screen_on", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to turn screen on: {str(e)}")
        return False


@mcp.tool(name="screen_off", description="Turn screen off")
def screen_off(device_id: Optional[str] = None) -> bool:
    """Turn the device screen off.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if the screen was turned off successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.screen_off()

        # RECORDING: Log this action if recording is active
        _record_action("screen_off", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to turn screen off: {str(e)}")
        return False


@mcp.tool(name="get_device_info", description="Get detailed device information")
def get_device_info(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about the device.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        A dictionary containing detailed device information
    """
    try:
        d = u2.connect(device_id)
        info = d.info
        display = d.window_size()
        return {
            "serial": d.serial,
            "resolution": f"{display[0]}x{display[1]}",
            "version": info.get("version", {}).get("release", ""),
            "sdk": info.get("version", {}).get("sdk", 0),
            "battery": d.battery_info,
            "wifi_ip": d.wlan_ip,
            "manufacturer": info.get("manufacturer", ""),
            "model": info.get("model", ""),
            "is_screen_on": d.screen_on(),
        }
    except Exception as e:
        print(f"Failed to get device info: {str(e)}")
        return {}


@mcp.tool(name="press_key", description="Press a key on the device")
def press_key(key: str, device_id: Optional[str] = None) -> bool:
    """Press a key on the device.

    Args:
        key: The key to press (e.g., 'home', 'back', 'menu', etc.)
        device_id: Optional device ID to connect to

    Returns:
        True if the key was pressed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.press(key)

        # RECORDING: Log this action if recording is active
        _record_action("press_key", {
            "key": key,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to press key {key}: {str(e)}")
        return False


@mcp.tool(name="unlock_screen", description="Unlock the device screen")
def unlock_screen(device_id: Optional[str] = None) -> bool:
    """Unlock the device screen.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if the screen was unlocked successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        if not d.info["screenOn"]:
            d.screen_on()
        d.unlock()

        # RECORDING: Log this action if recording is active
        _record_action("unlock_screen", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to unlock screen: {str(e)}")
        return False


def get_adb_path() -> Optional[str]:
    """Get ADB path from environment variables or system PATH.

    Checks in order:
    1. ADB_PATH environment variable (direct path to adb binary)
    2. ANDROID_HOME environment variable (looks for platform-tools/adb)
    3. System PATH

    Returns:
        Path to adb binary if found, None otherwise
    """
    # Check for direct ADB_PATH
    adb_path = os.environ.get("ADB_PATH")
    if adb_path and Path(adb_path).is_file():
        return adb_path

    # Check for ANDROID_HOME/platform-tools/adb
    android_home = os.environ.get("ANDROID_HOME")
    if android_home:
        potential_path = Path(android_home) / "platform-tools" / "adb"
        if potential_path.is_file():
            return str(potential_path)

    # Fall back to system PATH
    return shutil.which("adb")


@mcp.tool(name="check_adb", description="Check ADB and list devices")
def check_adb_and_list_devices() -> Dict[str, Any]:
    """Check if ADB is available and list connected devices.

    Returns:
        A dictionary containing ADB status and connected devices

    Environment Variables:
        ANDROID_HOME: Path to Android SDK (e.g., /Users/username/Library/Android/sdk)
        ADB_PATH: Direct path to adb binary (overrides ANDROID_HOME)
    """
    adb_path = get_adb_path()
    if not adb_path:
        return {
            "adb_exists": False,
            "devices": [],
            "error": "adb not found. Set ANDROID_HOME or ADB_PATH in .env file, or add adb to PATH",
        }
    try:
        result = subprocess.run(
            [adb_path, "devices"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().splitlines()
        devices = []
        for line in lines[1:]:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
        return {
            "adb_exists": True,
            "devices": devices,
            "error": None,
            "adb_path": adb_path,
        }
    except Exception as e:
        return {"adb_exists": True, "devices": [], "error": str(e), "adb_path": adb_path}


@mcp.tool(name="wait_for_screen_on", description="Wait until device screen is on")
async def wait_for_screen_on(device_id: str) -> str:
    """Wait until the device screen is turned on.

    Args:
        device_id: The device ID to connect to

    Returns:
        A message indicating the screen is now on
    """
    d = u2.connect(device_id)
    while not d.screen_on():
        await asyncio.sleep(1)
    return "Screen is now on"


@mcp.tool(
    name="click", description="Click on an element by text, description, or resource ID"
)
def click(
    selector: str,
    selector_type: str = "text",
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> bool:
    """Click on an element on the device screen.

    For Jetpack Compose views that don't respond to direct clicks,
    this function automatically falls back to coordinate-based clicking.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        timeout: Timeout for waiting for the element
        device_id: Optional device ID to connect to

    Returns:
        True if the element was clicked successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            el = d(text=selector)
        elif selector_type == "resourceId":
            el = d(resourceId=selector)
        elif selector_type == "description":
            el = d(description=selector)
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        if el.wait(timeout=timeout) and el.exists:
            # Use coordinate-based clicking for reliability (works for both XML and Compose)
            info = el.info
            bounds = info.get("bounds", {})
            if bounds:
                center_x = (bounds.get("left", 0) + bounds.get("right", 0)) / 2
                center_y = (bounds.get("top", 0) + bounds.get("bottom", 0)) / 2
                d.click(center_x, center_y)

                # RECORDING: Log this action if recording is active
                _record_action("click", {
                    "selector": selector,
                    "selector_type": selector_type,
                    "timeout": timeout,
                    "device_id": device_id
                }, True)

                return True
        return False
    except Exception as e:
        print(f"Failed to click element {selector}: {str(e)}")
        return False


@mcp.tool(
    name="send_text",
    description="Send text to current focused element or clear and send if clear=True",
)
def send_text(text: str, clear: bool = True, device_id: Optional[str] = None) -> bool:
    """Send text to the currently focused element on the device.

    Args:
        text: The text to send
        clear: Whether to clear the existing text before sending
        device_id: Optional device ID to connect to

    Returns:
        True if the text was sent successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.send_keys(text, clear=clear)

        # RECORDING: Log this action if recording is active
        _record_action("send_text", {
            "text": text,
            "clear": clear,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to send text: {str(e)}")
        return False


@mcp.tool(
    name="get_element_info",
    description="Get information about an element by text, description, or resource ID",
)
def get_element_info(
    selector: str,
    selector_type: str = "text",
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> ElementInfo:
    """Get information about an element on the device screen.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        timeout: Timeout for waiting for the element
        device_id: Optional device ID to connect to

    Returns:
        A dictionary containing information about the element
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            el = d(text=selector).wait(timeout=timeout)
        elif selector_type == "resourceId":
            el = d(resourceId=selector).wait(timeout=timeout)
        elif selector_type == "description":
            el = d(description=selector).wait(timeout=timeout)
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        if el and el.exists:
            info = el.info
            return {
                "text": info.get("text", ""),
                "resourceId": info.get("resourceId", ""),
                "description": info.get("contentDescription", ""),
                "className": info.get("className", ""),
                "enabled": info.get("enabled", False),
                "clickable": info.get("clickable", False),
                "bounds": info.get("bounds", {}),
                "selected": info.get("selected", False),
                "focused": info.get("focused", False),
            }
        return {}
    except Exception as e:
        print(f"Failed to get element info for {selector}: {str(e)}")
        return {}


@mcp.tool(name="swipe", description="Perform a swipe gesture from one point to another")
def swipe(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    duration: float = 0.5,
    device_id: Optional[str] = None,
) -> bool:
    """Perform a swipe gesture on the device screen.

    Args:
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        duration: Duration of the swipe
        device_id: Optional device ID to connect to

    Returns:
        True if the swipe was performed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.swipe(start_x, start_y, end_x, end_y, duration=duration)

        # RECORDING: Log this action if recording is active
        _record_action("swipe", {
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "duration": duration,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to perform swipe: {str(e)}")
        return False


@mcp.tool(
    name="wait_for_element", description="Wait for an element to appear on screen"
)
def wait_for_element(
    selector: str,
    selector_type: str = "text",
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> bool:
    """Wait for an element to appear on the device screen.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        timeout: Timeout for waiting for the element
        device_id: Optional device ID to connect to

    Returns:
        True if the element appeared successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        result = False
        if selector_type == "text":
            result = d(text=selector).wait(timeout=timeout)
        elif selector_type == "resourceId":
            result = d(resourceId=selector).wait(timeout=timeout)
        elif selector_type == "description":
            el = d(description=selector).wait(timeout=timeout)
            result = el is not None and el.exists
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        # RECORDING: Log this action if recording is active
        _record_action("wait_for_element", {
            "selector": selector,
            "selector_type": selector_type,
            "timeout": timeout,
            "device_id": device_id
        }, result)

        return result
    except Exception as e:
        print(f"Failed to wait for element {selector}: {str(e)}")
        return False


@mcp.tool(
    name="screenshot", description="Take a screenshot and save it to the specified path"
)
def screenshot(filename: str, device_id: Optional[str] = None) -> bool:
    """Take a screenshot of the device screen.

    Args:
        filename: The file path to save the screenshot
        device_id: Optional device ID to connect to

    Returns:
        True if the screenshot was taken successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.screenshot(filename)

        # RECORDING: Log this action if recording is active
        _record_action("screenshot", {
            "filename": filename,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to take screenshot: {str(e)}")
        return False


@mcp.tool(name="long_click", description="Long click on an element")
def long_click(
    selector: str,
    selector_type: str = "text",
    duration: float = 1.0,
    device_id: Optional[str] = None,
) -> bool:
    """Perform a long click on an element on the device screen.

    For Jetpack Compose views that don't respond to direct long clicks,
    this function automatically falls back to coordinate-based long clicking.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        duration: Duration of the long click
        device_id: Optional device ID to connect to

    Returns:
        True if the long click was performed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            el = d(text=selector)
        elif selector_type == "resourceId":
            el = d(resourceId=selector)
        elif selector_type == "description":
            el = d(description=selector)
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        if el and el.exists:
            # Use coordinate-based clicking for reliability (works for both XML and Compose)
            info = el.info
            bounds = info.get("bounds", {})
            if bounds:
                center_x = (bounds.get("left", 0) + bounds.get("right", 0)) / 2
                center_y = (bounds.get("top", 0) + bounds.get("bottom", 0)) / 2
                d.long_click(center_x, center_y, duration)

                # RECORDING: Log this action if recording is active
                _record_action("long_click", {
                    "selector": selector,
                    "selector_type": selector_type,
                    "duration": duration,
                    "device_id": device_id
                }, True)

                return True
        return False
    except Exception as e:
        print(f"Failed to long click element {selector}: {str(e)}")
        return False


@mcp.tool(name="scroll_to", description="Scroll to an element")
def scroll_to(
    selector: str, selector_type: str = "text", device_id: Optional[str] = None
) -> bool:
    """Scroll to an element on the device screen.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        device_id: Optional device ID to connect to

    Returns:
        True if the scroll was performed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        result = False
        if selector_type == "text":
            result = d(scrollable=True).scroll.to(text=selector)
        elif selector_type == "resourceId":
            result = d(scrollable=True).scroll.to(resourceId=selector)
        elif selector_type == "description":
            el = d(scrollable=True).scroll.to(description=selector)
            result = el is not None and el.exists
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        # RECORDING: Log this action if recording is active
        _record_action("scroll_to", {
            "selector": selector,
            "selector_type": selector_type,
            "device_id": device_id
        }, result)

        return result
    except Exception as e:
        print(f"Failed to scroll to element {selector}: {str(e)}")
        return False


@mcp.tool(name="drag", description="Drag an element to a specific location")
def drag(
    selector: str,
    selector_type: str,
    to_x: int,
    to_y: int,
    device_id: Optional[str] = None,
) -> bool:
    """Drag an element to a specific location on the device screen.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        to_x: The X coordinate to drag to
        to_y: The Y coordinate to drag to
        device_id: Optional device ID to connect to

    Returns:
        True if the drag was performed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            el = d(text=selector)
        elif selector_type == "resourceId":
            el = d(resourceId=selector)
        elif selector_type == "description":
            el = d(description=selector)
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        if el and el.exists:
            el.drag_to(to_x, to_y)

            # RECORDING: Log this action if recording is active
            _record_action("drag", {
                "selector": selector,
                "selector_type": selector_type,
                "to_x": to_x,
                "to_y": to_y,
                "device_id": device_id
            }, True)

            return True
        return False
    except Exception as e:
        print(f"Failed to drag element {selector}: {str(e)}")
        return False


@mcp.tool(name="get_toast", description="Get the text of the last toast message")
def get_toast(device_id: Optional[str] = None) -> str:
    """Get the text of the last toast message displayed on the device.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        The text of the last toast message
    """
    try:
        d = u2.connect(device_id)
        return d.toast.get_message(10.0) or ""
    except Exception as e:
        print(f"Failed to get toast message: {str(e)}")
        return ""


@mcp.tool(name="clear_app_data", description="Clear an app's data")
def clear_app_data(package_name: str, device_id: Optional[str] = None) -> bool:
    """Clear the data of an application on the device.

    Args:
        package_name: The package name of the application
        device_id: Optional device ID to connect to

    Returns:
        True if the app data was cleared successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.app_clear(package_name)

        # RECORDING: Log this action if recording is active
        _record_action("clear_app_data", {
            "package_name": package_name,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to clear app data for {package_name}: {str(e)}")
        return False


@mcp.tool(name="wait_activity", description="Wait for a specific activity to appear")
def wait_activity(
    activity: str, timeout: float = 10.0, device_id: Optional[str] = None
) -> bool:
    """Wait for a specific activity to appear on the device.

    Args:
        activity: The name of the activity to wait for
        timeout: Timeout for waiting for the activity
        device_id: Optional device ID to connect to

    Returns:
        True if the activity appeared successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        result = d.wait_activity(activity, timeout=timeout)

        # RECORDING: Log this action if recording is active
        _record_action("wait_activity", {
            "activity": activity,
            "timeout": timeout,
            "device_id": device_id
        }, result)

        return result
    except Exception as e:
        print(f"Failed to wait for activity {activity}: {str(e)}")
        return False


@mcp.tool(
    name="dump_hierarchy", description="Dump the UI hierarchy of the current screen"
)
def dump_hierarchy(
    compressed: bool = False,
    pretty: bool = True,
    max_depth: int = 50,
    device_id: Optional[str] = None,
) -> str:
    """Dump the UI hierarchy of the current screen.

    Args:
        compressed: Whether to include not important nodes (False to include all nodes)
        pretty: Whether to format the output XML
        max_depth: Maximum depth of the XML hierarchy to include
        device_id: Optional device ID to connect to

    Returns:
        XML string representation of the UI hierarchy
    """
    try:
        d = u2.connect(device_id)
        xml = d.dump_hierarchy(
            compressed=compressed, pretty=pretty, max_depth=max_depth
        )
        return xml
    except Exception as e:
        print(f"Failed to dump UI hierarchy: {str(e)}")
        return ""


# ============================================================================
# XPATH SELECTOR TOOLS
# ============================================================================


@mcp.tool(name="click_xpath", description="Click element using XPath selector")
def click_xpath(
    xpath: str, timeout: float = 10.0, device_id: Optional[str] = None
) -> bool:
    """Click on an element using XPath selector.

    For Jetpack Compose views that don't respond to direct clicks,
    this function automatically falls back to coordinate-based clicking.

    Args:
        xpath: XPath expression to locate the element (e.g., "//node[@text='Submit']")
        timeout: Timeout for waiting for the element
        device_id: Optional device ID to connect to

    Returns:
        True if the element was clicked successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        xpath_selector = d.xpath(xpath)
        if xpath_selector.wait(timeout=timeout):
            # Use coordinate-based clicking for reliability (works for both XML and Compose)
            info = xpath_selector.info
            bounds = info.get("bounds", {})
            if bounds:
                center_x = (bounds.get("left", 0) + bounds.get("right", 0)) / 2
                center_y = (bounds.get("top", 0) + bounds.get("bottom", 0)) / 2
                d.click(center_x, center_y)

                # RECORDING: Log this action if recording is active
                _record_action("click_xpath", {
                    "xpath": xpath,
                    "timeout": timeout,
                    "device_id": device_id
                }, True)

                return True
        return False
    except Exception as e:
        print(f"Failed to click element with XPath {xpath}: {str(e)}")
        return False


@mcp.tool(
    name="get_element_xpath",
    description="Get element information using XPath selector",
)
def get_element_xpath(
    xpath: str, timeout: float = 10.0, device_id: Optional[str] = None
) -> ElementInfo:
    """Get information about an element using XPath selector.

    Args:
        xpath: XPath expression to locate the element
        timeout: Timeout for waiting for the element
        device_id: Optional device ID to connect to

    Returns:
        A dictionary containing information about the element
    """
    try:
        d = u2.connect(device_id)
        xpath_selector = d.xpath(xpath)
        if xpath_selector.wait(timeout=timeout):
            info = xpath_selector.info
            return {
                "text": info.get("text", ""),
                "resourceId": info.get("resourceId", ""),
                "description": info.get("contentDescription", ""),
                "className": info.get("className", ""),
                "enabled": info.get("enabled", False),
                "clickable": info.get("clickable", False),
                "bounds": info.get("bounds", {}),
                "selected": info.get("selected", False),
                "focused": info.get("focused", False),
            }
        return {}
    except Exception as e:
        print(f"Failed to get element info with XPath {xpath}: {str(e)}")
        return {}


@mcp.tool(name="wait_xpath", description="Wait for element using XPath selector")
def wait_xpath(
    xpath: str, timeout: float = 10.0, device_id: Optional[str] = None
) -> bool:
    """Wait for an element to appear using XPath selector.

    Args:
        xpath: XPath expression to locate the element
        timeout: Timeout for waiting for the element
        device_id: Optional device ID to connect to

    Returns:
        True if the element appeared, False otherwise
    """
    try:
        d = u2.connect(device_id)
        el = d.xpath(xpath).wait(timeout=timeout)
        result = el is not None

        # RECORDING: Log this action if recording is active
        _record_action("wait_xpath", {
            "xpath": xpath,
            "timeout": timeout,
            "device_id": device_id
        }, result)

        return result
    except Exception as e:
        print(f"Failed to wait for element with XPath {xpath}: {str(e)}")
        return False


@mcp.tool(name="long_click_xpath", description="Long click element using XPath")
def long_click_xpath(
    xpath: str, duration: float = 1.0, device_id: Optional[str] = None
) -> bool:
    """Perform a long click on an element using XPath selector.

    For Jetpack Compose views that don't respond to direct long clicks,
    this function automatically falls back to coordinate-based long clicking.

    Args:
        xpath: XPath expression to locate the element
        duration: Duration of the long click in seconds
        device_id: Optional device ID to connect to

    Returns:
        True if the long click was performed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        xpath_selector = d.xpath(xpath)
        if xpath_selector.exists:
            # Use coordinate-based clicking for reliability (works for both XML and Compose)
            info = xpath_selector.info
            bounds = info.get("bounds", {})
            if bounds:
                center_x = (bounds.get("left", 0) + bounds.get("right", 0)) / 2
                center_y = (bounds.get("top", 0) + bounds.get("bottom", 0)) / 2
                d.long_click(center_x, center_y, duration)

                # RECORDING: Log this action if recording is active
                _record_action("long_click_xpath", {
                    "xpath": xpath,
                    "duration": duration,
                    "device_id": device_id
                }, True)

                return True
        return False
    except Exception as e:
        print(f"Failed to long click element with XPath {xpath}: {str(e)}")
        return False


@mcp.tool(name="send_text_xpath", description="Send text to element using XPath")
def send_text_xpath(
    xpath: str, text: str, clear: bool = True, device_id: Optional[str] = None
) -> bool:
    """Send text to an element located by XPath.

    Args:
        xpath: XPath expression to locate the element
        text: The text to send
        clear: Whether to clear existing text first
        device_id: Optional device ID to connect to

    Returns:
        True if text was sent successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        el = d.xpath(xpath)
        if el.exists:
            if clear:
                el.clear_text()
            el.set_text(text)

            # RECORDING: Log this action if recording is active
            _record_action("send_text_xpath", {
                "xpath": xpath,
                "text": text,
                "clear": clear,
                "device_id": device_id
            }, True)

            return True
        return False
    except Exception as e:
        print(f"Failed to send text to element with XPath {xpath}: {str(e)}")
        return False


# ============================================================================
# APP MANAGEMENT TOOLS
# ============================================================================


@mcp.tool(name="install_app", description="Install APK from URL or local path")
def install_app(apk_path: str, device_id: Optional[str] = None) -> bool:
    """Install an application from an APK file.

    Args:
        apk_path: Path to APK file (local path or URL)
        device_id: Optional device ID to connect to

    Returns:
        True if the app was installed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.app_install(apk_path)

        # RECORDING: Log this action if recording is active
        _record_action("install_app", {
            "apk_path": apk_path,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to install app from {apk_path}: {str(e)}")
        return False


@mcp.tool(name="uninstall_app", description="Uninstall app by package name")
def uninstall_app(package_name: str, device_id: Optional[str] = None) -> bool:
    """Uninstall an application by package name.

    Args:
        package_name: The package name of the application to uninstall
        device_id: Optional device ID to connect to

    Returns:
        True if the app was uninstalled successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.app_uninstall(package_name)

        # RECORDING: Log this action if recording is active
        _record_action("uninstall_app", {
            "package_name": package_name,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to uninstall app {package_name}: {str(e)}")
        return False


@mcp.tool(name="get_app_info", description="Get detailed app information")
def get_app_info(package_name: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about an installed application.

    Args:
        package_name: The package name of the application
        device_id: Optional device ID to connect to

    Returns:
        Dictionary containing app information
    """
    try:
        d = u2.connect(device_id)
        info = d.app_info(package_name)
        return info
    except Exception as e:
        print(f"Failed to get app info for {package_name}: {str(e)}")
        return {}


# ============================================================================
# CLIPBOARD & COORDINATE OPERATIONS
# ============================================================================


@mcp.tool(name="set_clipboard", description="Set clipboard content")
def set_clipboard(text: str, device_id: Optional[str] = None) -> bool:
    """Set the device clipboard content.

    Args:
        text: The text to set in clipboard
        device_id: Optional device ID to connect to

    Returns:
        True if clipboard was set successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.set_clipboard(text)

        # RECORDING: Log this action if recording is active
        _record_action("set_clipboard", {
            "text": text,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to set clipboard: {str(e)}")
        return False


@mcp.tool(name="get_clipboard", description="Get clipboard content")
def get_clipboard(device_id: Optional[str] = None) -> str:
    """Get the current device clipboard content.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        The clipboard text content
    """
    try:
        d = u2.connect(device_id)
        return d.clipboard or ""
    except Exception as e:
        print(f"Failed to get clipboard: {str(e)}")
        return ""


@mcp.tool(name="click_at", description="Click at specific coordinates")
def click_at(x: float, y: float, device_id: Optional[str] = None) -> bool:
    """Click at specific screen coordinates.

    Args:
        x: X coordinate
        y: Y coordinate
        device_id: Optional device ID to connect to

    Returns:
        True if click was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.click(x, y)

        # RECORDING: Log this action if recording is active
        _record_action("click_at", {
            "x": x,
            "y": y,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to click at ({x}, {y}): {str(e)}")
        return False


@mcp.tool(name="double_click_at", description="Double click at coordinates")
def double_click_at(x: float, y: float, device_id: Optional[str] = None) -> bool:
    """Double click at specific screen coordinates.

    Args:
        x: X coordinate
        y: Y coordinate
        device_id: Optional device ID to connect to

    Returns:
        True if double click was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.double_click(x, y)

        # RECORDING: Log this action if recording is active
        _record_action("double_click_at", {
            "x": x,
            "y": y,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to double click at ({x}, {y}): {str(e)}")
        return False


# ============================================================================
# SYSTEM OPERATIONS
# ============================================================================


@mcp.tool(name="shell", description="Execute ADB shell command")
def shell_command(command: str, device_id: Optional[str] = None) -> str:
    """Execute an ADB shell command on the device.

    Args:
        command: The shell command to execute
        device_id: Optional device ID to connect to

    Returns:
        The command output
    """
    try:
        d = u2.connect(device_id)
        result = d.shell(command)
        return result.output
    except Exception as e:
        print(f"Failed to execute shell command '{command}': {str(e)}")
        return ""


@mcp.tool(name="pull_file", description="Pull file from device")
def pull_file(
    device_path: str, local_path: str, device_id: Optional[str] = None
) -> bool:
    """Pull a file from the device to local system.

    Args:
        device_path: Path to file on device
        local_path: Local path to save the file
        device_id: Optional device ID to connect to

    Returns:
        True if file was pulled successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.pull(device_path, local_path)

        # RECORDING: Log this action if recording is active
        _record_action("pull_file", {
            "device_path": device_path,
            "local_path": local_path,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to pull file from {device_path}: {str(e)}")
        return False


@mcp.tool(name="push_file", description="Push file to device")
def push_file(
    local_path: str, device_path: str, device_id: Optional[str] = None
) -> bool:
    """Push a file from local system to device.

    Args:
        local_path: Local path to the file
        device_path: Path on device where to save the file
        device_id: Optional device ID to connect to

    Returns:
        True if file was pushed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.push(local_path, device_path)

        # RECORDING: Log this action if recording is active
        _record_action("push_file", {
            "local_path": local_path,
            "device_path": device_path,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to push file to {device_path}: {str(e)}")
        return False


# ============================================================================
# SCREEN & ORIENTATION CONTROLS
# ============================================================================


@mcp.tool(name="set_orientation", description="Set screen orientation")
def set_orientation(orientation: str, device_id: Optional[str] = None) -> bool:
    """Set the device screen orientation.

    Args:
        orientation: Orientation to set ('natural', 'left', 'right', 'upsidedown')
        device_id: Optional device ID to connect to

    Returns:
        True if orientation was set successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.set_orientation(orientation)

        # RECORDING: Log this action if recording is active
        _record_action("set_orientation", {
            "orientation": orientation,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to set orientation to {orientation}: {str(e)}")
        return False


@mcp.tool(name="get_orientation", description="Get current screen orientation")
def get_orientation(device_id: Optional[str] = None) -> str:
    """Get the current device screen orientation.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        Current orientation ('natural', 'left', 'right', 'upsidedown')
    """
    try:
        d = u2.connect(device_id)
        return d.orientation
    except Exception as e:
        print(f"Failed to get orientation: {str(e)}")
        return ""


@mcp.tool(name="freeze_rotation", description="Lock/unlock screen rotation")
def freeze_rotation(freeze: bool = True, device_id: Optional[str] = None) -> bool:
    """Lock or unlock screen rotation.

    Args:
        freeze: True to lock rotation, False to unlock
        device_id: Optional device ID to connect to

    Returns:
        True if operation was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.freeze_rotation(freeze)

        # RECORDING: Log this action if recording is active
        _record_action("freeze_rotation", {
            "freeze": freeze,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to freeze rotation: {str(e)}")
        return False


# ============================================================================
# ADVANCED INTERACTIONS
# ============================================================================


@mcp.tool(name="double_click", description="Double click on an element")
def double_click(
    selector: str,
    selector_type: str = "text",
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> bool:
    """Perform a double click on an element.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        timeout: Timeout for waiting for the element
        device_id: Optional device ID to connect to

    Returns:
        True if the double click was performed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            el = d(text=selector).wait(timeout=timeout)
        elif selector_type == "resourceId":
            el = d(resourceId=selector).wait(timeout=timeout)
        elif selector_type == "description":
            el = d(description=selector).wait(timeout=timeout)
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        if el and el.exists:
            el.double_click()

            # RECORDING: Log this action if recording is active
            _record_action("double_click", {
                "selector": selector,
                "selector_type": selector_type,
                "timeout": timeout,
                "device_id": device_id
            }, True)

            return True
        return False
    except Exception as e:
        print(f"Failed to double click element {selector}: {str(e)}")
        return False


@mcp.tool(name="scroll_forward", description="Scroll forward in scrollable container")
def scroll_forward(steps: int = 1, device_id: Optional[str] = None) -> bool:
    """Scroll forward in a scrollable container.

    Args:
        steps: Number of scroll steps
        device_id: Optional device ID to connect to

    Returns:
        True if scroll was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d(scrollable=True).scroll.forward(steps=steps)

        # RECORDING: Log this action if recording is active
        _record_action("scroll_forward", {
            "steps": steps,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to scroll forward: {str(e)}")
        return False


@mcp.tool(name="scroll_backward", description="Scroll backward in scrollable container")
def scroll_backward(steps: int = 1, device_id: Optional[str] = None) -> bool:
    """Scroll backward in a scrollable container.

    Args:
        steps: Number of scroll steps
        device_id: Optional device ID to connect to

    Returns:
        True if scroll was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d(scrollable=True).scroll.backward(steps=steps)

        # RECORDING: Log this action if recording is active
        _record_action("scroll_backward", {
            "steps": steps,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to scroll backward: {str(e)}")
        return False


@mcp.tool(name="fling_forward", description="Fast fling gesture forward")
def fling_forward(device_id: Optional[str] = None) -> bool:
    """Perform a fast fling gesture forward in a scrollable container.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if fling was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d(scrollable=True).fling.forward()

        # RECORDING: Log this action if recording is active
        _record_action("fling_forward", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to fling forward: {str(e)}")
        return False


@mcp.tool(name="fling_backward", description="Fast fling gesture backward")
def fling_backward(device_id: Optional[str] = None) -> bool:
    """Perform a fast fling gesture backward in a scrollable container.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if fling was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d(scrollable=True).fling.backward()

        # RECORDING: Log this action if recording is active
        _record_action("fling_backward", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to fling backward: {str(e)}")
        return False


@mcp.tool(name="scroll_to_beginning", description="Scroll to beginning of container")
def scroll_to_beginning(device_id: Optional[str] = None) -> bool:
    """Scroll to the beginning of a scrollable container.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if scroll was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d(scrollable=True).scroll.toBeginning()

        # RECORDING: Log this action if recording is active
        _record_action("scroll_to_beginning", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to scroll to beginning: {str(e)}")
        return False


@mcp.tool(name="scroll_to_end", description="Scroll to end of container")
def scroll_to_end(device_id: Optional[str] = None) -> bool:
    """Scroll to the end of a scrollable container.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if scroll was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d(scrollable=True).scroll.toEnd()

        # RECORDING: Log this action if recording is active
        _record_action("scroll_to_end", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to scroll to end: {str(e)}")
        return False


# ============================================================================
# NOTIFICATION & POPUP HANDLING
# ============================================================================


@mcp.tool(name="open_notification", description="Open notification drawer")
def open_notification(device_id: Optional[str] = None) -> bool:
    """Open the device notification drawer.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if notification drawer was opened successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.open_notification()

        # RECORDING: Log this action if recording is active
        _record_action("open_notification", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to open notification: {str(e)}")
        return False


@mcp.tool(name="open_quick_settings", description="Open quick settings panel")
def open_quick_settings(device_id: Optional[str] = None) -> bool:
    """Open the device quick settings panel.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if quick settings was opened successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.open_quick_settings()

        # RECORDING: Log this action if recording is active
        _record_action("open_quick_settings", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to open quick settings: {str(e)}")
        return False


@mcp.tool(name="disable_popups", description="Auto-dismiss system popups")
def disable_popups(enable: bool = True, device_id: Optional[str] = None) -> bool:
    """Enable or disable automatic dismissal of system popups.

    Args:
        enable: True to enable auto-dismiss, False to disable
        device_id: Optional device ID to connect to

    Returns:
        True if operation was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.disable_popups(enable)

        # RECORDING: Log this action if recording is active
        _record_action("disable_popups", {
            "enable": enable,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to disable popups: {str(e)}")
        return False


# ============================================================================
# ADVANCED FEATURES
# ============================================================================


@mcp.tool(name="healthcheck", description="Reset device to clean state")
def healthcheck(device_id: Optional[str] = None) -> bool:
    """Perform a health check and reset device to a clean state.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if healthcheck was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.healthcheck()

        # RECORDING: Log this action if recording is active
        _record_action("healthcheck", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to perform healthcheck: {str(e)}")
        return False


@mcp.tool(name="reset_uiautomator", description="Restart UIAutomator service")
def reset_uiautomator(device_id: Optional[str] = None) -> bool:
    """Reset/restart the UIAutomator service on the device.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if reset was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.reset_uiautomator()

        # RECORDING: Log this action if recording is active
        _record_action("reset_uiautomator", {
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to reset uiautomator: {str(e)}")
        return False


@mcp.tool(name="send_action", description="Send IME action (search, done, etc.)")
def send_action(action: str = "search", device_id: Optional[str] = None) -> bool:
    """Send an input method editor (IME) action.

    Args:
        action: IME action to send ('search', 'go', 'done', 'next', 'previous', 'send')
        device_id: Optional device ID to connect to

    Returns:
        True if action was sent successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.send_action(action)

        # RECORDING: Log this action if recording is active
        _record_action("send_action", {
            "action": action,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to send action {action}: {str(e)}")
        return False


@mcp.tool(name="pinch_in", description="Pinch gesture (zoom out)")
def pinch_in(
    percent: int = 100, steps: int = 50, device_id: Optional[str] = None
) -> bool:
    """Perform a pinch-in gesture (zoom out).

    Args:
        percent: Percentage of pinch (0-100)
        steps: Number of steps for the gesture
        device_id: Optional device ID to connect to

    Returns:
        True if pinch was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.pinch_in(percent=percent, steps=steps)

        # RECORDING: Log this action if recording is active
        _record_action("pinch_in", {
            "percent": percent,
            "steps": steps,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to pinch in: {str(e)}")
        return False


@mcp.tool(name="pinch_out", description="Pinch gesture (zoom in)")
def pinch_out(
    percent: int = 100, steps: int = 50, device_id: Optional[str] = None
) -> bool:
    """Perform a pinch-out gesture (zoom in).

    Args:
        percent: Percentage of pinch (0-100)
        steps: Number of steps for the gesture
        device_id: Optional device ID to connect to

    Returns:
        True if pinch was successful, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.pinch_out(percent=percent, steps=steps)

        # RECORDING: Log this action if recording is active
        _record_action("pinch_out", {
            "percent": percent,
            "steps": steps,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to pinch out: {str(e)}")
        return False


@mcp.tool(name="watcher_start", description="Start a UI watcher")
def watcher_start(name: str, device_id: Optional[str] = None) -> bool:
    """Start a previously configured UI watcher.

    Args:
        name: Name of the watcher to start
        device_id: Optional device ID to connect to

    Returns:
        True if watcher was started successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.watcher(name).start()

        # RECORDING: Log this action if recording is active
        _record_action("watcher_start", {
            "name": name,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to start watcher {name}: {str(e)}")
        return False


@mcp.tool(name="watcher_stop", description="Stop a UI watcher")
def watcher_stop(name: str, device_id: Optional[str] = None) -> bool:
    """Stop a running UI watcher.

    Args:
        name: Name of the watcher to stop
        device_id: Optional device ID to connect to

    Returns:
        True if watcher was stopped successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.watcher(name).stop()

        # RECORDING: Log this action if recording is active
        _record_action("watcher_stop", {
            "name": name,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to stop watcher {name}: {str(e)}")
        return False


@mcp.tool(name="watcher_remove", description="Remove a UI watcher")
def watcher_remove(name: str, device_id: Optional[str] = None) -> bool:
    """Remove a UI watcher configuration.

    Args:
        name: Name of the watcher to remove
        device_id: Optional device ID to connect to

    Returns:
        True if watcher was removed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.watcher(name).remove()

        # RECORDING: Log this action if recording is active
        _record_action("watcher_remove", {
            "name": name,
            "device_id": device_id
        }, True)

        return True
    except Exception as e:
        print(f"Failed to remove watcher {name}: {str(e)}")
        return False


if __name__ == "__main__":
    import sys

    # Check if --sse flag is provided
    if "--sse" in sys.argv:
        # SSE transport for HTTP-based MCP connections
        # FastMCP handles SSE internally, just use run()
        mcp.run(transport="sse")
    else:
        # stdio transport for Claude Desktop/VS Code
        mcp.run(transport="stdio")
