"""
Agent registry for the Android Scenario Recording & Espresso Test Generation system.

Provides centralized registration and lookup of all agent types.
"""

from typing import Dict, Optional, Type

from .base import AgentBase


class AgentRegistry:
    """
    Central registry for all agents in the system.

    Allows looking up agent classes by their subagent_type identifier
    for use with Claude Code's Task tool.
    """

    def __init__(self):
        self._registry: Dict[str, Type[AgentBase]] = {}

    def register(self, subagent_type: str, agent_class: Type[AgentBase]) -> None:
        """
        Register an agent class with a subagent_type identifier.

        Args:
            subagent_type: The identifier used in Task tool invocations
            agent_class: The agent class to register
        """
        self._registry[subagent_type] = agent_class

    def get(self, subagent_type: str) -> Optional[Type[AgentBase]]:
        """
        Get an agent class by its subagent_type.

        Args:
            subagent_type: The identifier to look up

        Returns:
            The agent class, or None if not found
        """
        return self._registry.get(subagent_type)

    def list_agents(self) -> list[str]:
        """
        Get a list of all registered agent types.

        Returns:
            List of subagent_type identifiers
        """
        return list(self._registry.keys())

    def is_registered(self, subagent_type: str) -> bool:
        """
        Check if a subagent_type is registered.

        Args:
            subagent_type: The identifier to check

        Returns:
            True if registered, False otherwise
        """
        return subagent_type in self._registry


# Global registry instance
_global_registry = AgentRegistry()


def register_agent(subagent_type: str, agent_class: Type[AgentBase]) -> None:
    """
    Register an agent with the global registry.

    Args:
        subagent_type: The identifier for Task tool invocations
        agent_class: The agent class to register
    """
    _global_registry.register(subagent_type, agent_class)


def get_agent(subagent_type: str) -> Optional[Type[AgentBase]]:
    """
    Get an agent class from the global registry.

    Args:
        subagent_type: The identifier to look up

    Returns:
        The agent class, or None if not found
    """
    return _global_registry.get(subagent_type)


def list_agents() -> list[str]:
    """
    Get all registered agent types.

    Returns:
        List of subagent_type identifiers
    """
    return _global_registry.list_agents()


def is_registered(subagent_type: str) -> bool:
    """
    Check if an agent type is registered.

    Args:
        subagent_type: The identifier to check

    Returns:
        True if registered, False otherwise
    """
    return _global_registry.is_registered(subagent_type)


# This will be populated as agents are imported and register themselves
# Each agent module should call register_agent() at module level
AGENT_REGISTRY = {
    # Recording System
    "recording-engine": None,  # Will be set by recording.recording_engine module
    "action-interceptor": None,  # Will be set by recording.action_interceptor module
    "screenshot-manager": None,  # Will be set by recording.screenshot_manager module
    # Replay System
    "scenario-player": None,  # Will be set by replay.scenario_player module
    "scenario-parser": None,  # Will be set by replay.scenario_parser module
    "action-executor": None,  # Will be set by replay.action_executor module
    "ui-validator": None,  # Will be set by replay.ui_validator module
    # Code Generation
    "espresso-code-generator": None,  # Will be set by codegen.espresso_generator module
    "selector-mapper": None,  # Will be set by codegen.selector_mapper module
    "action-mapper": None,  # Will be set by codegen.action_mapper module
    "compose-detector": None,  # Will be set by codegen.compose_detector module
    "code-formatter": None,  # Will be set by codegen.code_formatter module
    # Support Agents
    "test-writer": None,  # Will be set by quality.test_writer module
    "code-reviewer": None,  # Will be set by quality.code_reviewer module
    "integration-tester": None,  # Will be set by quality.integration_tester module
    "documentation": None,  # Will be set by docs.documentation_agent module
}
