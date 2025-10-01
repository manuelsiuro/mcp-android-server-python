# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Android Agent is an MCP (Model Context Protocol) server for automating Android devices using uiautomator2. It exposes Android device control functionality through MCP tools that can be consumed by AI agents like Claude Desktop, GitHub Copilot Chat, or VS Code agent mode.

**Requirements:** Python 3.10+ (tested on 3.10, 3.11, 3.12, 3.13)

## Development Commands

### Environment Setup

**Quick Install (Automated):**
```bash
# Run the installation script (handles everything)
./install.sh
```

**Manual Install:**
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (using uv - preferred)
uv pip install -e .

# Or using traditional pip
pip install -r requirements.txt
```

### ADB Configuration

If ADB is not in your system PATH:

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and configure your Android SDK path:
```bash
# Recommended: Set ANDROID_HOME
ANDROID_HOME=/Users/username/Library/Android/sdk

# Alternative: Set direct ADB path
# ADB_PATH=/Users/username/Library/Android/sdk/platform-tools/adb
```

The server checks for ADB in this order:
1. `ADB_PATH` environment variable (direct path)
2. `ANDROID_HOME/platform-tools/adb`
3. System PATH

### Running the Server

**Quick Start:**
```bash
# MCP stdio mode (for Claude Desktop, VS Code)
./start.sh

# HTTP mode (for development/testing)
./start-http.sh
```

**Manual Start:**
```bash
# Activate virtual environment first
source .venv/bin/activate

# MCP stdio mode (for AI agent integration)
python3 server.py

# HTTP mode with uvicorn (for development/testing)
uvicorn server:app --factory --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_server.py
```

### Code Quality
```bash
# Lint and format with ruff
ruff check .
ruff format .
```

### UI Inspection Tool
```bash
# Install and run UI inspector for Android UI debugging
uv pip install uiautodev
uiauto.dev
# Opens browser at https://uiauto.dev
```

## Architecture

### Core Components

- **server.py**: Single-file MCP server implementation using FastMCP framework
  - All MCP tools are defined as decorated functions using `@mcp.tool()`
  - Uses uiautomator2 (u2) library for Android device communication
  - Supports both stdio (MCP) and HTTP (uvicorn) transports
  - All tools accept optional `device_id` parameter for multi-device support

### Tool Categories (63 Total Tools)

1. **Device Management**: `connect_device`, `check_adb`, `get_device_info`, `wait_for_screen_on`
2. **App Control**: `start_app`, `stop_app`, `stop_all_apps`, `get_installed_apps`, `get_current_app`, `install_app`, `uninstall_app`, `get_app_info`, `clear_app_data`
3. **Screen Control**: `screen_on`, `screen_off`, `unlock_screen`, `press_key`, `set_orientation`, `get_orientation`, `freeze_rotation`
4. **UI Interaction - Basic**: `click`, `long_click`, `double_click`, `send_text`, `swipe`, `drag`, `click_at`, `double_click_at`
5. **UI Interaction - XPath**: `click_xpath`, `get_element_xpath`, `wait_xpath`, `long_click_xpath`, `send_text_xpath`
6. **UI Inspection**: `get_element_info`, `wait_for_element`, `dump_hierarchy`
7. **Scrolling & Gestures**: `scroll_to`, `scroll_forward`, `scroll_backward`, `scroll_to_beginning`, `scroll_to_end`, `fling_forward`, `fling_backward`, `pinch_in`, `pinch_out`
8. **System Operations**: `shell`, `pull_file`, `push_file`, `set_clipboard`, `get_clipboard`
9. **Notifications & Popups**: `open_notification`, `open_quick_settings`, `disable_popups`
10. **Watchers**: `watcher_start`, `watcher_stop`, `watcher_remove`
11. **Advanced**: `screenshot`, `get_toast`, `wait_activity`, `send_action`, `healthcheck`, `reset_uiautomator`

### Selector System

UI interaction tools use a flexible selector system:
- **Standard Selectors**: `selector_type` can be "text", "resourceId", or "description"
  - Work reliably with traditional XML views
  - **May not work with Jetpack Compose views** - use XPath instead
- **XPath Selectors**: Dedicated XPath tools support complex queries like `"//node[@text='Submit' and @clickable='true']"`
  - **Recommended for Jetpack Compose views** - automatically use coordinate-based clicking
  - Work with all view types (XML and Compose)
- **Coordinate-based**: Direct `click_at(x, y)` and `double_click_at(x, y)` for precise positioning
- Elements are located using uiautomator2's selector syntax: `d(text=...), d(resourceId=...), d(description=...)` or `d.xpath(...)`
- All UI tools include timeout parameters for waiting on elements

**Important Note:** Jetpack Compose apps use deeply nested view hierarchies without resource-ids. For Compose views, XPath selectors are more reliable as they can traverse the entire hierarchy and automatically fall back to coordinate-based clicking when direct element interaction fails.

## Essential Tools Reference

This section documents the most commonly used tools with detailed examples and best practices.

### 🔍 UI Interaction Tools

#### `click_xpath` ⭐ Recommended for Compose Apps
**Purpose:** Click elements using XPath selectors with automatic coordinate fallback.

**When to use:**
- Jetpack Compose applications
- Complex UI hierarchies
- When standard `click()` fails
- Elements without resource IDs

**Parameters:**
- `xpath` (required): XPath expression (e.g., `//*[@text='Submit']`)
- `timeout` (optional): Wait time in seconds (default: 10.0)
- `device_id` (optional): Device identifier (default: first available device)

