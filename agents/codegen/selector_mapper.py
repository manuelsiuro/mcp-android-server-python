"""SelectorMapper Agent - Maps UIAutomator selectors to Espresso ViewMatchers."""

import re
from typing import Any, Dict, List, Tuple

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

        # Handle XPath specially
        if selector_type == "xpath":
            return self._map_xpath_selector(selector, language, ui_framework)

        if ui_framework == UIFramework.COMPOSE:
            return self._map_compose_selector(selector, selector_type, language)
        else:
            return self._map_espresso_selector(selector, selector_type, language)

    def _map_espresso_selector(
        self, selector: str, selector_type: str, language: Language
    ) -> MappedSelector:
        """Map to Espresso ViewMatcher."""
        mapping = self.SELECTOR_MAPPINGS.get(selector_type, {})

        if not mapping:
            return MappedSelector(
                espresso_code=f'// TODO: Implement selector type "{selector_type}"',
                imports=[],
                fallback_selectors=[],
                warnings=[f"Unknown selector type: {selector_type}"],
                confidence=0.0,
            )

        if selector_type == "resourceId":
            # Extract ID part from full resource ID
            id_part = selector.split("/")[-1] if "/" in selector else selector
            # Remove package prefix from resource ID
            id_part = id_part.split(":")[-1] if ":" in id_part else id_part
            code = mapping["espresso"].format(id_part=id_part)
        else:
            code = mapping["espresso"].format(value=selector)

        # Generate fallback selectors
        fallback_selectors = self._generate_fallback_selectors(
            selector, selector_type
        )

        return MappedSelector(
            espresso_code=code,
            imports=mapping.get("imports", []),
            fallback_selectors=fallback_selectors,
            warnings=[],
            confidence=1.0,
        )

    def _map_compose_selector(
        self, selector: str, selector_type: str, language: Language
    ) -> MappedSelector:
        """Map to Compose test selector."""
        mapping = self.COMPOSE_MAPPINGS.get(selector_type, {})

        if not mapping:
            return MappedSelector(
                espresso_code=f'// TODO: Implement Compose selector "{selector_type}"',
                imports=[],
                fallback_selectors=[],
                warnings=[f"Unknown Compose selector type: {selector_type}"],
                confidence=0.0,
            )

        code = mapping.get("compose", "").format(value=selector)

        return MappedSelector(
            espresso_code=code,
            imports=mapping.get("imports", []),
            fallback_selectors=[],
            warnings=[],
            confidence=1.0,
        )

    def _map_xpath_selector(
        self, xpath: str, language: Language, ui_framework: UIFramework
    ) -> MappedSelector:
        """Map XPath selector to Espresso/Compose syntax."""
        # Parse XPath to extract selector information
        parsed = self._parse_xpath(xpath)

        if not parsed:
            return MappedSelector(
                espresso_code=f'// TODO: Complex XPath needs manual implementation: {xpath}',
                imports=[],
                fallback_selectors=[],
                warnings=["XPath is too complex for automatic conversion"],
                confidence=0.0,
            )

        selector_type, value = parsed

        # Map based on parsed type
        if ui_framework == UIFramework.COMPOSE:
            return self._map_compose_selector(value, selector_type, language)
        else:
            return self._map_espresso_selector(value, selector_type, language)

    def _parse_xpath(self, xpath: str) -> Tuple[str, str] | None:
        """
        Parse XPath expression to extract selector type and value.

        Supports common patterns:
        - //*[@text='value'] -> ('text', 'value')
        - //*[@resource-id='id'] -> ('resourceId', 'id')
        - //*[@content-desc='desc'] -> ('description', 'desc')
        - //*[contains(@text, 'value')] -> ('text', 'value')
        """
        # Pattern for exact match: //*[@attribute='value']
        exact_pattern = r"/\/\*\[@([\w-]+)=['\"]([^'\"]+)['\"]\]"
        match = re.search(exact_pattern, xpath)
        if match:
            attribute = match.group(1)
            value = match.group(2)
            return self._xpath_attribute_to_type(attribute), value

        # Pattern for contains: //*[contains(@attribute, 'value')]
        contains_pattern = r"/\/\*\[contains\(@([\w-]+),\s*['\"]([^'\"]+)['\"]\)\]"
        match = re.search(contains_pattern, xpath)
        if match:
            attribute = match.group(1)
            value = match.group(2)
            # For contains, we might need to use containsString matcher
            return self._xpath_attribute_to_type(attribute), value

        return None

    def _xpath_attribute_to_type(self, attribute: str) -> str:
        """Convert XPath attribute name to selector type."""
        mapping = {
            "text": "text",
            "resource-id": "resourceId",
            "content-desc": "description",
        }
        return mapping.get(attribute, "text")

    def _generate_fallback_selectors(
        self, selector: str, selector_type: str
    ) -> List[str]:
        """Generate alternative selectors for fallback."""
        fallbacks = []

        # If text selector, suggest content description fallback
        if selector_type == "text":
            fallbacks.append(f'withContentDescription("{selector}")')

        # If resourceId, suggest text fallback
        if selector_type == "resourceId":
            fallbacks.append(f'withText("{selector.split("/")[-1]}")')

        return fallbacks


register_agent("selector-mapper", SelectorMapperAgent)
