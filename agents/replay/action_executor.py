"""ActionExecutor Agent - Subagent for Action Execution."""

import time
from typing import Any, Dict

from ..base import SubAgent
from ..models import ActionResult, ActionStatus, RetryConfig
from ..registry import register_agent


class ActionExecutorAgent(SubAgent):
    """Execute individual actions with proper timing and retry logic."""

    def __init__(self):
        super().__init__("ActionExecutor", parent_agent="ScenarioPlayer")

    def _process(self, inputs: Dict[str, Any]) -> ActionResult:
        """Execute an action with retry logic."""
        action_data = inputs["action"]
        device_id = inputs.get("device_id")
        retry_config = self._parse_retry_config(inputs.get("retry_config", {}))

        return self._execute_with_retry(action_data, device_id, retry_config)

    def _parse_retry_config(self, config_dict: Dict[str, Any]) -> RetryConfig:
        """Parse retry configuration."""
        return RetryConfig(
            max_retries=config_dict.get("max_retries", 3),
            backoff_factor=config_dict.get("backoff_factor", 1.5),
        )

    def _execute_with_retry(
        self, action_data: Dict[str, Any], device_id: str, retry_config: RetryConfig
    ) -> ActionResult:
        """Execute action with retry logic."""
        action_id = action_data["id"]
        retry_count = 0
        last_error = None

        for attempt in range(retry_config.max_retries + 1):
            try:
                # Apply delays
                if "delay_before_ms" in action_data:
                    time.sleep(action_data["delay_before_ms"] / 1000)

                # Execute the MCP tool
                # In real implementation, would dynamically call MCP tool
                # For now, simulate
                start_time = time.time()
                # result = self._execute_mcp_tool(action_data["tool"], action_data["params"])
                execution_time_ms = int((time.time() - start_time) * 1000)

                return ActionResult(
                    action_id=action_id,
                    status=ActionStatus.PASSED,
                    execution_time_ms=execution_time_ms,
                    result=None,
                    error=None,
                    retry_count=retry_count,
                )

            except Exception as e:
                last_error = str(e)
                retry_count += 1

                if attempt < retry_config.max_retries:
                    # Backoff before retry
                    backoff_time = retry_config.backoff_factor**attempt
                    time.sleep(backoff_time)
                    self.logger.warning(
                        f"Action {action_id} failed, retrying... ({retry_count}/{retry_config.max_retries})"
                    )

        # All retries exhausted
        return ActionResult(
            action_id=action_id,
            status=ActionStatus.FAILED,
            execution_time_ms=0,
            result=None,
            error=last_error,
            retry_count=retry_count,
        )


register_agent("action-executor", ActionExecutorAgent)