**Returns:** `bool` - `True` if click succeeded, `False` otherwise

**How it works:**
1. Locates element using XPath expression
2. Waits up to `timeout` seconds for element to appear
3. Extracts element bounds from UI hierarchy
4. Clicks at element center coordinates (automatic fallback)

**Example:**
```python
# Simple text match
click_xpath("//*[@text='Login']", device_id="R3CXA0B7EPD")

# Contains text (partial match)
click_xpath("//*[contains(@text, 'Submit')]", timeout=15)

# Complex condition
click_xpath("//node[@clickable='true' and contains(@text, 'Accept')]")

# Multiple attributes
click_xpath("//*[@text='Settings' and @class='android.widget.TextView']")
```

**XPath Syntax Reference:**
- `//*[@text='value']` - Exact text match
- `//*[contains(@text, 'value')]` - Partial text match
- `//*[@resource-id='com.app:id/button']` - Resource ID
- `//*[@content-desc='Submit']` - Content description
- `//*[@class='android.widget.Button']` - By class name
- `//node[@clickable='true']` - By attribute
- `//*[@text='Login']/parent::node` - Parent element
- `//*[@text='Header']/following-sibling::node[@text='Item']` - Sibling

**Troubleshooting:**
- Returns `False` → Element not found or not clickable
- Use `dump_hierarchy()` to inspect available elements
- Check `visible-to-user="true"` in hierarchy
- Verify XPath syntax with online validators

---

#### `click`
**Purpose:** Click elements using standard selectors (text, resourceId, description).

**When to use:**
- Traditional XML-based Android views
- Elements with resource IDs
- Simple text-based interactions

**Limitations:** May not work with Jetpack Compose views - use `click_xpath` instead.

**Parameters:**
- `selector` (required): Text, resource ID, or content description
- `selector_type` (optional): `"text"`, `"resourceId"`, or `"description"` (default: "text")
- `timeout` (optional): Wait time in seconds (default: 10.0)
- `device_id` (optional): Device identifier

**Returns:** `bool` - `True` if click succeeded, `False` otherwise

**Example:**
```python
# Click by visible text
click("Login", selector_type="text", device_id="device123")

# Click by resource ID (XML views)
click("com.example.app:id/login_button", selector_type="resourceId")

# Click by content description
click("Submit button", selector_type="description")

# With custom timeout
click("Slow Loading Button", timeout=20)
```

---

#### `click_at`
**Purpose:** Click at specific screen coordinates.

**When to use:**
- Precise positioning required
- As fallback when selectors fail
- Games or custom UI components
- After extracting bounds from `dump_hierarchy()`

**Parameters:**
- `x` (required): X coordinate in pixels
- `y` (required): Y coordinate in pixels
- `device_id` (optional): Device identifier

**Returns:** `bool` - `True` if click succeeded

**Example:**
```python
# Click at specific coordinates
click_at(540, 1050, device_id="device123")

# Extract coordinates from bounds in hierarchy
# bounds="[100,200][300,400]" → center is (200, 300)
center_x = (100 + 300) / 2
center_y = (200 + 400) / 2
click_at(center_x, center_y)
```

**Getting Coordinates:**
1. Run `dump_hierarchy()` to get UI XML
2. Find target element's `bounds` attribute: `bounds="[x1,y1][x2,y2]"`
3. Calculate center: `x = (x1+x2)/2`, `y = (y1+y2)/2`
4. Click at center coordinates

---

### 📱 UI Inspection Tools

#### `dump_hierarchy` ⭐ Essential for Debugging
**Purpose:** Retrieve complete UI hierarchy as XML for inspection and debugging.

**When to use:**
- Before writing any selectors
- When clicks or interactions fail
- Understanding app UI structure
- Finding element attributes (text, resource-id, bounds)
- Identifying Compose vs XML views

**Parameters:**
- `compressed` (optional): Remove whitespace (default: False)
- `pretty` (optional): Format with indentation (default: True)
- `max_depth` (optional): Limit nesting levels to reduce output (default: 50)
- `device_id` (optional): Device identifier

**Returns:** `str` - XML string of UI hierarchy

**Example:**
```python
# Get readable, formatted hierarchy
xml = dump_hierarchy(pretty=True, max_depth=10, device_id="device123")

# Get compact hierarchy for parsing
xml = dump_hierarchy(compressed=True, pretty=False)

# Full depth inspection
xml = dump_hierarchy(max_depth=50)
```

