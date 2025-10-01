"""
Base classes and utilities for the agent system.

Provides common functionality for all agents including logging, error handling,
and standardized input/output formats.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from .models import AgentError, AgentMetadata, AgentResponse, AgentStatus, Severity


# Configure logging
logger = logging.getLogger(__name__)


class AgentVersion:
    """Agent version tracking"""

    MAJOR = 1
    MINOR = 0
    PATCH = 0

    @classmethod
    def version_string(cls) -> str:
        """Get version as string"""
        return f"{cls.MAJOR}.{cls.MINOR}.{cls.PATCH}"


class AgentBase(ABC):
    """
    Base class for all agents in the system.

    Provides common functionality:
    - Standardized execute() method with error handling
    - Logging and timing
    - Consistent input/output format
    - Version tracking
    """

    def __init__(self, agent_name: str):
        """
        Initialize agent.

        Args:
            agent_name: Name of this agent for logging and identification
        """
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")

    def execute(self, inputs: Dict[str, Any]) -> AgentResponse:
        """
        Main execution method with error handling and logging.

        Args:
            inputs: Input parameters for the agent

        Returns:
            AgentResponse with status, data, and any errors
        """
        self.logger.info(f"{self.agent_name} started")
        start_time = time.time()
        errors = []

        try:
            # Validate inputs
            validation_errors = self._validate_inputs(inputs)
            if validation_errors:
                return AgentResponse(
                    agent=self.agent_name,
                    status=AgentStatus.ERROR,
                    data=None,
                    errors=validation_errors,
                    metadata=self._create_metadata(start_time),
                )

            # Execute agent-specific logic
            result = self._process(inputs)

            # Calculate execution time
            duration_ms = int((time.time() - start_time) * 1000)
            self.logger.info(f"{self.agent_name} completed in {duration_ms}ms")

            return AgentResponse(
                agent=self.agent_name,
                status=AgentStatus.SUCCESS,
                data=result,
                errors=errors,
                metadata=self._create_metadata(start_time),
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.logger.error(
                f"{self.agent_name} failed after {duration_ms}ms: {e}", exc_info=True
            )

            return AgentResponse(
                agent=self.agent_name,
                status=AgentStatus.ERROR,
                data=None,
                errors=[
                    AgentError(
                        severity=Severity.CRITICAL,
                        message=str(e),
                        context={"inputs": inputs},
                    )
                ],
                metadata=self._create_metadata(start_time),
            )

    def _create_metadata(self, start_time: float) -> AgentMetadata:
        """Create metadata for agent response"""
        duration_ms = int((time.time() - start_time) * 1000)
        return AgentMetadata(
            execution_time_ms=duration_ms,
            agent_version=AgentVersion.version_string(),
            timestamp=datetime.now().isoformat(),
        )

    def _validate_inputs(self, inputs: Dict[str, Any]) -> list[AgentError]:
        """
        Validate input parameters.

        Override in subclasses to add specific validation logic.

        Args:
            inputs: Input parameters to validate

        Returns:
            List of validation errors (empty if valid)
        """
        return []

    @abstractmethod
    def _process(self, inputs: Dict[str, Any]) -> Any:
        """
        Core agent processing logic.

        Must be implemented by all subclasses.

        Args:
            inputs: Validated input parameters

        Returns:
            Agent-specific result data
        """
        pass


class PrimaryAgent(AgentBase):
    """
    Base class for primary agents that orchestrate subagents.

    Primary agents are responsible for:
    - Coordinating multiple subagents
    - Managing workflow state
    - Aggregating results
    """

    def __init__(self, agent_name: str):
        super().__init__(agent_name)
        self.subagents: Dict[str, "AgentBase"] = {}

    def register_subagent(self, name: str, agent: AgentBase) -> None:
        """
        Register a subagent for use by this primary agent.

        Args:
            name: Name/identifier for the subagent
            agent: The subagent instance
        """
        self.subagents[name] = agent
        self.logger.debug(f"Registered subagent: {name}")

    def invoke_subagent(self, name: str, inputs: Dict[str, Any]) -> AgentResponse:
        """
        Invoke a registered subagent.

        Args:
            name: Name of the subagent to invoke
            inputs: Inputs to pass to the subagent

        Returns:
            Response from the subagent

        Raises:
            ValueError: If subagent not found
        """
        if name not in self.subagents:
            raise ValueError(f"Subagent '{name}' not registered")

        self.logger.debug(f"Invoking subagent: {name}")
        return self.subagents[name].execute(inputs)


class SubAgent(AgentBase):
    """
    Base class for subagents that perform focused tasks.

    Subagents are invoked by primary agents and focus on a single
    specific responsibility within the larger workflow.
    """

    def __init__(self, agent_name: str, parent_agent: Optional[str] = None):
        super().__init__(agent_name)
        self.parent_agent = parent_agent


class SupportAgent(AgentBase):
    """
    Base class for support agents that provide cross-cutting functionality.

    Support agents handle tasks like testing, code review, and documentation
    that span across multiple primary workflows.
    """

    def __init__(self, agent_name: str):
        super().__init__(agent_name)


# Utility functions for agents


def format_error_message(
    error: Exception, context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Format an exception into a readable error message.

    Args:
        error: The exception to format
        context: Optional context information

    Returns:
        Formatted error message string
    """
    msg = f"{type(error).__name__}: {str(error)}"
    if context:
        msg += f"\nContext: {context}"
    return msg


def merge_agent_responses(responses: list[AgentResponse]) -> AgentResponse:
    """
    Merge multiple agent responses into a single response.

    Useful for aggregating results from parallel agents.

    Args:
        responses: List of agent responses to merge

    Returns:
        Merged agent response
    """
    if not responses:
        return AgentResponse(
            agent="merged",
            status=AgentStatus.ERROR,
            data=None,
            errors=[AgentError(Severity.CRITICAL, "No responses to merge", {})],
        )

    # Determine overall status
    if any(r.status == AgentStatus.ERROR for r in responses):
        status = AgentStatus.ERROR
    elif any(r.status == AgentStatus.PARTIAL for r in responses):
        status = AgentStatus.PARTIAL
    else:
        status = AgentStatus.SUCCESS

    # Merge data
    merged_data = {r.agent: r.data for r in responses}

    # Collect all errors
    all_errors = []
    for r in responses:
        all_errors.extend(r.errors)

    # Calculate total execution time
    total_time_ms = sum(r.metadata.execution_time_ms for r in responses if r.metadata)

    return AgentResponse(
        agent="merged",
        status=status,
        data=merged_data,
        errors=all_errors,
        metadata=AgentMetadata(
            execution_time_ms=total_time_ms,
            agent_version=AgentVersion.version_string(),
            timestamp=datetime.now().isoformat(),
        ),
    )
