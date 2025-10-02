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
        "click_xpath": {
            "espresso": "perform(click())",
            "compose": "performClick()",
            "imports": ["androidx.test.espresso.action.ViewActions.click"],
        },
        "click_at": {
            "espresso": "EspressoTestHelpers.clickAt({x}f, {y}f)",
            "compose": "performTouchInput {{ click(Offset({x}f, {y}f)) }}",
            "imports": ["com.android.test.espresso.utils.EspressoTestHelpers"],
            "custom_action": None,  # No custom action needed, using utils
        },
        "double_click": {
            "espresso": "perform(doubleClick())",
            "compose": "performClick(); performClick()",
            "imports": ["androidx.test.espresso.action.ViewActions.doubleClick"],
        },
        "double_click_at": {
            "espresso": "EspressoTestHelpers.doubleClickAt({x}f, {y}f)",
            "compose": "performTouchInput {{ click(Offset({x}f, {y}f)); click(Offset({x}f, {y}f)) }}",
            "imports": ["com.android.test.espresso.utils.EspressoTestHelpers"],
            "custom_action": None,  # No custom action needed, using utils
        },
        "long_click": {
            "espresso": "perform(longClick())",
            "compose": "performTouchInput {{ longClick() }}",
            "imports": ["androidx.test.espresso.action.ViewActions.longClick"],
        },
        "long_click_xpath": {
            "espresso": "perform(longClick())",
            "compose": "performTouchInput {{ longClick() }}",
            "imports": ["androidx.test.espresso.action.ViewActions.longClick"],
        },
        "send_text": {
            "espresso": 'perform(clearText(), typeText("{text}"))',
            "compose": 'performTextClearance(); performTextInput("{text}")',
            "imports": [
                "androidx.test.espresso.action.ViewActions.clearText",
                "androidx.test.espresso.action.ViewActions.typeText",
            ],
        },
        "send_text_xpath": {
            "espresso": 'perform(clearText(), typeText("{text}"))',
            "compose": 'performTextClearance(); performTextInput("{text}")',
            "imports": [
                "androidx.test.espresso.action.ViewActions.clearText",
                "androidx.test.espresso.action.ViewActions.typeText",
            ],
        },
        "swipe": {
            "espresso": "perform(swipe({start_x}, {start_y}, {end_x}, {end_y}))",  # Custom
            "compose": "performTouchInput {{ swipe(start = Offset({start_x}f, {start_y}f), end = Offset({end_x}f, {end_y}f)) }}",
            "imports": ["androidx.test.espresso.action.ViewActions.swipe"],
            "custom_action": "customSwipe",
        },
        "scroll_to": {
            "espresso": "perform(scrollTo())",
            "compose": "performScrollTo()",
            "imports": ["androidx.test.espresso.action.ViewActions.scrollTo"],
        },
        "scroll_forward": {
            "espresso": "perform(swipeUp())",
            "compose": "performScrollToIndex({steps})",
            "imports": ["androidx.test.espresso.action.ViewActions.swipeUp"],
        },
        "scroll_backward": {
            "espresso": "perform(swipeDown())",
            "compose": "performScrollToIndex(-{steps})",
            "imports": ["androidx.test.espresso.action.ViewActions.swipeDown"],
        },
        "scroll_to_beginning": {
            "espresso": "perform(swipeDown())",  # Repeated swipes
            "compose": "performScrollToIndex(0)",
            "imports": ["androidx.test.espresso.action.ViewActions.swipeDown"],
        },
        "scroll_to_end": {
            "espresso": "perform(swipeUp())",  # Repeated swipes
            "compose": "performScrollToNode(hasScrollAction())",
            "imports": ["androidx.test.espresso.action.ViewActions.swipeUp"],
        },
        "press_key": {
            "espresso": 'pressKey("{key}")',  # Espresso.pressKey
            "compose": 'performKeyPress(KeyEvent(Key.{key}))',
            "imports": ["androidx.test.espresso.Espresso.pressKey"],
        },
        "screenshot": {
            "espresso": "// Screenshot captured",
            "compose": "// Screenshot captured",
            "imports": [],
        },
        "wait_for_element": {
            "espresso": "check(matches(isDisplayed()))",
            "compose": "assertExists()",
            "imports": [
                "androidx.test.espresso.assertion.ViewAssertions.matches",
                "androidx.test.espresso.matcher.ViewMatchers.isDisplayed",
            ],
        },
        "wait_xpath": {
            "espresso": "check(matches(isDisplayed()))",
            "compose": "assertExists()",
            "imports": [
                "androidx.test.espresso.assertion.ViewAssertions.matches",
                "androidx.test.espresso.matcher.ViewMatchers.isDisplayed",
            ],
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

        if not mapping:
            # Unknown action - return comment
            return MappedAction(
                espresso_code=f"// TODO: Implement {tool} action manually",
                custom_actions=[],
                assertions=[],
                imports=[],
            )

        if ui_framework == UIFramework.COMPOSE:
            code = mapping.get("compose", "")
        else:
            code = mapping.get("espresso", "")

        # Substitute all parameters in the code
        try:
            code = code.format(**params)
        except KeyError as e:
            self.logger.warning(f"Missing parameter {e} for action {tool}")

        # Check if custom action is needed
        custom_actions = []
        if "custom_action" in mapping:
            custom_actions.append(mapping["custom_action"])

        # Generate assertions if this is a wait/check action
        assertions = []
        if tool.startswith("wait_"):
            assertions.append("Element should be visible and interactable")

        return MappedAction(
            espresso_code=code,
            custom_actions=custom_actions,
            assertions=assertions,
            imports=mapping.get("imports", []),
        )


register_agent("action-mapper", ActionMapperAgent)
