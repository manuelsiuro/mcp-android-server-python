"""
Unit Tests for ActionDispatcher Module

Tests the action dispatcher's ability to map tool names to functions
and execute them with proper parameter handling.
"""

import pytest
from unittest.mock import patch, MagicMock

from replay.action_dispatcher import ActionDispatcher


class TestActionDispatcherInitialization:
    """Test ActionDispatcher initialization and registry setup."""

    def test_initialization_with_real_server(self):
        """Test that dispatcher initializes successfully with real server."""
        dispatcher = ActionDispatcher()

        # Registry should be populated with 48 tools
        assert len(dispatcher._tool_registry) == 48
        assert isinstance(dispatcher._tool_registry, dict)


class TestActionDispatcherToolRegistry:
    """Test tool registration and lookup."""

    def test_all_48_tools_registered(self):
        """Test that all 48 action tools are registered in dispatcher."""
        expected_tools = [
            # UI Interaction Tools (10)
            'click', 'long_click', 'double_click', 'send_text', 'swipe',
            'drag', 'click_at', 'double_click_at', 'screenshot', 'wait_for_element',
            # XPath Tools (4) - get_element_xpath is read-only, excluded
            'click_xpath', 'long_click_xpath', 'send_text_xpath', 'wait_xpath',
            # Scrolling Tools (7)
            'scroll_to', 'scroll_forward', 'scroll_backward',
            'scroll_to_beginning', 'scroll_to_end', 'fling_forward', 'fling_backward',
            # App Control Tools (6)
            'start_app', 'stop_app', 'stop_all_apps',
            'install_app', 'uninstall_app', 'clear_app_data',
            # Screen Control Tools (6)
            'press_key', 'screen_on', 'screen_off',
            'unlock_screen', 'set_orientation', 'freeze_rotation',
            # Gesture Tools (2)
            'pinch_in', 'pinch_out',
            # System Tools (3) - get_clipboard and shell are read-only, excluded
            'set_clipboard', 'pull_file', 'push_file',
            # Notification & Popup Tools (3)
            'open_notification', 'open_quick_settings', 'disable_popups',
            # Wait Tools (1)
            'wait_activity',
            # Advanced Tools (3)
            'healthcheck', 'reset_uiautomator', 'send_action',
            # Watcher Tools (3)
            'watcher_start', 'watcher_stop', 'watcher_remove'
            # Note: Inspection tools (get_element_info, dump_hierarchy) are read-only, excluded
        ]

        dispatcher = ActionDispatcher()

        # Verify all 48 tools are registered
        assert len(dispatcher._tool_registry) == 48, \
            f"Expected 48 tools, got {len(dispatcher._tool_registry)}"

        # Verify each expected tool is present
        registered_tools = dispatcher.get_supported_tools()
        for tool_name in expected_tools:
            assert tool_name in registered_tools, \
                f"Tool '{tool_name}' not registered"

    def test_get_supported_tools_returns_sorted_list(self):
        """Test get_supported_tools returns alphabetically sorted list."""
        dispatcher = ActionDispatcher()
        tools = dispatcher.get_supported_tools()

        # Verify sorted
        assert tools == sorted(tools)
        assert len(tools) == 48

    def test_is_supported_returns_true_for_registered_tool(self):
        """Test is_supported returns True for registered tools."""
        dispatcher = ActionDispatcher()

        assert dispatcher.is_supported('click') is True
        assert dispatcher.is_supported('send_text') is True
        assert dispatcher.is_supported('click_xpath') is True

    def test_is_supported_returns_false_for_unknown_tool(self):
        """Test is_supported returns False for unknown tools."""
        dispatcher = ActionDispatcher()

        assert dispatcher.is_supported('unknown_tool') is False
        assert dispatcher.is_supported('fake_action') is False


