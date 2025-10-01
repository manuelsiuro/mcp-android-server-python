# Specialized Agent Architecture for Android Scenario Recording & Espresso Test Generation

## Document Version 1.0

**Purpose:** Define specialized agents and subagents for implementing the Android Scenario Recording & Espresso Test Generation system within Claude Code.

**Target Platform:** Claude Code CLI with Task tool and MCP integration

**Date:** October 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Agent Design Principles](#agent-design-principles)
3. [Agent Hierarchy Overview](#agent-hierarchy-overview)
4. [Core Agent Definitions](#core-agent-definitions)
5. [Agent Communication Protocols](#agent-communication-protocols)
6. [Workflow Orchestration Examples](#workflow-orchestration-examples)
7. [Implementation Guidelines](#implementation-guidelines)
8. [Agent Performance Metrics](#agent-performance-metrics)

---

## Executive Summary

This document defines a **hierarchical multi-agent system** for implementing the Android Scenario Recording & Espresso Test Generation project. The architecture consists of:

- **5 Primary Agents** (major system components)
- **15 Specialized Subagents** (focused tasks)
- **3 Support Agents** (cross-cutting concerns)

All agents are designed to work within **Claude Code's Task tool system** and leverage the existing **MCP Android server** infrastructure.

### Key Benefits

✅ **Parallel Development**: Multiple agents can work simultaneously on independent components
✅ **Clear Separation**: Each agent has well-defined responsibilities and interfaces
✅ **Testability**: Agents can be tested independently before integration
✅ **Maintainability**: Changes to one agent don't affect others
✅ **Scalability**: New agents can be added without disrupting existing ones
✅ **Quality Control**: Dedicated agents for review and testing ensure high standards

---

## Agent Design Principles

### 1. Single Responsibility Principle

Each agent focuses on **one specific aspect** of the system:
- ✅ RecordingEngine agent → handles recording logic only
- ✅ EspressoGenerator agent → generates Espresso code only
- ❌ Universal agent → tries to do everything (avoid this)

### 2. Clear Input/Output Contracts

Every agent defines:
- **Inputs**: What data/context it needs to start
- **Outputs**: What deliverables it produces
- **Side Effects**: What files/state it modifies
- **Error Conditions**: What can go wrong and how to handle it

### 3. Stateless Operation

Agents should be **stateless** where possible:
- Accept all necessary context as input parameters
- Return complete results (not partial state)
- Don't rely on external mutable state
- Enable parallel execution without race conditions

### 4. Composability

Agents should be **composable**:
- Small agents can be combined to create complex workflows
- Outputs of one agent can be inputs to another
- Agents can call other agents as needed
- Create agent pipelines for multi-step processes

### 5. Claude Code Integration

All agents use **Claude Code native features**:
- Invoked via `Task` tool with `subagent_type` parameter
- Use `Read`, `Write`, `Edit`, `Grep`, `Bash` tools
- Access MCP Android server tools when needed
- Report progress via structured outputs
- Handle errors gracefully with retries

---

## Agent Hierarchy Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                            │
│              (Top-level coordination)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┬──────────────────────┐
         │                               │                       │
┌────────▼─────────┐         ┌──────────▼────────┐   ┌─────────▼─────────┐
│  RECORDING       │         │  REPLAY           │   │  CODE GENERATION  │
│  SYSTEM AGENTS   │         │  SYSTEM AGENTS    │   │  AGENTS           │
└────────┬─────────┘         └──────────┬────────┘   └─────────┬─────────┘
         │                               │                       │
    ┌────┴────┐                     ┌────┴────┐            ┌────┴────┐
    │         │                     │         │            │         │
┌───▼──┐ ┌───▼──┐            ┌─────▼──┐ ┌────▼───┐   ┌───▼──┐ ┌───▼──┐
│Action│ │Screen│            │Scenario│ │Action  │   │Mapper│ │Format│
│Inter │ │shot  │            │Parser  │ │Executor│   │Agent │ │Agent │
│ceptor│ │Mgr   │            │        │ │        │   │      │ │      │
└──────┘ └──────┘            └────────┘ └────────┘   └──────┘ └──────┘

┌─────────────────────────────────────────────────────────────────┐
│              SUPPORT AGENTS (Cross-cutting)                      │
├─────────────────────────────────────────────────────────────────┤
│  • TestWriter Agent                                              │
│  • CodeReviewer Agent                                            │
│  • DocumentationAgent                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Agent Definitions

### 1. Recording System Agents

#### 1.1 RecordingEngine Agent (Primary)

**Purpose:** Orchestrates the recording process and manages recording state.

**Responsibilities:**
- Initialize recording session
- Manage recording lifecycle (start/stop/pause)
- Coordinate subagents (ActionInterceptor, ScreenshotManager)
- Serialize recorded data to JSON
- Handle recording errors and recovery

**Inputs:**
```python
{
    "session_name": str,           # Name for this recording
    "description": str,             # Optional description
    "device_id": Optional[str],     # Target device
    "config": {
        "capture_screenshots": bool,
        "capture_hierarchy": bool,
        "auto_delays": bool
    }
}
```

**Outputs:**
```python
{
    "recording_id": str,
    "session_file": str,            # Path to scenario.json
    "screenshot_folder": str,
    "actions_captured": int,
    "duration_ms": int,
    "status": "success" | "error",
    "warnings": List[str]
}
```

**Implementation Files:**
- `recording/recording_engine.py`
- `recording/recording_state.py`
- `recording/config.py`

**Key Methods:**
```python
class RecordingEngineAgent:
    def start_recording(session_name: str, config: RecordingConfig) -> RecordingSession
    def stop_recording(recording_id: str) -> ScenarioFile
    def pause_recording(recording_id: str) -> bool
    def resume_recording(recording_id: str) -> bool
    def get_recording_status(recording_id: str) -> RecordingStatus
```

**Dependencies:**
- ActionInterceptorAgent (subagent)
- ScreenshotManagerAgent (subagent)
- MCP tools: `screenshot`, `dump_hierarchy`

**Claude Code Invocation:**
```python
# From orchestrator or user command
result = Task(
    subagent_type="recording-engine",
    prompt="""
    Start a new recording session with the following parameters:
    - Session name: "login_flow_test"
    - Description: "Test login with valid credentials"
    - Device: Connected Android device
    - Capture screenshots: Yes
    - Capture UI hierarchy: Yes

    Initialize all necessary subagents and prepare for action interception.
    Return the recording_id and confirm ready state.
    """,
    description="Initialize recording session"
)
```

---

#### 1.2 ActionInterceptor Agent (Subagent)

**Purpose:** Intercept and log MCP tool calls during recording.

**Responsibilities:**
- Apply `@recordable` decorator to MCP tools
- Capture action metadata (tool, params, timestamp)
- Extract timing information (delays)
- Buffer actions in memory
- Pass actions to parent RecordingEngine

**Inputs:**
```python
{
    "recording_id": str,
    "tools_to_intercept": List[str],  # e.g., ["click", "send_text", "swipe"]
    "capture_timing": bool
}
```

**Outputs:**
```python
{
    "action": {
        "id": int,
        "timestamp": str,
        "tool": str,
        "params": dict,
        "result": any,
        "delay_before_ms": int,
        "delay_after_ms": int
    }
}
```

**Implementation Files:**
- `recording/action_interceptor.py`
- `recording/decorators.py`

**Key Methods:**
```python
class ActionInterceptorAgent:
    def install_interceptors(tools: List[str]) -> None
    def capture_action(tool_name: str, params: dict, result: any) -> Action
    def calculate_timing(previous_action: Action, current_action: Action) -> Timing
    def buffer_action(action: Action) -> None
    def flush_buffer() -> List[Action]
```

**Interception Pattern:**
```python
def recordable(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if ActionInterceptorAgent.is_active():
            action_data = ActionInterceptorAgent.capture_pre_execution(
                func.__name__, args, kwargs
            )

            result = func(*args, **kwargs)

            ActionInterceptorAgent.capture_post_execution(
                action_data, result
            )

            return result
        else:
            return func(*args, **kwargs)
    return wrapper
```

---

#### 1.3 ScreenshotManager Agent (Subagent)

**Purpose:** Manage screenshot capture and storage during recording.

**Responsibilities:**
- Capture screenshots at appropriate times
- Name and organize screenshots
- Compress images (optional)
- Handle storage errors
- Link screenshots to actions

**Inputs:**
```python
{
    "recording_id": str,
    "output_folder": str,
    "action_id": int,
    "action_type": str,
    "device_id": Optional[str]
}
```

**Outputs:**
```python
{
    "screenshot_path": str,
    "file_size_bytes": int,
    "capture_time_ms": int,
    "success": bool
}
```

**Implementation Files:**
- `recording/screenshot_manager.py`
- `recording/image_utils.py`

**Key Methods:**
```python
class ScreenshotManagerAgent:
    def capture_screenshot(action_id: int, action_type: str) -> ScreenshotResult
    def organize_screenshots(recording_id: str) -> FolderStructure
    def compress_screenshot(path: str, quality: int) -> bool
    def cleanup_on_error(recording_id: str) -> None
```

**Screenshot Naming Convention:**
```
screenshots/
├── 001_click_login.png
├── 002_input_username.png
├── 003_input_password.png
├── 004_click_submit.png
└── 005_welcome_screen.png
```

---

### 2. Replay System Agents

#### 2.1 ScenarioPlayer Agent (Primary)

**Purpose:** Orchestrate scenario replay and generate replay reports.

**Responsibilities:**
- Load and validate scenario JSON
- Execute actions in sequence
- Coordinate validation (optional)
- Handle errors and retries
- Generate comprehensive replay report

**Inputs:**
```python
{
    "scenario_file": str,
    "device_id": Optional[str],
    "config": {
        "validate_ui_state": bool,
        "take_screenshots": bool,
        "continue_on_error": bool,
        "speed_multiplier": float,
        "timeout_multiplier": float
    }
}
```

**Outputs:**
```python
{
    "replay_id": str,
    "status": "PASSED" | "FAILED" | "PARTIAL",
    "duration_ms": int,
    "actions_total": int,
    "actions_passed": int,
    "actions_failed": int,
    "report_file": str,
    "screenshot_comparison": Optional[dict]
}
```

**Implementation Files:**
- `replay/scenario_player.py`
- `replay/replay_config.py`
- `replay/report_generator.py`

**Key Methods:**
```python
class ScenarioPlayerAgent:
    def load_scenario(file_path: str) -> Scenario
    def validate_scenario(scenario: Scenario) -> ValidationResult
    def replay(scenario: Scenario, config: ReplayConfig) -> ReplayReport
    def handle_action_failure(action: Action, error: Exception) -> RetryDecision
    def generate_report(results: List[ActionResult]) -> ReplayReport
```

**Dependencies:**
- ScenarioParserAgent (subagent)
- ActionExecutorAgent (subagent)
- UIValidatorAgent (subagent, optional)
- All MCP tools for action execution

---

#### 2.2 ScenarioParser Agent (Subagent)

**Purpose:** Parse and validate scenario JSON files.

**Responsibilities:**
- Load JSON from file
- Validate schema version
- Validate action structure
- Extract metadata
- Detect missing or corrupted data

**Inputs:**
```python
{
    "scenario_file": str
}
```

**Outputs:**
```python
{
    "scenario": Scenario,  # Parsed data structure
    "metadata": {
        "name": str,
        "created_at": str,
        "device": dict,
        "action_count": int
    },
    "validation_errors": List[str],
    "warnings": List[str]
}
```

**Implementation Files:**
- `replay/scenario_parser.py`
- `replay/schema_validator.py`

**Key Methods:**
```python
class ScenarioParserAgent:
    def parse_json(file_path: str) -> Scenario
    def validate_schema(scenario: dict) -> ValidationResult
    def extract_metadata(scenario: dict) -> Metadata
    def validate_action_sequence(actions: List[Action]) -> ValidationResult
```

**Validation Rules:**
```python
REQUIRED_FIELDS = {
    "schema_version": str,
    "metadata": dict,
    "actions": list
}

ACTION_REQUIRED_FIELDS = {
    "id": int,
    "timestamp": str,
    "tool": str,
    "params": dict
}
```

---

#### 2.3 ActionExecutor Agent (Subagent)

**Purpose:** Execute individual actions from scenario with proper timing.

**Responsibilities:**
- Execute MCP tool calls
- Apply delays (before/after)
- Handle action-specific logic
- Retry on transient failures
- Capture action results

**Inputs:**
```python
{
    "action": Action,
    "device_id": Optional[str],
    "timeout_multiplier": float,
    "retry_config": {
        "max_retries": int,
        "backoff_factor": float
    }
}
```

**Outputs:**
```python
{
    "action_id": int,
    "status": "PASSED" | "FAILED" | "SKIPPED",
    "execution_time_ms": int,
    "result": any,
    "error": Optional[str],
    "retry_count": int
}
```

**Implementation Files:**
- `replay/action_executor.py`
- `replay/retry_logic.py`

**Key Methods:**
```python
class ActionExecutorAgent:
    def execute_action(action: Action, device_id: str) -> ActionResult
    def apply_delays(action: Action, speed_multiplier: float) -> None
    def execute_with_retry(action: Action, retry_config: RetryConfig) -> ActionResult
    def map_tool_to_mcp(tool_name: str, params: dict) -> MCPToolCall
```

**Execution Flow:**
```python
def execute_action(action: Action) -> ActionResult:
    # 1. Apply delay_before
    time.sleep(action.delay_before_ms / 1000 * speed_multiplier)

    # 2. Execute MCP tool with retry
    for attempt in range(max_retries):
        try:
            result = execute_mcp_tool(action.tool, action.params)
            break
        except TransientError as e:
            if attempt < max_retries - 1:
                time.sleep(backoff_factor ** attempt)
            else:
                raise

    # 3. Apply delay_after
    time.sleep(action.delay_after_ms / 1000 * speed_multiplier)

    return ActionResult(success=True, result=result)
```

---

#### 2.4 UIValidator Agent (Subagent, Optional)

**Purpose:** Validate UI state matches recorded expectations.

**Responsibilities:**
- Compare current UI to recorded snapshot
- Check element existence
- Verify element properties
- Report validation failures
- Provide detailed diff

**Inputs:**
```python
{
    "action_id": int,
    "expected_ui_state": dict,  # From recording
    "device_id": Optional[str],
    "tolerance": {
        "ignore_dynamic_content": bool,
        "fuzzy_text_match": bool
    }
}
```

**Outputs:**
```python
{
    "validation_passed": bool,
    "mismatches": List[{
        "element": str,
        "expected": any,
        "actual": any,
        "severity": "critical" | "warning"
    }],
    "screenshot_similarity": float  # 0.0 to 1.0
}
```

**Implementation Files:**
- `replay/ui_validator.py`
- `replay/diff_engine.py`

**Key Methods:**
```python
class UIValidatorAgent:
    def validate_ui_state(expected: dict, device_id: str) -> ValidationResult
    def compare_hierarchy(expected_xml: str, actual_xml: str) -> DiffResult
    def compare_screenshots(expected_path: str, actual_path: str) -> float
    def generate_diff_report(mismatches: List[Mismatch]) -> str
```

---

### 3. Code Generation Agents

#### 3.1 EspressoCodeGenerator Agent (Primary)

**Purpose:** Generate complete Espresso test code from scenarios.

**Responsibilities:**
- Orchestrate code generation pipeline
- Generate test class structure
- Coordinate subagents for specific tasks
- Format final code
- Generate both Java and Kotlin

**Inputs:**
```python
{
    "scenario_file": str,
    "language": "java" | "kotlin",
    "package_name": Optional[str],
    "class_name": Optional[str],
    "options": {
        "include_comments": bool,
        "use_idling_resources": bool,
        "generate_custom_actions": bool
    }
}
```

**Outputs:**
```python
{
    "code": str,                    # Generated test code
    "file_path": str,               # Where code was saved
    "imports": List[str],           # Required imports
    "custom_actions": List[str],    # Custom ViewActions needed
    "warnings": List[str],          # Manual adjustments needed
    "ui_framework": "xml" | "compose" | "hybrid"
}
```

**Implementation Files:**
- `codegen/espresso_generator.py`
- `codegen/code_templates.py`
- `codegen/formatter.py`

**Key Methods:**
```python
class EspressoCodeGeneratorAgent:
    def generate(scenario: Scenario, language: str) -> GeneratedCode
    def detect_ui_framework(scenario: Scenario) -> UIFramework
    def generate_test_class(scenario: Scenario, language: str) -> str
    def generate_imports(actions: List[Action]) -> List[str]
    def format_code(code: str, language: str) -> str
```

**Dependencies:**
- SelectorMapperAgent (subagent)
- ActionMapperAgent (subagent)
- ComposeDetectorAgent (subagent)
- CodeFormatterAgent (subagent)

**Claude Code Invocation:**
```python
result = Task(
    subagent_type="espresso-code-generator",
    prompt="""
    Generate Espresso test code from the scenario file:
    scenarios/login_flow_20250101_143022/scenario.json

    Requirements:
    - Language: Kotlin
    - Package: com.example.app
    - Test class name: LoginFlowTest
    - Include detailed comments
    - Generate custom ViewActions for coordinate-based clicks

    Analyze the scenario to detect UI framework (XML vs Compose) and
    generate appropriate test code. Return complete, compilable code.
    """,
    description="Generate Espresso test code"
)
```

---

#### 3.2 SelectorMapper Agent (Subagent)

**Purpose:** Map UIAutomator selectors to Espresso ViewMatchers.

**Responsibilities:**
- Parse UIAutomator selector syntax
- Generate Espresso ViewMatcher code
- Handle XPath to ViewMatcher conversion
- Generate fallback strategies
- Create resource ID mappings

**Inputs:**
```python
{
    "selector": str,
    "selector_type": "text" | "resourceId" | "description" | "xpath",
    "target_language": "java" | "kotlin",
    "ui_framework": "xml" | "compose"
}
```

**Outputs:**
```python
{
    "espresso_code": str,           # e.g., "withText("Login")"
    "imports": List[str],           # Required imports
    "fallback_selectors": List[str], # Alternative selectors
    "warnings": List[str],          # Manual review needed
    "confidence": float             # 0.0 to 1.0
}
```

**Implementation Files:**
- `codegen/selector_mapper.py`
- `codegen/xpath_parser.py`

**Mapping Table:**
```python
SELECTOR_MAPPINGS = {
    "text": {
        "espresso": "withText(\"{value}\")",
        "imports": ["androidx.test.espresso.matcher.ViewMatchers.withText"]
    },
    "resourceId": {
        "espresso": "withId(R.id.{id_part})",
        "imports": ["androidx.test.espresso.matcher.ViewMatchers.withId"]
    },
    "description": {
        "espresso": "withContentDescription(\"{value}\")",
        "imports": ["androidx.test.espresso.matcher.ViewMatchers.withContentDescription"]
    }
}

COMPOSE_MAPPINGS = {
    "text": {
        "compose": "onNodeWithText(\"{value}\")",
        "imports": ["androidx.compose.ui.test.onNodeWithText"]
    },
    "description": {
        "compose": "onNodeWithContentDescription(\"{value}\")",
        "imports": ["androidx.compose.ui.test.onNodeWithContentDescription"]
    }
}
```

**Key Methods:**
```python
class SelectorMapperAgent:
    def map_selector(selector: str, type: str, framework: str) -> MappedSelector
    def parse_xpath(xpath: str) -> SelectorComponents
    def generate_viewmatcher(selector: SelectorComponents, lang: str) -> str
    def generate_compose_selector(selector: SelectorComponents, lang: str) -> str
    def create_fallback_chain(selector: str) -> List[str]
```

---

#### 3.3 ActionMapper Agent (Subagent)

**Purpose:** Map UIAutomator actions to Espresso ViewActions.

**Responsibilities:**
- Convert action types to Espresso syntax
- Generate ViewAction calls
- Handle special cases (coordinates, swipes)
- Create custom actions when needed
- Add appropriate assertions

**Inputs:**
```python
{
    "action": Action,
    "target_language": "java" | "kotlin",
    "ui_framework": "xml" | "compose"
}
```

**Outputs:**
```python
{
    "espresso_code": str,
    "custom_actions": List[str],    # Custom ViewAction code if needed
    "assertions": List[str],        # Generated assertions
    "imports": List[str]
}
```

**Implementation Files:**
- `codegen/action_mapper.py`
- `codegen/custom_actions.py`

**Mapping Table:**
```python
ACTION_MAPPINGS = {
    "click": {
        "espresso": "perform(click())",
        "compose": "performClick()",
        "imports": ["androidx.test.espresso.action.ViewActions.click"]
    },
    "send_text": {
        "espresso": "perform(clearText(), typeText(\"{text}\"))",
        "compose": "performTextInput(\"{text}\")",
        "imports": [
            "androidx.test.espresso.action.ViewActions.clearText",
            "androidx.test.espresso.action.ViewActions.typeText"
        ]
    },
    "swipe": {
        "espresso": "perform(swipeLeft())",  # or custom
        "compose": "performTouchInput {{ swipeLeft() }}",
        "imports": ["androidx.test.espresso.action.ViewActions.swipeLeft"]
    }
}
```

**Key Methods:**
```python
class ActionMapperAgent:
    def map_action(action: Action, framework: str, lang: str) -> MappedAction
    def generate_viewaction(action: Action, lang: str) -> str
    def generate_compose_action(action: Action, lang: str) -> str
    def create_custom_action(action: Action, lang: str) -> str
    def generate_assertion(action: Action) -> str
```

---

#### 3.4 ComposeDetector Agent (Subagent)

**Purpose:** Detect whether app uses Jetpack Compose or XML views.

**Responsibilities:**
- Analyze UI hierarchy snapshots
- Identify Compose view signatures
- Determine UI framework per screen
- Report hybrid apps (mix of XML and Compose)

**Inputs:**
```python
{
    "scenario": Scenario,
    "ui_hierarchies": List[str]  # XML hierarchies from actions
}
```

**Outputs:**
```python
{
    "ui_framework": "xml" | "compose" | "hybrid",
    "compose_screens": List[int],   # Action IDs with Compose
    "xml_screens": List[int],       # Action IDs with XML
    "confidence": float
}
```

**Implementation Files:**
- `codegen/compose_detector.py`

**Detection Rules:**
```python
COMPOSE_INDICATORS = [
    "androidx.compose.ui.platform.ComposeView",
    "androidx.compose.ui.platform.AndroidComposeView",
    "android.view.View"  # Generic views in deep nesting
]

def is_compose_screen(hierarchy_xml: str) -> bool:
    tree = parse_xml(hierarchy_xml)

    # Check for ComposeView
    if tree.find(".//node[@class='androidx.compose.ui.platform.ComposeView']"):
        return True

    # Check for deep nesting with generic views
    max_depth = calculate_max_depth(tree)
    generic_views = count_generic_views(tree)

    if max_depth > 10 and generic_views > 20:
        return True  # Likely Compose

    return False
```

**Key Methods:**
```python
class ComposeDetectorAgent:
    def detect_framework(scenario: Scenario) -> FrameworkDetection
    def analyze_hierarchy(xml: str) -> FrameworkType
    def identify_hybrid_screens(scenario: Scenario) -> HybridAnalysis
```

---

#### 3.5 CodeFormatter Agent (Subagent)

**Purpose:** Format generated code according to language standards.

**Responsibilities:**
- Format Java code (google-java-format style)
- Format Kotlin code (ktlint style)
- Organize imports
- Apply consistent indentation
- Add appropriate spacing

**Inputs:**
```python
{
    "code": str,
    "language": "java" | "kotlin",
    "style": "google" | "android" | "custom"
}
```

**Outputs:**
```python
{
    "formatted_code": str,
    "changes_made": List[str]
}
```

**Implementation Files:**
- `codegen/code_formatter.py`

**Key Methods:**
```python
class CodeFormatterAgent:
    def format_java(code: str, style: str) -> str
    def format_kotlin(code: str, style: str) -> str
    def organize_imports(code: str, language: str) -> str
    def apply_indentation(code: str, spaces: int) -> str
```

---

### 4. Testing & Quality Agents

#### 4.1 TestWriter Agent (Support Agent)

**Purpose:** Generate unit tests for the scenario recording/replay system itself.

**Responsibilities:**
- Generate pytest test cases
- Create test fixtures
- Mock MCP tool responses
- Test edge cases
- Ensure code coverage

**Inputs:**
```python
{
    "module_to_test": str,          # e.g., "recording/recording_engine.py"
    "test_cases": List[str],        # Specific scenarios to test
    "coverage_target": int          # e.g., 80%
}
```

**Outputs:**
```python
{
    "test_file": str,
    "test_count": int,
    "coverage_estimate": int,
    "fixtures_created": List[str]
}
```

**Implementation Files:**
- `tests/test_generators/test_writer.py`

**Key Methods:**
```python
class TestWriterAgent:
    def generate_tests(module: str, cases: List[str]) -> str
    def create_fixtures(module: str) -> List[Fixture]
    def generate_mocks(dependencies: List[str]) -> str
    def calculate_coverage(tests: List[Test], module: str) -> int
```

**Example Generated Test:**
```python
import pytest
from recording.recording_engine import RecordingEngineAgent

@pytest.fixture
def mock_device():
    return MockDevice(device_id="test_device")

@pytest.fixture
def recording_engine(mock_device):
    return RecordingEngineAgent(device=mock_device)

def test_start_recording_success(recording_engine):
    """Test successful recording start."""
    result = recording_engine.start_recording(
        session_name="test_session",
        config=RecordingConfig()
    )

    assert result.recording_id is not None
    assert result.status == "active"
    assert recording_engine.is_recording() is True

def test_stop_recording_saves_json(recording_engine, tmp_path):
    """Test recording stop saves JSON file."""
    recording_engine.start_recording("test_session")
    result = recording_engine.stop_recording()

    assert Path(result.session_file).exists()
    with open(result.session_file) as f:
        data = json.load(f)
        assert data["schema_version"] == "1.0"
        assert "actions" in data
```

---

#### 4.2 CodeReviewer Agent (Support Agent)

**Purpose:** Review generated code for quality, correctness, and best practices.

**Responsibilities:**
- Static code analysis
- Check for common bugs
- Verify coding standards
- Suggest improvements
- Ensure security practices

**Inputs:**
```python
{
    "code": str,
    "language": "python" | "java" | "kotlin",
    "review_checklist": List[str]   # Specific things to check
}
```

**Outputs:**
```python
{
    "review_score": int,            # 0-100
    "critical_issues": List[str],
    "warnings": List[str],
    "suggestions": List[str],
    "approved": bool
}
```

**Implementation Files:**
- `quality/code_reviewer.py`

**Review Checklist:**
```python
REVIEW_CRITERIA = {
    "python": [
        "PEP8 compliance",
        "Type hints present",
        "Docstrings for public methods",
        "Error handling",
        "No hardcoded paths",
        "Proper logging",
        "Security: input validation"
    ],
    "java": [
        "Google Java Style",
        "Javadoc for public methods",
        "Exception handling",
        "Resource cleanup",
        "Thread safety",
        "Security: avoid injection"
    ],
    "kotlin": [
        "Kotlin conventions",
        "KDoc for public APIs",
        "Null safety",
        "Immutability where possible",
        "Coroutine safety",
        "Security best practices"
    ]
}
```

**Key Methods:**
```python
class CodeReviewerAgent:
    def review_code(code: str, language: str) -> ReviewResult
    def check_style(code: str, language: str) -> List[StyleIssue]
    def check_security(code: str, language: str) -> List[SecurityIssue]
    def check_performance(code: str, language: str) -> List[PerformanceIssue]
    def generate_review_report(issues: List[Issue]) -> str
```

---

#### 4.3 IntegrationTester Agent (Support Agent)

**Purpose:** Test integration between components and with MCP server.

**Responsibilities:**
- End-to-end testing
- Test recording → replay workflow
- Test code generation from scenarios
- Verify MCP tool integration
- Test on real devices

**Inputs:**
```python
{
    "test_scenario": str,           # What to test
    "device_id": Optional[str],
    "real_device": bool             # Use real device vs mock
}
```

**Outputs:**
```python
{
    "test_passed": bool,
    "duration_ms": int,
    "issues_found": List[str],
    "logs": str,
    "screenshots": List[str]
}
```

**Implementation Files:**
- `tests/integration/integration_tester.py`

**Key Methods:**
```python
class IntegrationTesterAgent:
    def test_recording_flow(device_id: str) -> TestResult
    def test_replay_flow(scenario_file: str, device_id: str) -> TestResult
    def test_code_generation(scenario_file: str) -> TestResult
    def test_full_workflow() -> TestResult
```

**Example Test Workflow:**
```python
def test_full_workflow():
    # 1. Start recording
    recording = start_recording("integration_test")

    # 2. Perform some actions
    click("Login")
    send_text("test@example.com")
    click("Submit")

    # 3. Stop recording
    scenario = stop_recording(recording.recording_id)

    # 4. Replay scenario
    replay_result = replay_scenario(scenario.session_file)
    assert replay_result.status == "PASSED"

    # 5. Generate Espresso code
    code = generate_espresso_code(scenario.session_file, language="kotlin")

    # 6. Verify code compiles (syntax check)
    assert verify_kotlin_syntax(code.code)

    return TestResult(passed=True)
```

---

### 5. Support Agents

#### 5.1 DocumentationAgent (Support Agent)

**Purpose:** Generate and maintain project documentation.

**Responsibilities:**
- Generate API documentation
- Create usage examples
- Write tutorials
- Update README files
- Generate architecture diagrams

**Inputs:**
```python
{
    "doc_type": "api" | "tutorial" | "readme" | "architecture",
    "target_file": str,
    "content_source": List[str]     # Files to document
}
```

**Outputs:**
```python
{
    "documentation": str,
    "file_path": str,
    "format": "markdown" | "html" | "pdf"
}
```

**Implementation Files:**
- `docs/documentation_agent.py`

**Key Methods:**
```python
class DocumentationAgent:
    def generate_api_docs(modules: List[str]) -> str
    def generate_tutorial(scenario: str) -> str
    def update_readme(changes: List[str]) -> str
    def create_architecture_diagram(components: List[str]) -> str
```

---

## Agent Communication Protocols

### 1. Parent-Subagent Communication

**Pattern:** Parent agents invoke subagents via Claude Code's Task tool.

**Example:**
```python
# Parent: RecordingEngine Agent
def start_recording(self, session_name: str) -> RecordingSession:
    # Initialize subagents
    action_interceptor = Task(
        subagent_type="action-interceptor",
        prompt=f"""
        Initialize action interception for recording session: {session_name}

        Install interceptors on the following MCP tools:
        - click, click_xpath, click_at
        - send_text, send_text_xpath
        - swipe, scroll_to, scroll_forward
        - press_key

        Begin capturing action metadata and return ready status.
        """,
        description="Initialize action interceptor"
    )

    screenshot_mgr = Task(
        subagent_type="screenshot-manager",
        prompt=f"""
        Initialize screenshot management for recording: {session_name}

        Create output folder: scenarios/{session_name}/screenshots/
        Prepare for screenshot capture on action completion.
        Return folder path and ready status.
        """,
        description="Initialize screenshot manager"
    )

    # Continue with recording logic...
```

### 2. Agent Output Format

All agents return **structured JSON** for easy parsing:

```python
{
    "agent": "RecordingEngineAgent",
    "status": "success" | "error" | "partial",
    "data": {
        # Agent-specific output
    },
    "errors": [
        {
            "severity": "critical" | "warning",
            "message": str,
            "context": dict
        }
    ],
    "metadata": {
        "execution_time_ms": int,
        "agent_version": str,
        "timestamp": str
    }
}
```

### 3. Error Handling Protocol

**Escalation Chain:**
1. **Subagent Error** → Report to parent agent
2. **Parent Agent Error** → Report to orchestrator
3. **Orchestrator Error** → Report to user

**Example:**
```python
# Subagent error
try:
    result = capture_screenshot(action_id)
except ScreenshotError as e:
    return {
        "status": "error",
        "errors": [{
            "severity": "warning",
            "message": f"Screenshot capture failed: {e}",
            "context": {"action_id": action_id}
        }]
    }

# Parent handles subagent error
screenshot_result = screenshot_mgr.capture()
if screenshot_result.status == "error":
    # Decide: Continue without screenshot or fail?
    if config.require_screenshots:
        raise RecordingError("Screenshot required but failed")
    else:
        warnings.append("Screenshot capture failed, continuing")
```

### 4. Progress Reporting

Agents report progress for long-running tasks:

```python
def generate_espresso_code(scenario: Scenario) -> GeneratedCode:
    progress = ProgressReporter()

    progress.update(10, "Parsing scenario JSON")
    scenario_obj = parse_scenario(scenario)

    progress.update(30, "Detecting UI framework")
    framework = detect_ui_framework(scenario_obj)

    progress.update(50, "Mapping selectors to Espresso")
    mapped_selectors = map_selectors(scenario_obj)

    progress.update(70, "Generating test class structure")
    code = generate_test_class(mapped_selectors, framework)

    progress.update(90, "Formatting code")
    formatted = format_code(code, "kotlin")

    progress.update(100, "Code generation complete")
    return GeneratedCode(code=formatted)
```

---

## Workflow Orchestration Examples

### Example 1: Full Recording → Replay → Code Generation

```python
# USER COMMAND: /adaptive "Record a login scenario, replay it, and generate Espresso code"

# ORCHESTRATOR AGENT
def orchestrate_full_workflow(scenario_name: str):
    # Phase 1: Recording
    recording_result = Task(
        subagent_type="recording-engine",
        prompt=f"""
        Start recording session: {scenario_name}

        1. Initialize all subagents (ActionInterceptor, ScreenshotManager)
        2. Begin capturing actions on the device
        3. User will perform actions (click, input, etc.)
        4. Wait for user to indicate recording stop
        5. Save scenario JSON and screenshots

        Return: recording_id, scenario_file, action_count
        """,
        description="Record user scenario"
    )

    # Phase 2: Replay
    replay_result = Task(
        subagent_type="scenario-player",
        prompt=f"""
        Replay the recorded scenario: {recording_result.scenario_file}

        1. Parse scenario JSON
        2. Execute each action in sequence
        3. Validate UI state at each step
        4. Take screenshots for comparison
        5. Generate replay report

        Return: replay status, report_file, pass/fail
        """,
        description="Replay recorded scenario"
    )

    # Phase 3: Code Generation
    if replay_result.status == "PASSED":
        code_result = Task(
            subagent_type="espresso-code-generator",
            prompt=f"""
            Generate Espresso test code from: {recording_result.scenario_file}

            1. Detect UI framework (XML/Compose)
            2. Map selectors and actions
            3. Generate test class in Kotlin
            4. Format code
            5. Save to file

            Return: generated code, file_path, warnings
            """,
            description="Generate Espresso test code"
        )

        return {
            "recording": recording_result,
            "replay": replay_result,
            "code": code_result,
            "status": "success"
        }
    else:
        return {
            "recording": recording_result,
            "replay": replay_result,
            "status": "replay_failed",
            "message": "Replay must pass before generating code"
        }
```

### Example 2: Parallel Agent Execution

```python
# Orchestrator spawns multiple agents in parallel for independent tasks

def parallel_code_generation(scenario_files: List[str]):
    # Spawn multiple code generator agents in parallel
    results = []

    # Create parallel tasks
    tasks = []
    for scenario_file in scenario_files:
        task = Task(
            subagent_type="espresso-code-generator",
            prompt=f"""
            Generate Espresso test code from: {scenario_file}
            Language: Kotlin
            Include comments and custom actions.
            """,
            description=f"Generate code for {Path(scenario_file).stem}"
        )
        tasks.append(task)

    # All tasks execute in parallel (if Claude Code supports it)
    # Otherwise, they execute sequentially
    for task in tasks:
        results.append(task.result)

    return {
        "total_files": len(scenario_files),
        "successful": sum(1 for r in results if r.status == "success"),
        "failed": sum(1 for r in results if r.status == "error"),
        "results": results
    }
```

### Example 3: Agent Pipeline

```python
# Chain agents together: output of one becomes input to next

def code_generation_pipeline(scenario_file: str):
    # Step 1: Parse scenario
    parsed = Task(
        subagent_type="scenario-parser",
        prompt=f"Parse and validate scenario: {scenario_file}",
        description="Parse scenario JSON"
    )

    if parsed.validation_errors:
        return {"status": "error", "message": "Invalid scenario"}

    # Step 2: Detect UI framework
    framework = Task(
        subagent_type="compose-detector",
        prompt=f"""
        Detect UI framework from scenario hierarchies.
        Scenario data: {parsed.scenario}
        """,
        description="Detect UI framework"
    )

    # Step 3: Map selectors
    selectors = Task(
        subagent_type="selector-mapper",
        prompt=f"""
        Map all selectors in scenario to Espresso ViewMatchers.
        Framework: {framework.ui_framework}
        Language: Kotlin
        Scenario: {parsed.scenario}
        """,
        description="Map selectors"
    )

    # Step 4: Map actions
    actions = Task(
        subagent_type="action-mapper",
        prompt=f"""
        Map all actions in scenario to Espresso ViewActions.
        Framework: {framework.ui_framework}
        Language: Kotlin
        Scenario: {parsed.scenario}
        """,
        description="Map actions"
    )

    # Step 5: Generate test class
    code = generate_test_class(
        scenario=parsed.scenario,
        selectors=selectors.mapped_selectors,
        actions=actions.mapped_actions,
        framework=framework.ui_framework
    )

    # Step 6: Format code
    formatted = Task(
        subagent_type="code-formatter",
        prompt=f"""
        Format Kotlin code according to ktlint style:
        {code}
        """,
        description="Format generated code"
    )

    return {
        "status": "success",
        "code": formatted.formatted_code,
        "pipeline_steps": 6
    }
```

---

## Implementation Guidelines

### 1. Agent Development Process

**Step 1: Define Agent Specification**
```markdown
## Agent: [Name]
**Purpose:** [One-sentence description]
**Responsibilities:** [Bulleted list]
**Inputs:** [JSON schema]
**Outputs:** [JSON schema]
**Dependencies:** [List of other agents/tools]
```

**Step 2: Create Agent Prompt File**

Location: `.claude/commands/agents/[agent_name].md`

```markdown
# [Agent Name]

You are a **[Agent Name]**, specialized in [specific task].

## Inputs
[Detailed input specification]

## Processing Steps
<think hard>
1. [Step 1]
2. [Step 2]
...
</think hard>

## Outputs
[Detailed output specification]

## Error Handling
[How to handle errors]
```

**Step 3: Implement Agent Logic**

```python
# agents/[agent_name].py

class [AgentName]:
    """
    [Agent description]

    This agent is invoked by Claude Code's Task tool with subagent_type="[agent-name]"
    """

    def execute(self, inputs: dict) -> dict:
        """
        Main execution method.

        Args:
            inputs: Input parameters from Task tool

        Returns:
            Structured output dictionary
        """
        try:
            # Agent logic
            result = self._process(inputs)
            return {
                "status": "success",
                "data": result,
                "errors": []
            }
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "errors": [{
                    "severity": "critical",
                    "message": str(e)
                }]
            }

    def _process(self, inputs: dict) -> any:
        """Internal processing logic."""
        pass
```

**Step 4: Add Unit Tests**

```python
# tests/agents/test_[agent_name].py

import pytest
from agents.[agent_name] import [AgentName]

@pytest.fixture
def agent():
    return [AgentName]()

def test_agent_success_case(agent):
    inputs = {...}
    result = agent.execute(inputs)
    assert result["status"] == "success"
    assert result["data"] is not None

def test_agent_error_case(agent):
    inputs = {...}  # Invalid inputs
    result = agent.execute(inputs)
    assert result["status"] == "error"
```

**Step 5: Register Agent**

Add to `agents/registry.py`:

```python
AGENT_REGISTRY = {
    "recording-engine": RecordingEngineAgent,
    "action-interceptor": ActionInterceptorAgent,
    "screenshot-manager": ScreenshotManagerAgent,
    # ... all agents
}

def get_agent(subagent_type: str):
    """Get agent class by type."""
    return AGENT_REGISTRY.get(subagent_type)
```

### 2. Testing Strategy

**Unit Tests:** Test each agent independently with mocked dependencies
**Integration Tests:** Test agent communication and data flow
**End-to-End Tests:** Test full workflows with real devices

```python
# Example integration test
def test_recording_to_code_generation():
    # Record a simple scenario
    recording = RecordingEngine().start_recording("test")
    # Simulate actions
    ActionInterceptor.capture(click("Login"))
    recording_result = recording.stop()

    # Generate code from recording
    code = EspressoGenerator().generate(
        recording_result.scenario_file,
        language="kotlin"
    )

    # Verify code is valid
    assert "fun testScenario()" in code
    assert "onView(withText(\"Login\"))" in code
```

### 3. Agent Versioning

Track agent versions for compatibility:

```python
class AgentVersion:
    MAJOR = 1  # Breaking changes
    MINOR = 0  # New features
    PATCH = 0  # Bug fixes

    @classmethod
    def version_string(cls):
        return f"{cls.MAJOR}.{cls.MINOR}.{cls.PATCH}"
```

### 4. Agent Monitoring

Log agent execution for debugging:

```python
import logging

logger = logging.getLogger(__name__)

class AgentBase:
    def execute(self, inputs: dict) -> dict:
        logger.info(f"{self.__class__.__name__} started")
        start_time = time.time()

        try:
            result = self._process(inputs)
            duration = time.time() - start_time

            logger.info(f"{self.__class__.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            logger.error(f"{self.__class__.__name__} failed: {e}")
            raise
```

---

## Agent Performance Metrics

### 1. Execution Time Targets

| Agent | Target Time | Max Time | Notes |
|-------|------------|----------|-------|
| RecordingEngine | N/A | N/A | User-driven, indefinite |
| ActionInterceptor | <50ms | 100ms | Per action capture |
| ScreenshotManager | <500ms | 1000ms | Per screenshot |
| ScenarioPlayer | Varies | N/A | Depends on scenario length |
| ScenarioParser | <1s | 5s | For scenarios <100 actions |
| ActionExecutor | Varies | N/A | Depends on action type |
| UIValidator | <2s | 10s | Per validation |
| EspressoCodeGenerator | <5s | 30s | For scenarios <50 actions |
| SelectorMapper | <100ms | 500ms | Per selector |
| ActionMapper | <100ms | 500ms | Per action |
| ComposeDetector | <1s | 5s | Per scenario |
| CodeFormatter | <1s | 5s | Per file |
| TestWriter | <10s | 60s | Per module |
| CodeReviewer | <5s | 30s | Per file |

### 2. Quality Metrics

**Code Coverage Targets:**
- Core agents (Recording, Replay, CodeGen): **≥90%**
- Subagents: **≥80%**
- Support agents: **≥70%**

**Code Quality:**
- Complexity: Max cyclomatic complexity **≤10** per method
- Documentation: 100% of public APIs documented
- Type hints: 100% of function signatures
- Linting: Zero critical issues from ruff/pylint

**Test Metrics:**
- Unit test pass rate: **100%**
- Integration test pass rate: **≥95%**
- End-to-end test pass rate: **≥90%**

### 3. Agent Reliability

**Success Rate Targets:**
- Critical agents (Recording, Replay): **≥99%**
- Code generation agents: **≥95%**
- Support agents: **≥90%**

**Error Recovery:**
- All agents must handle errors gracefully
- No unhandled exceptions in production
- Clear error messages for users
- Automatic retry for transient failures (up to 3 times)

---

## Conclusion

This specialized agent architecture provides a **modular, scalable, and maintainable** approach to implementing the Android Scenario Recording & Espresso Test Generation system.

### Key Advantages

1. **Modularity**: Each agent focuses on one responsibility
2. **Testability**: Agents can be tested independently
3. **Parallelization**: Independent agents can run concurrently
4. **Maintainability**: Changes are localized to specific agents
5. **Extensibility**: New agents can be added easily
6. **Claude Code Native**: Designed specifically for Claude Code's Task system

### Next Steps

1. **Phase 1**: Implement core agents (RecordingEngine, ScenarioPlayer)
2. **Phase 2**: Implement subagents (ActionInterceptor, ScreenshotManager, etc.)
3. **Phase 3**: Implement code generation agents
4. **Phase 4**: Implement support agents (testing, review, docs)
5. **Phase 5**: Integration testing and optimization

### Agent Count Summary

- **Primary Agents**: 5
- **Subagents**: 15
- **Support Agents**: 3
- **Total Agents**: 23

Each agent is designed to be invoked via Claude Code's `Task` tool, ensuring seamless integration with the existing workflow system.

---

**Document End**

*This agent architecture is ready for implementation in Claude Code. Each agent can be developed, tested, and deployed independently, enabling parallel development and rapid iteration.*
