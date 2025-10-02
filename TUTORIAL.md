# Android Test Automation Tutorial
## Complete Guide: Record, Replay & Generate Espresso Tests

**Use Case:** Testing the Vera app (com.centile.vera) - Login and Navigate to Contacts

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Part 1: Recording a Test Scenario](#part-1-recording-a-test-scenario)
4. [Part 2: Replaying the Scenario](#part-2-replaying-the-scenario)
5. [Part 3: Generating Espresso Tests](#part-3-generating-espresso-tests)
6. [Part 4: Using Generated Tests in Android Studio](#part-4-using-generated-tests-in-android-studio)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Tips](#advanced-tips)

---

## Prerequisites

### Required Software

1. **Python 3.10+** (tested on 3.10, 3.11, 3.12, 3.13)
2. **Android SDK** with ADB installed
3. **Android Device** (physical or emulator) with USB debugging enabled
4. **Vera App** (com.centile.vera) installed on the device
5. **Git** (for cloning the repository)

### Verify ADB Installation

```bash
# Check ADB is installed
adb version

# Should output something like:
# Android Debug Bridge version 1.0.41
```

### Check Connected Device

```bash
# List connected devices
adb devices

# Should show:
# List of devices attached
# R3CXA0B7EPD    device
```

---

## Setup

### 1. Clone and Install the MCP Android Server

```bash
# Clone the repository
git clone https://github.com/your-org/mcp-android-server-python.git
cd mcp-android-server-python

# Run automated installation
./install.sh

# Or install manually:
# python3 -m venv .venv
# source .venv/bin/activate
# pip install -e .
```

### 2. Configure ADB Path (if needed)

If ADB is not in your system PATH:

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your Android SDK path
# ANDROID_HOME=/Users/username/Library/Android/sdk
# Or set direct ADB path:
# ADB_PATH=/Users/username/Library/Android/sdk/platform-tools/adb
```

### 3. Verify Installation

```bash
# Activate virtual environment
source .venv/bin/activate

# Test the server
python3 -c "import server; print(server.check_adb_and_list_devices())"

# Should output device information
```

### 4. Start the MCP Server

```bash
# In one terminal, start the server
python3 server.py

# Server starts in MCP stdio mode
# Keep this running in the background
```

---

## Part 1: Recording a Test Scenario

### Scenario Overview

We'll record the following user flow:
1. Launch Vera app
2. Enter login credentials
3. Submit login
4. Navigate to Contacts screen
5. Save the scenario

### Step 1: Prepare the Device

```bash
# In a new terminal (with venv activated)
python3

# Import server functions
>>> import server
>>> from datetime import datetime

# Check device connection
>>> device_info = server.connect_device()
>>> print(f"Connected to {device_info['manufacturer']} {device_info['model']}")
# Connected to Google Pixel 6
```

### Step 2: Start Recording

```python
# Start recording session
>>> recording = server.start_recording(
...     session_name="vera_login_contacts",
...     description="Test Vera app login and navigate to contacts",
...     device_id=None  # Uses first connected device
... )

>>> print(recording)
# {
#   'recording_id': 'vera_login_contacts_20251002_120000',
#   'session_name': 'vera_login_contacts',
#   'start_time': '2025-10-02T12:00:00.123456',
#   'screenshots_dir': 'scenarios/vera_login_contacts_20251002_120000/screenshots',
#   'status': 'active'
# }
```

✅ **Recording is now active!** All subsequent MCP tool calls will be captured.

### Step 3: Launch the Vera App

```python
# Start the Vera app
>>> server.start_app(
...     package_name="com.centile.vera",
...     wait=True
... )
# True

# Wait for app to fully load
>>> import time
>>> time.sleep(2)
```

### Step 4: Perform Login Actions

**Important:** The Vera app may use Jetpack Compose. Always use `click_xpath()` for Compose apps.

```python
# First, inspect the UI to find login elements
>>> hierarchy = server.dump_hierarchy(pretty=True, max_depth=15)
>>> print(hierarchy[:500])  # Print first 500 chars to see structure

# Look for login field - example for Compose app:
# <node class="androidx.compose.ui.platform.ComposeView">
#   <node text="Username" bounds="[100,300][500,400]" />
# </node>

# Click on username field (adjust selector based on actual UI)
>>> server.click_xpath("//*[@text='Username' or contains(@content-desc, 'username')]")
# True

# Enter username
>>> server.send_text("testuser@example.com", clear=True)
# True

# Click on password field
>>> server.click_xpath("//*[@text='Password' or contains(@content-desc, 'password')]")
# True

# Enter password
>>> server.send_text("SecurePass123", clear=True)
# True

# Click login button
>>> server.click_xpath("//*[@text='Login' or @text='Sign In']")
# True

# Wait for login to complete
>>> time.sleep(3)
```

### Step 5: Navigate to Contacts

```python
# Method 1: If there's a bottom navigation bar (usually XML)
>>> server.click(
...     selector="fi.elisa.labsring:id/layout_contact",  # Example resource ID
...     selector_type="resourceId"
... )

# Method 2: If using Compose or text-based navigation
>>> server.click_xpath("//*[@text='Contacts']")
# True

# Wait for contacts to load
>>> time.sleep(2)

# Optional: Take a verification screenshot
>>> server.screenshot("scenarios/current_session/verification.png")
# True
```

### Step 6: Stop Recording

```python
# Stop recording and save the scenario
>>> result = server.stop_recording()
>>> print(result)
# {
#   'scenario_file': 'scenarios/vera_login_contacts_20251002_120000/scenario.json',
#   'screenshot_folder': 'scenarios/vera_login_contacts_20251002_120000/screenshots',
#   'action_count': 8,
#   'duration_ms': 15420,
#   'status': 'success'
# }

# Save the scenario path for later use
>>> scenario_file = result['scenario_file']
>>> print(f"Scenario saved to: {scenario_file}")
```

✅ **Recording complete!** Your scenario is now saved with all actions and screenshots.

### Inspect the Recorded Scenario

```bash
# View the scenario JSON
cat scenarios/vera_login_contacts_20251002_120000/scenario.json | python3 -m json.tool | head -50

# View screenshots
ls -la scenarios/vera_login_contacts_20251002_120000/screenshots/
# 001_start_app.png
# 002_click_xpath.png
# 003_send_text.png
# ...
```

---

## Part 2: Replaying the Scenario

### Why Replay?

- **Regression Testing:** Verify the scenario still works after app updates
- **Validation:** Confirm the recording is accurate before generating tests
- **Cross-Device Testing:** Run the same scenario on different devices

### Step 1: Prepare for Replay

```python
# In Python shell (with venv activated)
>>> import server

# Reset the app to initial state (optional)
>>> server.clear_app_data("com.centile.vera")
# True

# Or just stop the app
>>> server.stop_app("com.centile.vera")
# True
```

### Step 2: Run the Replay

```python
# Replay the scenario with default settings
>>> replay_result = server.replay_scenario(
...     scenario_file="scenarios/vera_login_contacts_20251002_120000/scenario.json",
...     device_id=None,
...     config={
...         "validate_ui_state": True,
...         "take_screenshots": True,
...         "stop_on_error": False,
...         "speed_multiplier": 1.0,
...         "retry_attempts": 3
...     }
... )

# Monitor progress (replay happens automatically)
# ...

>>> print(replay_result)
# {
#   'scenario': 'vera_login_contacts_20251002_120000',
#   'status': 'PASSED',
#   'duration_ms': 16230,
#   'actions_total': 8,
#   'actions_passed': 8,
#   'actions_failed': 0,
#   'report_file': 'scenarios/vera_login_contacts_20251002_120000/replay_report_20251002_120500.json'
# }
```

### Step 3: Review Replay Report

```bash
# View the detailed replay report
cat scenarios/vera_login_contacts_20251002_120000/replay_report_20251002_120500.json | python3 -m json.tool
```

**Example Report:**

```json
{
  "scenario": "vera_login_contacts_20251002_120000",
  "replayed_at": "2025-10-02T12:05:00Z",
  "status": "PASSED",
  "duration_ms": 16230,
  "actions_total": 8,
  "actions_passed": 8,
  "actions_failed": 0,
  "details": [
    {
      "action_id": 1,
      "tool": "start_app",
      "status": "PASSED",
      "execution_time_ms": 1250
    },
    {
      "action_id": 2,
      "tool": "click_xpath",
      "status": "PASSED",
      "execution_time_ms": 850
    }
    // ... more actions
  ]
}
```

✅ **Replay successful!** The scenario works correctly on the device.

### Replay with Different Speeds

```python
# Fast replay (2x speed)
>>> server.replay_scenario(
...     scenario_file="scenarios/vera_login_contacts_20251002_120000/scenario.json",
...     config={"speed_multiplier": 2.0}
... )

# Slow replay for debugging (0.5x speed)
>>> server.replay_scenario(
...     scenario_file="scenarios/vera_login_contacts_20251002_120000/scenario.json",
...     config={"speed_multiplier": 0.5}
... )
```

---

## Part 3: Generating Espresso Tests

### Step 1: Generate Kotlin Espresso Test

```python
# In Python shell
>>> import server

# Generate Kotlin test
>>> espresso_result = server.generate_espresso_code(
...     scenario_file="scenarios/vera_login_contacts_20251002_120000/scenario.json",
...     language="kotlin",
...     package_name="com.centile.vera.test",
...     class_name="VeraLoginContactsTest"
... )

>>> print(espresso_result)
# {
#   'code': '... generated Kotlin code ...',
#   'file_path': 'scenarios/vera_login_contacts_20251002_120000/generated/VeraLoginContactsTest.kt',
#   'imports': [...],
#   'ui_framework': 'compose',
#   'custom_actions': [],
#   'warnings': [],
#   'status': 'success'
# }
```

### Step 2: View Generated Test

```bash
# View the generated Kotlin test
cat scenarios/vera_login_contacts_20251002_120000/generated/VeraLoginContactsTest.kt
```

**Example Generated Kotlin Test:**

```kotlin
package com.centile.vera.test

import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.matcher.ViewMatchers.*
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Generated Espresso test from recorded scenario
 * Scenario: vera_login_contacts
 * Description: Test Vera app login and navigate to contacts
 * Generated on: 2025-10-02T12:10:00Z
 */
@RunWith(AndroidJUnit4::class)
class VeraLoginContactsTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testVeraLoginContacts() {
        // Action 1: Launch app
        // App launches automatically via activityRule

        Thread.sleep(2000)

        // Action 2: Click username field
        onView(withText("Username")).perform(click())

        // Action 3: Enter username
        onView(isFocused()).perform(clearText(), typeText("testuser@example.com"))

        // Action 4: Click password field
        onView(withText("Password")).perform(click())

        // Action 5: Enter password
        onView(isFocused()).perform(clearText(), typeText("SecurePass123"))

        // Action 6: Click login button
        onView(withText("Login")).perform(click())

        Thread.sleep(3000)

        // Action 7: Navigate to Contacts
        onView(withText("Contacts")).perform(click())

        Thread.sleep(2000)
    }
}
```

### Step 3: Generate Java Test (Alternative)

```python
# Generate Java version
>>> espresso_java = server.generate_espresso_code(
...     scenario_file="scenarios/vera_login_contacts_20251002_120000/scenario.json",
...     language="java",
...     package_name="com.centile.vera.test",
...     class_name="VeraLoginContactsTest"
... )

# View Java version
>>> print(espresso_java['file_path'])
# scenarios/vera_login_contacts_20251002_120000/generated/VeraLoginContactsTest.java
```

---

## Part 4: Using Generated Tests in Android Studio

### Step 1: Copy Test to Android Project

```bash
# Navigate to your Vera app Android project
cd /path/to/vera-android-project

# Create test directory if it doesn't exist
mkdir -p app/src/androidTest/java/com/centile/vera/test

# Copy generated test
cp /path/to/mcp-android-server-python/scenarios/vera_login_contacts_20251002_120000/generated/VeraLoginContactsTest.kt \
   app/src/androidTest/java/com/centile/vera/test/
```

### Step 2: Add Espresso Dependencies

Edit `app/build.gradle`:

```groovy
dependencies {
    // Existing dependencies...

    // Espresso dependencies
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
    androidTestImplementation 'androidx.test:runner:1.5.2'
    androidTestImplementation 'androidx.test:rules:1.5.0'
}

android {
    defaultConfig {
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }
}
```

### Step 3: Sync and Build

In Android Studio:
1. Click **Sync Now** to sync Gradle files
2. Build the project: **Build > Make Project**

### Step 4: Run the Test

**Option 1: From Android Studio**
1. Open `VeraLoginContactsTest.kt`
2. Click the green play button next to `testVeraLoginContacts()`
3. Select a connected device or emulator
4. Watch the test execute!

**Option 2: From Command Line**

```bash
# Run the specific test
./gradlew connectedAndroidTest --tests com.centile.vera.test.VeraLoginContactsTest

# Or run all instrumentation tests
./gradlew connectedAndroidTest
```

### Step 5: View Test Results

```bash
# Test report location
open app/build/reports/androidTests/connected/index.html

# Or check logs
adb logcat | grep -i "test"
```

✅ **Success!** Your generated Espresso test is now running in your Android project.

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Element Not Found During Recording

**Symptom:** `click_xpath()` or `click()` returns `False`

**Solutions:**

1. **Use `dump_hierarchy()` to inspect the UI:**
   ```python
   >>> hierarchy = server.dump_hierarchy(pretty=True, max_depth=15)
   >>> print(hierarchy)
   # Look for the actual element attributes
   ```

2. **For Compose apps, always use XPath:**
   ```python
   # ❌ Don't use for Compose:
   >>> server.click("Login", selector_type="text")

   # ✅ Do use for Compose:
   >>> server.click_xpath("//*[@text='Login']")
   ```

3. **Use partial text matching:**
   ```python
   >>> server.click_xpath("//*[contains(@text, 'Log')]")
   ```

#### Issue 2: Recording Captures Extra Actions

**Symptom:** Scenario has unexpected actions

**Solution:** Ensure you call `stop_recording()` before any cleanup:

```python
# ✅ Correct order:
>>> result = server.stop_recording()
>>> server.stop_app("com.centile.vera")  # Cleanup AFTER stopping

# ❌ Wrong order:
>>> server.stop_app("com.centile.vera")  # This gets recorded!
>>> result = server.stop_recording()
```

#### Issue 3: Replay Fails on Different Device

**Symptom:** Replay works on one device but fails on another

**Solutions:**

1. **Screen size differences - use relative coordinates:**
   - The system already uses coordinate-based clicking
   - Ensure UI elements are in the same relative positions

2. **Device-specific timing:**
   ```python
   # Adjust speed for slower devices
   >>> server.replay_scenario(
   ...     scenario_file="...",
   ...     config={"speed_multiplier": 0.5}  # Slower
   ... )
   ```

3. **Check Android version compatibility:**
   ```bash
   adb shell getprop ro.build.version.sdk
   ```

#### Issue 4: Generated Test Doesn't Compile

**Symptom:** Import errors or syntax errors in Android Studio

**Solutions:**

1. **Check package name matches:**
   ```kotlin
   // Generated test
   package com.centile.vera.test

   // Should match your app package
   ```

2. **Update imports if needed:**
   ```kotlin
   // Add any missing imports
   import androidx.test.espresso.Espresso.onView
   import androidx.test.espresso.action.ViewActions.*
   import androidx.test.espresso.matcher.ViewMatchers.*
   ```

3. **Fix MainActivity reference:**
   ```kotlin
   // Update to your actual main activity
   val activityRule = ActivityScenarioRule(YourMainActivity::class.java)
   ```

#### Issue 5: ADB Not Found

**Symptom:** `adb not found` error

**Solutions:**

1. **Set ANDROID_HOME in `.env`:**
   ```bash
   ANDROID_HOME=/Users/username/Library/Android/sdk
   ```

2. **Or add ADB to PATH:**
   ```bash
   export PATH=$PATH:/Users/username/Library/Android/sdk/platform-tools
   ```

3. **Or set direct ADB_PATH:**
   ```bash
   ADB_PATH=/Users/username/Library/Android/sdk/platform-tools/adb
   ```

---

## Advanced Tips

### Tip 1: Recording Complex Gestures

```python
# Swipe gesture
>>> server.swipe(
...     start_x=540, start_y=1500,
...     end_x=540, end_y=500,
...     duration=0.3
... )

# Long press
>>> server.long_click_xpath(
...     xpath="//*[@text='Contact Name']",
...     duration=1.5
... )

# Scroll to element
>>> server.scroll_to("Contact Name", selector_type="text")
```

### Tip 2: Handling Dynamic Content

```python
# Use contains() for partial matches
>>> server.click_xpath("//*[contains(@text, 'Loading')]")

# Wait for element to appear
>>> server.wait_xpath("//*[@text='Contacts']", timeout=15)

# Check element exists before clicking
>>> if server.wait_for_element("Submit", timeout=5):
...     server.click_xpath("//*[@text='Submit']")
```

### Tip 3: Debugging UI Issues

```python
# Take screenshot for debugging
>>> server.screenshot("/tmp/debug_screen.png")

# Get element info
>>> info = server.get_element_xpath("//*[@text='Login']")
>>> print(info)
# {'text': 'Login', 'bounds': {...}, 'clickable': True}

# Dump full hierarchy to file
>>> hierarchy = server.dump_hierarchy(pretty=True, max_depth=20)
>>> with open("/tmp/ui_hierarchy.xml", "w") as f:
...     f.write(hierarchy)
```

### Tip 4: Batch Processing Multiple Scenarios

```bash
# Create a script: run_all_scenarios.py
import server

scenarios = [
    "scenarios/vera_login_contacts_20251002_120000/scenario.json",
    "scenarios/vera_search_contacts_20251002_120100/scenario.json",
    "scenarios/vera_add_contact_20251002_120200/scenario.json"
]

for scenario_file in scenarios:
    print(f"Replaying: {scenario_file}")
    result = server.replay_scenario(scenario_file)
    print(f"Status: {result['status']}")
    print(f"Passed: {result['actions_passed']}/{result['actions_total']}")
    print("-" * 50)
```

### Tip 5: CI/CD Integration

```yaml
# .github/workflows/android-tests.yml
name: Android UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install MCP Android Server
        run: |
          cd mcp-android-server-python
          pip install -e .

      - name: Set up Android Emulator
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 33
          script: |
            # Replay all scenarios
            python3 -c "
            import server
            result = server.replay_scenario('scenarios/vera_login_contacts_20251002_120000/scenario.json')
            assert result['status'] == 'PASSED'
            "
```

---

## Summary

You've learned how to:

✅ **Record** user interactions on Android apps
✅ **Replay** scenarios for regression testing
✅ **Generate** Espresso test code automatically
✅ **Integrate** generated tests into Android Studio
✅ **Troubleshoot** common issues

### Next Steps

1. **Record More Scenarios:** Capture different user flows
2. **Create Test Suite:** Generate Espresso tests for all scenarios
3. **Automate:** Set up CI/CD pipeline with scenario replay
4. **Extend:** Add custom assertions and validations

### Resources

- [MCP Android Server Documentation](./CLAUDE.md)
- [Espresso Testing Guide](https://developer.android.com/training/testing/espresso)
- [UIAutomator2 Documentation](https://github.com/openatx/uiautomator2)

---

**Happy Testing!** 🎉

For questions or issues, please check the [Troubleshooting](#troubleshooting) section or open an issue on GitHub.
