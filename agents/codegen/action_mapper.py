"""ActionMapper Agent - Maps UIAutomator actions to Espresso ViewActions."""

from typing import Any, Dict

from ..base import SubAgent
from ..models import Language, MappedAction, UIFramework
from ..registry import register_agent


class ActionMapperAgent(SubAgent):
    """Map UIAutomator actions to Espresso ViewActions."""

    ACTION_MAPPINGS = {
        "click": {
            "espresso": "perform(click())",
            "compose": "performClick()",
            "imports": ["androidx.test.espresso.action.ViewActions.click"],
        },
        "send_text": {
            "espresso": 'perform(clearText(), typeText("{text}"))',
            "compose": 'performTextInput("{text}")',
            "imports": [
                "androidx.test.espresso.action.ViewActions.clearText",
                "androidx.test.espresso.action.ViewActions.typeText",
            ],
        },
        "swipe": {
            "espresso": "perform(swipeLeft())",
            "compose": "performTouchInput { swipeLeft() }",
            "imports": ["androidx.test.espresso.action.ViewActions.swipeLeft"],
        },
    }

    def __init__(self):
        super().__init__("ActionMapper", parent_agent="EspressoCodeGenerator")

    def _process(self, inputs: Dict[str, Any]) -> MappedAction:
        """Map an action to Espresso/Compose syntax."""
        action = inputs["action"]
        Language(inputs.get("target_language", "kotlin"))
        ui_framework = UIFramework(inputs.get("ui_framework", "xml"))

        tool = action.get("tool", "")
        params = action.get("params", {})

        mapping = self.ACTION_MAPPINGS.get(tool, {})

        if ui_framework == UIFramework.COMPOSE:
            code = mapping.get("compose", "")
        else:
            code = mapping.get("espresso", "")

        # Substitute parameters
        if "{text}" in code and "text" in params:
            code = code.format(text=params["text"])

        return MappedAction(
            espresso_code=code,
            custom_actions=[],
            assertions=[],
            imports=mapping.get("imports", []),
        )


register_agent("action-mapper", ActionMapperAgent)
