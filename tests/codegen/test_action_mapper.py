"""Unit tests for ActionMapper agent."""

import pytest
from agents.codegen.action_mapper import ActionMapperAgent
from agents.models import UIFramework


@pytest.fixture
def action_mapper():
    """Create an ActionMapper agent instance."""
    return ActionMapperAgent()


class TestActionMapperBasicActions:
    """Test basic action mapping (click, text, swipe)."""

    def test_map_click_action_xml(self, action_mapper):
        """Test mapping click action for XML views."""
        action = {
            "tool": "click",
            "params": {
                "selector": "Login",
                "selector_type": "text"
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "perform(click())" in data.espresso_code
        assert "androidx.test.espresso.action.ViewActions.click" in data.imports

    def test_map_send_text_action(self, action_mapper):
        """Test mapping send_text action."""
        action = {
            "tool": "send_text",
            "params": {
                "text": "testuser@example.com",
                "clear": True
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "clearText()" in data.espresso_code
        assert "typeText" in data.espresso_code
        assert "testuser@example.com" in data.espresso_code

    def test_map_long_click_action(self, action_mapper):
        """Test mapping long_click action."""
        action = {
            "tool": "long_click",
            "params": {
                "selector": "Item",
                "duration": 2
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "longClick()" in data.espresso_code

    def test_map_double_click_action(self, action_mapper):
        """Test mapping double_click action."""
        action = {
            "tool": "double_click",
            "params": {
                "selector": "Button"
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "doubleClick()" in data.espresso_code


class TestActionMapperXPathActions:
    """Test XPath-based action mapping."""

    def test_map_click_xpath_action(self, action_mapper):
        """Test mapping click_xpath action."""
        action = {
            "tool": "click_xpath",
            "params": {
                "xpath": "//*[@text='Submit']"
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "click()" in data.espresso_code

    def test_map_send_text_xpath_action(self, action_mapper):
        """Test mapping send_text_xpath action."""
        action = {
            "tool": "send_text_xpath",
            "params": {
                "xpath": "//*[@resource-id='username']",
                "text": "myusername"
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "myusername" in data.espresso_code


class TestActionMapperCoordinateActions:
    """Test coordinate-based action mapping."""

    def test_map_click_at_action(self, action_mapper):
        """Test mapping click_at action with coordinates."""
        action = {
            "tool": "click_at",
            "params": {
                "x": 540,
                "y": 1200
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "540" in data.espresso_code
        assert "1200" in data.espresso_code
        # Should use EspressoTestHelpers (no custom action needed)
        assert "EspressoTestHelpers.clickAt" in data.espresso_code
        assert "com.android.test.espresso.utils.EspressoTestHelpers" in data.imports

    def test_map_double_click_at_action(self, action_mapper):
        """Test mapping double_click_at action."""
        action = {
            "tool": "double_click_at",
            "params": {
                "x": 100,
                "y": 200
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "100" in data.espresso_code
        assert "200" in data.espresso_code
        # Should use EspressoTestHelpers (no custom action needed)
        assert "EspressoTestHelpers.doubleClickAt" in data.espresso_code
        assert "com.android.test.espresso.utils.EspressoTestHelpers" in data.imports

    def test_map_swipe_action(self, action_mapper):
        """Test mapping swipe action with coordinates."""
        action = {
            "tool": "swipe",
            "params": {
                "start_x": 500,
                "start_y": 1500,
                "end_x": 500,
                "end_y": 500,
                "duration": 0.3
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Should include coordinates
        assert "500" in data.espresso_code
        assert "1500" in data.espresso_code


class TestActionMapperScrollActions:
    """Test scroll action mapping."""

    def test_map_scroll_to_action(self, action_mapper):
        """Test mapping scroll_to action."""
        action = {
            "tool": "scroll_to",
            "params": {
                "selector": "Item 50"
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "scrollTo()" in data.espresso_code

    def test_map_scroll_forward_action(self, action_mapper):
        """Test mapping scroll_forward action."""
        action = {
            "tool": "scroll_forward",
            "params": {
                "steps": 1
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "swipeUp()" in data.espresso_code

    def test_map_scroll_backward_action(self, action_mapper):
        """Test mapping scroll_backward action."""
        action = {
            "tool": "scroll_backward",
            "params": {
                "steps": 1
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "swipeDown()" in data.espresso_code


class TestActionMapperSystemActions:
    """Test system action mapping (press_key, screenshot, wait)."""

    def test_map_press_key_action(self, action_mapper):
        """Test mapping press_key action."""
        action = {
            "tool": "press_key",
            "params": {
                "key": "back"
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "back" in data.espresso_code

    def test_map_screenshot_action(self, action_mapper):
        """Test mapping screenshot action."""
        action = {
            "tool": "screenshot",
            "params": {
                "filename": "/tmp/screen.png"
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Screenshot should result in a comment
        assert "Screenshot" in data.espresso_code

    def test_map_wait_for_element_action(self, action_mapper):
        """Test mapping wait_for_element action."""
        action = {
            "tool": "wait_for_element",
            "params": {
                "selector": "Welcome",
                "timeout": 10
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Wait should generate assertion
        assert "isDisplayed()" in data.espresso_code
        assert len(data.assertions) > 0


class TestActionMapperComposeActions:
    """Test Compose action mapping."""

    def test_map_click_compose(self, action_mapper):
        """Test mapping click action for Compose."""
        action = {
            "tool": "click",
            "params": {}
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "compose"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "performClick()" in data.espresso_code

    def test_map_send_text_compose(self, action_mapper):
        """Test mapping send_text for Compose."""
        action = {
            "tool": "send_text",
            "params": {
                "text": "test input"
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "compose"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "performTextInput" in data.espresso_code
        assert "test input" in data.espresso_code


class TestActionMapperEdgeCases:
    """Test edge cases and error handling."""

    def test_unknown_action_tool(self, action_mapper):
        """Test handling of unknown action tool."""
        action = {
            "tool": "unknown_action",
            "params": {}
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Should generate TODO comment
        assert "TODO" in data.espresso_code
        assert "unknown_action" in data.espresso_code

    def test_missing_required_parameters(self, action_mapper):
        """Test action with missing required parameters."""
        action = {
            "tool": "send_text",
            "params": {
                # Missing 'text' parameter
                "clear": True
            }
        }
        inputs = {
            "action": action,
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = action_mapper.execute(inputs)

        # Should still return success but with incomplete code
        assert result["status"] == "success"
        # Code might have placeholder or missing value
