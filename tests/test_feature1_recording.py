"""
Comprehensive Test Suite for Feature 1: Recording Extended to All Action Tools

This test suite validates that all 48 action tools have recording functionality
working correctly.
"""

import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import json

import server


class TestFeature1RecordingCoverage:
    """Test that all 48 action tools have recording capability."""

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

    def teardown_method(self):
        """Clean up test artifacts."""
        if Path("scenarios").exists():
            import shutil
            shutil.rmtree("scenarios")

    # ========================================================================
    # UI INTERACTION TOOLS (10 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_click_has_recording(self, mock_connect):
        """Test click() records action."""
        mock_device = MagicMock()
        mock_element = MagicMock()
        mock_element.wait.return_value = True
        mock_element.exists = True
        mock_element.info = {"bounds": {"left": 0, "top": 0, "right": 100, "bottom": 100}}
        mock_device.return_value = mock_element
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.click("Test", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "click"
        assert server._recording_state["actions"][0]["params"]["selector"] == "Test"

    @patch('server.u2.connect')
    def test_send_text_has_recording(self, mock_connect):
        """Test send_text() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.send_text("test text", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "send_text"
        assert server._recording_state["actions"][0]["params"]["text"] == "test text"

    @patch('server.u2.connect')
    def test_long_click_has_recording(self, mock_connect):
        """Test long_click() records action."""
        mock_device = MagicMock()
        mock_element = MagicMock()
        mock_element.exists = True
        mock_element.info = {"bounds": {"left": 0, "top": 0, "right": 100, "bottom": 100}}
        mock_device.return_value = mock_element
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.long_click("Test", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "long_click"

    @patch('server.u2.connect')
    def test_double_click_has_recording(self, mock_connect):
        """Test double_click() records action."""
        mock_device = MagicMock()
        mock_element = MagicMock()
        mock_element.wait.return_value = mock_element
        mock_element.exists = True
        mock_device.return_value = mock_element
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.double_click("Test", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "double_click"

    @patch('server.u2.connect')
    def test_swipe_has_recording(self, mock_connect):
        """Test swipe() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.swipe(100, 200, 300, 400, device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "swipe"
        assert server._recording_state["actions"][0]["params"]["start_x"] == 100

    @patch('server.u2.connect')
    def test_drag_has_recording(self, mock_connect):
        """Test drag() records action."""
        mock_device = MagicMock()
        mock_element = MagicMock()
        mock_element.exists = True
        mock_device.return_value = mock_element
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.drag("Test", "text", 500, 600, device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "drag"

    @patch('server.u2.connect')
    def test_click_at_has_recording(self, mock_connect):
        """Test click_at() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.click_at(100, 200, device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "click_at"
        assert server._recording_state["actions"][0]["params"]["x"] == 100

    @patch('server.u2.connect')
    def test_double_click_at_has_recording(self, mock_connect):
        """Test double_click_at() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.double_click_at(150, 250, device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "double_click_at"

    @patch('server.u2.connect')
    def test_screenshot_has_recording(self, mock_connect):
        """Test screenshot() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.screenshot("/tmp/test.png", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "screenshot"

    @patch('server.u2.connect')
    def test_wait_for_element_has_recording(self, mock_connect):
        """Test wait_for_element() records action."""
        mock_device = MagicMock()
        mock_element = MagicMock()
        mock_element.wait.return_value = True
        mock_device.return_value = mock_element
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.wait_for_element("Test", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "wait_for_element"

    # ========================================================================
    # XPATH TOOLS (4 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_click_xpath_has_recording(self, mock_connect):
        """Test click_xpath() records action."""
        mock_device = MagicMock()
        mock_xpath = MagicMock()
        mock_xpath.wait.return_value = True
        mock_xpath.info = {"bounds": {"left": 0, "top": 0, "right": 100, "bottom": 100}}
        mock_device.xpath.return_value = mock_xpath
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.click_xpath("//node[@text='Test']", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "click_xpath"

    @patch('server.u2.connect')
    def test_long_click_xpath_has_recording(self, mock_connect):
        """Test long_click_xpath() records action."""
        mock_device = MagicMock()
        mock_xpath = MagicMock()
        mock_xpath.exists = True
        mock_xpath.info = {"bounds": {"left": 0, "top": 0, "right": 100, "bottom": 100}}
        mock_device.xpath.return_value = mock_xpath
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.long_click_xpath("//node[@text='Test']", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "long_click_xpath"

    @patch('server.u2.connect')
    def test_send_text_xpath_has_recording(self, mock_connect):
        """Test send_text_xpath() records action."""
        mock_device = MagicMock()
        mock_xpath = MagicMock()
        mock_xpath.exists = True
        mock_device.xpath.return_value = mock_xpath
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.send_text_xpath("//node[@text='Input']", "test", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "send_text_xpath"

    @patch('server.u2.connect')
    def test_wait_xpath_has_recording(self, mock_connect):
        """Test wait_xpath() records action."""
        mock_device = MagicMock()
        mock_xpath = MagicMock()
        mock_xpath.wait.return_value = True
        mock_device.xpath.return_value = mock_xpath
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.wait_xpath("//node[@text='Test']", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "wait_xpath"

    # ========================================================================
    # SCROLLING TOOLS (6 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_scroll_to_has_recording(self, mock_connect):
        """Test scroll_to() records action."""
        mock_device = MagicMock()
        mock_scrollable = MagicMock()
        mock_scroll = MagicMock()
        mock_scroll.to.return_value = True
        mock_scrollable.scroll = mock_scroll
        mock_device.return_value = mock_scrollable
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.scroll_to("Test", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "scroll_to"

    @patch('server.u2.connect')
    def test_scroll_forward_has_recording(self, mock_connect):
        """Test scroll_forward() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.scroll_forward(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "scroll_forward"

    @patch('server.u2.connect')
    def test_scroll_backward_has_recording(self, mock_connect):
        """Test scroll_backward() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.scroll_backward(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "scroll_backward"

    @patch('server.u2.connect')
    def test_scroll_to_beginning_has_recording(self, mock_connect):
        """Test scroll_to_beginning() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.scroll_to_beginning(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "scroll_to_beginning"

    @patch('server.u2.connect')
    def test_scroll_to_end_has_recording(self, mock_connect):
        """Test scroll_to_end() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.scroll_to_end(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "scroll_to_end"

    @patch('server.u2.connect')
    def test_fling_forward_has_recording(self, mock_connect):
        """Test fling_forward() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.fling_forward(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "fling_forward"

    @patch('server.u2.connect')
    def test_fling_backward_has_recording(self, mock_connect):
        """Test fling_backward() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.fling_backward(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "fling_backward"

    # ========================================================================
    # APP CONTROL TOOLS (6 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_start_app_has_recording(self, mock_connect):
        """Test start_app() records action."""
        mock_device = MagicMock()
        mock_device.app_wait.return_value = 123
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.start_app("com.test.app", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "start_app"
        assert server._recording_state["actions"][0]["params"]["package_name"] == "com.test.app"

    @patch('server.u2.connect')
    def test_stop_app_has_recording(self, mock_connect):
        """Test stop_app() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.stop_app("com.test.app", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "stop_app"

    @patch('server.u2.connect')
    def test_stop_all_apps_has_recording(self, mock_connect):
        """Test stop_all_apps() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.stop_all_apps(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "stop_all_apps"

    @patch('server.u2.connect')
    def test_install_app_has_recording(self, mock_connect):
        """Test install_app() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.install_app("/path/to/app.apk", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "install_app"

    @patch('server.u2.connect')
    def test_uninstall_app_has_recording(self, mock_connect):
        """Test uninstall_app() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.uninstall_app("com.test.app", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "uninstall_app"

    @patch('server.u2.connect')
    def test_clear_app_data_has_recording(self, mock_connect):
        """Test clear_app_data() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.clear_app_data("com.test.app", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "clear_app_data"

    # ========================================================================
    # SCREEN CONTROL TOOLS (6 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_press_key_has_recording(self, mock_connect):
        """Test press_key() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.press_key("home", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "press_key"
        assert server._recording_state["actions"][0]["params"]["key"] == "home"

    @patch('server.u2.connect')
    def test_screen_on_has_recording(self, mock_connect):
        """Test screen_on() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.screen_on(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "screen_on"

    @patch('server.u2.connect')
    def test_screen_off_has_recording(self, mock_connect):
        """Test screen_off() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.screen_off(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "screen_off"

    @patch('server.u2.connect')
    def test_unlock_screen_has_recording(self, mock_connect):
        """Test unlock_screen() records action."""
        mock_device = MagicMock()
        mock_device.info = {"screenOn": True}
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.unlock_screen(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "unlock_screen"

    @patch('server.u2.connect')
    def test_set_orientation_has_recording(self, mock_connect):
        """Test set_orientation() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.set_orientation("landscape", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "set_orientation"

    @patch('server.u2.connect')
    def test_freeze_rotation_has_recording(self, mock_connect):
        """Test freeze_rotation() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.freeze_rotation(True, device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "freeze_rotation"

    # ========================================================================
    # GESTURE TOOLS (2 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_pinch_in_has_recording(self, mock_connect):
        """Test pinch_in() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.pinch_in(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "pinch_in"

    @patch('server.u2.connect')
    def test_pinch_out_has_recording(self, mock_connect):
        """Test pinch_out() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.pinch_out(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "pinch_out"

    # ========================================================================
    # SYSTEM TOOLS (3 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_set_clipboard_has_recording(self, mock_connect):
        """Test set_clipboard() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.set_clipboard("test text", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "set_clipboard"

    @patch('server.u2.connect')
    def test_pull_file_has_recording(self, mock_connect):
        """Test pull_file() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.pull_file("/device/path", "/local/path", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "pull_file"

    @patch('server.u2.connect')
    def test_push_file_has_recording(self, mock_connect):
        """Test push_file() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.push_file("/local/path", "/device/path", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "push_file"

    # ========================================================================
    # NOTIFICATION & POPUP TOOLS (3 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_open_notification_has_recording(self, mock_connect):
        """Test open_notification() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.open_notification(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "open_notification"

    @patch('server.u2.connect')
    def test_open_quick_settings_has_recording(self, mock_connect):
        """Test open_quick_settings() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.open_quick_settings(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "open_quick_settings"

    @patch('server.u2.connect')
    def test_disable_popups_has_recording(self, mock_connect):
        """Test disable_popups() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.disable_popups(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "disable_popups"

    # ========================================================================
    # WAIT TOOLS (2 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_wait_activity_has_recording(self, mock_connect):
        """Test wait_activity() records action."""
        mock_device = MagicMock()
        mock_device.wait_activity.return_value = True
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.wait_activity(".MainActivity", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "wait_activity"

    # ========================================================================
    # ADVANCED TOOLS (3 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_healthcheck_has_recording(self, mock_connect):
        """Test healthcheck() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.healthcheck(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "healthcheck"

    @patch('server.u2.connect')
    def test_reset_uiautomator_has_recording(self, mock_connect):
        """Test reset_uiautomator() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.reset_uiautomator(device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "reset_uiautomator"

    @patch('server.u2.connect')
    def test_send_action_has_recording(self, mock_connect):
        """Test send_action() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.send_action("search", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "send_action"

    # ========================================================================
    # WATCHER TOOLS (3 tools)
    # ========================================================================

    @patch('server.u2.connect')
    def test_watcher_start_has_recording(self, mock_connect):
        """Test watcher_start() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.watcher_start("test_watcher", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "watcher_start"

    @patch('server.u2.connect')
    def test_watcher_stop_has_recording(self, mock_connect):
        """Test watcher_stop() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.watcher_stop("test_watcher", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "watcher_stop"

    @patch('server.u2.connect')
    def test_watcher_remove_has_recording(self, mock_connect):
        """Test watcher_remove() records action."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test")
        server.watcher_remove("test_watcher", device_id="device1")

        assert len(server._recording_state["actions"]) == 1
        assert server._recording_state["actions"][0]["tool"] == "watcher_remove"

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    @patch('server.u2.connect')
    def test_multiple_actions_sequence(self, mock_connect):
        """Test recording multiple actions in sequence."""
        mock_device = MagicMock()
        mock_element = MagicMock()
        mock_element.wait.return_value = True
        mock_element.exists = True
        mock_element.info = {"bounds": {"left": 0, "top": 0, "right": 100, "bottom": 100}}
        mock_device.return_value = mock_element
        mock_device.app_wait.return_value = 123
        mock_connect.return_value = mock_device

        server.start_recording("test_sequence")

        # Perform multiple actions
        server.start_app("com.test.app", device_id="device1")
        server.click("Button", device_id="device1")
        server.send_text("test", device_id="device1")
        server.press_key("enter", device_id="device1")
        server.screenshot("/tmp/test.png", device_id="device1")

        # Verify all actions recorded
        assert len(server._recording_state["actions"]) == 5
        assert server._recording_state["actions"][0]["tool"] == "start_app"
        assert server._recording_state["actions"][1]["tool"] == "click"
        assert server._recording_state["actions"][2]["tool"] == "send_text"
        assert server._recording_state["actions"][3]["tool"] == "press_key"
        assert server._recording_state["actions"][4]["tool"] == "screenshot"

    def test_recording_inactive_no_capture(self):
        """Test that actions are not recorded when recording is inactive."""
        with patch('server.u2.connect'):
            # Don't start recording
            server.press_key("home")

            assert len(server._recording_state["actions"]) == 0

    @patch('server.u2.connect')
    def test_recording_captures_all_parameters(self, mock_connect):
        """Test that recording captures all function parameters."""
        mock_device = MagicMock()
        mock_connect.return_value = mock_device

        server.start_recording("test_params")
        server.swipe(100, 200, 300, 400, duration=0.5, device_id="device1")

        action = server._recording_state["actions"][0]
        assert action["params"]["start_x"] == 100
        assert action["params"]["start_y"] == 200
        assert action["params"]["end_x"] == 300
        assert action["params"]["end_y"] == 400
        assert action["params"]["duration"] == 0.5
        assert action["params"]["device_id"] == "device1"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
