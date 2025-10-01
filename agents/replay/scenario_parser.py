"""ScenarioParser Agent - Subagent for Scenario Validation."""

import json
from typing import Any, Dict

from ..base import SubAgent
from ..models import ValidationResult
from ..registry import register_agent


class ScenarioParserAgent(SubAgent):
    """Parse and validate scenario JSON files."""

    def __init__(self):
        super().__init__("ScenarioParser", parent_agent="ScenarioPlayer")

    def _process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate a scenario file."""
        scenario_file = inputs["scenario_file"]

        # Load JSON
        scenario_data = self._load_json(scenario_file)

        # Validate schema
        validation = self._validate_schema(scenario_data)

        # Extract metadata
        metadata = self._extract_metadata(scenario_data) if validation.valid else None

        return {
            "scenario": scenario_data,
            "metadata": metadata,
            "validation": {
                "valid": validation.valid,
                "errors": validation.errors,
                "warnings": validation.warnings,
            },
        }

    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load scenario JSON file."""
        with open(file_path, "r") as f:
            return json.load(f)

    def _validate_schema(self, scenario: Dict[str, Any]) -> ValidationResult:
        """Validate scenario schema."""
        errors = []
        warnings = []

        # Check required fields
        if "schema_version" not in scenario:
            errors.append("Missing required field: schema_version")
        if "metadata" not in scenario:
            errors.append("Missing required field: metadata")
        if "actions" not in scenario:
            errors.append("Missing required field: actions")

        # Validate actions
        if "actions" in scenario:
            for i, action in enumerate(scenario["actions"]):
                if "id" not in action:
                    errors.append(f"Action {i}: Missing 'id' field")
                if "tool" not in action:
                    errors.append(f"Action {i}: Missing 'tool' field")
                if "params" not in action:
                    errors.append(f"Action {i}: Missing 'params' field")

        return ValidationResult(
            valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def _extract_metadata(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from scenario."""
        return scenario.get("metadata", {})


register_agent("scenario-parser", ScenarioParserAgent)
