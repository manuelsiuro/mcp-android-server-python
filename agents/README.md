# Android Scenario Recording & Espresso Test Generation Agent System

A hierarchical multi-agent system for recording Android UI interactions, replaying scenarios, and generating Espresso test code.

## Overview

This agent system provides a modular, scalable architecture for automating Android UI testing workflows. It consists of 16 specialized agents organized into functional groups:

- **Recording System** (3 agents): Capture Android UI interactions
- **Replay System** (4 agents): Execute recorded scenarios
- **Code Generation** (5 agents): Generate Espresso test code
- **Quality & Support** (4 agents): Testing, review, and documentation

## Architecture

### Agent Hierarchy

```
agents/
├── base.py                 # Base classes for all agents
├── models.py               # Data models and types
├── registry.py             # Agent registration and lookup
├── recording/              # Recording system agents
│   ├── recording_engine.py       # Primary: Orchestrates recording
│   ├── action_interceptor.py     # Subagent: Captures MCP tool calls
│   └── screenshot_manager.py     # Subagent: Manages screenshots
├── replay/                 # Replay system agents
│   ├── scenario_player.py        # Primary: Orchestrates replay
│   ├── scenario_parser.py        # Subagent: Parses JSON scenarios
│   ├── action_executor.py        # Subagent: Executes actions
│   └── ui_validator.py           # Subagent: Validates UI state
├── codegen/                # Code generation agents
│   ├── espresso_generator.py     # Primary: Generates test code
│   ├── selector_mapper.py        # Subagent: Maps selectors
│   ├── action_mapper.py          # Subagent: Maps actions
│   ├── compose_detector.py       # Subagent: Detects UI framework
│   └── code_formatter.py         # Subagent: Formats code
├── quality/                # Quality assurance agents
│   ├── test_writer.py            # Support: Generates unit tests
│   ├── code_reviewer.py          # Support: Reviews code quality
│   └── integration_tester.py     # Support: Integration tests
└── docs/                   # Documentation agent
    └── documentation_agent.py    # Support: Generates docs
```

## Agent Types

### Primary Agents

Orchestrate complex workflows and coordinate subagents:

- **RecordingEngine**: Manages recording sessions, coordinates action capture and screenshot management
- **ScenarioPlayer**: Executes recorded scenarios, handles error recovery and retry logic
- **EspressoCodeGenerator**: Generates Espresso test code, coordinates mapping and formatting

### Subagents

Perform focused, specialized tasks:

- **ActionInterceptor**: Intercepts and captures MCP tool calls during recording
- **ScreenshotManager**: Captures and organizes screenshots
- **ScenarioParser**: Parses and validates scenario JSON files
- **ActionExecutor**: Executes individual actions with timing and retry
- **UIValidator**: Validates UI state during replay
- **SelectorMapper**: Maps UIAutomator selectors to Espresso ViewMatchers
- **ActionMapper**: Maps UIAutomator actions to Espresso ViewActions
- **ComposeDetector**: Detects Jetpack Compose vs XML views
- **CodeFormatter**: Formats generated code

### Support Agents

Provide cross-cutting functionality:

- **TestWriter**: Generates unit tests for the system
- **CodeReviewer**: Reviews code quality and security
- **IntegrationTester**: Tests integration between components
- **DocumentationAgent**: Generates and maintains documentation

## Usage

### Basic Agent Invocation

```python
from agents import get_agent

# Get an agent class by type
RecordingEngine = get_agent("recording-engine")

# Create instance and execute
agent = RecordingEngine()
result = agent.execute({
    "action": "start",
    "session_name": "login_test",
    "device_id": "emulator-5554",
    "config": {
        "capture_screenshots": True,
        "capture_hierarchy": True
    }
})

print(f"Status: {result.status}")
print(f"Recording ID: {result.data['recording_id']}")
```

### Recording a Scenario

```python
from agents.recording import RecordingEngineAgent

engine = RecordingEngineAgent()

# Start recording
start_result = engine.execute({
    "action": "start",
    "session_name": "checkout_flow",
    "description": "Test checkout process",
    "device_id": None,  # Use default device
    "config": {
        "capture_screenshots": True,
        "capture_hierarchy": True,
        "auto_delays": True
    }
})

recording_id = start_result.data["recording_id"]

# ... user performs actions on device ...

# Stop recording
stop_result = engine.execute({
    "action": "stop",
    "recording_id": recording_id
})

print(f"Scenario saved to: {stop_result.data.session_file}")
```

### Replaying a Scenario

```python
from agents.replay import ScenarioPlayerAgent

player = ScenarioPlayerAgent()

result = player.execute({
    "scenario_file": "scenarios/checkout_flow/scenario.json",
    "device_id": "emulator-5554",
    "config": {
        "validate_ui_state": False,
        "take_screenshots": True,
        "continue_on_error": False,
        "speed_multiplier": 1.0
    }
})

print(f"Replay status: {result.data.status}")
print(f"Actions passed: {result.data.actions_passed}/{result.data.actions_total}")
```

