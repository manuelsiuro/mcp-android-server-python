"""
ScenarioPlayer Agent - Primary Agent for Replay System.

Orchestrates scenario replay and generates replay reports.
"""

import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..base import PrimaryAgent
from ..models import (
    ActionResult,
    ActionStatus,
    ReplayConfig,
    ReplayReport,
    ReplayStatus,
    Scenario,
)
from ..registry import register_agent


class ScenarioPlayerAgent(PrimaryAgent):
    """
    Primary agent that orchestrates Android UI scenario replay.

    Responsibilities:
    - Load and validate scenario JSON
    - Execute actions in sequence
    - Coordinate validation (optional)
    - Handle errors and retries
    - Generate comprehensive replay report
    """

    def __init__(self):
        super().__init__("ScenarioPlayer")

    def _process(self, inputs: Dict[str, Any]) -> ReplayReport:
        """
        Main processing logic for scenario replay.

        Args:
            inputs: Contains scenario_file, device_id, and config

        Returns:
            ReplayReport with execution results
        """
        scenario_file = inputs["scenario_file"]
        device_id = inputs.get("device_id")
        config = self._parse_config(inputs.get("config", {}))

        # Generate replay ID
        replay_id = str(uuid.uuid4())
        start_time = time.time()

        self.logger.info(f"Starting scenario replay: {scenario_file} (ID: {replay_id})")

        # Load and parse scenario
        scenario = self._load_scenario(scenario_file)

        # Validate scenario
        validation = self._validate_scenario(scenario)
        if not validation["valid"]:
            raise ValueError(f"Invalid scenario: {validation['errors']}")

        # Execute actions
        action_results = self._execute_scenario(scenario, device_id, config)

        # Calculate statistics
        duration_ms = int((time.time() - start_time) * 1000)
        passed_count = sum(1 for r in action_results if r.status == ActionStatus.PASSED)
        failed_count = sum(1 for r in action_results if r.status == ActionStatus.FAILED)
        total_count = len(action_results)

        # Determine overall status
        if failed_count == 0:
            status = ReplayStatus.PASSED
        elif passed_count == 0:
            status = ReplayStatus.FAILED
        else:
            status = ReplayStatus.PARTIAL

        # Generate report file
        report_file = self._generate_report_file(
            replay_id, scenario_file, action_results, status
        )

        self.logger.info(f"Replay complete: {passed_count}/{total_count} passed")

        return ReplayReport(
            replay_id=replay_id,
            status=status,
            duration_ms=duration_ms,
            actions_total=total_count,
            actions_passed=passed_count,
            actions_failed=failed_count,
            report_file=report_file,
            action_results=action_results,
        )

    def _parse_config(self, config_dict: Dict[str, Any]) -> ReplayConfig:
        """Parse configuration dictionary into ReplayConfig"""
        return ReplayConfig(
            validate_ui_state=config_dict.get("validate_ui_state", False),
            take_screenshots=config_dict.get("take_screenshots", False),
            continue_on_error=config_dict.get("continue_on_error", False),
            speed_multiplier=config_dict.get("speed_multiplier", 1.0),
            timeout_multiplier=config_dict.get("timeout_multiplier", 1.0),
        )

    def _load_scenario(self, scenario_file: str) -> Scenario:
        """Load scenario from JSON file"""
        with open(scenario_file, "r") as f:
            data = json.load(f)

        # In real implementation, would use ScenarioParser subagent
        # For now, basic loading
        return data

    def _validate_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scenario structure"""
        errors = []

        if "schema_version" not in scenario:
            errors.append("Missing schema_version")
        if "metadata" not in scenario:
            errors.append("Missing metadata")
        if "actions" not in scenario:
            errors.append("Missing actions")

        return {"valid": len(errors) == 0, "errors": errors}

    def _execute_scenario(
        self, scenario: Dict[str, Any], device_id: str, config: ReplayConfig
    ) -> List[ActionResult]:
        """Execute all actions in the scenario"""
        results = []
        actions = scenario.get("actions", [])

        for action_data in actions:
            # Execute action using ActionExecutor subagent
            result = self._execute_action(action_data, device_id, config)
            results.append(result)

            # Stop on error if configured
            if not config.continue_on_error and result.status == ActionStatus.FAILED:
                self.logger.warning(
                    f"Stopping replay due to failed action {action_data['id']}"
                )
                break

        return results

    def _execute_action(
        self, action_data: Dict[str, Any], device_id: str, config: ReplayConfig
    ) -> ActionResult:
        """Execute a single action"""
        action_id = action_data["id"]
        start_time = time.time()

        try:
            # In real implementation, would use ActionExecutor subagent
            # For now, simulate execution
            # Apply delays
            delay_before = (
                action_data.get("delay_before_ms", 0) * config.speed_multiplier / 1000
            )
            time.sleep(delay_before)

            # Simulate action execution
            # In real implementation: execute the MCP tool call

            execution_time_ms = int((time.time() - start_time) * 1000)

            return ActionResult(
                action_id=action_id,
                status=ActionStatus.PASSED,
                execution_time_ms=execution_time_ms,
                result=None,
                error=None,
                retry_count=0,
            )

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.error(f"Action {action_id} failed: {e}")

            return ActionResult(
                action_id=action_id,
                status=ActionStatus.FAILED,
                execution_time_ms=execution_time_ms,
                result=None,
                error=str(e),
                retry_count=0,
            )

    def _generate_report_file(
        self,
        replay_id: str,
        scenario_file: str,
        action_results: List[ActionResult],
        status: ReplayStatus,
    ) -> str:
        """Generate detailed report file"""
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"replay_{timestamp}_{replay_id[:8]}.json"

        # Build report data
        report_data = {
            "replay_id": replay_id,
            "scenario_file": scenario_file,
            "timestamp": datetime.now().isoformat(),
            "status": status.value,
            "action_results": [
                {
                    "action_id": r.action_id,
                    "status": r.status.value,
                    "execution_time_ms": r.execution_time_ms,
                    "error": r.error,
                    "retry_count": r.retry_count,
                }
                for r in action_results
            ],
        }

        # Write report
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        self.logger.info(f"Generated report: {report_file}")

        return str(report_file)


# Register this agent
register_agent("scenario-player", ScenarioPlayerAgent)
