"""SelectorMapper Agent - Maps UIAutomator selectors to Espresso ViewMatchers."""

from typing import Any, Dict

from ..base import SubAgent
from ..models import Language, MappedSelector, UIFramework
from ..registry import register_agent


class SelectorMapperAgent(SubAgent):
    """Map UIAutomator selectors to Espresso ViewMatchers."""

    # Mapping tables
    SELECTOR_MAPPINGS = {
        "text": {
            "espresso": 'withText("{value}")',
            "imports": ["androidx.test.espresso.matcher.ViewMatchers.withText"],
        },
        "resourceId": {
            "espresso": "withId(R.id.{id_part})",
            "imports": ["androidx.test.espresso.matcher.ViewMatchers.withId"],
        },
        "description": {
            "espresso": 'withContentDescription("{value}")',
            "imports": [
                "androidx.test.espresso.matcher.ViewMatchers.withContentDescription"
            ],
        },
    }

    COMPOSE_MAPPINGS = {
        "text": {
            "compose": 'onNodeWithText("{value}")',
            "imports": ["androidx.compose.ui.test.onNodeWithText"],
        },
        "description": {
            "compose": 'onNodeWithContentDescription("{value}")',
            "imports": ["androidx.compose.ui.test.onNodeWithContentDescription"],
        },
    }

    def __init__(self):
        super().__init__("SelectorMapper", parent_agent="EspressoCodeGenerator")

    def _process(self, inputs: Dict[str, Any]) -> MappedSelector:
        """Map a selector to Espresso/Compose syntax."""
        selector = inputs["selector"]
        selector_type = inputs.get("selector_type", "text")
        language = Language(inputs.get("target_language", "kotlin"))
        ui_framework = UIFramework(inputs.get("ui_framework", "xml"))

        if ui_framework == UIFramework.COMPOSE:
            return self._map_compose_selector(selector, selector_type, language)
        else:
            return self._map_espresso_selector(selector, selector_type, language)

    def _map_espresso_selector(
        self, selector: str, selector_type: str, language: Language
    ) -> MappedSelector:
        """Map to Espresso ViewMatcher."""
        mapping = self.SELECTOR_MAPPINGS.get(selector_type, {})

        if selector_type == "resourceId":
            # Extract ID part from full resource ID
            id_part = selector.split("/")[-1] if "/" in selector else selector
            code = mapping["espresso"].format(id_part=id_part)
        else:
            code = mapping["espresso"].format(value=selector)

        return MappedSelector(
            espresso_code=code,
            imports=mapping.get("imports", []),
            fallback_selectors=[],
            warnings=[],
            confidence=1.0,
        )

    def _map_compose_selector(
        self, selector: str, selector_type: str, language: Language
    ) -> MappedSelector:
        """Map to Compose test selector."""
        mapping = self.COMPOSE_MAPPINGS.get(selector_type, {})
        code = mapping.get("compose", "").format(value=selector)

        return MappedSelector(
            espresso_code=code,
            imports=mapping.get("imports", []),
            fallback_selectors=[],
            warnings=[],
            confidence=1.0,
        )


register_agent("selector-mapper", SelectorMapperAgent)