**What to Look For in Output:**

**1. Identify App Type:**
```xml
<!-- Jetpack Compose App -->
<node class="androidx.compose.ui.platform.ComposeView" ...>
  <node class="android.view.View" ...>  <!-- Generic views, no resource-ids -->
    <node text="Button Text" clickable="true" bounds="[100,200][300,400]" />
  </node>
</node>

<!-- Traditional XML App -->
<node class="android.widget.FrameLayout" ...>
  <node resource-id="com.app:id/login_button" class="android.widget.Button" ...>
    <node text="Login" />
  </node>
</node>
```

**2. Extract Selector Information:**
- `text="Login"` → Use `click("Login", selector_type="text")` or `//*[@text='Login']`
- `resource-id="com.app:id/button"` → Use `click("com.app:id/button", selector_type="resourceId")`
- `content-desc="Submit"` → Use `click("Submit", selector_type="description")`
- `bounds="[100,200][500,600]"` → Use `click_at(300, 400)` (center point)

**3. Check Element State:**
- `visible-to-user="true"` → Element is visible and interactable
- `clickable="true"` → Element accepts clicks
- `enabled="true"` → Element is not disabled
- `focused="true"` → Element currently has focus

**Troubleshooting Tips:**
- **Compose apps:** Look for `ComposeView` class → Use XPath selectors
- **Element not found:** Check `visible-to-user` and `bounds` are within screen
- **Multiple matches:** Add more specific attributes to XPath query
- **Deep nesting:** Reduce `max_depth` to make output more readable

---

#### `screenshot`
**Purpose:** Capture current screen state as PNG image.

**When to use:**
- Visual verification of UI state
- Debugging test failures
- Creating test documentation
- Before/after comparisons

**Parameters:**
- `filename` (required): Path to save PNG file (e.g., "/tmp/screen.png")
- `device_id` (optional): Device identifier

**Returns:** `bool` - `True` if screenshot saved successfully

**Example:**
```python
# Capture screen
screenshot("/tmp/debug_screen.png", device_id="device123")

# Capture at different test stages
screenshot("/tmp/before_click.png")
click_xpath("//*[@text='Submit']")
screenshot("/tmp/after_click.png")

# With timestamp
import time
timestamp = int(time.time())
screenshot(f"/tmp/test_{timestamp}.png")
```

---

#### `get_element_xpath`
**Purpose:** Get detailed information about an element using XPath.

**Parameters:**
- `xpath` (required): XPath expression
- `timeout` (optional): Wait time (default: 10.0)
- `device_id` (optional): Device identifier

**Returns:** `ElementInfo` dict with:
```python
{
    "text": str,           # Visible text content
    "resourceId": str,     # Resource ID (e.g., "com.app:id/button")
    "description": str,    # Content description
    "className": str,      # Widget class name
    "enabled": bool,       # Whether element is enabled
    "clickable": bool,     # Whether element is clickable
    "bounds": dict,        # {"left": int, "top": int, "right": int, "bottom": int}
    "selected": bool,      # Whether element is selected
    "focused": bool        # Whether element has focus
}
```

**Example:**
```python
# Get element info
info = get_element_xpath("//*[@text='Login']")
print(f"Element bounds: {info['bounds']}")
print(f"Clickable: {info['clickable']}")

# Check if element is ready for interaction
if info and info['clickable'] and info['enabled']:
    click_xpath("//*[@text='Login']")
```

---

### ⌨️ Text Input Tools

#### `send_text`
**Purpose:** Type text into currently focused element.

**Parameters:**
- `text` (required): Text to send
- `clear` (optional): Clear existing text first (default: True)
- `device_id` (optional): Device identifier

**Returns:** `bool` - `True` if text sent successfully

**Example:**
```python
# Click field first, then send text
click_xpath("//*[contains(@text, 'Search')]")
send_text("John Doe", clear=False, device_id="device123")

# Clear and type new text
click("username_field", selector_type="resourceId")
send_text("new_username", clear=True)
```

**Important:** Element must be focused before calling `send_text`. Click the input field first.

---

### 📦 App Management Tools

#### `start_app`
**Purpose:** Launch an application by package name.

**Parameters:**
- `package_name` (required): App package (e.g., "com.android.contacts")
- `wait` (optional): Wait for app to be in foreground (default: True)
- `device_id` (optional): Device identifier

**Returns:** `bool` - `True` if app started successfully

**Example:**
```python
# Launch app and wait
start_app("com.android.contacts", device_id="device123")

# Launch without waiting
start_app("com.example.app", wait=False)
```

**Finding Package Names:**
```bash
# List installed packages
adb shell pm list packages

# Get package of foreground app
adb shell dumpsys window windows | grep -E 'mCurrentFocus'
```

---

#### `stop_app`
**Purpose:** Force stop an application.

**Parameters:**
- `package_name` (required): App package
- `device_id` (optional): Device identifier