### Generating Espresso Code

```python
from agents.codegen import EspressoCodeGeneratorAgent

generator = EspressoCodeGeneratorAgent()

result = generator.execute({
    "scenario_file": "scenarios/checkout_flow/scenario.json",
    "language": "kotlin",
    "package_name": "com.example.shop",
    "class_name": "CheckoutFlowTest",
    "options": {
        "include_comments": True,
        "use_idling_resources": False,
        "generate_custom_actions": True
    }
})

print(f"Generated code saved to: {result.data.file_path}")
print(f"UI Framework: {result.data.ui_framework}")
```

## Data Models

All agents use standardized data models defined in `models.py`:

### Recording Models

- `RecordingConfig`: Configuration for recording sessions
- `Action`: Represents a captured or replayed action
- `RecordingSession`: Active recording state
- `RecordingResult`: Result of completed recording

### Replay Models

- `Scenario`: Complete scenario structure
- `ReplayConfig`: Configuration for replay
- `ActionResult`: Result of action execution
- `ReplayReport`: Complete replay report

### Code Generation Models

- `GeneratedCode`: Result of code generation
- `MappedSelector`: Mapped selector to Espresso
- `MappedAction`: Mapped action to Espresso
- `FrameworkDetection`: UI framework detection result

### Agent Communication

- `AgentResponse`: Standard agent response format
- `AgentError`: Structured error information
- `AgentMetadata`: Execution metadata

## Agent Communication Protocol

All agents follow a standardized communication protocol:

### Input Format

```python
inputs = {
    "action": "start",  # Action to perform
    # ... action-specific parameters
}
```

### Output Format

```python
AgentResponse(
    agent="RecordingEngine",
    status=AgentStatus.SUCCESS,
    data={...},  # Agent-specific output
    errors=[],
    metadata=AgentMetadata(
        execution_time_ms=1250,
        agent_version="1.0.0",
        timestamp="2025-01-15T10:30:00"
    )
)
```

### Error Handling

```python
AgentResponse(
    agent="ScenarioParser",
    status=AgentStatus.ERROR,
    data=None,
    errors=[
        AgentError(
            severity=Severity.CRITICAL,
            message="Invalid scenario format",
            context={"file": "scenario.json"}
        )
    ],
    metadata=...
)
```

## Development

### Creating a New Agent

1. **Inherit from appropriate base class:**

```python
from agents.base import SubAgent
from agents.registry import register_agent

class MyCustomAgent(SubAgent):
    def __init__(self):
        super().__init__("MyCustomAgent", parent_agent="ParentAgent")

    def _process(self, inputs: Dict[str, Any]) -> Any:
        # Implement agent logic
        return result

# Register the agent
register_agent("my-custom-agent", MyCustomAgent)
```

2. **Add to module `__init__.py`**
3. **Write unit tests in `tests/agents/`**

### Running Tests

```bash
# Run all agent tests
pytest tests/agents/

# Run specific agent test
pytest tests/agents/test_recording_engine.py

# Run with coverage
pytest --cov=agents tests/agents/
```

### Code Quality

```bash
# Lint with ruff
ruff check agents/

# Format code
ruff format agents/

# Type checking
mypy agents/
```

## Integration with Claude Code

This agent system is designed to work seamlessly with Claude Code's Task tool:

```python
# In Claude Code context
result = Task(
    subagent_type="recording-engine",
    prompt="""
    Start a new recording session:
    - Session name: "login_flow"
    - Device: Connected Android device
    - Capture screenshots and UI hierarchy
    Return the recording_id and confirm ready state.
    """,
    description="Initialize recording session"
)
```

## Best Practices

1. **Always validate inputs** in `_validate_inputs()` method
2. **Use logging** for debugging and monitoring
3. **Return structured data** using defined models
4. **Handle errors gracefully** with appropriate error levels
5. **Document agent behavior** with clear docstrings
6. **Write tests** for all agent logic
7. **Version your agents** for compatibility tracking

## Performance Targets

| Agent Type | Target Time | Max Time |
|------------|-------------|----------|
| ActionInterceptor | <50ms | 100ms |
| ScreenshotManager | <500ms | 1000ms |
| ScenarioParser | <1s | 5s |
| UIValidator | <2s | 10s |
| EspressoCodeGenerator | <5s | 30s |
| SelectorMapper | <100ms | 500ms |

## Quality Metrics

- **Code Coverage**: ≥80% for all agents
- **Complexity**: Max cyclomatic complexity ≤10 per method
- **Documentation**: 100% of public APIs documented
- **Type Hints**: 100% of function signatures

## License

See project root LICENSE file.

## Contributing

See CONTRIBUTING.md for guidelines.