class TestActionDispatcherToolSignature:
    """Test tool signature retrieval."""

    def test_get_tool_signature_returns_signature_string(self):
        """Test get_tool_signature returns function signature."""
        dispatcher = ActionDispatcher()
        signature = dispatcher.get_tool_signature('click')

        # Verify signature is returned as string
        assert isinstance(signature, str)
        assert 'selector' in signature

    def test_get_tool_signature_raises_keyerror_for_unknown_tool(self):
        """Test get_tool_signature raises KeyError for unknown tool."""
        dispatcher = ActionDispatcher()

        with pytest.raises(KeyError, match="Tool 'unknown_tool' not found"):
            dispatcher.get_tool_signature('unknown_tool')


class TestActionDispatcherDispatch:
    """Test action dispatching and execution."""

    @patch('server.u2.connect')
    def test_dispatch_success_returns_tool_result(self, mock_connect):
        """Test successful dispatch returns tool execution result."""
        # Mock device
        mock_device = MagicMock()
        mock_element = MagicMock()
        mock_element.wait.return_value = True
        mock_element.exists = True
        mock_element.info = {"bounds": {"left": 0, "top": 0, "right": 100, "bottom": 100}}
        mock_device.return_value = mock_element
        mock_connect.return_value = mock_device

        dispatcher = ActionDispatcher()

        result = dispatcher.dispatch('click', {
            'selector': 'Login',
            'selector_type': 'text',
            'device_id': 'device123'
        })

        # Result might be True or False depending on mock
        assert isinstance(result, bool)

    def test_dispatch_unknown_tool_raises_keyerror(self):
        """Test dispatch raises KeyError for unknown tool."""
        dispatcher = ActionDispatcher()

        with pytest.raises(KeyError, match="Tool 'unknown_tool' not found"):
            dispatcher.dispatch('unknown_tool', {})

    def test_dispatch_keyerror_includes_supported_tools_list(self):
        """Test KeyError message includes list of supported tools."""
        dispatcher = ActionDispatcher()

        with pytest.raises(KeyError) as exc_info:
            dispatcher.dispatch('unknown_tool', {})

        error_message = str(exc_info.value)
        assert 'Supported tools:' in error_message
        assert 'click' in error_message


class TestActionDispatcherParameterTransformation:
    """Test parameter transformation logic."""

    @patch('server.u2.connect')
    def test_transform_parameters_screenshot_filepath_to_filename(self, mock_connect):
        """Test parameter transformation for screenshot tool."""
        mock_device = MagicMock()
        mock_device.screenshot.return_value = b'fake_image_data'
        mock_connect.return_value = mock_device

        dispatcher = ActionDispatcher()

        # Dispatch with 'filepath' instead of 'filename'
        result = dispatcher.dispatch('screenshot', {
            'filepath': '/tmp/test.png',
            'device_id': 'device123'
        })

        # Should not raise error
        assert isinstance(result, bool)

    @patch('server.u2.connect')
    def test_transform_parameters_does_not_mutate_original(self, mock_connect):
        """Test parameter transformation creates copy."""
        mock_device = MagicMock()
        mock_element = MagicMock()
        mock_element.wait.return_value = True
        mock_element.exists = True
        mock_element.info = {"bounds": {"left": 0, "top": 0, "right": 100, "bottom": 100}}
        mock_device.return_value = mock_element
        mock_connect.return_value = mock_device

        dispatcher = ActionDispatcher()

        original_params = {
            'selector': 'Test',
            'selector_type': 'text'
        }
        original_params_copy = original_params.copy()

        dispatcher.dispatch('click', original_params)

        # Verify original params were not mutated
        assert original_params == original_params_copy


class TestActionDispatcherEdgeCases:
    """Test edge cases and error handling."""

    def test_dispatch_with_none_parameters(self):
        """Test dispatch with None as parameters."""
        dispatcher = ActionDispatcher()

        # Should handle None gracefully or raise appropriate error
        with pytest.raises((TypeError, AttributeError)):
            dispatcher.dispatch('screen_on', None)

    def test_registry_contains_callable_objects(self):
        """Test that registry contains callable functions."""
        dispatcher = ActionDispatcher()

        # Verify all registry entries are callable
        for tool_name, tool_func in dispatcher._tool_registry.items():
            assert callable(tool_func), f"Tool '{tool_name}' is not callable"