**Returns:** `bool` - `True` if app stopped successfully

---

### 🔄 Synchronization Tools

#### `wait_for_element`
**Purpose:** Wait for an element to appear on screen.

**Parameters:**
- `selector` (required): Element selector
- `selector_type` (optional): Type of selector (default: "text")
- `timeout` (optional): Max wait time (default: 10.0)
- `device_id` (optional): Device identifier

**Returns:** `bool` - `True` if element appeared within timeout

**Example:**
```python
# Wait for element before interacting
if wait_for_element("Login", timeout=15):
    click("Login")
else:
    print("Login button never appeared")
```

---

#### `wait_xpath`
**Purpose:** Wait for an element to appear using XPath.

**Parameters:**
- `xpath` (required): XPath expression
- `timeout` (optional): Max wait time (default: 10.0)
- `device_id` (optional): Device identifier

**Returns:** `bool` - `True` if element appeared

**Example:**
```python
# Wait for Compose element
if wait_xpath("//*[@text='Submit']", timeout=20):
    click_xpath("//*[@text='Submit']")
```

---

### 🎮 Device Control Tools

#### `press_key`
**Purpose:** Send keypress events to device.

**Common Keys:**
- `"home"` - Home button
- `"back"` - Back button
- `"menu"` - Menu button
- `"power"` - Power button
- `"volume_up"`, `"volume_down"` - Volume controls
- `"enter"` - Enter/OK

**Parameters:**
- `key` (required): Key name (see above)
- `device_id` (optional): Device identifier

**Returns:** `bool` - `True` if keypress succeeded

**Example:**
```python
# Navigate back
press_key("back", device_id="device123")

# Go to home screen
press_key("home")

# Press enter in text field
send_text("username")
press_key("enter")
```

---

## Common Workflows

Real-world examples combining multiple tools for typical automation tasks.

### 🔍 Workflow 1: Search and Select a Contact

**Scenario:** Search for "ronan" in a Jetpack Compose contacts app and open the contact details.

**Tools Used:** `start_app`, `click_at`, `send_text`, `click_xpath`, `screenshot`, `dump_hierarchy`

**Step-by-Step:**

```python
# 1. Launch the contacts app
start_app("com.android.contacts", device_id="R3CXA0B7EPD")

# 2. Wait for app to load
import time
time.sleep(2)

# 3. Inspect UI to find search field (Compose app)
hierarchy = dump_hierarchy(pretty=True, max_depth=10)
# Look for EditText with search-related text/hint

# 4. Click search field using coordinates from hierarchy
# Found bounds="[48,487][936,725]" in hierarchy
search_x = (48 + 936) / 2
search_y = (487 + 725) / 2
click_at(search_x, search_y)

# 5. Type search query
time.sleep(1)  # Wait for keyboard
send_text("ronan", clear=False)

# 6. Wait for search results
time.sleep(2)

# 7. Click on the contact using XPath (Compose requires XPath)
# Note: Standard click("Ronan guillou") would fail in Compose apps
click_xpath("//*[@text='Ronan guillou']")

# 8. Verify navigation with screenshot
time.sleep(1)
screenshot("/tmp/contact_details.png")
```

**Key Learnings:**
- **Compose apps need XPath** for reliable element selection
- Use `dump_hierarchy()` first to locate elements
- Extract coordinates from `bounds` attribute for precise clicking
- Add `time.sleep()` for UI transitions (or use `wait_for_element`)
- Screenshot for verification

**Common Issues:**
- **Search field not clickable:** Get exact coordinates from hierarchy
- **XPath returns False:** Element might not be visible - scroll first
- **Text not appearing:** Keyboard might not be visible - check with screenshot

---

### 📞 Workflow 2: Navigate App with Bottom Navigation

**Scenario:** Switch between tabs in a Compose app (Contacts → Calls → Messages).

**Tools Used:** `click_xpath`, `dump_hierarchy`, `screenshot`

**Step-by-Step:**

```python
device_id = "R3CXA0B7EPD"

# 1. Inspect bottom navigation structure
hierarchy = dump_hierarchy(max_depth=8)
# Look for navigation bar elements with resource-ids or content descriptions

# 2. Click "Calls" tab (XML view with resource-id)
click("fi.elisa.labsring:id/layout_calls",
      selector_type="resourceId",
      device_id=device_id)

screenshot("/tmp/calls_tab.png")

# 3. Click "Contacts" tab
time.sleep(1)
click("fi.elisa.labsring:id/layout_contact",
      selector_type="resourceId",
      device_id=device_id)

screenshot("/tmp/contacts_tab.png")

# 4. Alternative: Click by content description
click("Contacts", selector_type="description")
```

**Key Learnings:**
- Bottom navigation often uses **XML views** with resource IDs (not Compose)
- Check hierarchy for `resource-id` or `content-desc` attributes
- Standard `click()` with `resourceId` selector works well here
- Tab switches may have animations - add delays

