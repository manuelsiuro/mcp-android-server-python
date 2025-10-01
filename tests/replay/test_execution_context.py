"""
Unit Tests for ExecutionContext Module

Tests retry logic, screenshot capture, and metrics collection
for action execution.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock, call
import time
from pathlib import Path

from replay.execution_context import ExecutionContext, ReplayConfig
from replay.replay_report import ActionStatus, ActionResult


class TestExecutionContextInitialization:
    """Test ExecutionContext initialization."""

    def test_initialization_creates_screenshot_directory(self, replay_config_default):
        """Test that ExecutionContext creates screenshot directory."""
        context = ExecutionContext(device_id="device123", config=replay_config_default)

        assert context.screenshot_dir == Path("replay_screenshots")
        assert context.screenshot_dir.exists()
        assert context.device_id == "device123"
        assert context.config == replay_config_default

    def test_initialization_with_none_device_id(self, replay_config_default):
        """Test initialization with None device_id."""
        context = ExecutionContext(device_id=None, config=replay_config_default)

        assert context.device_id is None


class TestExecutionContextRetryLogic:
    """Test retry logic for action execution."""

    def test_execute_with_retry_success_first_attempt(self, replay_config_default, mock_dispatcher):
        """Test successful execution on first attempt (no retries)."""
        context = ExecutionContext(device_id="device123", config=replay_config_default)

        mock_dispatcher.dispatch.return_value = True

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Verify success
        assert result.status == ActionStatus.SUCCESS
        assert result.result is True
        assert result.error is None

        # Verify no retries occurred
        assert result.metrics.retry_count == 0

        # Verify dispatch called once
        assert mock_dispatcher.dispatch.call_count == 1

    def test_execute_with_retry_success_after_retries(self, replay_config_default, mock_dispatcher):
        """Test successful execution after retries."""
        context = ExecutionContext(device_id="device123", config=replay_config_default)

        # Fail twice, then succeed
        mock_dispatcher.dispatch.side_effect = [
            RuntimeError("Attempt 1 failed"),
            RuntimeError("Attempt 2 failed"),
            True  # Success on attempt 3
        ]

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Verify eventual success
        assert result.status == ActionStatus.SUCCESS
        assert result.result is True
        assert result.error is None

        # Verify retries occurred
        assert result.metrics.retry_count == 2

        # Verify dispatch called 3 times
        assert mock_dispatcher.dispatch.call_count == 3

    def test_execute_with_retry_all_retries_failed(self, replay_config_default, mock_dispatcher):
        """Test all retry attempts fail."""
        context = ExecutionContext(device_id="device123", config=replay_config_default)

        # Fail all attempts
        mock_dispatcher.dispatch.side_effect = RuntimeError("Element not found")

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Verify failure
        assert result.status == ActionStatus.FAILED
        assert result.result is None
        assert "Element not found" in result.error

        # Verify all retries exhausted
        assert result.metrics.retry_count == replay_config_default.retry_attempts

        # Verify dispatch called retry_attempts times
        assert mock_dispatcher.dispatch.call_count == replay_config_default.retry_attempts

    def test_exponential_backoff_timing(self, replay_config_default, mock_dispatcher):
        """Test exponential backoff increases delay between retries."""
        context = ExecutionContext(device_id="device123", config=replay_config_default)

        # Fail all attempts to trigger retries
        mock_dispatcher.dispatch.side_effect = RuntimeError("Retry test")

        start_time = time.time()
        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )
        end_time = time.time()

        # Verify failure (expected)
        assert result.status == ActionStatus.FAILED

        # Calculate expected delay: 0.5s + 1.0s = 1.5s minimum
        # (delay between retry 1->2 and 2->3)
        base_delay = replay_config_default.retry_delay_ms / 1000.0
        expected_min_delay = base_delay * (1 + 2)  # 0.5 * 3 = 1.5s

        actual_duration = end_time - start_time

        # Allow some tolerance for execution time
        assert actual_duration >= expected_min_delay * 0.9, \
            f"Expected at least {expected_min_delay}s, got {actual_duration}s"

    def test_no_retry_delay_on_last_attempt(self, replay_config_default, mock_dispatcher):
        """Test no delay after last retry attempt."""
        context = ExecutionContext(device_id="device123", config=replay_config_default)

        call_times = []

        def failing_dispatch(*args, **kwargs):
            call_times.append(time.time())
            raise RuntimeError("Test failure")

        mock_dispatcher.dispatch.side_effect = failing_dispatch

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Verify 3 attempts were made
        assert len(call_times) == 3

        # Check there's no significant delay after the last call
        # (function should return immediately after 3rd attempt)
        assert result.status == ActionStatus.FAILED

    def test_retry_with_zero_retry_attempts(self, replay_config_fast, mock_dispatcher):
        """Test execution with retry_attempts=1 (no retries)."""
        context = ExecutionContext(device_id="device123", config=replay_config_fast)

        mock_dispatcher.dispatch.side_effect = RuntimeError("First attempt fails")

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Should fail immediately
        assert result.status == ActionStatus.FAILED
        assert mock_dispatcher.dispatch.call_count == 1


class TestExecutionContextScreenshotCapture:
    """Test screenshot capture functionality."""

    @patch('replay.execution_context.server')
    def test_screenshot_capture_success_before_and_after(
        self, mock_server, replay_config_debug, mock_dispatcher
    ):
        """Test screenshots captured before and after action."""
        mock_server.screenshot.return_value = True
        mock_dispatcher.dispatch.return_value = True

        context = ExecutionContext(device_id="device123", config=replay_config_debug)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=5,
            dispatcher=mock_dispatcher
        )

        # Verify success
        assert result.status == ActionStatus.SUCCESS

        # Verify screenshots captured
        assert result.screenshot_before is not None
        assert result.screenshot_after is not None

        # Verify screenshot filenames
        assert "action_005_before.png" in result.screenshot_before
        assert "action_005_after.png" in result.screenshot_after

        # Verify server.screenshot called twice
        assert mock_server.screenshot.call_count == 2

    @patch('replay.execution_context.server')
    def test_screenshot_capture_disabled(
        self, mock_server, replay_config_fast, mock_dispatcher
    ):
        """Test no screenshots when capture_screenshots=False."""
        mock_server.screenshot.return_value = True
        mock_dispatcher.dispatch.return_value = True

        context = ExecutionContext(device_id="device123", config=replay_config_fast)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Verify success
        assert result.status == ActionStatus.SUCCESS

        # Verify no screenshots
        assert result.screenshot_before is None
        assert result.screenshot_after is None

        # Verify screenshot never called
        assert mock_server.screenshot.call_count == 0

    @patch('replay.execution_context.server')
    def test_screenshot_on_error(
        self, mock_server, replay_config_default, mock_dispatcher
    ):
        """Test screenshot captured on error when screenshot_on_error=True."""
        mock_server.screenshot.return_value = True
        mock_dispatcher.dispatch.side_effect = RuntimeError("Action failed")

        context = ExecutionContext(device_id="device123", config=replay_config_default)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=3,
            dispatcher=mock_dispatcher
        )

        # Verify failure
        assert result.status == ActionStatus.FAILED

        # Verify error screenshot captured
        assert result.screenshot_after is not None
        assert "action_003_error.png" in result.screenshot_after

        # Verify screenshot called once (error screenshot)
        assert mock_server.screenshot.call_count == 1

    @patch('replay.execution_context.server')
    def test_screenshot_capture_failure_handled_gracefully(
        self, mock_server, replay_config_debug, mock_dispatcher
    ):
        """Test screenshot capture failure doesn't break execution."""
        mock_server.screenshot.side_effect = Exception("Screenshot failed")
        mock_dispatcher.dispatch.return_value = True

        context = ExecutionContext(device_id="device123", config=replay_config_debug)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Action should still succeed despite screenshot failure
        assert result.status == ActionStatus.SUCCESS

        # Screenshots should be None due to failure
        assert result.screenshot_before is None
        assert result.screenshot_after is None

    @patch('replay.execution_context.server')
    def test_screenshot_filenames_use_action_index(
        self, mock_server, replay_config_debug, mock_dispatcher
    ):
        """Test screenshot filenames use zero-padded action index."""
        mock_server.screenshot.return_value = True
        mock_dispatcher.dispatch.return_value = True

        context = ExecutionContext(device_id="device123", config=replay_config_debug)

        # Test different indices
        for idx in [0, 5, 42, 999]:
            result = context.execute_with_retry(
                tool_name="click",
                parameters={"selector": "Button"},
                action_index=idx,
                dispatcher=mock_dispatcher
            )

            expected_before = f"action_{idx:03d}_before.png"
            expected_after = f"action_{idx:03d}_after.png"

            assert expected_before in result.screenshot_before
            assert expected_after in result.screenshot_after


