"""
Execution Context Module

Provides execution context with retry logic, timeouts, and metrics collection.
Implements resilience patterns for robust scenario replay.
"""

from dataclasses import dataclass
from typing import Any, Optional, Dict
import time
from pathlib import Path
import server

from .replay_report import ActionResult, ActionStatus, ExecutionMetrics


@dataclass
class ReplayConfig:
    """Configuration for replay execution"""
    retry_attempts: int = 3
    retry_delay_ms: int = 500
    capture_screenshots: bool = False
    screenshot_on_error: bool = True
    compare_screenshots: bool = False
    speed_multiplier: float = 1.0
    timeout_multiplier: float = 1.0
    stop_on_error: bool = False
    wait_for_screen_on: bool = True


class ExecutionContext:
    """
    Provides execution context with resilience patterns.

    Wraps action execution with:
    - Automatic retries on failure
    - Configurable timeouts
    - Screenshot capture for debugging
    - Detailed timing metrics
    """

    def __init__(
        self,
        device_id: Optional[str],
        config: ReplayConfig
    ):
        self.device_id = device_id
        self.config = config
        self.screenshot_dir = Path("replay_screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)

    def execute_with_retry(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        action_index: int,
        dispatcher
    ) -> ActionResult:
        """
        Execute action with retry logic and comprehensive error handling.

        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            action_index: Index in action sequence
            dispatcher: ActionDispatcher instance

        Returns:
            ActionResult with execution details
        """
        metrics = None
        last_error = None
        screenshot_before = None
        screenshot_after = None

        # Capture before screenshot if enabled
        if self.config.capture_screenshots:
            screenshot_before = self._capture_screenshot(
                action_index, "before"
            )

        start_time = time.time()

        # Retry loop
        for attempt in range(self.config.retry_attempts):
            try:
                # Execute action
                result = dispatcher.dispatch(tool_name, parameters)

                # Success path
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000

                metrics = ExecutionMetrics(
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=duration_ms,
                    retry_count=attempt,
                    timeout_occurred=False,
                    screenshot_captured=self.config.capture_screenshots
                )

                # Capture after screenshot on success
                if self.config.capture_screenshots:
                    screenshot_after = self._capture_screenshot(
                        action_index, "after"
                    )

                return ActionResult(
                    action_index=action_index,
                    tool_name=tool_name,
                    parameters=parameters,
                    status=ActionStatus.SUCCESS,
                    result=result,
                    error=None,
                    metrics=metrics,
                    screenshot_before=screenshot_before,
                    screenshot_after=screenshot_after
                )

            except Exception as e:
                last_error = str(e)

                # Wait before retry (exponential backoff)
                if attempt < self.config.retry_attempts - 1:
                    delay = self.config.retry_delay_ms / 1000.0
                    delay *= (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)

        # All retries failed
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        metrics = ExecutionMetrics(
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            retry_count=self.config.retry_attempts,
            timeout_occurred=False,
            screenshot_captured=False
        )

        # Capture error screenshot
        if self.config.screenshot_on_error:
            screenshot_after = self._capture_screenshot(
                action_index, "error"
            )

        return ActionResult(
            action_index=action_index,
            tool_name=tool_name,
            parameters=parameters,
            status=ActionStatus.FAILED,
            result=None,
            error=last_error,
            metrics=metrics,
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after
        )

    def _capture_screenshot(
        self,
        action_index: int,
        stage: str
    ) -> Optional[str]:
        """
        Capture screenshot for action.

        Args:
            action_index: Action index
            stage: "before", "after", or "error"

        Returns:
            Screenshot file path or None if capture failed
        """
        try:
            filename = str(self.screenshot_dir / f"action_{action_index:03d}_{stage}.png")
            success = server.screenshot(filename, self.device_id)

            if success:
                return filename
        except Exception as e:
            print(f"Screenshot capture failed: {e}")

        return None