---

### 🐛 Workflow 3: Debug When Interactions Fail

**Scenario:** Your click isn't working and you need to diagnose why.

**Systematic Debugging Approach:**

```python
device_id = "device123"

# Step 1: Capture current state
print("=== Capturing UI State ===")
screenshot("/tmp/debug_before.png")
hierarchy = dump_hierarchy(pretty=True, max_depth=15)

# Save hierarchy to file for inspection
with open("/tmp/hierarchy.xml", "w") as f:
    f.write(hierarchy)

print("Hierarchy saved to /tmp/hierarchy.xml")

# Step 2: Analyze hierarchy
# Look for these indicators:
# - <node class="androidx.compose.ui.platform.ComposeView"> = Compose app
# - visible-to-user="false" = Element not visible
# - clickable="false" = Element not clickable
# - bounds outside screen dimensions = Element off-screen

# Step 3: Try progressively more specific approaches

# Attempt 1: Standard text selector
success = click("Button Text", device_id=device_id)
print(f"Standard click: {'✓' if success else '✗'}")

if not success:
    # Attempt 2: XPath with exact text
    success = click_xpath("//*[@text='Button Text']", device_id=device_id)
    print(f"XPath exact match: {'✓' if success else '✗'}")

if not success:
    # Attempt 3: XPath with partial match
    success = click_xpath("//*[contains(@text, 'Button')]", device_id=device_id)
    print(f"XPath partial match: {'✓' if success else '✗'}")

if not success:
    # Attempt 4: XPath by class and text
    success = click_xpath("//node[@clickable='true' and contains(@text, 'Button')]",
                          device_id=device_id)
    print(f"XPath clickable elements: {'✓' if success else '✗'}")

if not success:
    # Attempt 5: Manual coordinates from hierarchy
    # Extract bounds from hierarchy.xml for target element
    # Example: bounds="[100,200][500,600]"
    center_x = (100 + 500) / 2  # Replace with actual values
    center_y = (200 + 600) / 2
    click_at(center_x, center_y, device_id=device_id)
    print("Clicked using coordinates")

# Step 4: Verify result
time.sleep(1)
screenshot("/tmp/debug_after.png")
```

**Diagnostic Checklist:**

| Issue | Check in Hierarchy | Solution |
|-------|-------------------|----------|
| Element not found | `text=` attribute exists? | Use exact text from hierarchy |
| Click fails | `clickable="true"`? | Find parent clickable element |
| Element not visible | `visible-to-user="true"`? | Scroll to element first |
| Compose app | `ComposeView` class? | Use XPath selectors |
| Element off-screen | `bounds` within screen? | Use `scroll_to()` |
| Multiple matches | Multiple nodes with same text? | Add more XPath conditions |

---

### 📝 Workflow 4: Form Filling in XML App

**Scenario:** Fill out a login form with username, password, and submit.

**Tools Used:** `click`, `send_text`, `press_key`, `wait_for_element`

```python
device_id = "device123"

# 1. Wait for form to load
if wait_for_element("username", selector_type="resourceId", timeout=10):

    # 2. Fill username field
    click("com.app:id/username", selector_type="resourceId")
    send_text("testuser@example.com", clear=True)

    # 3. Fill password field
    click("com.app:id/password", selector_type="resourceId")
    send_text("secretpass123", clear=True)

    # 4. Hide keyboard (optional)
    press_key("back")

    # 5. Submit form
    click("com.app:id/login_button", selector_type="resourceId")

    # 6. Wait for next screen
    if wait_for_element("Dashboard", timeout=15):
        print("Login successful!")
        screenshot("/tmp/logged_in.png")
    else:
        print("Login may have failed")
        screenshot("/tmp/error.png")
else:
    print("Login form never appeared")
```

**Best Practices:**
- Always `clear=True` when filling form fields
- Wait for elements before interacting
- Hide keyboard with `press_key("back")` if it blocks UI
- Screenshot before/after for verification
- Handle error states

---

### 🎯 Workflow 5: Scrolling and List Navigation

**Scenario:** Scroll through a list and click specific item.

**Tools Used:** `scroll_to`, `scroll_forward`, `click_xpath`, `dump_hierarchy`

```python
device_id = "device123"

# Method 1: Scroll to specific text (works if element exists in hierarchy)
success = scroll_to("Target Item", selector_type="text", device_id=device_id)
if success:
    click_xpath("//*[@text='Target Item']")

# Method 2: Scroll forward multiple times to load more items
for i in range(5):
    scroll_forward(device_id=device_id)
    time.sleep(0.5)  # Wait for scroll animation

    # Check if target item is now visible
    if wait_xpath("//*[@text='Target Item']", timeout=2):
        click_xpath("//*[@text='Target Item']")
        break

# Method 3: Scroll to end of list
scroll_to_end(device_id=device_id)
time.sleep(1)

# Method 4: Custom swipe gesture for precise scrolling
swipe(
    start_x=540,  # Center X of screen (1080/2)
    start_y=1500, # Lower part of screen
    end_x=540,    # Same X (vertical swipe)
    end_y=500,    # Upper part of screen
    duration=0.3, # Fast swipe
    device_id=device_id
)
```