class TestExecutionContextMetricsCollection:
    """Test execution metrics collection."""

    def test_metrics_collection_success(self, replay_config_default, mock_dispatcher):
        """Test metrics collected on successful execution."""
        mock_dispatcher.dispatch.return_value = True

        context = ExecutionContext(device_id="device123", config=replay_config_default)

        start_time = time.time()
        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )
        end_time = time.time()

        # Verify metrics present
        assert result.metrics is not None
        assert result.metrics.start_time >= start_time
        assert result.metrics.end_time <= end_time
        assert result.metrics.duration_ms > 0
        assert result.metrics.retry_count == 0
        assert result.metrics.timeout_occurred is False
        assert result.metrics.screenshot_captured is False

    def test_metrics_collection_with_retries(self, replay_config_default, mock_dispatcher):
        """Test metrics track retry count."""
        # Fail twice, succeed on third
        mock_dispatcher.dispatch.side_effect = [
            RuntimeError("Fail 1"),
            RuntimeError("Fail 2"),
            True
        ]

        context = ExecutionContext(device_id="device123", config=replay_config_default)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Verify retry count
        assert result.metrics.retry_count == 2

    def test_metrics_duration_accurate(self, replay_config_fast, mock_dispatcher):
        """Test metrics duration is accurate."""
        def slow_dispatch(*args, **kwargs):
            time.sleep(0.1)
            return True

        mock_dispatcher.dispatch.side_effect = slow_dispatch

        context = ExecutionContext(device_id="device123", config=replay_config_fast)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Verify duration is approximately 100ms
        assert result.metrics.duration_ms >= 90  # Allow some tolerance
        assert result.metrics.duration_ms < 200

    @patch('replay.execution_context.server')
    def test_metrics_screenshot_captured_flag(
        self, mock_server, replay_config_debug, mock_dispatcher
    ):
        """Test screenshot_captured flag in metrics."""
        mock_server.screenshot.return_value = True
        mock_dispatcher.dispatch.return_value = True

        context = ExecutionContext(device_id="device123", config=replay_config_debug)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Verify screenshot flag
        assert result.metrics.screenshot_captured is True

    def test_metrics_on_failure(self, replay_config_default, mock_dispatcher):
        """Test metrics collected even on failure."""
        mock_dispatcher.dispatch.side_effect = RuntimeError("Failed")

        context = ExecutionContext(device_id="device123", config=replay_config_default)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Verify metrics present despite failure
        assert result.metrics is not None
        assert result.metrics.duration_ms > 0
        assert result.metrics.retry_count == replay_config_default.retry_attempts


