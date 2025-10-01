"""
Android Scenario Recording & Espresso Test Generation Agent System.

This package provides a hierarchical multi-agent system for:
- Recording Android UI interactions
- Replaying scenarios
- Generating Espresso test code
- Quality assurance and testing

Agents are designed to work with Claude Code's Task tool system.
"""

from .base import AgentBase, PrimaryAgent, SubAgent, SupportAgent
from .models import (
    Action,
    ActionResult,
    ActionStatus,
    AgentError,
    AgentResponse,
    AgentStatus,
    CodeGenerationOptions,
    FrameworkDetection,
    GeneratedCode,
    IntegrationTestResult,
    Language,
    MappedAction,
    MappedSelector,
    Metadata,
    RecordingConfig,
    RecordingResult,
    RecordingSession,
    ReplayConfig,
    ReplayReport,
    ReplayStatus,
    Scenario,
    ScreenshotResult,
    SelectorType,
    Severity,
    UIFramework,
    UIValidationResult,
    ValidationResult,
)
from .registry import get_agent, is_registered, list_agents, register_agent

__version__ = "1.0.0"

__all__ = [
    # Base classes
    "AgentBase",
    "PrimaryAgent",
    "SubAgent",
    "SupportAgent",
    # Registry functions
    "register_agent",
    "get_agent",
    "list_agents",
    "is_registered",
    # Models - Enums
    "AgentStatus",
    "ActionStatus",
    "ReplayStatus",
    "Severity",
    "UIFramework",
    "Language",
    "SelectorType",
    # Models - Recording
    "RecordingConfig",
    "RecordingSession",
    "RecordingResult",
    "Action",
    "ScreenshotResult",
    # Models - Replay
    "Scenario",
    "Metadata",
    "ValidationResult",
    "ReplayConfig",
    "ActionResult",
    "ReplayReport",
    "UIValidationResult",
    # Models - Code Generation
    "CodeGenerationOptions",
    "GeneratedCode",
    "MappedSelector",
    "MappedAction",
    "FrameworkDetection",
    # Models - Agent Communication
    "AgentError",
    "AgentResponse",
    # Models - Testing
    "IntegrationTestResult",
]