---

## Complete Tool Reference Table

Quick lookup for all 63 MCP tools.

| Tool | Category | Purpose | Returns | Compose Support |
|------|----------|---------|---------|-----------------|
| **Device Management** |
| `connect_device` | Device | Connect and get device info | `DeviceInfo` dict | N/A |
| `check_adb` | Device | Verify ADB and list devices | dict with devices list | N/A |
| `get_device_info` | Device | Get detailed device specs | dict with device details | N/A |
| `wait_for_screen_on` | Device | Wait for screen to activate | str message | N/A |
| **App Control** |
| `start_app` | App | Launch app by package name | `bool` | N/A |
| `stop_app` | App | Force stop app | `bool` | N/A |
| `stop_all_apps` | App | Stop all running apps | `bool` | N/A |
| `get_installed_apps` | App | List installed packages | `List[AppInfo]` | N/A |
| `get_current_app` | App | Get foreground app info | `AppInfo` dict | N/A |
| `install_app` | App | Install APK from path/URL | `bool` | N/A |
| `uninstall_app` | App | Remove app by package | `bool` | N/A |
| `get_app_info` | App | Get app details | dict | N/A |
| `clear_app_data` | App | Clear app data and cache | `bool` | N/A |
| **Screen Control** |
| `screen_on` | Screen | Turn screen on | `bool` | N/A |
| `screen_off` | Screen | Turn screen off | `bool` | N/A |
| `unlock_screen` | Screen | Unlock device | `bool` | N/A |
| `press_key` | Screen | Send keypress event | `bool` | N/A |
| `set_orientation` | Screen | Set screen orientation | `bool` | N/A |
| `get_orientation` | Screen | Get current orientation | str | N/A |
| `freeze_rotation` | Screen | Lock/unlock rotation | `bool` | N/A |
| **UI Interaction - Basic** |
| `click` | UI | Click by text/resourceId/desc | `bool` | ⚠️ XML only |
| `long_click` | UI | Long press element | `bool` | ⚠️ XML only |
| `double_click` | UI | Double click element | `bool` | ⚠️ XML only |
| `send_text` | UI | Type text to focused element | `bool` | ✅ Yes |
| `swipe` | UI | Swipe gesture | `bool` | ✅ Yes |
| `drag` | UI | Drag element to position | `bool` | ⚠️ Limited |
| `click_at` | UI | Click at coordinates | `bool` | ✅ Yes |
| `double_click_at` | UI | Double click at coordinates | `bool` | ✅ Yes |
| **UI Interaction - XPath** |
| `click_xpath` ⭐ | UI | Click using XPath | `bool` | ✅ Yes (Recommended) |
| `get_element_xpath` | UI | Get element info via XPath | `ElementInfo` dict | ✅ Yes |
| `wait_xpath` | UI | Wait for element via XPath | `bool` | ✅ Yes |
| `long_click_xpath` | UI | Long press via XPath | `bool` | ✅ Yes |
| `send_text_xpath` | UI | Type to element via XPath | `bool` | ✅ Yes |
| **UI Inspection** |
| `get_element_info` | Inspection | Get element details | `ElementInfo` dict | ⚠️ XML only |
| `wait_for_element` | Inspection | Wait for element appearance | `bool` | ⚠️ XML only |
| `dump_hierarchy` ⭐ | Inspection | Get full UI XML | str (XML) | ✅ Yes |
| **Scrolling & Gestures** |
| `scroll_to` | Scroll | Scroll to element | `bool` | ⚠️ Limited |
| `scroll_forward` | Scroll | Scroll down/forward | `bool` | ✅ Yes |
| `scroll_backward` | Scroll | Scroll up/backward | `bool` | ✅ Yes |
| `scroll_to_beginning` | Scroll | Scroll to top | `bool` | ✅ Yes |
| `scroll_to_end` | Scroll | Scroll to bottom | `bool` | ✅ Yes |
| `fling_forward` | Gesture | Fast fling gesture forward | `bool` | ✅ Yes |
| `fling_backward` | Gesture | Fast fling gesture backward | `bool` | ✅ Yes |
| `pinch_in` | Gesture | Pinch to zoom out | `bool` | ✅ Yes |
| `pinch_out` | Gesture | Pinch to zoom in | `bool` | ✅ Yes |
| **System Operations** |
| `shell` | System | Execute ADB shell command | str (output) | N/A |
| `pull_file` | System | Download file from device | `bool` | N/A |
| `push_file` | System | Upload file to device | `bool` | N/A |
| `set_clipboard` | System | Set clipboard content | `bool` | N/A |
| `get_clipboard` | System | Get clipboard content | str | N/A |
| **Notifications & Popups** |
| `open_notification` | System | Open notification drawer | `bool` | N/A |
| `open_quick_settings` | System | Open quick settings | `bool` | N/A |
| `disable_popups` | System | Auto-dismiss system popups | `bool` | N/A |
| **Watchers** |
| `watcher_start` | Watcher | Start UI watcher | `bool` | N/A |
| `watcher_stop` | Watcher | Stop UI watcher | `bool` | N/A |
| `watcher_remove` | Watcher | Remove UI watcher | `bool` | N/A |
| **Advanced** |
| `screenshot` | Advanced | Capture screen as PNG | `bool` | ✅ Yes |
| `get_toast` | Advanced | Get toast message text | str | ✅ Yes |
| `wait_activity` | Advanced | Wait for activity | `bool` | N/A |
| `send_action` | Advanced | Send IME action | `bool` | ✅ Yes |
| `healthcheck` | Advanced | Reset to clean state | `bool` | N/A |
| `reset_uiautomator` | Advanced | Restart UIAutomator service | `bool` | N/A |

