"""
POC Unit Tests for Recording Mechanism

This tests the core recording functionality without requiring a real device.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the server module
import server


class TestRecordingMechanism:
    """Test the recording mechanism POC."""

    def setup_method(self):
        """Reset recording state before each test."""
        server._recording_state = {
            "active": False,
            "session_name": None,
            "actions": [],
            "screenshots_dir": None,
            "start_time": None,
            "action_counter": 0,
            "device_id": None,
            "last_action_time": None
        }
        # Clean up any test scenarios
        if Path("scenarios").exists():
            import shutil
            shutil.rmtree("scenarios")

    def test_start_recording_success(self):
        """Test successful recording start."""
        result = server.start_recording("unit_test", description="Test scenario")

        assert result["status"] == "active"
        assert "unit_test_" in result["recording_id"]
        assert result["capture_screenshots"] is True
        assert server._recording_state["active"] is True

    def test_start_recording_already_active(self):
        """Test starting recording when already active."""
        # Start first recording
        server.start_recording("test1")

        # Try to start second recording
        result = server.start_recording("test2")

        assert "error" in result
        assert "already in progress" in result["error"]

    def test_stop_recording_no_active_session(self):
        """Test stopping when no recording is active."""
        result = server.stop_recording()

        assert "error" in result
        assert "No active recording session" in result["error"]

    def test_record_action_when_inactive(self):
        """Test that actions are not recorded when recording is inactive."""
        server._record_action("click", {"selector": "test"}, True)

        assert len(server._recording_state["actions"]) == 0

    def test_record_action_when_active(self):
        """Test action recording when recording is active."""
        # Start recording
        server.start_recording("test_actions")

        # Record an action
        server._record_action("click", {
            "selector": "Login",
            "selector_type": "text"
        }, True)

        assert len(server._recording_state["actions"]) == 1
        action = server._recording_state["actions"][0]
        assert action["id"] == 1
        assert action["tool"] == "click"
        assert action["params"]["selector"] == "Login"

    def test_recording_delay_calculation(self):
        """Test that delays between actions are calculated."""
        import time

        server.start_recording("test_delays")

        # Record first action
        server._record_action("click", {"selector": "A"}, True)

        # Wait a bit
        time.sleep(0.1)

        # Record second action
        server._record_action("click", {"selector": "B"}, True)

        actions = server._recording_state["actions"]
        assert len(actions) == 2
        assert actions[0]["delay_before_ms"] == 0  # First action has no delay
        assert actions[1]["delay_before_ms"] >= 100  # Second action has ~100ms delay

    @patch('server.u2.connect')
    def test_stop_recording_saves_json(self, mock_connect):
        """Test that stop_recording saves a valid JSON file."""
        # Mock device info
        mock_device = MagicMock()
        mock_device.info = {
            "manufacturer": "TestManufacturer",
            "model": "TestModel",
            "version": {"release": "13", "sdk": 33}
        }
        mock_connect.return_value = mock_device

        # Start recording
        server.start_recording("test_json", description="Test JSON generation")

        # Record some actions
        server._record_action("click", {"selector": "Button1"}, True)
        server._record_action("send_text", {"text": "test"}, True)

        # Stop recording
        result = server.stop_recording()

        assert result["status"] == "saved"
        assert result["action_count"] == 2
        assert Path(result["scenario_file"]).exists()

        # Verify JSON structure
        with open(result["scenario_file"]) as f:
            scenario = json.load(f)

        assert scenario["schema_version"] == "1.0"
        assert scenario["metadata"]["description"] == "Test JSON generation"
        assert len(scenario["actions"]) == 2
        assert scenario["actions"][0]["tool"] == "click"
        assert scenario["actions"][1]["tool"] == "send_text"

    def test_get_recording_status_inactive(self):
        """Test status check when no recording is active."""
        result = server.get_recording_status()

        assert result["active"] is False
        assert "No recording" in result["message"]

    def test_get_recording_status_active(self):
        """Test status check when recording is active."""
        server.start_recording("test_status")
        server._record_action("click", {"selector": "Test"}, True)

        result = server.get_recording_status()

        assert result["active"] is True
        assert result["action_count"] == 1
        assert "test_status_" in result["session_name"]

    @patch('server.u2.connect')
    def test_click_records_action(self, mock_connect):
        """Test that click() function records actions when recording is active."""
        # Mock device and element
        mock_device = MagicMock()
        mock_element = MagicMock()
        mock_element.wait.return_value = True
        mock_element.exists = True
        mock_element.info = {
            "bounds": {"left": 100, "top": 200, "right": 300, "bottom": 400}
        }
        mock_device.return_value = mock_element
        mock_connect.return_value = mock_device

        # Start recording
        server.start_recording("test_click_recording")

        # Call click
        result = server.click("Login", selector_type="text")

        # Verify click succeeded
        assert result is True

        # Verify action was recorded
        assert len(server._recording_state["actions"]) == 1
        action = server._recording_state["actions"][0]
        assert action["tool"] == "click"
        assert action["params"]["selector"] == "Login"
        assert action["params"]["selector_type"] == "text"

    @patch('server.u2.connect')
    def test_send_text_records_action(self, mock_connect):
        """Test that send_text() function records actions when recording is active."""
        # Mock device
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        # Start recording
        server.start_recording("test_send_text_recording")

        # Call send_text
        result = server.send_text("testuser", clear=True)

        # Verify send_text succeeded
        assert result is True

        # Verify action was recorded
        assert len(server._recording_state["actions"]) == 1
        action = server._recording_state["actions"][0]
        assert action["tool"] == "send_text"
        assert action["params"]["text"] == "testuser"
        assert action["params"]["clear"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
