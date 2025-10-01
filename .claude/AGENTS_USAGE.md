# Using the Agent System with Claude Code

This guide shows how to invoke the specialized agents from Claude Code conversations.

## Quick Start

### Method 1: Direct Python Usage

You can use agents directly in Python code:

```python
from agents.recording import RecordingEngineAgent
from agents.replay import ScenarioPlayerAgent
from agents.codegen import EspressoCodeGeneratorAgent

# Start a recording
recording_agent = RecordingEngineAgent()
result = recording_agent.execute({
    "action": "start",
    "session_name": "login_test",
    "device_id": "emulator-5554",
    "config": {
        "capture_screenshots": True,
        "capture_hierarchy": True
    }
})

print(f"Recording ID: {result.data['recording_id']}")

# Later, stop the recording
stop_result = recording_agent.execute({
    "action": "stop",
    "recording_id": result.data['recording_id']
})

print(f"Scenario saved to: {stop_result.data['session_file']}")

# Replay the scenario
player_agent = ScenarioPlayerAgent()
replay_result = player_agent.execute({
    "scenario_file": stop_result.data['session_file'],
    "device_id": "emulator-5554",
    "config": {
        "continue_on_error": False,
        "speed_multiplier": 1.0
    }
})

print(f"Replay status: {replay_result.data.status}")

# Generate Espresso code
codegen_agent = EspressoCodeGeneratorAgent()
code_result = codegen_agent.execute({
    "scenario_file": stop_result.data['session_file'],
    "language": "kotlin",
    "package_name": "com.example.app",
    "options": {
        "include_comments": True,
        "generate_custom_actions": True
    }
})

print(f"Generated code saved to: {code_result.data.file_path}")
```

### Method 2: Ask Claude Code to Use Agents

You can ask me to use the agents in natural language:

**Example 1: Recording**
```
User: "Start a recording session named 'checkout_flow' for testing the checkout process"

Claude: [Uses RecordingEngine agent to start recording]
```

**Example 2: Replay**
```
User: "Replay the scenario from scenarios/checkout_flow/scenario.json"

Claude: [Uses ScenarioPlayer agent to replay]
```

**Example 3: Code Generation**
```
User: "Generate Kotlin Espresso test code from scenarios/checkout_flow/scenario.json"

Claude: [Uses EspressoCodeGenerator agent to generate code]
```

### Method 3: Task Tool (Advanced)

For complex workflows, I can use the Task tool to invoke agents:

```python
result = Task(
    subagent_type="recording-engine",
    prompt="""
    Start a new recording session:
    - Session name: "login_flow"
    - Description: "Test login with valid credentials"
    - Device: emulator-5554
    - Capture screenshots and UI hierarchy

    Return the recording_id and confirm ready state.
    """,
    description="Initialize recording session"
)
```

## Available Agents

### Primary Agents

1. **recording-engine** - Start/stop/manage recording sessions
2. **scenario-player** - Replay recorded scenarios
3. **espresso-code-generator** - Generate Espresso test code

### Subagents (used internally by primary agents)

- **action-interceptor** - Captures MCP tool calls during recording
- **screenshot-manager** - Manages screenshot capture
- **scenario-parser** - Parses and validates scenario JSON
- **action-executor** - Executes individual actions with retry
- **ui-validator** - Validates UI state during replay
- **selector-mapper** - Maps selectors to Espresso
- **action-mapper** - Maps actions to Espresso
- **compose-detector** - Detects Jetpack Compose vs XML
- **code-formatter** - Formats generated code

### Support Agents

- **test-writer** - Generates unit tests
- **code-reviewer** - Reviews code quality
- **integration-tester** - Integration testing
- **documentation** - Generates documentation

## Common Workflows

### Workflow 1: Record → Replay → Generate Code

```python
# 1. Record
recording_agent = RecordingEngineAgent()
rec_result = recording_agent.execute({
    "action": "start",
    "session_name": "user_registration"
})

# ... perform actions on device ...

stop_result = recording_agent.execute({
    "action": "stop",
    "recording_id": rec_result.data['recording_id']
})

# 2. Replay
player_agent = ScenarioPlayerAgent()
replay_result = player_agent.execute({
    "scenario_file": stop_result.data['session_file']
})

# 3. Generate Code (only if replay passed)
if replay_result.data.status == "PASSED":
    codegen_agent = EspressoCodeGeneratorAgent()
    code_result = codegen_agent.execute({
        "scenario_file": stop_result.data['session_file'],
        "language": "kotlin"
    })
```

### Workflow 2: Generate Code from Existing Scenario

```python
codegen_agent = EspressoCodeGeneratorAgent()
result = codegen_agent.execute({
    "scenario_file": "scenarios/existing_scenario/scenario.json",
    "language": "kotlin",
    "package_name": "com.myapp",
    "class_name": "MyFeatureTest"
})
```

## Agent Response Format

All agents return standardized responses:

```python
{
    "agent": "RecordingEngine",
    "status": "success" | "error" | "partial",
    "data": { ... },  # Agent-specific results
    "errors": [
        {
            "severity": "critical" | "warning" | "info",
            "message": "Error description",
            "context": { ... }
        }
    ],
    "metadata": {
        "execution_time_ms": 1250,
        "agent_version": "1.0.0",
        "timestamp": "2025-01-15T10:30:00"
    }
}
```

## Tips

1. **Always check response status** before using data:
   ```python
   if result.status == AgentStatus.SUCCESS:
       # Use result.data
   else:
       # Handle errors from result.errors
   ```

2. **Use device_id consistently** across recording and replay

3. **Save recording_id** when starting recording - you'll need it to stop

4. **Check replay status** before generating code - only generate from successful replays

5. **Review generated code** - agents may add warnings for manual adjustments

## Next Steps

- See `agents/README.md` for detailed agent documentation
- See `.claude/commands/agents/*.md` for individual agent prompts
- See `agent-architecture.md` for system architecture details

## Need Help?

Just ask me! For example:
- "Start a recording session for testing login"
- "Replay the scenario from scenarios/test/scenario.json"
- "Generate Kotlin test code from my latest recording"
- "How do I use the ActionInterceptor agent?"