**Legend:**
- ⭐ = Most frequently used tool
- ✅ Yes = Full Jetpack Compose support
- ⚠️ XML only = Works with traditional XML views, may fail with Compose
- ⚠️ Limited = Partial support, may require workarounds

---

## Working with Jetpack Compose Apps

Jetpack Compose is Android's modern UI toolkit that uses a different rendering approach than traditional XML layouts. This creates unique challenges for UI automation.

### Key Differences

| Aspect | Traditional XML | Jetpack Compose |
|--------|----------------|-----------------|
| **View Hierarchy** | Shallow, well-defined | Deep (10-15+ levels), generic |
| **Resource IDs** | Most elements have IDs | ❌ Rarely has resource IDs |
| **Class Names** | Specific (`Button`, `TextView`) | Generic (`android.view.View`) |
| **Standard Selectors** | ✅ Work well | ❌ Often fail |
| **XPath Selectors** | ✅ Work | ✅ Work (Recommended) |
| **Coordinate Clicking** | ✅ Work | ✅ Work (Auto-fallback) |

### How to Identify Compose Apps

Run `dump_hierarchy()` and look for:

```xml
<!-- This is a Compose app -->
<node class="androidx.compose.ui.platform.ComposeView" package="com.example.app">
  <node class="android.view.View">
    <node class="android.view.View">
      <node class="android.view.View" text="Button Text" clickable="true" />
    </node>
  </node>
</node>
```

**Indicators:**
- `androidx.compose.ui.platform.ComposeView` class present
- Many nested `android.view.View` nodes
- No `resource-id` attributes on interactive elements
- Very deep hierarchy (max_depth > 10 typical)

### Best Practices for Compose

**1. Always Use XPath Selectors**
```python
# ❌ DON'T: Standard selectors often fail
click("Submit", selector_type="text")  # May return False

# ✅ DO: Use XPath
click_xpath("//*[@text='Submit']")  # Works reliably
```

**2. Use `dump_hierarchy()` First**
```python
# Inspect UI before writing automation
hierarchy = dump_hierarchy(max_depth=15, pretty=True)
with open("/tmp/ui.xml", "w") as f:
    f.write(hierarchy)
# Open /tmp/ui.xml to find exact element attributes
```

**3. Coordinate Clicking Auto-Fallback**
The XPath tools automatically extract coordinates and click at element center when direct interaction fails:
```python
# This happens automatically - no manual coordinate extraction needed
click_xpath("//*[@text='Button']")
# 1. Finds element via XPath
# 2. Gets bounds: [100,200][500,600]
# 3. Calculates center: (300, 400)
# 4. Clicks at center coordinates
```

**4. Partial Text Matching**
Compose often has dynamic text. Use `contains()`:
```python
# ❌ Exact match may fail if text changes
click_xpath("//*[@text='Items: 5']")

# ✅ Partial match is more robust
click_xpath("//*[contains(@text, 'Items:')]")
```

**5. Check Visibility**
```python
# Ensure element is visible before clicking
click_xpath("//*[@text='Button' and @visible-to-user='true']")
```

### Troubleshooting Compose Apps

**Problem:** `click()` returns `False`
```python
# Solution: Switch to XPath
click_xpath("//*[@text='Button Text']")
```

**Problem:** Element exists but not clickable
```python
# Solution: Find parent clickable element
click_xpath("//*[@text='Text']

/parent::node[@clickable='true']")
# Or click parent by class
click_xpath("//node[@clickable='true' and .//node[@text='Text']]")
```

**Problem:** Multiple elements with same text
```python
# Solution: Add more conditions
click_xpath("//*[@text='Submit' and @bounds='[100,200][300,400]']")
# Or use position
click_xpath("(//*[@text='Submit'])[1]")  # First match
click_xpath("(//*[@text='Submit'])[2]")  # Second match
```

