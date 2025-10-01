"""
Common data models and types for the Android Scenario Recording & Espresso Test Generation system.

This module defines all data structures used across agents for consistent typing and validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path


# ============================================================================
# Enumerations
# ============================================================================


class AgentStatus(str, Enum):
    """Status of agent execution"""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class Severity(str, Enum):
    """Error severity levels"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ReplayStatus(str, Enum):
    """Status of scenario replay"""

    PASSED = "PASSED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class ActionStatus(str, Enum):
    """Status of individual action execution"""

    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class UIFramework(str, Enum):
    """Android UI framework type"""

    XML = "xml"
    COMPOSE = "compose"
    HYBRID = "hybrid"


class Language(str, Enum):
    """Programming language for code generation"""

    JAVA = "java"
    KOTLIN = "kotlin"


class SelectorType(str, Enum):
    """Type of UI selector"""

    TEXT = "text"
    RESOURCE_ID = "resourceId"
    DESCRIPTION = "description"
    XPATH = "xpath"


# ============================================================================
# Recording System Models
# ============================================================================


@dataclass
class RecordingConfig:
    """Configuration for recording sessions"""

    capture_screenshots: bool = True
    capture_hierarchy: bool = True
    auto_delays: bool = True
    output_folder: Optional[str] = None


@dataclass
class Action:
    """Represents a recorded or replayed action"""

    id: int
    timestamp: str
    tool: str
    params: Dict[str, Any]
    result: Optional[Any] = None
    delay_before_ms: int = 0
    delay_after_ms: int = 0
    screenshot_path: Optional[str] = None
    ui_hierarchy: Optional[str] = None
    error: Optional[str] = None


@dataclass
class RecordingSession:
    """Active recording session state"""

    recording_id: str
    session_name: str
    description: Optional[str]
    device_id: Optional[str]
    config: RecordingConfig
    actions: List[Action] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    status: str = "active"


@dataclass
class RecordingResult:
    """Result of a completed recording"""

    recording_id: str
    session_file: str
    screenshot_folder: str
    actions_captured: int
    duration_ms: int
    status: AgentStatus
    warnings: List[str] = field(default_factory=list)


@dataclass
class ScreenshotResult:
    """Result of screenshot capture"""

    screenshot_path: str
    file_size_bytes: int
    capture_time_ms: int
    success: bool


# ============================================================================
# Scenario & Replay Models
# ============================================================================


@dataclass
class Metadata:
    """Scenario metadata"""

    name: str
    created_at: str
    device: Dict[str, Any]
    action_count: int
    description: Optional[str] = None
    schema_version: str = "1.0"


@dataclass
class Scenario:
    """Complete scenario structure"""

    schema_version: str
    metadata: Metadata
    actions: List[Action]


@dataclass
class ValidationResult:
    """Result of scenario validation"""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ReplayConfig:
    """Configuration for scenario replay"""

    validate_ui_state: bool = False
    take_screenshots: bool = False
    continue_on_error: bool = False
    speed_multiplier: float = 1.0
    timeout_multiplier: float = 1.0


@dataclass
class ActionResult:
    """Result of executing a single action"""

    action_id: int
    status: ActionStatus
    execution_time_ms: int
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class ReplayReport:
    """Complete replay execution report"""

    replay_id: str
    status: ReplayStatus
    duration_ms: int
    actions_total: int
    actions_passed: int
    actions_failed: int
    report_file: str
    screenshot_comparison: Optional[Dict[str, Any]] = None
    action_results: List[ActionResult] = field(default_factory=list)


@dataclass
class RetryConfig:
    """Configuration for action retry logic"""

    max_retries: int = 3
    backoff_factor: float = 1.5


@dataclass
class UIValidationResult:
    """Result of UI state validation"""

    validation_passed: bool
    mismatches: List[Dict[str, Any]] = field(default_factory=list)
    screenshot_similarity: float = 0.0


