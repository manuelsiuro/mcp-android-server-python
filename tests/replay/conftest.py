"""
Fixtures for Feature 3 Replay Engine Tests

Provides common test data and mock objects for replay engine testing.
"""

import pytest
from unittest.mock import MagicMock, Mock
from pathlib import Path
import json
import tempfile
from typing import Dict, Any

from replay.execution_context import ReplayConfig
from replay.replay_report import ActionStatus, ExecutionMetrics


@pytest.fixture
def mock_device():
    """Mock uiautomator2 device object."""
    device = MagicMock()
    device.device_info = {"serial": "TEST_DEVICE_123"}
    device.info = {"model": "TestPhone", "version": "13"}

    # Mock element selector
    mock_element = MagicMock()
    mock_element.exists = True
    mock_element.wait.return_value = True
    mock_element.click.return_value = True
    mock_element.info = {
        "bounds": {"left": 100, "top": 200, "right": 300, "bottom": 400}
    }
    device.return_value = mock_element
    device.xpath.return_value = mock_element

    # Mock screen operations
    device.screen_on.return_value = None
    device.screen_off.return_value = None
    device.press.return_value = None

    # Mock app operations
    device.app_start.return_value = None
    device.app_stop.return_value = None

    # Mock text input
    device.set_fastinput_ime.return_value = True
    device.send_keys.return_value = True

    return device


@pytest.fixture
def mock_dispatcher():
    """Mock ActionDispatcher with all tools registered."""
    dispatcher = MagicMock()

    # Simulate successful dispatch
    dispatcher.dispatch.return_value = True

    # Mock tool registry
    dispatcher.is_supported.return_value = True
    dispatcher.get_supported_tools.return_value = [
        'click', 'click_xpath', 'send_text', 'swipe',
        'start_app', 'press_key', 'screenshot'
    ]
    dispatcher.get_tool_signature.return_value = "(selector: str, selector_type: str = 'text', timeout: float = 10.0, device_id: Optional[str] = None) -> bool"

    return dispatcher


@pytest.fixture
def replay_config_default():
    """Default replay configuration."""
    return ReplayConfig(
        retry_attempts=3,
        retry_delay_ms=500,
        capture_screenshots=False,
        screenshot_on_error=True,
        compare_screenshots=False,
        speed_multiplier=1.0,
        timeout_multiplier=1.0,
        stop_on_error=False,
        wait_for_screen_on=True
    )


@pytest.fixture
def replay_config_fast():
    """Fast replay configuration (no retries, no screenshots)."""
    return ReplayConfig(
        retry_attempts=1,
        retry_delay_ms=0,
        capture_screenshots=False,
        screenshot_on_error=False,
        compare_screenshots=False,
        speed_multiplier=10.0,
        timeout_multiplier=0.5,
        stop_on_error=False,
        wait_for_screen_on=False
    )


@pytest.fixture
def replay_config_debug():
    """Debug replay configuration (screenshots enabled)."""
    return ReplayConfig(
        retry_attempts=1,
        retry_delay_ms=0,
        capture_screenshots=True,
        screenshot_on_error=True,
        compare_screenshots=False,
        speed_multiplier=1.0,
        timeout_multiplier=1.0,
        stop_on_error=True,
        wait_for_screen_on=False
    )


@pytest.fixture
def mock_scenario_simple() -> Dict[str, Any]:
    """Simple scenario with single action."""
    return {
        "session_name": "simple_test",
        "device_id": "TEST_DEVICE_123",
        "timestamp": "2025-10-01T12:00:00",
        "description": "Simple test scenario",
        "actions": [
            {
                "index": 0,
                "tool": "click",
                "params": {
                    "selector": "Login",
                    "selector_type": "text",
                    "device_id": "TEST_DEVICE_123"
                },
                "timestamp": "2025-10-01T12:00:01",
                "delay_before_ms": 0
            }
        ]
    }