**Problem:** Element not found
```python
# 1. Check if it's on screen
hierarchy = dump_hierarchy(max_depth=15)
if "Target Text" in hierarchy:
    # Element exists, may need to scroll
    scroll_forward()
    click_xpath("//*[@text='Target Text']")
else:
    print("Element not in UI hierarchy")
```

---

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_server.py

# Run specific test
pytest tests/test_server.py::test_click_xpath
```

### Test Coverage Notes
- ✅ Standard selector functions have comprehensive unit tests
- ⚠️ XPath functions (`click_xpath`, `get_element_xpath`, etc.) currently lack unit tests
- ⚠️ Integration tests for Compose vs XML view interaction are recommended
- 💡 Consider adding mock hierarchy dumps as test fixtures

### Device Connection

- uiautomator2 handles device connection via `u2.connect(device_id)`
- If `device_id` is None, connects to the first available device
- ADB must be installed and accessible in PATH
- USB debugging must be enabled on target Android devices

## Key Dependencies

- **mcp[cli]**: FastMCP framework for creating MCP servers
- **uiautomator2**: Python wrapper for Android UIAutomator testing framework
- **uiautodev**: Optional UI inspection tool for debugging Android UI
- **pytest**: Testing framework with asyncio support

## Client Configuration

### Claude Code CLI
**This repository is pre-configured** with `.claude/mcp-servers.json`. When you start Claude Code in this directory, the MCP server will be automatically available.

For global configuration or use in other projects, see [CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md).

### Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-android": {
      "type": "stdio",
      "command": "bash",
      "args": ["-c", "cd /Users/manuel.siuro/www/mcp-android-server-python && source .venv/bin/activate && python3 server.py"]
    }
  }
}
```

### VS Code Agent Mode
Create `.vscode/mcp.json` in your project:
```json
{
  "servers": {
    "mcp-android": {
      "type": "stdio",
      "command": "bash",
      "args": ["-c", "cd /Users/manuel.siuro/www/mcp-android-server-python && source .venv/bin/activate && python3 server.py"]
    }
  }
}
```

## Git Workflow & Branch Strategy

### Branch Management Rules

**IMPORTANT:** All feature development must follow this workflow:

1. **Feature Branch Required**: Create a new branch for each feature, bugfix, or enhancement
2. **User Confirmation Required**: Before merging to `main`, you MUST ask for user confirmation
3. **No Direct Main Commits**: Never commit directly to `main` branch (except initial setup)

### Workflow Steps

**For every new feature/change:**

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/descriptive-name

# Examples:
# git checkout -b feature/recording-engine
# git checkout -b feature/espresso-generator
# git checkout -b bugfix/screenshot-timeout
# git checkout -b docs/update-readme

# 2. Work on your feature
# Make changes, test, commit as needed
git add .
git commit -m "Descriptive commit message"

# 3. Push feature branch to GitHub
git push -u origin feature/descriptive-name

# 4. Request user confirmation before merge
# ASK USER: "Feature X is complete. Should I merge to main?"

# 5. After user approval, merge to main
git checkout main
git merge feature/descriptive-name
git push origin main

# 6. Delete feature branch (optional, after successful merge)
git branch -d feature/descriptive-name
git push origin --delete feature/descriptive-name
```

### Branch Naming Conventions

- `feature/` - New features (e.g., `feature/recording-engine`)
- `bugfix/` - Bug fixes (e.g., `bugfix/screenshot-crash`)
- `hotfix/` - Urgent production fixes (e.g., `hotfix/security-patch`)
- `docs/` - Documentation updates (e.g., `docs/api-reference`)
- `refactor/` - Code refactoring (e.g., `refactor/cleanup-imports`)
- `test/` - Test additions/improvements (e.g., `test/add-unit-tests`)

### Commit Message Format

Follow conventional commits:

```
<type>: <short description>

<optional detailed description>

<optional footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**
```bash
git commit -m "feat: add recording engine with action interception"
git commit -m "fix: resolve screenshot timeout on slow devices"
git commit -m "docs: update installation instructions"
git commit -m "refactor: simplify selector mapping logic"
```

### Before Merging to Main - Checklist

Before requesting merge approval, ensure:

- ✅ All tests pass (`pytest`)
- ✅ Code is linted and formatted (`ruff check . && ruff format .`)
- ✅ Documentation is updated (if needed)
- ✅ No sensitive data committed (API keys, passwords, etc.)
- ✅ Changes are committed with clear messages
- ✅ Feature branch is pushed to GitHub

### Example Workflow Conversation

```
Claude: "I've completed the recording engine feature on branch
feature/recording-engine. All tests pass and code is formatted.
Should I merge this to main?"

User: "Yes, merge it"

Claude: [Merges to main and pushes]
```

---

## Important Notes

- All tools return typed results using TypedDict definitions
- Error handling follows a pattern: try/catch with printed errors and fallback returns
- Tools use consistent parameter ordering: required params first, `device_id` always optional last
- The server runs in stdio mode by default for MCP protocol compatibility
- Boolean return values indicate success/failure for action-based tools
