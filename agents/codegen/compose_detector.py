"""ComposeDetector Agent - Detects Jetpack Compose vs XML views."""

from typing import Any, Dict

from ..base import SubAgent
from ..models import FrameworkDetection, UIFramework
from ..registry import register_agent


class ComposeDetectorAgent(SubAgent):
    """Detect whether app uses Jetpack Compose or XML views."""

    COMPOSE_INDICATORS = [
        "androidx.compose.ui.platform.ComposeView",
        "androidx.compose.ui.platform.AndroidComposeView",
    ]

    def __init__(self):
        super().__init__("ComposeDetector", parent_agent="EspressoCodeGenerator")

    def _process(self, inputs: Dict[str, Any]) -> FrameworkDetection:
        """Detect UI framework from scenario."""
        scenario = inputs["scenario"]
        inputs.get("ui_hierarchies", [])

        # Analyze each action's UI hierarchy
        compose_screens = []
        xml_screens = []

        for action in scenario.get("actions", []):
            action_id = action.get("id")
            hierarchy = action.get("ui_hierarchy", "")

            if self._is_compose_screen(hierarchy):
                compose_screens.append(action_id)
            else:
                xml_screens.append(action_id)

        # Determine overall framework
        if compose_screens and not xml_screens:
            framework = UIFramework.COMPOSE
        elif xml_screens and not compose_screens:
            framework = UIFramework.XML
        elif compose_screens and xml_screens:
            framework = UIFramework.HYBRID
        else:
            framework = UIFramework.XML  # Default

        return FrameworkDetection(
            ui_framework=framework,
            compose_screens=compose_screens,
            xml_screens=xml_screens,
            confidence=1.0,
        )

    def _is_compose_screen(self, hierarchy_xml: str) -> bool:
        """Check if UI hierarchy indicates Compose."""
        if not hierarchy_xml:
            return False

        # Check for Compose indicators
        for indicator in self.COMPOSE_INDICATORS:
            if indicator in hierarchy_xml:
                return True

        # Check for deep nesting with generic views (Compose characteristic)
        if hierarchy_xml.count("android.view.View") > 20:
            return True

        return False


register_agent("compose-detector", ComposeDetectorAgent)
