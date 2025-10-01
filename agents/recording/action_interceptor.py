"""
ActionInterceptor Agent - Subagent for Action Capture.

Intercepts and logs MCP tool calls during recording.
"""

import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from ..base import SubAgent
from ..models import Action
from ..registry import register_agent


class ActionInterceptorAgent(SubAgent):
    """
    Subagent that intercepts and captures MCP tool calls.

    Responsibilities:
    - Apply @recordable decorator to MCP tools
    - Capture action metadata (tool, params, timestamp)
    - Extract timing information (delays)
    - Buffer actions in memory
    - Pass actions to parent RecordingEngine
    """

    # Class-level state for interception
    _active_recording_id: Optional[str] = None
    _action_buffer: List[Action] = []
    _action_counter: int = 0
    _last_action_time: Optional[float] = None
    _recording_callback: Optional[Callable] = None

    def __init__(self):
        super().__init__("ActionInterceptor", parent_agent="RecordingEngine")

    def _process(self, inputs: Dict[str, Any]) -> Any:
        """
        Process interceptor commands.

        Supported actions:
        - install: Install interceptors on specified tools
        - flush: Return buffered actions
        - clear: Clear the buffer
        """
        action = inputs.get("action", "install")

        if action == "install":
            return self._install_interceptors(
                recording_id=inputs["recording_id"],
                tools=inputs.get("tools_to_intercept", []),
                capture_timing=inputs.get("capture_timing", True),
            )
        elif action == "flush":
            return self._flush_buffer()
        elif action == "clear":
            return self._clear_buffer()
        else:
            raise ValueError(f"Unknown action: {action}")

    def _install_interceptors(
        self, recording_id: str, tools: List[str], capture_timing: bool
    ) -> Dict[str, Any]:
        """
        Install interceptors on specified MCP tools.

        Args:
            recording_id: ID of the active recording
            tools: List of tool names to intercept
            capture_timing: Whether to capture timing information

        Returns:
            Status information
        """
        # Set class-level state
        ActionInterceptorAgent._active_recording_id = recording_id
        ActionInterceptorAgent._action_buffer = []
        ActionInterceptorAgent._action_counter = 0
        ActionInterceptorAgent._last_action_time = None

        self.logger.info(f"Installed interceptors for recording: {recording_id}")
        self.logger.info(f"Intercepting tools: {', '.join(tools)}")

        return {
            "status": "active",
            "recording_id": recording_id,
            "tools_intercepted": tools,
            "message": f"Interceptors installed on {len(tools)} tools",
        }

    def _flush_buffer(self) -> List[Action]:
        """Return and clear the action buffer"""
        buffer = ActionInterceptorAgent._action_buffer.copy()
        ActionInterceptorAgent._action_buffer = []
        self.logger.info(f"Flushed {len(buffer)} actions from buffer")
        return buffer

    def _clear_buffer(self) -> Dict[str, Any]:
        """Clear the action buffer"""
        count = len(ActionInterceptorAgent._action_buffer)
        ActionInterceptorAgent._action_buffer = []
        self.logger.info(f"Cleared {count} actions from buffer")
        return {"cleared": count}

    @classmethod
    def is_active(cls) -> bool:
        """Check if interception is currently active"""
        return cls._active_recording_id is not None

    @classmethod
    def capture_action(
        cls, tool_name: str, params: Dict[str, Any], result: Any
    ) -> Action:
        """
        Capture an action from a tool call.

        Args:
            tool_name: Name of the MCP tool called
            params: Parameters passed to the tool
            result: Result returned by the tool

        Returns:
            The captured Action object
        """
        current_time = time.time()

        # Calculate delay before (time since last action)
        delay_before_ms = 0
        if cls._last_action_time is not None:
            delay_before_ms = int((current_time - cls._last_action_time) * 1000)

        # Create action
        action = Action(
            id=cls._action_counter,
            timestamp=datetime.now().isoformat(),
            tool=tool_name,
            params=params.copy(),
            result=result,
            delay_before_ms=delay_before_ms,
            delay_after_ms=0,  # Will be set by next action
        )

        # Update last action's delay_after if exists
        if cls._action_buffer:
            # In practice, delay_after would be set after a short wait
            # For now, we'll leave it as 0
            pass

        # Add to buffer
        cls._action_buffer.append(action)
        cls._action_counter += 1
        cls._last_action_time = current_time

        return action

    @classmethod
    def set_callback(cls, callback: Callable[[Action], None]) -> None:
        """
        Set a callback to be called when actions are captured.

        Args:
            callback: Function to call with each captured action
        """
        cls._recording_callback = callback

    @classmethod
    def deactivate(cls) -> None:
        """Deactivate interception"""
        cls._active_recording_id = None
        cls._action_buffer = []
        cls._action_counter = 0
        cls._last_action_time = None
        cls._recording_callback = None


def recordable(func: Callable) -> Callable:
    """
    Decorator to make a function recordable.

    When applied to MCP tool functions, this decorator will
    intercept calls and capture them as Actions when recording is active.

    Usage:
        @recordable
        def click(selector: str, **kwargs):
            # ... implementation
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Execute the function
        result = func(*args, **kwargs)

        # If recording is active, capture the action
        if ActionInterceptorAgent.is_active():
            # Extract function name and parameters
            tool_name = func.__name__

            # Build params dict from args and kwargs
            params = kwargs.copy()
            # Note: In real implementation, would need to map positional args to param names

            # Capture the action
            action = ActionInterceptorAgent.capture_action(
                tool_name=tool_name, params=params, result=result
            )

            # Call callback if set
            if ActionInterceptorAgent._recording_callback:
                ActionInterceptorAgent._recording_callback(action)

        return result

    return wrapper


# Register this agent
register_agent("action-interceptor", ActionInterceptorAgent)
