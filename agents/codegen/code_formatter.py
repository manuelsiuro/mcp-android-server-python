"""CodeFormatter Agent - Formats generated code according to language standards."""

from typing import Any, Dict

from ..base import SubAgent
from ..models import Language
from ..registry import register_agent


class CodeFormatterAgent(SubAgent):
    """Format generated code according to language standards."""

    def __init__(self):
        super().__init__("CodeFormatter", parent_agent="EspressoCodeGenerator")

    def _process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Format code according to language style."""
        code = inputs["code"]
        language = Language(inputs.get("language", "kotlin"))
        style = inputs.get("style", "google")

        if language == Language.KOTLIN:
            formatted_code = self._format_kotlin(code, style)
        else:
            formatted_code = self._format_java(code, style)

        # Organize imports
        formatted_code = self._organize_imports(formatted_code, language)

        return {
            "formatted_code": formatted_code,
            "changes_made": ["Applied formatting", "Organized imports"],
        }

    def _format_kotlin(self, code: str, style: str) -> str:
        """Format Kotlin code (ktlint style)."""
        # In real implementation, would use ktlint or similar
        return code

    def _format_java(self, code: str, style: str) -> str:
        """Format Java code (google-java-format style)."""
        # In real implementation, would use google-java-format
        return code

    def _organize_imports(self, code: str, language: Language) -> str:
        """Organize imports alphabetically."""
        lines = code.split("\n")
        imports = []
        other_lines = []

        for line in lines:
            if line.strip().startswith("import "):
                imports.append(line)
            else:
                other_lines.append(line)

        # Sort imports
        imports.sort()

        # Reconstruct code
        if imports:
            # Find where imports should go (after package declaration)
            result = []
            found_package = False
            for line in other_lines:
                result.append(line)
                if not found_package and line.strip().startswith("package "):
                    found_package = True
                    result.append("")  # Blank line after package
                    result.extend(imports)
                    result.append("")  # Blank line after imports

            if not found_package:
                # No package declaration, put imports at top
                result = imports + [""] + other_lines

            return "\n".join(result)

        return code


register_agent("code-formatter", CodeFormatterAgent)
