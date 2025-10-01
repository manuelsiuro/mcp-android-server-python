"""
Replay Engine Module

Main orchestrator for scenario replay execution.
Coordinates action sequence execution, error handling, and reporting.
"""

from typing import Dict, Any, Optional
import time
import json
from pathlib import Path
import server

from .action_dispatcher import ActionDispatcher
from .execution_context import ExecutionContext, ReplayConfig
from .replay_report import ReplayReport


class ReplayEngine:
    """
    Main orchestrator for scenario replay.

    Coordinates action execution, error handling, and reporting
    for recorded test scenarios.
    """

    def __init__(
        self,
        device_id: Optional[str] = None,
        config: Optional[ReplayConfig] = None
    ):
        self.device_id = device_id
        self.config = config or ReplayConfig()
        self.dispatcher = ActionDispatcher()
        self.context = ExecutionContext(
            device_id=device_id,
            config=self.config
        )
        self.report = ReplayReport()

    def load_scenario(self, scenario_path: str) -> Dict[str, Any]:
        """
        Load and validate scenario JSON file.

        Args:
            scenario_path: Path to scenario JSON file

        Returns:
            Scenario dictionary with metadata and actions

        Raises:
            ValueError: If scenario format is invalid
            FileNotFoundError: If scenario file doesn't exist
        """
        path = Path(scenario_path)
        if not path.exists():
            raise FileNotFoundError(f"Scenario not found: {scenario_path}")

        with open(path, 'r') as f:
            scenario = json.load(f)

        # Validate required fields
        required = ['session_name', 'device_id', 'actions']
        missing = [f for f in required if f not in scenario]
        if missing:
            raise ValueError(f"Invalid scenario: missing fields {missing}")

        # Validate actions array
        if not isinstance(scenario['actions'], list):
            raise ValueError("Invalid scenario: 'actions' must be a list")

        return scenario

    def replay(self, scenario_path: str) -> Dict[str, Any]:
        """
        Execute scenario replay with full error handling and reporting.

        Args:
            scenario_path: Path to recorded scenario JSON

        Returns:
            Execution report dictionary with:
                - success: bool (overall success)
                - total_actions: int
                - successful_actions: int
                - failed_actions: int
                - skipped_actions: int
                - duration_seconds: float
                - action_results: List[ActionResult]
                - errors: List[str]
        """
        start_time = time.time()

        try:
            # 1. Load scenario
            scenario = self.load_scenario(scenario_path)
            self.report.set_scenario_metadata(scenario)

            # 2. Prepare device
            if self.config.wait_for_screen_on:
                self._ensure_device_ready()

            # 3. Execute action sequence
            actions = scenario.get('actions', [])
            for idx, action in enumerate(actions):
                result = self._execute_action(action, idx)
                self.report.add_action_result(result)

                # Stop on error if configured
                if not result.status == result.status.SUCCESS and self.config.stop_on_error:
                    print(f"Stopping replay due to error in action {idx}")
                    break

                # Apply speed multiplier delay
                if idx < len(actions) - 1:
                    self._apply_delay(action, actions[idx + 1])

        except Exception as e:
            self.report.add_global_error(f"Replay error: {str(e)}")

        finally:
            duration = time.time() - start_time

        return self.report.generate(duration)

    def _execute_action(
        self,
        action: Dict[str, Any],
        index: int
    ) -> Any:
        """
        Execute single action with retry logic.

        Args:
            action: Action dictionary from scenario
            index: Action index in sequence

        Returns:
            ActionResult with execution details
        """
        tool_name = action.get('tool')
        parameters = action.get('params', {})

        # Execute with context (handles retries, screenshots, timing)
        result = self.context.execute_with_retry(
            tool_name=tool_name,
            parameters=parameters,
            action_index=index,
            dispatcher=self.dispatcher
        )

        return result

    def _ensure_device_ready(self):
        """
        Ensure device screen is on and ready.

        Calls wait_for_screen_on if device_id is available.
        """
        try:
            if self.device_id:
                server.screen_on(self.device_id)
                # Wait a bit for screen to stabilize
                time.sleep(1)
        except Exception as e:
            print(f"Warning: Could not ensure device ready: {e}")

    def _apply_delay(self, current_action: Dict[str, Any], next_action: Dict[str, Any]):
        """
        Apply timing delay based on recorded actions.

        Calculates delay between current and next action,
        scaled by speed_multiplier.

        Args:
            current_action: Current action dict
            next_action: Next action dict
        """
        # Check if next action has delay_before_ms
        delay_ms = next_action.get('delay_before_ms', 0)

        if delay_ms > 0:
            # Apply speed multiplier (higher = faster, lower = slower)
            scaled_delay = delay_ms / 1000.0 / self.config.speed_multiplier
            if scaled_delay > 0:
                time.sleep(scaled_delay)