# ============================================================================
# Code Generation Models
# ============================================================================


@dataclass
class CodeGenerationOptions:
    """Options for Espresso code generation"""

    include_comments: bool = True
    use_idling_resources: bool = False
    generate_custom_actions: bool = True


@dataclass
class GeneratedCode:
    """Result of code generation"""

    code: str
    file_path: str
    imports: List[str]
    custom_actions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    ui_framework: UIFramework = UIFramework.XML


@dataclass
class MappedSelector:
    """Mapped selector from UIAutomator to Espresso"""

    espresso_code: str
    imports: List[str]
    fallback_selectors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class MappedAction:
    """Mapped action from UIAutomator to Espresso"""

    espresso_code: str
    custom_actions: List[str] = field(default_factory=list)
    assertions: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)


@dataclass
class FrameworkDetection:
    """UI framework detection result"""

    ui_framework: UIFramework
    compose_screens: List[int] = field(default_factory=list)
    xml_screens: List[int] = field(default_factory=list)
    confidence: float = 1.0


# ============================================================================
# Agent Communication Models
# ============================================================================


@dataclass
class AgentError:
    """Structured error information"""

    severity: Severity
    message: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMetadata:
    """Agent execution metadata"""

    execution_time_ms: int
    agent_version: str
    timestamp: str


@dataclass
class AgentResponse:
    """Standard agent response format"""

    agent: str
    status: AgentStatus
    data: Any
    errors: List[AgentError] = field(default_factory=list)
    metadata: Optional[AgentMetadata] = None

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access for backward compatibility."""
        return getattr(self, key)


# ============================================================================
# Quality & Testing Models
# ============================================================================


@dataclass
class TestCase:
    """Individual test case"""

    name: str
    description: str
    code: str
    fixtures: List[str] = field(default_factory=list)


@dataclass
class TestGenerationResult:
    """Result of test generation"""

    test_file: str
    test_count: int
    coverage_estimate: int
    fixtures_created: List[str] = field(default_factory=list)


@dataclass
class StyleIssue:
    """Code style issue"""

    line: int
    message: str
    severity: Severity


@dataclass
class SecurityIssue:
    """Security vulnerability"""

    line: int
    message: str
    severity: Severity
    cwe_id: Optional[str] = None


@dataclass
class PerformanceIssue:
    """Performance concern"""

    location: str
    message: str
    suggestion: str


@dataclass
class CodeReviewResult:
    """Result of code review"""

    review_score: int
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    approved: bool = False
    style_issues: List[StyleIssue] = field(default_factory=list)
    security_issues: List[SecurityIssue] = field(default_factory=list)
    performance_issues: List[PerformanceIssue] = field(default_factory=list)


@dataclass
class IntegrationTestResult:
    """Result of integration test"""

    test_passed: bool
    duration_ms: int
    issues_found: List[str] = field(default_factory=list)
    logs: str = ""
    screenshots: List[str] = field(default_factory=list)


# ============================================================================
# Utility Functions
# ============================================================================


def to_dict(obj: Any) -> Dict[str, Any]:
    """Convert dataclass to dictionary"""
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, list):
                result[key] = [
                    to_dict(item) if hasattr(item, "__dataclass_fields__") else item
                    for item in value
                ]
            elif hasattr(value, "__dataclass_fields__"):
                result[key] = to_dict(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Path):
                result[key] = str(value)
            else:
                result[key] = value
        return result
    return obj


def from_dict(cls, data: Dict[str, Any]) -> Any:
    """Create dataclass instance from dictionary"""
    if not hasattr(cls, "__dataclass_fields__"):
        return data

    field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}
    kwargs = {}

    for key, value in data.items():
        if key in field_types:
            field_type = field_types[key]
            if hasattr(field_type, "__dataclass_fields__"):
                kwargs[key] = from_dict(field_type, value)
            else:
                kwargs[key] = value

    return cls(**kwargs)
