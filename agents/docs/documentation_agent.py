"""DocumentationAgent - Generates and maintains project documentation."""

from pathlib import Path
from typing import Any, Dict, List

from ..base import SupportAgent
from ..registry import register_agent


class DocumentationAgent(SupportAgent):
    """Generate and maintain project documentation."""

    def __init__(self):
        super().__init__("Documentation")

    def _process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation."""
        doc_type = inputs["doc_type"]
        target_file = inputs.get("target_file")
        content_source = inputs.get("content_source", [])

        if doc_type == "api":
            documentation = self._generate_api_docs(content_source)
        elif doc_type == "tutorial":
            documentation = self._generate_tutorial(content_source)
        elif doc_type == "readme":
            documentation = self._update_readme(content_source)
        elif doc_type == "architecture":
            documentation = self._create_architecture_diagram(content_source)
        else:
            raise ValueError(f"Unknown doc type: {doc_type}")

        # Save documentation if target file provided
        if target_file:
            file_path = target_file
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                f.write(documentation)
        else:
            file_path = f"docs/{doc_type}.md"

        return {
            "documentation": documentation,
            "file_path": file_path,
            "format": "markdown",
        }

    def _generate_api_docs(self, modules: List[str]) -> str:
        """Generate API documentation."""
        docs = "# API Documentation\n\n"
        docs += "This document describes the public API for all agents.\n\n"

        for module in modules:
            docs += f"## {module}\n\n"
            docs += f"Documentation for {module}.\n\n"

        return docs

    def _generate_tutorial(self, scenario: List[str]) -> str:
        """Generate tutorial documentation."""
        tutorial = "# Tutorial\n\n"
        tutorial += "Step-by-step guide for using the agent system.\n\n"
        return tutorial

    def _update_readme(self, changes: List[str]) -> str:
        """Update README file."""
        readme = "# Android Scenario Recording & Espresso Test Generation\n\n"
        readme += "Multi-agent system for automated Android UI testing.\n\n"
        readme += "## Features\n\n"
        readme += "- Record Android UI interactions\n"
        readme += "- Replay scenarios\n"
        readme += "- Generate Espresso test code\n"
        return readme

    def _create_architecture_diagram(self, components: List[str]) -> str:
        """Create architecture diagram in Markdown."""
        diagram = "# System Architecture\n\n"
        diagram += "```\n"
        diagram += "┌─────────────────────────────────────┐\n"
        diagram += "│     Recording System Agents         │\n"
        diagram += "├─────────────────────────────────────┤\n"
        diagram += "│  - RecordingEngine                  │\n"
        diagram += "│  - ActionInterceptor                │\n"
        diagram += "│  - ScreenshotManager                │\n"
        diagram += "└─────────────────────────────────────┘\n"
        diagram += "```\n\n"
        return diagram


register_agent("documentation", DocumentationAgent)