@pytest.fixture
def mock_scenario_complex() -> Dict[str, Any]:
    """Complex scenario with 5 actions."""
    return {
        "session_name": "complex_test",
        "device_id": "TEST_DEVICE_123",
        "timestamp": "2025-10-01T12:00:00",
        "description": "Complex test scenario with multiple actions",
        "actions": [
            {
                "index": 0,
                "tool": "start_app",
                "params": {
                    "package_name": "com.example.app",
                    "device_id": "TEST_DEVICE_123"
                },
                "timestamp": "2025-10-01T12:00:01",
                "delay_before_ms": 0
            },
            {
                "index": 1,
                "tool": "click_xpath",
                "params": {
                    "xpath": "//*[@text='Login']",
                    "device_id": "TEST_DEVICE_123"
                },
                "timestamp": "2025-10-01T12:00:03",
                "delay_before_ms": 2000
            },
            {
                "index": 2,
                "tool": "send_text",
                "params": {
                    "text": "testuser",
                    "clear": True,
                    "device_id": "TEST_DEVICE_123"
                },
                "timestamp": "2025-10-01T12:00:05",
                "delay_before_ms": 2000
            },
            {
                "index": 3,
                "tool": "press_key",
                "params": {
                    "key": "enter",
                    "device_id": "TEST_DEVICE_123"
                },
                "timestamp": "2025-10-01T12:00:06",
                "delay_before_ms": 1000
            },
            {
                "index": 4,
                "tool": "screenshot",
                "params": {
                    "filename": "/tmp/test_screenshot.png",
                    "device_id": "TEST_DEVICE_123"
                },
                "timestamp": "2025-10-01T12:00:08",
                "delay_before_ms": 2000
            }
        ]
    }


@pytest.fixture
def mock_scenario_with_failures() -> Dict[str, Any]:
    """Scenario designed to test failure handling."""
    return {
        "session_name": "failure_test",
        "device_id": "TEST_DEVICE_123",
        "timestamp": "2025-10-01T12:00:00",
        "description": "Test scenario with expected failures",
        "actions": [
            {
                "index": 0,
                "tool": "click",
                "params": {
                    "selector": "Exists",
                    "device_id": "TEST_DEVICE_123"
                },
                "timestamp": "2025-10-01T12:00:01",
                "delay_before_ms": 0
            },
            {
                "index": 1,
                "tool": "click",
                "params": {
                    "selector": "DoesNotExist",
                    "device_id": "TEST_DEVICE_123"
                },
                "timestamp": "2025-10-01T12:00:02",
                "delay_before_ms": 1000
            },
            {
                "index": 2,
                "tool": "click",
                "params": {
                    "selector": "AlsoExists",
                    "device_id": "TEST_DEVICE_123"
                },
                "timestamp": "2025-10-01T12:00:03",
                "delay_before_ms": 1000
            }
        ]
    }


@pytest.fixture
def tmp_scenario_file(tmp_path, mock_scenario_simple):
    """Create temporary scenario file."""
    scenario_file = tmp_path / "test_scenario.json"
    scenario_file.write_text(json.dumps(mock_scenario_simple, indent=2))
    return str(scenario_file)


@pytest.fixture
def tmp_scenario_file_complex(tmp_path, mock_scenario_complex):
    """Create temporary complex scenario file."""
    scenario_file = tmp_path / "test_scenario_complex.json"
    scenario_file.write_text(json.dumps(mock_scenario_complex, indent=2))
    return str(scenario_file)


@pytest.fixture
def tmp_scenario_file_with_failures(tmp_path, mock_scenario_with_failures):
    """Create temporary scenario file with failures."""
    scenario_file = tmp_path / "test_scenario_failures.json"
    scenario_file.write_text(json.dumps(mock_scenario_with_failures, indent=2))
    return str(scenario_file)


@pytest.fixture
def tmp_invalid_json_file(tmp_path):
    """Create temporary file with invalid JSON."""
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{ this is not valid json }")
    return str(invalid_file)


@pytest.fixture
def tmp_missing_fields_file(tmp_path):
    """Create temporary scenario file with missing required fields."""
    scenario_file = tmp_path / "missing_fields.json"
    incomplete_scenario = {
        "session_name": "test",
        # Missing device_id and actions
    }
    scenario_file.write_text(json.dumps(incomplete_scenario, indent=2))
    return str(scenario_file)


@pytest.fixture
def sample_execution_metrics():
    """Sample execution metrics."""
    return ExecutionMetrics(
        start_time=1000.0,
        end_time=1001.5,
        duration_ms=1500.0,
        retry_count=0,
        timeout_occurred=False,
        screenshot_captured=False
    )


@pytest.fixture
def sample_action_result(sample_execution_metrics):
    """Sample action result for testing."""
    from replay.replay_report import ActionResult, ActionStatus

    return ActionResult(
        action_index=0,
        tool_name="click",
        parameters={"selector": "Test", "selector_type": "text"},
        status=ActionStatus.SUCCESS,
        result=True,
        error=None,
        metrics=sample_execution_metrics,
        screenshot_before=None,
        screenshot_after=None,
        screenshot_diff=None
    )


@pytest.fixture(autouse=True)
def cleanup_replay_screenshots():
    """Cleanup replay_screenshots directory after each test."""
    yield

    screenshot_dir = Path("replay_screenshots")
    if screenshot_dir.exists():
        import shutil
        shutil.rmtree(screenshot_dir)
