"""
Action Dispatcher Module

Maps recorded action tool names to executable functions using a registry pattern.
Supports all 48 action tools from Feature 1 with dynamic dispatch.
"""

from typing import Dict, Any, Callable, Optional, List
import inspect


class ActionDispatcher:
    """
    Maps recorded action tool names to executable functions.

    Uses a registry pattern to avoid massive if-elif chains.
    Supports all 48 action tools from Feature 1.

    The dispatcher imports tool functions directly from server.py,
    which means recording logic is included but will be no-op during replay
    (since _recording_state["active"] will be False).
    """

    def __init__(self):
        self._tool_registry: Dict[str, Callable] = {}
        self._initialize_registry()

    def _initialize_registry(self):
        """
        Build mapping of tool names to actual functions.

        Imports tool implementations from server.py and registers them.
        """
        # Import all tool functions from server
        # Note: These are decorated with @mcp.tool but are still callable Python functions
        try:
            import server

            # UI Interaction Tools (10 tools)
            self._tool_registry['click'] = server.click
            self._tool_registry['long_click'] = server.long_click
            self._tool_registry['double_click'] = server.double_click
            self._tool_registry['send_text'] = server.send_text
            self._tool_registry['swipe'] = server.swipe
            self._tool_registry['drag'] = server.drag
            self._tool_registry['click_at'] = server.click_at
            self._tool_registry['double_click_at'] = server.double_click_at
            self._tool_registry['screenshot'] = server.screenshot
            self._tool_registry['wait_for_element'] = server.wait_for_element

            # XPath Tools (4 tools)
            self._tool_registry['click_xpath'] = server.click_xpath
            self._tool_registry['long_click_xpath'] = server.long_click_xpath
            self._tool_registry['send_text_xpath'] = server.send_text_xpath
            self._tool_registry['wait_xpath'] = server.wait_xpath

            # Scrolling Tools (7 tools)
            self._tool_registry['scroll_to'] = server.scroll_to
            self._tool_registry['scroll_forward'] = server.scroll_forward
            self._tool_registry['scroll_backward'] = server.scroll_backward
            self._tool_registry['scroll_to_beginning'] = server.scroll_to_beginning
            self._tool_registry['scroll_to_end'] = server.scroll_to_end
            self._tool_registry['fling_forward'] = server.fling_forward
            self._tool_registry['fling_backward'] = server.fling_backward

            # App Control Tools (6 tools)
            self._tool_registry['start_app'] = server.start_app
            self._tool_registry['stop_app'] = server.stop_app
            self._tool_registry['stop_all_apps'] = server.stop_all_apps
            self._tool_registry['install_app'] = server.install_app
            self._tool_registry['uninstall_app'] = server.uninstall_app
            self._tool_registry['clear_app_data'] = server.clear_app_data

            # Screen Control Tools (6 tools)
            self._tool_registry['press_key'] = server.press_key
            self._tool_registry['screen_on'] = server.screen_on
            self._tool_registry['screen_off'] = server.screen_off
            self._tool_registry['unlock_screen'] = server.unlock_screen
            self._tool_registry['set_orientation'] = server.set_orientation
            self._tool_registry['freeze_rotation'] = server.freeze_rotation

            # Gesture Tools (2 tools)
            self._tool_registry['pinch_in'] = server.pinch_in
            self._tool_registry['pinch_out'] = server.pinch_out

            # System Tools (3 tools)
            self._tool_registry['set_clipboard'] = server.set_clipboard
            self._tool_registry['pull_file'] = server.pull_file
            self._tool_registry['push_file'] = server.push_file

            # Notification & Popup Tools (3 tools)
            self._tool_registry['open_notification'] = server.open_notification
            self._tool_registry['open_quick_settings'] = server.open_quick_settings
            self._tool_registry['disable_popups'] = server.disable_popups

            # Wait Tools (1 tool)
            self._tool_registry['wait_activity'] = server.wait_activity

            # Advanced Tools (3 tools)
            self._tool_registry['healthcheck'] = server.healthcheck
            self._tool_registry['reset_uiautomator'] = server.reset_uiautomator
            self._tool_registry['send_action'] = server.send_action

            # Watcher Tools (3 tools)
            self._tool_registry['watcher_start'] = server.watcher_start
            self._tool_registry['watcher_stop'] = server.watcher_stop
            self._tool_registry['watcher_remove'] = server.watcher_remove

        except ImportError as e:
            print(f"Warning: Failed to import server module: {e}")
            # Registry will be empty, dispatcher will raise KeyError on dispatch

    def dispatch(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """
        Execute tool with given parameters.

        Args:
            tool_name: Name of tool to execute (e.g., "click_xpath")
            parameters: Parameter dictionary from recorded action

        Returns:
            Tool execution result

        Raises:
            KeyError: If tool_name not in registry
            TypeError: If parameters don't match tool signature
        """
        if tool_name not in self._tool_registry:
            raise KeyError(
                f"Tool '{tool_name}' not found in registry. "
                f"Supported tools: {', '.join(sorted(self._tool_registry.keys()))}"
            )

        tool_func = self._tool_registry[tool_name]

        # Transform parameters if needed (handle naming differences between recording and function params)
        transformed = self._transform_parameters(tool_name, parameters)

        # Execute tool
        try:
            result = tool_func(**transformed)
            return result
        except TypeError as e:
            # Parameter mismatch - provide detailed error
            sig = inspect.signature(tool_func)
            raise TypeError(
                f"Parameter error for {tool_name}: {e}\n"
                f"Expected signature: {sig}\n"
                f"Provided parameters: {transformed}"
            )

    def _transform_parameters(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform recorded parameters to execution parameters.

        Handles any differences between how parameters were recorded
        and how they're expected by the tool function.

        Args:
            tool_name: Name of tool
            parameters: Raw recorded parameters

        Returns:
            Transformed parameters ready for execution
        """
        # Handle special cases where recorded param names differ from function param names
        # For Feature 1, params are recorded directly, so usually no transformation needed

        # Example transformations (add as needed):
        if tool_name == 'screenshot':
            # In recording, might be called 'filepath' but function expects 'filename'
            if 'filepath' in parameters and 'filename' not in parameters:
                parameters['filename'] = parameters.pop('filepath')

        # Return copy to avoid mutating original
        return parameters.copy()

    def get_supported_tools(self) -> List[str]:
        """Return list of all supported tool names"""
        return sorted(self._tool_registry.keys())

    def is_supported(self, tool_name: str) -> bool:
        """Check if tool is supported for replay"""
        return tool_name in self._tool_registry

    def get_tool_signature(self, tool_name: str) -> str:
        """
        Get function signature for a tool.

        Args:
            tool_name: Name of tool

        Returns:
            String representation of function signature

        Raises:
            KeyError: If tool not found
        """
        if tool_name not in self._tool_registry:
            raise KeyError(f"Tool '{tool_name}' not found")

        tool_func = self._tool_registry[tool_name]
        return str(inspect.signature(tool_func))
