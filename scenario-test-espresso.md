# Android Scenario Recording & Espresso Test Generation System

## Project Document Version 1.0

**Author:** Research & Architecture Analysis
**Date:** October 2025
**Status:** Planning & Design Phase

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Market Research & Existing Solutions](#market-research--existing-solutions)
4. [Project Goals & Objectives](#project-goals--objectives)
5. [Technical Requirements](#technical-requirements)
6. [System Architecture](#system-architecture)
7. [Recording Mechanism Design](#recording-mechanism-design)
8. [Replay Mechanism Design](#replay-mechanism-design)
9. [Espresso Code Generation](#espresso-code-generation)
10. [MCP Server Integration](#mcp-server-integration)
11. [Implementation Phases](#implementation-phases)
12. [Technical Challenges & Solutions](#technical-challenges--solutions)
13. [Future Enhancements](#future-enhancements)
14. [Conclusion](#conclusion)

---

## Executive Summary

This document outlines the design and architecture for an **Android Scenario Recording & Espresso Test Generation System** that captures user interactions on Android devices, stores them as replayable scenarios, and automatically generates Espresso test code for integration into Android projects.

The system leverages the existing **MCP Android Agent** (based on uiautomator2) to record UI interactions, captures visual evidence (screenshots/video), and provides multiple output formats:
- **JSON scenario files** for replay within the MCP system
- **Espresso test code** (Java/Kotlin) for integration into Android Studio projects
- **Visual documentation** (screenshot sequences or screen recordings)

### Key Innovations

1. **Hybrid Recording Approach**: Combines event-based recording (action logs) with visual recording (screenshots/video)
2. **Multi-Format Output**: Generates both MCP-compatible scenarios and native Espresso test code
3. **Intelligent Mapping**: Translates UIAutomator2 actions to Espresso ViewMatchers and ViewActions
4. **Visual Validation**: Captures UI state at each step for debugging and documentation
5. **MCP Integration**: Seamlessly extends the existing MCP Android server

---

## Problem Statement

### Current Challenges

1. **Manual Test Creation**: Writing UI tests manually is time-consuming and error-prone
2. **Knowledge Barrier**: Creating Espresso tests requires deep framework knowledge
3. **Test Maintenance**: Tests break when UI changes, requiring constant updates
4. **Documentation Gap**: Test scenarios lack visual documentation of expected UI states
5. **Tool Fragmentation**: Existing tools (Espresso Test Recorder) only work within Android Studio and have limitations:
   - Cannot test external apps
   - Limited assertion capabilities
   - No support for cross-app workflows
   - No integration with external automation systems

### User Needs

**QA Engineers** need:
- Quick scenario recording without code knowledge
- Ability to test any app (not just their own)
- Visual documentation of test scenarios
- Easy replay for regression testing

**Android Developers** need:
- Generated Espresso code they can customize
- Integration with existing test suites
- Support for Jetpack Compose and XML views
- Maintainable test code with clear selectors

**Automation Engineers** need:
- Programmatic scenario execution via MCP
- JSON-based scenario storage for version control
- Integration with CI/CD pipelines
- Cross-platform compatibility (Python/AI agent control)

---

## Market Research & Existing Solutions

### 1. Espresso Test Recorder (Google Official)

**Description:** Built into Android Studio, records interactions and generates Espresso test code.

**Strengths:**
- Official tool with IDE integration
- Generates Espresso code directly
- Supports assertions

**Limitations:**
- Only works for the app being developed (cannot test other apps)
- Requires Android Studio
- Limited XPath support
- No support for complex gestures
- Cannot capture cross-app workflows
- Limited to single device testing

**Reference:** [Android Studio Test Recorder](https://developer.android.com/studio/test/other-testing-tools/espresso-test-recorder)

### 2. Android Test Recorder (Open Source)

**Description:** An open-source project that runs on the phone and works with Compose and Flutter apps.

**Strengths:**
- Works with modern UI frameworks (Compose)
- Runs on device
- Open source

**Limitations:**
- Limited community support
- No Espresso code generation
- Primarily focused on recording, not replay

**Reference:** [GitHub - xuduo/Android-Test-Recorder](https://github.com/xuduo/Android-Test-Recorder)

### 3. Appium + Espresso Driver

**Description:** Appium's Espresso driver allows cross-platform test automation.

**Strengths:**
- Cross-platform (iOS/Android)
- Supports multiple languages
- Large community

**Limitations:**
- Complex setup
- No built-in recording
- Requires Appium server infrastructure
- Different API from native Espresso

### 4. Commercial Tools (Testsigma, Ranorex, BrowserStack)

**Description:** Cloud-based or desktop applications with record-and-playback features.

**Strengths:**
- User-friendly interfaces
- Cloud device farms
- Advanced reporting

**Limitations:**
- Expensive (subscription-based)
- Vendor lock-in
- Generated code often proprietary
- Limited customization
- No MCP integration

### Market Gap

**None of the existing solutions provide:**
- ✗ Recording via remote API/MCP protocol
- ✗ AI agent-driven test creation
- ✗ Both JSON scenarios AND Espresso code output
- ✗ Free, open-source, self-hosted solution
- ✗ Integration with modern AI workflows
- ✗ UIAutomator2 + Espresso hybrid approach

**Our Solution Fills This Gap.**

---

## Project Goals & Objectives

### Primary Goals

1. **Record Android UI Interactions**: Capture user actions (clicks, swipes, text input) as structured data
2. **Generate Replayable Scenarios**: Create JSON files that can replay the exact same scenario
3. **Produce Espresso Test Code**: Automatically generate Java/Kotlin Espresso tests
4. **Visual Documentation**: Capture screenshots or video during recording for validation
5. **MCP Integration**: Extend the existing MCP Android server with recording capabilities

### Success Criteria

- ✅ Record at least 90% of common UI interactions (click, swipe, scroll, text input)
- ✅ Replay recorded scenarios with 95%+ accuracy
- ✅ Generate valid, compilable Espresso test code
- ✅ Capture visual evidence at each step
- ✅ Support both XML views and Jetpack Compose
- ✅ Process scenarios via MCP protocol (AI agent-friendly)
- ✅ Export scenarios to Android Studio projects

### Non-Goals (Out of Scope for v1.0)

- ❌ Real-time device mirroring/control UI
- ❌ Test execution within the tool (tests run in Android Studio/Gradle)
- ❌ Complex gesture recording (multi-touch, pinch-zoom) - basic gestures only
- ❌ Performance testing or load testing
- ❌ Network traffic recording/mocking
- ❌ iOS support (Android only)

---

## Technical Requirements

### Functional Requirements

1. **Recording**
   - FR-1: System shall record click actions with target element selectors
   - FR-2: System shall record swipe gestures with coordinates
   - FR-3: System shall record text input with field identification
   - FR-4: System shall record scroll actions
   - FR-5: System shall capture screenshots at each interaction
   - FR-6: System shall record app transitions (start_app, press_key)
   - FR-7: System shall capture UI hierarchy at each step

2. **Storage**
   - FR-8: System shall save scenarios in JSON format
   - FR-9: System shall store screenshots with timestamps
   - FR-10: System shall support scenario metadata (name, description, device info)
   - FR-11: System shall version scenario format for backward compatibility

3. **Replay**
   - FR-12: System shall replay scenarios from JSON files
   - FR-13: System shall validate UI state before each action (optional)
   - FR-14: System shall generate replay reports with pass/fail status
   - FR-15: System shall handle timing/synchronization automatically

4. **Code Generation**
   - FR-16: System shall generate Espresso test classes (Java/Kotlin)
   - FR-17: System shall map UIAutomator selectors to Espresso ViewMatchers
   - FR-18: System shall generate assertions based on UI state
   - FR-19: System shall include setup and teardown methods
   - FR-20: System shall generate Gradle-compatible test structure

### Non-Functional Requirements

1. **Performance**
   - NFR-1: Recording shall not introduce noticeable lag (<100ms per action)
   - NFR-2: Screenshot capture shall complete within 500ms
   - NFR-3: Scenario replay shall execute actions at configurable speed

2. **Reliability**
   - NFR-4: System shall handle app crashes gracefully
   - NFR-5: System shall recover from device disconnections
   - NFR-6: Recorded scenarios shall be deterministic (reproducible)

3. **Usability**
   - NFR-7: JSON scenario format shall be human-readable
   - NFR-8: Generated Espresso code shall follow Android best practices
   - NFR-9: System shall provide clear error messages

4. **Compatibility**
   - NFR-10: Support Android 7.0+ (API 24+)
   - NFR-11: Support both XML and Compose UI frameworks
   - NFR-12: Generated code shall be compatible with AndroidX Test libraries

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Android Server                          │
│                     (Python + FastMCP)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │   Recording    │  │     Replay     │  │  Code Generator  │  │
│  │    Engine      │  │    Engine      │  │    (Espresso)    │  │
│  └────────┬───────┘  └────────┬───────┘  └─────────┬────────┘  │
│           │                   │                     │            │
│           └───────────────────┴─────────────────────┘            │
│                              │                                   │
│                   ┌──────────▼──────────┐                        │
│                   │  Scenario Storage   │                        │
│                   │   (JSON + Images)   │                        │
│                   └─────────────────────┘                        │
│                                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  uiautomator2    │
                    │   (Python lib)   │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Android Device  │
                    │  (ADB + ATX)     │
                    └──────────────────┘
```

### Component Breakdown

#### 1. Recording Engine

**Responsibilities:**

- Intercept MCP tool calls during recording mode
- Log action metadata (tool name, parameters, timestamp)
- Capture UI hierarchy before each action
- Take screenshots after each action
- Store events in memory buffer
- Serialize to JSON on recording stop

**Key Classes:**

```python
class ScenarioRecorder:
    def start_recording(session_name: str) -> str
    def stop_recording() -> ScenarioFile
    def capture_action(tool_name: str, params: dict, result: any) -> None
    def take_screenshot() -> str
    def dump_ui_state() -> dict
```

#### 2. Replay Engine

**Responsibilities:**

- Load scenario JSON files
- Parse action sequence
- Execute actions via MCP tools
- Validate UI state (optional)
- Generate replay report
- Handle errors and retries

**Key Classes:**

```python
class ScenarioPlayer:
    def load_scenario(file_path: str) -> Scenario
    def replay(scenario: Scenario, config: ReplayConfig) -> ReplayReport
    def execute_action(action: Action) -> ActionResult
    def validate_state(expected_state: dict) -> bool
```

#### 3. Code Generator (Espresso)

**Responsibilities:**

- Parse scenario JSON
- Map UIAutomator actions to Espresso syntax
- Generate test class structure
- Create ViewMatchers from selectors
- Generate ViewActions and ViewAssertions
- Format code (Java or Kotlin)
- Add imports and annotations

**Key Classes:**

```python
class EspressoCodeGenerator:
    def generate(scenario: Scenario, language: str) -> str
    def map_action_to_espresso(action: Action) -> str
    def create_view_matcher(selector: dict) -> str
    def generate_test_method(actions: List[Action]) -> str
    def format_code(code: str, language: str) -> str
```

#### 4. Scenario Storage

**Responsibilities:**

- Persist scenarios to disk
- Organize screenshots in folders
- Version scenario format
- Support import/export

**Directory Structure:**

```
scenarios/
├── login_flow_20250101_143022/
│   ├── scenario.json
│   ├── metadata.json
│   ├── screenshots/
│   │   ├── 001_start.png
│   │   ├── 002_after_click_login.png
│   │   ├── 003_after_input_username.png
│   │   └── ...
│   └── generated/
│       ├── LoginFlowTest.java
│       └── LoginFlowTest.kt
└── ...
```

---

## Recording Mechanism Design

### Recording Workflow

```
User Initiates Recording
         │
         ▼
  [start_recording]
         │
         ▼
  Recording Mode Active
         │
         ├──► User performs actions on device
         │    │
         │    ├──► MCP tool called (e.g., click)
         │    │         │
         │    │         ├──► Capture action metadata
         │    │         ├──► Dump UI hierarchy
         │    │         ├──► Execute action
         │    │         └──► Take screenshot
         │    │
         │    └──► Repeat for each action
         │
         ▼
  [stop_recording]
         │
         ├──► Serialize to JSON
         ├──► Save screenshots
         └──► Return scenario file path
```

### Scenario JSON Schema

```json
{
  "schema_version": "1.0",
  "metadata": {
    "name": "Login Flow Test",
    "description": "Test user login with valid credentials",
    "created_at": "2025-01-01T14:30:22Z",
    "device": {
      "manufacturer": "Google",
      "model": "Pixel 6",
      "android_version": "13",
      "sdk": 33
    },
    "duration_ms": 15420
  },
  "setup": {
    "app_package": "com.example.app",
    "start_activity": ".MainActivity",
    "clear_data": false
  },
  "actions": [
    {
      "id": 1,
      "timestamp": "2025-01-01T14:30:25Z",
      "tool": "click",
      "params": {
        "selector": "Login",
        "selector_type": "text",
        "device_id": null
      },
      "result": true,
      "ui_state": {
        "activity": ".MainActivity",
        "hierarchy_snapshot": "xml_content_truncated"
      },
      "screenshot": "screenshots/001_click_login.png",
      "delay_before_ms": 0,
      "delay_after_ms": 1000
    },
    {
      "id": 2,
      "timestamp": "2025-01-01T14:30:27Z",
      "tool": "send_text",
      "params": {
        "text": "testuser@example.com",
        "clear": true,
        "device_id": null
      },
      "result": true,
      "ui_state": {
        "activity": ".LoginActivity",
        "focused_element": {
          "resource_id": "com.example.app:id/username_field",
          "text": "",
          "content_desc": "Username"
        }
      },
      "screenshot": "screenshots/002_input_username.png",
      "delay_before_ms": 500,
      "delay_after_ms": 500
    },
    {
      "id": 3,
      "timestamp": "2025-01-01T14:30:29Z",
      "tool": "click_xpath",
      "params": {
        "xpath": "//*[@text='Submit']",
        "timeout": 10,
        "device_id": null
      },
      "result": true,
      "ui_state": {
        "activity": ".LoginActivity"
      },
      "screenshot": "screenshots/003_click_submit.png",
      "delay_before_ms": 1000,
      "delay_after_ms": 2000
    }
  ],
  "assertions": [
    {
      "action_id": 3,
      "type": "element_exists",
      "params": {
        "selector": "Welcome",
        "selector_type": "text"
      },
      "description": "Welcome message appears after login"
    }
  ],
  "teardown": {
    "stop_app": true,
    "clear_data": false
  }
}
```

### Action Types Supported

| MCP Tool | Parameters Recorded | Espresso Equivalent |
|----------|-------------------|---------------------|
| `click` | selector, selector_type | `onView(withText()).perform(click())` |
| `click_xpath` | xpath | `onView(withText()).perform(click())` |
| `click_at` | x, y | `onView().perform(clickXY())` (custom) |
| `send_text` | text, clear | `onView().perform(replaceText())` |
| `swipe` | start_x, start_y, end_x, end_y | `onView().perform(swipeLeft())` |
| `scroll_to` | selector | `onView().perform(scrollTo())` |
| `long_click` | selector | `onView().perform(longClick())` |
| `press_key` | key | `pressBack()` or `pressKey()` |
| `start_app` | package_name | Launch intent |
| `wait_for_element` | selector, timeout | `onView().check(matches(isDisplayed()))` |

### Screenshot Management

**Timing:**
- Capture AFTER each action completes
- Before assertions/validations
- On errors (for debugging)

**Storage:**
- PNG format (lossless)
- Named sequentially: `{action_id}_{action_type}.png`
- Organized in scenario-specific folders
- Optionally compressed for storage efficiency

**Alternative: Video Recording**
- Use `adb shell screenrecord` for continuous recording
- Post-process to extract key frames at action timestamps
- Pros: Complete visual record, no missed states
- Cons: Larger file size, requires post-processing

**Recommendation:** Start with screenshots (simpler), add video option later

---

## Replay Mechanism Design

### Replay Workflow

```
Load Scenario JSON
         │
         ▼
  Parse Metadata & Setup
         │
         ├──► Connect to device
         ├──► Start app (if specified)
         └──► Clear data (if specified)
         │
         ▼
  For each action in sequence:
         │
         ├──► Apply delay_before
         ├──► Validate UI state (optional)
         ├──► Execute MCP tool with params
         ├──► Verify result
         ├──► Apply delay_after
         ├──► Take screenshot (comparison)
         └──► Log outcome
         │
         ▼
  Run assertions
         │
         ▼
  Execute teardown
         │
         ▼
  Generate replay report
```

### Replay Configuration

```python
class ReplayConfig:
    device_id: Optional[str] = None
    validate_ui_state: bool = True  # Check UI matches recorded state
    take_screenshots: bool = True   # Capture for comparison
    continue_on_error: bool = False # Stop or continue on failure
    speed_multiplier: float = 1.0   # Replay speed (1.0 = normal)
    timeout_multiplier: float = 1.0 # Adjust timeouts
    compare_screenshots: bool = False # Visual regression testing
```

### Replay Report

```json
{
  "scenario": "login_flow_20250101_143022",
  "replayed_at": "2025-01-02T10:15:30Z",
  "device": "Pixel_6_Emulator",
  "status": "PASSED",
  "duration_ms": 16230,
  "actions_total": 8,
  "actions_passed": 8,
  "actions_failed": 0,
  "actions_skipped": 0,
  "details": [
    {
      "action_id": 1,
      "status": "PASSED",
      "execution_time_ms": 1250,
      "screenshot_match": 0.98,
      "errors": []
    },
    {
      "action_id": 2,
      "status": "PASSED",
      "execution_time_ms": 850,
      "screenshot_match": 0.95,
      "errors": []
    }
  ],
  "assertions": [
    {
      "description": "Welcome message appears",
      "status": "PASSED"
    }
  ]
}
```

---

## Espresso Code Generation

### Mapping Strategy

#### UIAutomator Selector → Espresso ViewMatcher

| UIAutomator | Parameters | Espresso Equivalent |
|-------------|-----------|---------------------|
| text selector | `selector="Login"` | `withText("Login")` |
| resourceId | `selector="app:id/btn"` | `withId(R.id.btn)` |
| description | `selector="Submit button"` | `withContentDescription("Submit button")` |
| xpath (text) | `xpath="//*[@text='Login']"` | `withText("Login")` |
| xpath (id) | `xpath="//*[@resource-id='app:id/btn']"` | `withId(R.id.btn)` |
| coordinates | `x=540, y=1200` | Custom `clickXY()` ViewAction |

#### UIAutomator Action → Espresso ViewAction

| UIAutomator | Espresso |
|-------------|----------|
| `click()` | `perform(click())` |
| `long_click()` | `perform(longClick())` |
| `send_text(text, clear=True)` | `perform(clearText(), typeText(text))` |
| `send_text(text, clear=False)` | `perform(typeText(text))` |
| `swipe(x1, y1, x2, y2)` | `perform(swipeLeft())` or custom |
| `scroll_to()` | `perform(scrollTo())` |
| `press_key("back")` | `Espresso.pressBack()` |

### Generated Code Structure (Java)

```java
package com.example.app;

import androidx.test.ext.junit.rules.ActivityScenarioRule;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.espresso.Espresso;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;

import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.*;
import static androidx.test.espresso.assertion.ViewAssertions.*;
import static androidx.test.espresso.matcher.ViewMatchers.*;

/**
 * Generated Espresso test from recorded scenario
 * Scenario: Login Flow Test
 * Generated on: 2025-01-01T14:35:00Z
 *
 * Original scenario file: scenarios/login_flow_20250101_143022/scenario.json
 */
@RunWith(AndroidJUnit4.class)
public class LoginFlowTest {

    @Rule
    public ActivityScenarioRule<MainActivity> activityRule =
        new ActivityScenarioRule<>(MainActivity.class);

    @Test
    public void testLoginFlow() {
        // Action 1: Click on Login button
        onView(withText("Login"))
            .perform(click());

        // Wait for UI to stabilize
        try { Thread.sleep(1000); } catch (InterruptedException e) {}

        // Action 2: Enter username
        onView(withContentDescription("Username"))
            .perform(clearText(), typeText("testuser@example.com"));

        // Action 3: Click Submit button
        onView(withText("Submit"))
            .perform(click());

        // Wait for login to complete
        try { Thread.sleep(2000); } catch (InterruptedException e) {}

        // Assertion: Verify welcome message appears
        onView(withText("Welcome"))
            .check(matches(isDisplayed()));
    }
}
```

### Generated Code Structure (Kotlin)

```kotlin
package com.example.app

import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.*
import androidx.test.espresso.matcher.ViewMatchers.*
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Generated Espresso test from recorded scenario
 * Scenario: Login Flow Test
 * Generated on: 2025-01-01T14:35:00Z
 *
 * Original scenario file: scenarios/login_flow_20250101_143022/scenario.json
 */
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testLoginFlow() {
        // Action 1: Click on Login button
        onView(withText("Login"))
            .perform(click())

        // Wait for UI to stabilize
        Thread.sleep(1000)

        // Action 2: Enter username
        onView(withContentDescription("Username"))
            .perform(clearText(), typeText("testuser@example.com"))

        // Action 3: Click Submit button
        onView(withText("Submit"))
            .perform(click())

        // Wait for login to complete
        Thread.sleep(2000)

        // Assertion: Verify welcome message appears
        onView(withText("Welcome"))
            .check(matches(isDisplayed()))
    }
}
```

### Code Generation Challenges & Solutions

#### Challenge 1: Resource ID Mapping

**Problem:** UIAutomator uses full package names (`com.example.app:id/login_btn`), but Espresso uses `R.id.login_btn`.

**Solution:**
- Parse resource ID to extract just the ID part
- Generate `withId(R.id.login_btn)` syntax
- Add comment with original full ID for reference
- Provide mapping guide for developers

#### Challenge 2: XPath to ViewMatcher

**Problem:** Espresso doesn't support XPath directly.

**Solution:**
- Parse XPath to extract matching strategy
- Simple cases: `//*[@text='X']` → `withText("X")`
- Complex cases: Add comment explaining XPath, suggest manual refinement
- For coordinate-based XPath fallback, use `clickXY()` custom action

#### Challenge 3: Compose Support

**Problem:** Compose views don't work with standard ViewMatchers.

**Solution:**
- Detect Compose views from UI hierarchy (class name contains "Compose")
- Generate Compose test code separately using `onNodeWithText()` etc.
- Add flag in scenario metadata: `ui_framework: "compose"`
- Generate separate test file for Compose tests

#### Challenge 4: Timing/Synchronization

**Problem:** `Thread.sleep()` is bad practice in tests.

**Solution:**
- Generate `IdlingResource` suggestions in comments
- Recommend replacing sleeps with proper synchronization
- Add optional Espresso Idling Resource imports
- Provide best practices document

### Custom ViewActions for Edge Cases

Some actions don't have direct Espresso equivalents:

```java
// Custom action for coordinate-based clicks
public static ViewAction clickXY(final int x, final int y) {
    return new GeneralClickAction(
        Tap.SINGLE,
        view -> {
            int[] screenPos = new int[2];
            view.getLocationOnScreen(screenPos);
            float screenX = screenPos[0] + x;
            float screenY = screenPos[1] + y;
            return new float[]{screenX, screenY};
        },
        Press.FINGER
    );
}

// Custom action for swipe with specific coordinates
public static ViewAction swipeFromTo(int x1, int y1, int x2, int y2) {
    return new GeneralSwipeAction(
        Swipe.FAST,
        // ... implementation
    );
}
```

These custom actions will be included in generated test files when needed.

---

## MCP Server Integration

### New MCP Tools

#### 1. `start_recording`

```python
@mcp.tool(
    name="start_recording",
    description="Start recording Android UI interactions as a test scenario"
)
def start_recording(
    scenario_name: str,
    description: Optional[str] = None,
    device_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Start recording mode for capturing UI interactions.

    Args:
        scenario_name: Name for this test scenario
        description: Optional description of what this scenario tests
        device_id: Optional specific device to record from

    Returns:
        recording_id: Unique ID for this recording session
        start_time: Timestamp when recording started
        device_info: Information about the recording device
    """
```

#### 2. `stop_recording`

```python
@mcp.tool(
    name="stop_recording",
    description="Stop recording and save the scenario"
)
def stop_recording(
    recording_id: str,
    generate_espresso: bool = True,
    language: str = "java"
) -> Dict[str, Any]:
    """
    Stop recording and save the scenario.

    Args:
        recording_id: ID from start_recording
        generate_espresso: Whether to generate Espresso test code
        language: "java" or "kotlin" for generated code

    Returns:
        scenario_file: Path to saved scenario JSON
        screenshot_folder: Path to screenshots
        espresso_file: Path to generated test code (if requested)
        action_count: Number of actions recorded
        duration_ms: Total recording duration
    """
```

#### 3. `replay_scenario`

```python
@mcp.tool(
    name="replay_scenario",
    description="Replay a recorded scenario on a device"
)
def replay_scenario(
    scenario_file: str,
    device_id: Optional[str] = None,
    validate_ui: bool = True,
    take_screenshots: bool = True
) -> Dict[str, Any]:
    """
    Replay a previously recorded scenario.

    Args:
        scenario_file: Path to scenario JSON file
        device_id: Optional specific device (default: any connected device)
        validate_ui: Whether to validate UI state matches recording
        take_screenshots: Whether to capture screenshots during replay

    Returns:
        status: "PASSED" or "FAILED"
        duration_ms: Replay execution time
        actions_executed: Number of actions executed
        report_file: Path to detailed replay report
    """
```

#### 4. `generate_espresso_code`

```python
@mcp.tool(
    name="generate_espresso_code",
    description="Generate Espresso test code from a recorded scenario"
)
def generate_espresso_code(
    scenario_file: str,
    language: str = "java",
    package_name: Optional[str] = None,
    class_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate Espresso test code from scenario.

    Args:
        scenario_file: Path to scenario JSON
        language: "java" or "kotlin"
        package_name: Target package (default: from scenario metadata)
        class_name: Test class name (default: scenario name)

    Returns:
        code: Generated test code as string
        file_path: Path where code was saved
        warnings: List of manual adjustments needed
    """
```

#### 5. `list_scenarios`

```python
@mcp.tool(
    name="list_scenarios",
    description="List all recorded scenarios"
)
def list_scenarios() -> List[Dict[str, Any]]:
    """
    List all available recorded scenarios.

    Returns:
        List of scenario metadata (name, date, action count, etc.)
    """
```

### Integration Architecture

```
┌──────────────────────────────────────────┐
│         AI Agent / Claude Code           │
└─────────────────┬────────────────────────┘
                  │ MCP Protocol
┌─────────────────▼────────────────────────┐
│       MCP Android Server (Extended)      │
│                                           │
│  ┌──────────────────────────────────┐   │
│  │  Recording Manager               │   │
│  │  - Global recording state        │   │
│  │  - Action interceptor            │   │
│  │  - Event buffer                  │   │
│  └──────────────────────────────────┘   │
│                                           │
│  Existing Tools      New Tools            │
│  ┌──────────────┐   ┌─────────────────┐ │
│  │ click()      │   │ start_recording │ │
│  │ send_text()  │───│ stop_recording  │ │
│  │ screenshot() │   │ replay_scenario │ │
│  │ ...          │   └─────────────────┘ │
│  └──────────────┘                        │
└───────────────────────────────────────────┘
```

### Recording Interception Mechanism

```python
# Decorator to intercept tool calls during recording
def recordable(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if recording is active
        if RecordingManager.is_recording():
            # Capture action metadata
            action_data = {
                "tool": func.__name__,
                "params": {
                    "args": args,
                    "kwargs": kwargs
                },
                "timestamp": datetime.now().isoformat()
            }

            # Take screenshot before (optional)
            if RecordingManager.config.screenshot_before:
                action_data["screenshot_before"] = screenshot()

            # Dump UI state
            action_data["ui_state"] = dump_hierarchy()

            # Execute the actual tool
            result = func(*args, **kwargs)
            action_data["result"] = result

            # Take screenshot after
            if RecordingManager.config.screenshot_after:
                action_data["screenshot"] = screenshot()

            # Store action in recording buffer
            RecordingManager.add_action(action_data)

            return result
        else:
            # Normal execution when not recording
            return func(*args, **kwargs)

    return wrapper

# Apply to all action tools
@mcp.tool(...)
@recordable
def click(...):
    ...
```

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)

**Goals:**

- Set up project structure
- Define JSON schema
- Implement recording infrastructure

**Tasks:**

1. Create `RecordingManager` class
2. Implement action interceptor/decorator
3. Design and validate JSON schema
4. Set up scenario storage system
5. Add `start_recording` and `stop_recording` tools
6. Write unit tests for recording

**Deliverables:**

- ✅ Can start/stop recording
- ✅ Actions logged to JSON
- ✅ Basic metadata captured

### Phase 2: Core Recording (Weeks 3-4)

**Goals:**

- Capture all action types
- Implement screenshot management
- Test recording on real devices

**Tasks:**

1. Add `@recordable` decorator to all action tools
2. Implement screenshot capture integration
3. Add UI hierarchy dumping to actions
4. Handle timing/delays between actions
5. Test recording complex scenarios
6. Optimize screenshot storage

**Deliverables:**

- ✅ Full recording of click, swipe, text input, scroll
- ✅ Screenshots saved with each action
- ✅ UI state captured

### Phase 3: Replay Mechanism (Weeks 5-6)

**Goals:**

- Implement scenario replay
- Add validation and error handling
- Generate replay reports

**Tasks:**

1. Create `ScenarioPlayer` class
2. Implement JSON parsing and validation
3. Add action execution with delays
4. Implement optional UI state validation
5. Generate replay reports
6. Add error recovery mechanisms

**Deliverables:**

- ✅ `replay_scenario` tool working
- ✅ Can replay recorded scenarios
- ✅ Generates pass/fail reports

### Phase 4: Espresso Code Generation (Weeks 7-9)

**Goals:**

- Generate valid Espresso test code
- Handle Java and Kotlin
- Map UIAutomator to Espresso

**Tasks:**

1. Create `EspressoCodeGenerator` class
2. Implement action → ViewAction mapping
3. Implement selector → ViewMatcher mapping
4. Generate test class structure
5. Add imports and annotations
6. Format code properly
7. Handle edge cases (coordinates, XPath, etc.)
8. Generate both Java and Kotlin variants

**Deliverables:**

- ✅ `generate_espresso_code` tool working
- ✅ Generates compilable Java/Kotlin code
- ✅ Code follows Android best practices

### Phase 5: Integration & Polish (Weeks 10-12)

**Goals:**

- End-to-end testing
- Documentation
- Performance optimization
- Bug fixes

**Tasks:**

1. Test full workflow: record → replay → generate code
2. Test on multiple devices and Android versions
3. Test with various apps (XML and Compose)
4. Write comprehensive documentation
5. Create example scenarios
6. Optimize performance (screenshot compression, etc.)
7. Add CLI tools for standalone usage
8. Create tutorial videos/guides

**Deliverables:**

- ✅ Complete, tested system
- ✅ Documentation
- ✅ Example scenarios
- ✅ Ready for release

### Phase 6: Advanced Features (Future)

**Goals:**

- Video recording
- Visual regression testing
- Compose-specific code generation
- AI-powered test generation

**Tasks:**

- Integrate video recording via `screenrecord`
- Implement screenshot comparison algorithms
- Add Compose test generation
- AI suggestions for assertions
- Test data parameterization
- Cloud storage integration

---

## Technical Challenges & Solutions

### Challenge 1: Selector Reliability

**Problem:** UI elements may not have stable IDs or text, causing replay failures.

**Solutions:**

1. **Multi-Strategy Selectors**: Store multiple ways to find element (text, ID, description, XPath)
2. **Fallback Chain**: Try selectors in order until one works
3. **Fuzzy Matching**: Allow partial text matches (contains instead of exact)
4. **Visual Anchoring**: Use relative positioning ("element below X")
5. **AI-Assisted Healing**: Use AI to suggest alternative selectors when one fails

**Implementation:**

```json
{
  "selector_strategies": [
    {"type": "resourceId", "value": "com.app:id/login_btn", "priority": 1},
    {"type": "text", "value": "Log In", "priority": 2},
    {"type": "description", "value": "Login button", "priority": 3},
    {"type": "xpath", "value": "//android.widget.Button[@text='Log In']", "priority": 4}
  ]
}
```

### Challenge 2: Timing and Synchronization

**Problem:** App animations, network delays, and loading states cause timing issues.

**Solutions:**

1. **Smart Waits**: Record implicit waits automatically
2. **Element Polling**: Wait until element is visible/clickable before acting
3. **Configurable Delays**: Allow users to adjust delays during replay
4. **Idling Resources**: Generate Espresso IdlingResource code
5. **Retry Logic**: Automatically retry failed actions with backoff

**Implementation:**

```python
def execute_action_with_retry(action, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = execute_action(action)
            if result:
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1 * (attempt + 1))  # Exponential backoff
            else:
                raise
```

### Challenge 3: Jetpack Compose Support

**Problem:** Compose views have different structure and don't work with ViewMatchers.

**Solutions:**

1. **UI Framework Detection**: Analyze hierarchy to detect Compose
2. **Separate Code Path**: Generate Compose-specific test code
3. **Semantic Selectors**: Use Compose semantics properties
4. **Hybrid Tests**: Support apps with both XML and Compose

**Generated Compose Test:**

```kotlin
@Test
fun testLoginFlow() {
    composeTestRule.onNodeWithText("Login")
        .performClick()

    composeTestRule.onNodeWithContentDescription("Username")
        .performTextInput("testuser@example.com")

    composeTestRule.onNodeWithText("Submit")
        .performClick()

    composeTestRule.onNodeWithText("Welcome")
        .assertIsDisplayed()
}
```

### Challenge 4: Cross-App Workflows

**Problem:** Tests may need to interact with system UI or other apps (e.g., permissions, file picker).

**Solutions:**

1. **UIAutomator Integration**: Generate UIAutomator code for system interactions
2. **Hybrid Tests**: Mix Espresso (in-app) and UIAutomator (system)
3. **Intent Stubbing**: Generate intent stubbing code for isolated testing
4. **Clear Annotations**: Mark cross-app actions in generated code

**Example:**

```java
// For in-app actions: Espresso
onView(withId(R.id.upload_button)).perform(click());

// For system UI: UIAutomator
UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
UiObject allowButton = device.findObject(new UiSelector().text("Allow"));
allowButton.click();

// Back to in-app: Espresso
onView(withText("File uploaded")).check(matches(isDisplayed()));
```

### Challenge 5: Test Data Management

**Problem:** Tests need different data for each run (usernames, etc.).

**Solutions:**

1. **Parameterization**: Extract input data to test method parameters
2. **Data-Driven Tests**: Generate `@ParameterizedTest` code
3. **Placeholders**: Use `{{username}}` placeholders in scenarios
4. **Test Data Files**: Generate separate JSON/CSV test data files

**Example:**

```java
@ParameterizedTest
@CsvSource({
    "user1@example.com, password123, Welcome user1",
    "user2@example.com, pass456, Welcome user2"
})
void testLogin(String username, String password, String expectedWelcome) {
    onView(withId(R.id.username)).perform(typeText(username));
    onView(withId(R.id.password)).perform(typeText(password));
    onView(withId(R.id.login_btn)).perform(click());
    onView(withText(expectedWelcome)).check(matches(isDisplayed()));
}
```

### Challenge 6: Generated Code Quality

**Problem:** Auto-generated code may not follow best practices.

**Solutions:**

1. **Code Templates**: Use well-structured templates
2. **Code Formatting**: Run formatter (google-java-format, ktlint)
3. **Comments**: Add helpful comments explaining actions
4. **TODOs**: Mark sections needing manual adjustment
5. **Best Practices Doc**: Provide guide on improving generated code

**Generated Code Features:**

- Proper indentation and spacing
- Javadoc/KDoc comments
- Import organization
- Descriptive variable names
- Action comments linking to original scenario

---

## Future Enhancements

### Phase 2 Features (After v1.0)

1. **Video Recording Integration**
   - Use `adb shell screenrecord` to capture full video
   - Extract frames at action timestamps
   - Provide video playback alongside scenario
   - Visual regression testing by comparing video frames

2. **Visual Regression Testing**
   - Compare screenshots during replay to originals
   - Perceptual diff algorithms (SSIM, MSE)
   - Highlight visual differences
   - Configurable tolerance thresholds

3. **AI-Powered Test Improvement**
   - GPT/Claude integration for generating assertions
   - Suggest additional test cases based on scenario
   - Auto-heal broken selectors using AI
   - Generate test descriptions automatically

4. **Compose-First Code Generation**
   - Detect Compose apps automatically
   - Generate `@Composable` test functions
   - Use semantic properties for robust selectors
   - Support Compose animations and transitions

5. **Cloud Storage & Collaboration**
   - Upload scenarios to cloud (S3, GCS)
   - Share scenarios across team
   - Version control for scenarios
   - Collaborative test review

6. **CI/CD Integration**
   - GitHub Actions workflow templates
   - GitLab CI integration
   - Jenkins pipeline snippets
   - Automatic test execution on PR

7. **Multi-Device Testing**
   - Record once, replay on multiple devices
   - Parallel execution
   - Device farm integration (Firebase Test Lab)
   - Cross-device compatibility reports

8. **Advanced Assertions**
   - Visual element matching
   - Performance assertions (response time)
   - Network request validation
   - Database state checks

9. **Test Maintenance Tools**
   - Detect flaky tests
   - Suggest selector improvements
   - Auto-update scenarios when UI changes
   - Test impact analysis

10. **Accessibility Testing**
    - Check accessibility during recording
    - Generate accessibility-focused tests
    - Validate content descriptions
    - Check contrast ratios

---

## Conclusion

### Project Feasibility: ✅ HIGHLY FEASIBLE

This project is **entirely feasible** using the existing MCP Android Agent infrastructure. The uiautomator2 library provides all necessary capabilities:

- ✅ Action interception (via decorators)
- ✅ UI state capture (dump_hierarchy)
- ✅ Screenshot capture (screenshot tool)
- ✅ Precise action replay (all MCP tools)
- ✅ Device control (ADB access)

### Key Success Factors

1. **Solid Foundation**: MCP Android server already has 63 tools covering all common actions
2. **Proven Technology**: uiautomator2 is mature and widely used
3. **Clear Scope**: Well-defined features for v1.0
4. **Incremental Development**: Phased approach reduces risk
5. **Real Market Need**: Fills gap not addressed by existing tools

### Recommended Next Steps

1. **Validate Approach**: Create proof-of-concept for recording 2-3 simple actions
2. **Finalize JSON Schema**: Review and approve scenario format
3. **Set Up Development Environment**: Branch MCP server repo, set up testing devices
4. **Implement Phase 1**: Recording infrastructure (2 weeks)
5. **Early Testing**: Record real scenarios ASAP to validate assumptions

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Selector reliability issues | Medium | High | Multi-strategy selectors, fallback chains |
| Timing problems in replay | Medium | Medium | Smart waits, retry logic |
| Espresso mapping complexity | Low | Medium | Start with common cases, iterate |
| Compose compatibility | Medium | Medium | Separate code path for Compose |
| Performance (screenshot overhead) | Low | Low | Optimize compression, async capture |

### Expected Timeline

- **Phase 1-3** (Basic recording & replay): 6 weeks
- **Phase 4** (Espresso generation): 3 weeks
- **Phase 5** (Polish & docs): 3 weeks
- **Total to v1.0**: **12 weeks** (3 months)

### Resources Required

- 1 Senior Python Developer (MCP server, recording/replay)
- 1 Android Developer (Espresso code generation, testing)
- 1-2 QA Engineers (testing scenarios, validation)
- Android test devices (3-5 devices, various OS versions)

### Return on Investment

**Benefits:**
- Saves hours of manual test writing per scenario
- Enables non-developers to create tests
- Improves test coverage
- Reduces QA cycle time
- Documents user flows visually

**Costs:**
- ~3 months development time
- Minimal infrastructure (storage for scenarios)
- Ongoing maintenance

**ROI**: High - Tool pays for itself if it saves even 1 hour per week per user

---

## Appendix

### A. JSON Schema Specification

See [Recording Mechanism Design](#scenario-json-schema) section for full schema.

### B. Espresso API Reference

- [Espresso Documentation](https://developer.android.com/training/testing/espresso)
- [ViewMatchers](https://developer.android.com/reference/androidx/test/espresso/matcher/ViewMatchers)
- [ViewActions](https://developer.android.com/reference/androidx/test/espresso/action/ViewActions)
- [ViewAssertions](https://developer.android.com/reference/androidx/test/espresso/assertion/ViewAssertions)

### C. UIAutomator2 Resources

- [openatx/uiautomator2 GitHub](https://github.com/openatx/uiautomator2)
- [uiautomator2 Documentation](https://uiautomator2.readthedocs.io/)

### D. Accessibility Service Considerations

While accessibility services can record user interactions system-wide, they have significant limitations:

- Requires user to manually enable in Settings
- Android 13+ restrictions on non-accessibility use cases
- May cause app rejection from Play Store if misused
- Security/privacy concerns
- High implementation complexity

**Recommendation**: 
Do NOT use accessibility services for this project. The MCP-based approach (recording via explicit API calls) is:

- More reliable
- No permission issues
- No Play Store restrictions
- Easier to implement
- More transparent to users

### E. Alternative Approaches Considered

1. **Accessibility Service Recording**: ❌ Too restrictive, privacy concerns
2. **Monkey Runner**: ❌ Deprecated, limited functionality
3. **Appium Inspector**: ❌ Requires Appium infrastructure
4. **Manual Test Authoring**: ❌ Defeats purpose of automation
5. **MCP-Based Recording**: ✅ **SELECTED** - Best fit for requirements

---

**Document End**

*For questions or clarifications, please contact the project team.*

*Version History:*
- v1.0 (2025-01-01): Initial architecture document
