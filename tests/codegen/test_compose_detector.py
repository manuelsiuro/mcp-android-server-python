"""Unit tests for ComposeDetector agent."""

import pytest
from agents.codegen.compose_detector import ComposeDetectorAgent
from agents.models import UIFramework


@pytest.fixture
def compose_detector():
    """Create a ComposeDetector agent instance."""
    return ComposeDetectorAgent()


class TestComposeDetection:
    """Test Compose UI framework detection."""

    def test_detect_compose_app(self, compose_detector):
        """Test detection of Compose app."""
        scenario = {
            "actions": [
                {
                    "id": 1,
                    "ui_hierarchy": "<node class='androidx.compose.ui.platform.ComposeView'>...</node>"
                },
                {
                    "id": 2,
                    "ui_hierarchy": "<node class='androidx.compose.ui.platform.AndroidComposeView'>...</node>"
                }
            ]
        }
        inputs = {
            "scenario": scenario,
            "ui_hierarchies": []
        }
        result = compose_detector.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert data.ui_framework == UIFramework.COMPOSE
        assert len(data.compose_screens) == 2
        assert len(data.xml_screens) == 0

    def test_detect_xml_app(self, compose_detector):
        """Test detection of traditional XML app."""
        scenario = {
            "actions": [
                {
                    "id": 1,
                    "ui_hierarchy": "<node class='android.widget.LinearLayout'><node class='android.widget.Button' text='Login'/></node>"
                },
                {
                    "id": 2,
                    "ui_hierarchy": "<node class='android.widget.FrameLayout'>...</node>"
                }
            ]
        }
        inputs = {
            "scenario": scenario,
            "ui_hierarchies": []
        }
        result = compose_detector.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert data.ui_framework == UIFramework.XML
        assert len(data.compose_screens) == 0
        assert len(data.xml_screens) == 2

    def test_detect_hybrid_app(self, compose_detector):
        """Test detection of hybrid app (Compose + XML)."""
        scenario = {
            "actions": [
                {
                    "id": 1,
                    "ui_hierarchy": "<node class='androidx.compose.ui.platform.ComposeView'>...</node>"
                },
                {
                    "id": 2,
                    "ui_hierarchy": "<node class='android.widget.LinearLayout'>...</node>"
                }
            ]
        }
        inputs = {
            "scenario": scenario,
            "ui_hierarchies": []
        }
        result = compose_detector.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert data.ui_framework == UIFramework.HYBRID
        assert len(data.compose_screens) == 1
        assert len(data.xml_screens) == 1

    def test_detect_deep_nesting_compose(self, compose_detector):
        """Test detection based on deep nesting (characteristic of Compose)."""
        # Create hierarchy with many generic android.view.View nodes
        deep_hierarchy = "<node class='android.view.View'>" * 25 + "</node>" * 25
        scenario = {
            "actions": [
                {
                    "id": 1,
                    "ui_hierarchy": deep_hierarchy
                }
            ]
        }
        inputs = {
            "scenario": scenario,
            "ui_hierarchies": []
        }
        result = compose_detector.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Deep nesting with generic views suggests Compose
        assert data.ui_framework == UIFramework.COMPOSE
        assert 1 in data.compose_screens

    def test_empty_scenario(self, compose_detector):
        """Test detection with empty scenario."""
        scenario = {
            "actions": []
        }
        inputs = {
            "scenario": scenario,
            "ui_hierarchies": []
        }
        result = compose_detector.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Should default to XML when no screens
        assert data.ui_framework == UIFramework.XML


class TestComposeDetectorEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_ui_hierarchy(self, compose_detector):
        """Test action without ui_hierarchy field."""
        scenario = {
            "actions": [
                {
                    "id": 1
                    # No ui_hierarchy field
                }
            ]
        }
        inputs = {
            "scenario": scenario,
            "ui_hierarchies": []
        }
        result = compose_detector.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        # Should handle gracefully and default to XML
        assert data.ui_framework == UIFramework.XML

    def test_empty_ui_hierarchy(self, compose_detector):
        """Test action with empty ui_hierarchy."""
        scenario = {
            "actions": [
                {
                    "id": 1,
                    "ui_hierarchy": ""
                }
            ]
        }
        inputs = {
            "scenario": scenario,
            "ui_hierarchies": []
        }
        result = compose_detector.execute(inputs)

        assert result["status"] == "success"
        data = result["data"]
        assert data.ui_framework == UIFramework.XML
