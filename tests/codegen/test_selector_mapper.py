"""Unit tests for SelectorMapper agent."""

import pytest
from agents.codegen.selector_mapper import SelectorMapperAgent
from agents.models import Language, UIFramework


@pytest.fixture
def selector_mapper():
    """Create a SelectorMapper agent instance."""
    return SelectorMapperAgent()


class TestSelectorMapperBasicSelectors:
    """Test basic selector mapping (text, resourceId, description)."""

    def test_map_text_selector_xml(self, selector_mapper):
        """Test mapping text selector for XML views."""
        inputs = {
            "selector": "Login",
            "selector_type": "text",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert 'withText("Login")' in data.espresso_code
        assert "androidx.test.espresso.matcher.ViewMatchers.withText" in data.imports

    def test_map_resource_id_selector(self, selector_mapper):
        """Test mapping resourceId selector."""
        inputs = {
            "selector": "com.example.app:id/login_button",
            "selector_type": "resourceId",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Should extract just the ID part
        assert "withId(R.id.login_button)" in data.espresso_code
        assert "androidx.test.espresso.matcher.ViewMatchers.withId" in data.imports

    def test_map_description_selector(self, selector_mapper):
        """Test mapping content description selector."""
        inputs = {
            "selector": "Submit button",
            "selector_type": "description",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert 'withContentDescription("Submit button")' in data.espresso_code


class TestSelectorMapperXPath:
    """Test XPath selector parsing and mapping."""

    def test_xpath_text_exact_match(self, selector_mapper):
        """Test XPath with exact text match."""
        inputs = {
            "selector": "//*[@text='Login']",
            "selector_type": "xpath",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert 'withText("Login")' in data.espresso_code

    def test_xpath_resource_id(self, selector_mapper):
        """Test XPath with resource-id attribute."""
        inputs = {
            "selector": "//*[@resource-id='com.app:id/button']",
            "selector_type": "xpath",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert "withId(R.id.button)" in data.espresso_code

    def test_xpath_content_desc(self, selector_mapper):
        """Test XPath with content-desc attribute."""
        inputs = {
            "selector": "//*[@content-desc='Submit']",
            "selector_type": "xpath",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert 'withContentDescription("Submit")' in data.espresso_code

    def test_xpath_contains_text(self, selector_mapper):
        """Test XPath with contains() function."""
        inputs = {
            "selector": "//*[contains(@text, 'Log')]",
            "selector_type": "xpath",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Should extract the text value
        assert "Log" in data.espresso_code

    def test_xpath_complex_unparseable(self, selector_mapper):
        """Test complex XPath that can't be automatically converted."""
        inputs = {
            "selector": "//android.widget.Button[@clickable='true']/parent::node",
            "selector_type": "xpath",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Should generate TODO comment
        assert "TODO" in data.espresso_code
        assert len(data.warnings) > 0


class TestSelectorMapperCompose:
    """Test Compose selector mapping."""

    def test_compose_text_selector(self, selector_mapper):
        """Test text selector for Compose views."""
        inputs = {
            "selector": "Login",
            "selector_type": "text",
            "target_language": "kotlin",
            "ui_framework": "compose"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert 'onNodeWithText("Login")' in data.espresso_code
        assert "androidx.compose.ui.test.onNodeWithText" in data.imports

    def test_compose_description_selector(self, selector_mapper):
        """Test description selector for Compose views."""
        inputs = {
            "selector": "Submit button",
            "selector_type": "description",
            "target_language": "kotlin",
            "ui_framework": "compose"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert 'onNodeWithContentDescription("Submit button")' in data.espresso_code


class TestSelectorMapperEdgeCases:
    """Test edge cases and error handling."""

    def test_unknown_selector_type(self, selector_mapper):
        """Test handling of unknown selector type."""
        inputs = {
            "selector": "some_value",
            "selector_type": "unknown_type",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Should generate TODO comment
        assert "TODO" in data.espresso_code
        assert data.confidence == 0.0
        assert len(data.warnings) > 0

    def test_fallback_selectors_generated(self, selector_mapper):
        """Test that fallback selectors are generated."""
        inputs = {
            "selector": "Login",
            "selector_type": "text",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Should suggest content description as fallback
        assert len(data.fallback_selectors) > 0
        assert any("withContentDescription" in fb for fb in data.fallback_selectors)

    def test_resource_id_with_slash(self, selector_mapper):
        """Test resource ID with full package path and slash."""
        inputs = {
            "selector": "com.example.app/id/my_button",
            "selector_type": "resourceId",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Should extract just the ID part after the slash
        assert "withId(R.id.my_button)" in data.espresso_code


class TestSelectorMapperLanguages:
    """Test selector mapping for different target languages."""

    def test_kotlin_language(self, selector_mapper):
        """Test that Kotlin language is handled correctly."""
        inputs = {
            "selector": "Login",
            "selector_type": "text",
            "target_language": "kotlin",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        # Kotlin-specific assertions if any
        data = result["data"]
        assert 'withText("Login")' in data.espresso_code

    def test_java_language(self, selector_mapper):
        """Test that Java language is handled correctly."""
        inputs = {
            "selector": "Login",
            "selector_type": "text",
            "target_language": "java",
            "ui_framework": "xml"
        }
        result = selector_mapper.execute(inputs)

        assert result["status"] == "success"
        # Same code for both languages for selector mapping
        data = result["data"]
        assert 'withText("Login")' in data.espresso_code
