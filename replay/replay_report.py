"""
Replay Report Generation Module

Provides data structures and report generation for scenario replay execution.
Tracks action results, timing metrics, and generates comprehensive execution reports.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class ActionStatus(Enum):
    """Status of action execution"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class ExecutionMetrics:
    """Timing and performance metrics for action execution"""
    start_time: float
    end_time: float
    duration_ms: float
    retry_count: int
    timeout_occurred: bool
    screenshot_captured: bool


@dataclass
class ActionResult:
    """Result of single action execution"""
    action_index: int
    tool_name: str
    parameters: Dict[str, Any]
    status: ActionStatus
    result: Any
    error: Optional[str]
    metrics: Optional[ExecutionMetrics]
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None
    screenshot_diff: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'action_index': self.action_index,
            'tool_name': self.tool_name,
            'parameters': self.parameters,
            'status': self.status.value,
            'result': str(self.result) if self.result is not None else None,
            'error': self.error,
            'duration_ms': round(self.metrics.duration_ms, 2) if self.metrics else None,
            'retry_count': self.metrics.retry_count if self.metrics else 0,
            'screenshot_before': self.screenshot_before,
            'screenshot_after': self.screenshot_after,
            'screenshot_diff': self.screenshot_diff
        }


class ReplayReport:
    """
    Aggregates action results and generates execution report.

    Tracks success/failure rates, timing, and provides
    detailed breakdown of replay execution.
    """

    def __init__(self):
        self.scenario_metadata: Dict[str, Any] = {}
        self.action_results: List[ActionResult] = []
        self.global_errors: List[str] = []

    def set_scenario_metadata(self, scenario: Dict[str, Any]):
        """Store scenario metadata"""
        self.scenario_metadata = {
            'session_name': scenario.get('session_name'),
            'device_id': scenario.get('device_id'),
            'recorded_at': scenario.get('timestamp'),
            'total_actions': len(scenario.get('actions', []))
        }

    def add_action_result(self, result: ActionResult):
        """Add action execution result"""
        self.action_results.append(result)

    def add_global_error(self, error: str):
        """Add global error (not tied to specific action)"""
        self.global_errors.append(error)

    def generate(self, duration_seconds: float) -> Dict[str, Any]:
        """
        Generate final execution report.

        Args:
            duration_seconds: Total replay duration

        Returns:
            Structured report dictionary
        """
        # Calculate statistics
        total = len(self.action_results)
        successful = sum(
            1 for r in self.action_results
            if r.status == ActionStatus.SUCCESS
        )
        failed = sum(
            1 for r in self.action_results
            if r.status == ActionStatus.FAILED
        )
        skipped = sum(
            1 for r in self.action_results
            if r.status == ActionStatus.SKIPPED
        )

        # Success rate
        success_rate = (successful / total * 100) if total > 0 else 0

        # Average action duration
        durations = [
            r.metrics.duration_ms for r in self.action_results
            if r.metrics
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Retry statistics
        total_retries = sum(
            r.metrics.retry_count for r in self.action_results
            if r.metrics
        )

        # Build report
        report = {
            'success': failed == 0 and len(self.global_errors) == 0,
            'scenario': self.scenario_metadata,
            'execution': {
                'duration_seconds': round(duration_seconds, 2),
                'total_actions': total,
                'successful_actions': successful,
                'failed_actions': failed,
                'skipped_actions': skipped,
                'success_rate': round(success_rate, 2),
                'total_retries': total_retries,
                'avg_action_duration_ms': round(avg_duration, 2)
            },
            'action_results': [r.to_dict() for r in self.action_results],
            'errors': self.global_errors,
            'failed_actions': [
                r.to_dict() for r in self.action_results
                if r.status == ActionStatus.FAILED
            ]
        }

        return report

    def save_to_file(self, filepath: str, duration_seconds: float):
        """Save report to JSON file"""
        report = self.generate(duration_seconds)
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
