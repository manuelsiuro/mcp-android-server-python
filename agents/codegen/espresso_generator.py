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
        actions = scenario.get("actions", [])

        # Build test method body
        test_body_lines = []
        for action in actions:
            # In real implementation, would use SelectorMapper and ActionMapper
            tool = action.get("tool", "")
            params = action.get("params", {})

            if tool == "click":
                selector = params.get("selector", "")
                test_body_lines.append(
                    f'        onView(withText("{selector}")).perform(click())'
                )
            elif tool == "send_text":
                text = params.get("text", "")
                test_body_lines.append(
                    f'        onView(isFocused()).perform(typeText("{text}"))'
                )

        test_body = "\n".join(test_body_lines)

        code = f"""package {package_name}

import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.matcher.ViewMatchers.*
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

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

    def _generate_java_test(
        self,
        scenario: Dict[str, Any],
        package_name: str,
        class_name: str,
        ui_framework: UIFramework,
        options: CodeGenerationOptions,
    ) -> str:
        """Generate Java test code."""
        # Similar to Kotlin but with Java syntax
        return f"package {package_name};\n\n// Java test implementation\n"

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
