"""EspressoCodeGenerator Agent - Primary Agent for Code Generation."""

import json
from pathlib import Path
from typing import Any, Dict, List

from ..base import PrimaryAgent
from ..models import CodeGenerationOptions, GeneratedCode, Language, UIFramework
from ..registry import register_agent


class EspressoCodeGeneratorAgent(PrimaryAgent):
    """Generate complete Espresso test code from scenarios."""

    def __init__(self):
        super().__init__("EspressoCodeGenerator")

    def _process(self, inputs: Dict[str, Any]) -> GeneratedCode:
        """Generate Espresso test code from a scenario."""
        scenario_file = inputs["scenario_file"]
        language = Language(inputs.get("language", "kotlin"))
        package_name = inputs.get("package_name", "com.example.app")
        class_name = inputs.get("class_name")
        options = self._parse_options(inputs.get("options", {}))

        # Load scenario
        with open(scenario_file, "r") as f:
            scenario = json.load(f)

        # Detect UI framework
        ui_framework = self._detect_framework(scenario)

        # Generate class name if not provided
        if not class_name:
            class_name = self._generate_class_name(scenario)

        # Generate test code
        code = self._generate_test_class(
            scenario, language, package_name, class_name, ui_framework, options
        )

        # Format code
        formatted_code = self._format_code(code, language)

        # Determine output file path
        file_path = self._get_output_path(class_name, language)

        # Extract imports
        imports = self._extract_imports(formatted_code, ui_framework, language)

        # Save code
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(formatted_code)

        self.logger.info(f"Generated {language.value} test code: {file_path}")

        return GeneratedCode(
            code=formatted_code,
            file_path=file_path,
            imports=imports,
            custom_actions=[],
            warnings=[],
            ui_framework=ui_framework,
        )

    def _parse_options(self, options_dict: Dict[str, Any]) -> CodeGenerationOptions:
        """Parse code generation options."""
        return CodeGenerationOptions(
            include_comments=options_dict.get("include_comments", True),
            use_idling_resources=options_dict.get("use_idling_resources", False),
            generate_custom_actions=options_dict.get("generate_custom_actions", True),
        )

    def _detect_framework(self, scenario: Dict[str, Any]) -> UIFramework:
        """Detect UI framework used in the scenario."""
        # In real implementation, would use ComposeDetector subagent
        # For now, simple heuristic
        return UIFramework.XML

    def _generate_class_name(self, scenario: Dict[str, Any]) -> str:
        """Generate test class name from scenario."""
        name = scenario.get("metadata", {}).get("name", "Scenario")
        # Convert to PascalCase and add Test suffix
        class_name = "".join(word.capitalize() for word in name.split("_"))
        return f"{class_name}Test"

    def _generate_test_class(
        self,
        scenario: Dict[str, Any],
        language: Language,
        package_name: str,
        class_name: str,
        ui_framework: UIFramework,
        options: CodeGenerationOptions,
    ) -> str:
        """Generate the test class code."""
        if language == Language.KOTLIN:
            return self._generate_kotlin_test(
                scenario, package_name, class_name, ui_framework, options
            )
        else:
            return self._generate_java_test(
                scenario, package_name, class_name, ui_framework, options
            )

    def _generate_kotlin_test(
        self,
        scenario: Dict[str, Any],
        package_name: str,
        class_name: str,
        ui_framework: UIFramework,
        options: CodeGenerationOptions,
    ) -> str:
        """Generate Kotlin test code."""
        from .selector_mapper import SelectorMapperAgent
        from .action_mapper import ActionMapperAgent

        actions = scenario.get("actions", [])
        metadata = scenario.get("metadata", {})

        # Initialize subagents
        selector_mapper = SelectorMapperAgent()
        action_mapper = ActionMapperAgent()

        # Build test method body with comprehensive action mapping
        test_body_lines = []
        all_imports = set()

        if options.include_comments:
            test_body_lines.append(
                f"        // Generated from scenario: {metadata.get('name', 'Unknown')}"
            )
            test_body_lines.append(
                f"        // Created: {metadata.get('created_at', 'Unknown')}"
            )
            test_body_lines.append("        ")

        for i, action in enumerate(actions, 1):
            tool = action.get("tool", "")
            params = action.get("params", {})

            if options.include_comments:
                test_body_lines.append(f"        // Action {i}: {tool}")

            # Add delay if specified
            delay_before = action.get("delay_before_ms", 0)
            if delay_before > 0:
                test_body_lines.append(
                    f"        Thread.sleep({delay_before}L)"
                )

            # Map action using ActionMapper subagent
            try:
                mapped_action = action_mapper.execute({
                    "action": action,
                    "target_language": "kotlin",
                    "ui_framework": ui_framework.value
                })

                if mapped_action["status"] == "success":
                    action_data = mapped_action["data"]

                    # Map selector if needed
                    if tool in ["click", "click_xpath", "send_text", "long_click", "double_click"]:
                        selector = params.get("selector", params.get("xpath", ""))
                        selector_type = params.get("selector_type", "xpath" if "xpath" in tool else "text")

                        mapped_selector = selector_mapper.execute({
                            "selector": selector,
                            "selector_type": selector_type,
                            "target_language": "kotlin",
                            "ui_framework": ui_framework.value
                        })

                        if mapped_selector["status"] == "success":
                            selector_code = mapped_selector["data"].espresso_code
                            action_code = action_data.espresso_code

                            # Combine selector and action
                            test_body_lines.append(
                                f"        onView({selector_code}).{action_code}"
                            )

                            # Collect imports
                            all_imports.update(mapped_selector["data"].imports)
                            all_imports.update(action_data.imports)
                    else:
                        # Action without selector (e.g., press_key, scroll)
                        test_body_lines.append(f"        {action_data.espresso_code}")
                        all_imports.update(action_data.imports)

            except Exception as e:
                self.logger.warning(f"Failed to map action {tool}: {e}")
                test_body_lines.append(
                    f"        // TODO: Manual implementation needed for {tool}"
                )

            # Add delay after if specified
            delay_after = action.get("delay_after_ms", 0)
            if delay_after > 0:
                test_body_lines.append(
                    f"        Thread.sleep({delay_after}L)"
                )

            test_body_lines.append("")  # Blank line between actions

        test_body = "\n".join(test_body_lines)

        # Generate imports
        import_lines = self._generate_kotlin_imports(ui_framework, all_imports)

        code = f"""package {package_name}

{import_lines}

/**
 * Generated Espresso test from recorded scenario
 * Scenario: {metadata.get('name', 'Unknown')}
 * Generated on: {metadata.get('created_at', 'Unknown')}
 *
 * Original scenario file: {scenario.get('_source_file', 'Unknown')}
 */
@RunWith(AndroidJUnit4::class)
class {class_name} {{

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testScenario() {{
{test_body}
    }}
}}
"""
        return code

    def _generate_kotlin_imports(self, ui_framework: UIFramework, custom_imports: set) -> str:
        """Generate Kotlin imports section."""
        standard_imports = [
            "import androidx.test.ext.junit.rules.ActivityScenarioRule",
            "import androidx.test.ext.junit.runners.AndroidJUnit4",
            "import org.junit.Rule",
            "import org.junit.Test",
            "import org.junit.runner.RunWith",
        ]

        if ui_framework == UIFramework.XML:
            standard_imports.extend([
                "import androidx.test.espresso.Espresso.onView",
                "import androidx.test.espresso.action.ViewActions.*",
                "import androidx.test.espresso.assertion.ViewAssertions.*",
                "import androidx.test.espresso.matcher.ViewMatchers.*",
            ])
        elif ui_framework == UIFramework.COMPOSE:
            standard_imports.extend([
                "import androidx.compose.ui.test.junit4.createAndroidComposeRule",
                "import androidx.compose.ui.test.onNodeWithText",
                "import androidx.compose.ui.test.performClick",
                "import androidx.compose.ui.test.performTextInput",
            ])

        # Add custom imports
        all_imports = sorted(set(standard_imports) | custom_imports)
        return "\n".join(all_imports)

    def _generate_java_test(
        self,
        scenario: Dict[str, Any],
        package_name: str,
        class_name: str,
        ui_framework: UIFramework,
        options: CodeGenerationOptions,
    ) -> str:
        """Generate Java test code."""
        from .selector_mapper import SelectorMapperAgent
        from .action_mapper import ActionMapperAgent

        actions = scenario.get("actions", [])
        metadata = scenario.get("metadata", {})

        # Initialize subagents
        selector_mapper = SelectorMapperAgent()
        action_mapper = ActionMapperAgent()

        # Build test method body
        test_body_lines = []
        all_imports = set()

        if options.include_comments:
            test_body_lines.append(
                f"        // Generated from scenario: {metadata.get('name', 'Unknown')}"
            )
            test_body_lines.append(
                f"        // Created: {metadata.get('created_at', 'Unknown')}"
            )
            test_body_lines.append("        ")

        for i, action in enumerate(actions, 1):
            tool = action.get("tool", "")
            params = action.get("params", {})

            if options.include_comments:
                test_body_lines.append(f"        // Action {i}: {tool}")

            # Add delay if specified
            delay_before = action.get("delay_before_ms", 0)
            if delay_before > 0:
                test_body_lines.append(
                    f"        Thread.sleep({delay_before}L);"
                )

            # Map action using ActionMapper subagent
            try:
                mapped_action = action_mapper.execute({
                    "action": action,
                    "target_language": "java",
                    "ui_framework": ui_framework.value
                })

                if mapped_action["status"] == "success":
                    action_data = mapped_action["data"]

                    # Map selector if needed
                    if tool in ["click", "click_xpath", "send_text", "long_click", "double_click"]:
                        selector = params.get("selector", params.get("xpath", ""))
                        selector_type = params.get("selector_type", "xpath" if "xpath" in tool else "text")

                        mapped_selector = selector_mapper.execute({
                            "selector": selector,
                            "selector_type": selector_type,
                            "target_language": "java",
                            "ui_framework": ui_framework.value
                        })

                        if mapped_selector["status"] == "success":
                            selector_code = mapped_selector["data"].espresso_code
                            action_code = action_data.espresso_code

                            # Combine selector and action
                            test_body_lines.append(
                                f"        onView({selector_code}).{action_code};"
                            )

                            # Collect imports
                            all_imports.update(mapped_selector["data"].imports)
                            all_imports.update(action_data.imports)
                    else:
                        # Action without selector
                        test_body_lines.append(f"        {action_data.espresso_code};")
                        all_imports.update(action_data.imports)

            except Exception as e:
                self.logger.warning(f"Failed to map action {tool}: {e}")
                test_body_lines.append(
                    f"        // TODO: Manual implementation needed for {tool}"
                )

            # Add delay after if specified
            delay_after = action.get("delay_after_ms", 0)
            if delay_after > 0:
                test_body_lines.append(
                    f"        Thread.sleep({delay_after}L);"
                )

            test_body_lines.append("")  # Blank line between actions

        test_body = "\n".join(test_body_lines)

        # Generate imports
        import_lines = self._generate_java_imports(ui_framework, all_imports)

        code = f"""package {package_name};

{import_lines}

/**
 * Generated Espresso test from recorded scenario
 * Scenario: {metadata.get('name', 'Unknown')}
 * Generated on: {metadata.get('created_at', 'Unknown')}
 *
 * Original scenario file: {scenario.get('_source_file', 'Unknown')}
 */
@RunWith(AndroidJUnit4.class)
public class {class_name} {{

    @Rule
    public ActivityScenarioRule<MainActivity> activityRule =
        new ActivityScenarioRule<>(MainActivity.class);

    @Test
    public void testScenario() throws InterruptedException {{
{test_body}
    }}
}}
"""
        return code

    def _generate_java_imports(self, ui_framework: UIFramework, custom_imports: set) -> str:
        """Generate Java imports section."""
        standard_imports = [
            "import androidx.test.ext.junit.rules.ActivityScenarioRule;",
            "import androidx.test.ext.junit.runners.AndroidJUnit4;",
            "import org.junit.Rule;",
            "import org.junit.Test;",
            "import org.junit.runner.RunWith;",
        ]

        if ui_framework == UIFramework.XML:
            standard_imports.extend([
                "import static androidx.test.espresso.Espresso.onView;",
                "import static androidx.test.espresso.action.ViewActions.*;",
                "import static androidx.test.espresso.assertion.ViewAssertions.*;",
                "import static androidx.test.espresso.matcher.ViewMatchers.*;",
            ])
        elif ui_framework == UIFramework.COMPOSE:
            standard_imports.extend([
                "import androidx.compose.ui.test.junit4.ComposeTestRule;",
                "import androidx.compose.ui.test.junit4.createAndroidComposeRule;",
            ])

        # Add custom imports (ensure they end with semicolons for Java)
        formatted_custom = {imp if imp.endswith(";") else imp + ";" for imp in custom_imports}
        all_imports = sorted(set(standard_imports) | formatted_custom)
        return "\n".join(all_imports)

    def _format_code(self, code: str, language: Language) -> str:
        """Format generated code."""
        # In real implementation, would use CodeFormatter subagent
        return code

    def _get_output_path(self, class_name: str, language: Language) -> str:
        """Get output file path for generated code."""
        ext = "kt" if language == Language.KOTLIN else "java"
        return f"generated_tests/{class_name}.{ext}"

    def _extract_imports(
        self, code: str, ui_framework: UIFramework, language: Language
    ) -> List[str]:
        """Extract list of imports from generated code."""
        imports = []
        for line in code.split("\n"):
            if line.strip().startswith("import "):
                imports.append(line.strip())
        return imports


register_agent("espresso-code-generator", EspressoCodeGeneratorAgent)
