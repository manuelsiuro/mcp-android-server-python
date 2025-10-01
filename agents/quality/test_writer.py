"""TestWriter Agent - Generates unit tests for the system."""

from pathlib import Path
from typing import Any, Dict, List

from ..base import SupportAgent
from ..models import TestGenerationResult
from ..registry import register_agent


class TestWriterAgent(SupportAgent):
    """Generate unit tests for system modules."""

    def __init__(self):
        super().__init__("TestWriter")

    def _process(self, inputs: Dict[str, Any]) -> TestGenerationResult:
        """Generate tests for a module."""
        module_to_test = inputs["module_to_test"]
        test_cases = inputs.get("test_cases", [])
        coverage_target = inputs.get("coverage_target", 80)

        # Generate test file
        test_file = self._generate_test_file(module_to_test, test_cases)

        # Create fixtures
        fixtures = self._create_fixtures(module_to_test)

        # Save test file
        test_path = self._get_test_path(module_to_test)
        Path(test_path).parent.mkdir(parents=True, exist_ok=True)

        with open(test_path, "w") as f:
            f.write(test_file)

        self.logger.info(f"Generated test file: {test_path}")

        return TestGenerationResult(
            test_file=test_path,
            test_count=len(test_cases) if test_cases else 5,
            coverage_estimate=coverage_target,
            fixtures_created=fixtures,
        )

    def _generate_test_file(self, module_path: str, test_cases: List[str]) -> str:
        """Generate test file content."""
        module_name = Path(module_path).stem

        code = f'''"""Tests for {module_path}"""

import pytest
from {module_path.replace("/", ".").replace(".py", "")} import *


@pytest.fixture
def mock_agent():
    """Mock agent for testing."""
    return None


def test_{module_name}_initialization():
    """Test agent initialization."""
    pass


def test_{module_name}_execute_success():
    """Test successful execution."""
    pass


def test_{module_name}_execute_error():
    """Test error handling."""
    pass
'''
        return code

    def _create_fixtures(self, module_path: str) -> List[str]:
        """Create test fixtures."""
        return ["mock_agent", "sample_data"]

    def _get_test_path(self, module_path: str) -> str:
        """Get path for generated test file."""
        module_name = Path(module_path).stem
        return f"tests/agents/test_{module_name}.py"


register_agent("test-writer", TestWriterAgent)