class TestExecutionContextActionResult:
    """Test ActionResult structure and content."""

    def test_action_result_success_structure(self, replay_config_default, mock_dispatcher):
        """Test ActionResult contains all required fields on success."""
        mock_dispatcher.dispatch.return_value = True

        context = ExecutionContext(device_id="device123", config=replay_config_default)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button", "device_id": "device123"},
            action_index=5,
            dispatcher=mock_dispatcher
        )

        # Verify all fields present
        assert result.action_index == 5
        assert result.tool_name == "click"
        assert result.parameters == {"selector": "Button", "device_id": "device123"}
        assert result.status == ActionStatus.SUCCESS
        assert result.result is True
        assert result.error is None
        assert result.metrics is not None

    def test_action_result_failure_structure(self, replay_config_default, mock_dispatcher):
        """Test ActionResult contains all required fields on failure."""
        mock_dispatcher.dispatch.side_effect = RuntimeError("Element not found")

        context = ExecutionContext(device_id="device123", config=replay_config_default)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=3,
            dispatcher=mock_dispatcher
        )

        # Verify all fields present
        assert result.action_index == 3
        assert result.tool_name == "click"
        assert result.status == ActionStatus.FAILED
        assert result.result is None
        assert "Element not found" in result.error
        assert result.metrics is not None

    def test_action_result_preserves_parameters(self, replay_config_default, mock_dispatcher):
        """Test ActionResult preserves original parameters."""
        mock_dispatcher.dispatch.return_value = True

        context = ExecutionContext(device_id="device123", config=replay_config_default)

        original_params = {
            "selector": "Button",
            "selector_type": "text",
            "timeout": 15.0,
            "device_id": "device123"
        }

        result = context.execute_with_retry(
            tool_name="click",
            parameters=original_params,
            action_index=0,
            dispatcher=mock_dispatcher
        )

        # Verify parameters preserved
        assert result.parameters == original_params


class TestExecutionContextEdgeCases:
    """Test edge cases and error conditions."""

    def test_execute_with_empty_parameters(self, replay_config_default, mock_dispatcher):
        """Test execution with empty parameters."""
        mock_dispatcher.dispatch.return_value = None

        context = ExecutionContext(device_id="device123", config=replay_config_default)

        result = context.execute_with_retry(
            tool_name="screen_on",
            parameters={},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        assert result.status == ActionStatus.SUCCESS
        assert result.parameters == {}

    def test_execute_with_none_result(self, replay_config_default, mock_dispatcher):
        """Test execution when tool returns None."""
        mock_dispatcher.dispatch.return_value = None

        context = ExecutionContext(device_id="device123", config=replay_config_default)

        result = context.execute_with_retry(
            tool_name="screen_on",
            parameters={},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        assert result.status == ActionStatus.SUCCESS
        assert result.result is None

    def test_screenshot_directory_creation_idempotent(self, replay_config_default):
        """Test screenshot directory creation is idempotent."""
        # Create multiple contexts
        context1 = ExecutionContext(device_id="device123", config=replay_config_default)
        context2 = ExecutionContext(device_id="device456", config=replay_config_default)

        # Both should use same directory
        assert context1.screenshot_dir == context2.screenshot_dir
        assert context1.screenshot_dir.exists()

    def test_execute_preserves_exception_details(self, replay_config_default, mock_dispatcher):
        """Test exception details preserved in error message."""
        mock_dispatcher.dispatch.side_effect = ValueError("Invalid selector type: 'xyz'")

        context = ExecutionContext(device_id="device123", config=replay_config_default)

        result = context.execute_with_retry(
            tool_name="click",
            parameters={"selector": "Button"},
            action_index=0,
            dispatcher=mock_dispatcher
        )

        assert result.status == ActionStatus.FAILED
        assert "Invalid selector type" in result.error
        assert "'xyz'" in result.error
