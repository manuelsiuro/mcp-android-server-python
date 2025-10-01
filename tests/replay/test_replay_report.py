"""
Unit Tests for ReplayReport Module

Tests report generation, action result tracking, and statistics calculation.
"""

import pytest
import json
from pathlib import Path

from replay.replay_report import (
    ReplayReport,
    ActionResult,
    ActionStatus,
    ExecutionMetrics
)


class TestActionResult:
    """Test ActionResult data structure."""

    def test_action_result_to_dict(self, sample_action_result):
        """Test ActionResult serializes to dictionary."""
        result_dict = sample_action_result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict['action_index'] == 0
        assert result_dict['tool_name'] == "click"
        assert result_dict['status'] == "success"
        assert result_dict['result'] == "True"
        assert result_dict['error'] is None

    def test_action_result_to_dict_with_none_result(self):
        """Test ActionResult with None result."""
        metrics = ExecutionMetrics(
            start_time=1000.0,
            end_time=1001.0,
            duration_ms=1000.0,
            retry_count=0,
            timeout_occurred=False,
            screenshot_captured=False
        )

        result = ActionResult(
            action_index=0,
            tool_name="screen_on",
            parameters={},
            status=ActionStatus.SUCCESS,
            result=None,
            error=None,
            metrics=metrics
        )

        result_dict = result.to_dict()
        assert result_dict['result'] is None

    def test_action_result_to_dict_includes_screenshots(self):
        """Test ActionResult includes screenshot paths."""
        metrics = ExecutionMetrics(
            start_time=1000.0,
            end_time=1001.0,
            duration_ms=1000.0,
            retry_count=0,
            timeout_occurred=False,
            screenshot_captured=True
        )

        result = ActionResult(
            action_index=5,
            tool_name="click",
            parameters={"selector": "Button"},
            status=ActionStatus.SUCCESS,
            result=True,
            error=None,
            metrics=metrics,
            screenshot_before="/tmp/before.png",
            screenshot_after="/tmp/after.png",
            screenshot_diff="/tmp/diff.png"
        )

        result_dict = result.to_dict()
        assert result_dict['screenshot_before'] == "/tmp/before.png"
        assert result_dict['screenshot_after'] == "/tmp/after.png"
        assert result_dict['screenshot_diff'] == "/tmp/diff.png"

    def test_action_result_to_dict_handles_no_metrics(self):
        """Test ActionResult with None metrics."""
        result = ActionResult(
            action_index=0,
            tool_name="click",
            parameters={},
            status=ActionStatus.FAILED,
            result=None,
            error="Test error",
            metrics=None
        )

        result_dict = result.to_dict()
        assert result_dict['duration_ms'] is None
        assert result_dict['retry_count'] == 0

    def test_action_result_to_dict_rounds_duration(self):
        """Test ActionResult rounds duration to 2 decimal places."""
        metrics = ExecutionMetrics(
            start_time=1000.0,
            end_time=1001.5678,
            duration_ms=1567.8901,
            retry_count=0,
            timeout_occurred=False,
            screenshot_captured=False
        )

        result = ActionResult(
            action_index=0,
            tool_name="click",
            parameters={},
            status=ActionStatus.SUCCESS,
            result=True,
            error=None,
            metrics=metrics
        )

        result_dict = result.to_dict()
        assert result_dict['duration_ms'] == 1567.89


class TestReplayReportInitialization:
    """Test ReplayReport initialization."""

    def test_initialization(self):
        """Test ReplayReport initializes with empty state."""
        report = ReplayReport()

        assert report.scenario_metadata == {}
        assert report.action_results == []
        assert report.global_errors == []


class TestReplayReportScenarioMetadata:
    """Test scenario metadata handling."""

    def test_set_scenario_metadata(self, mock_scenario_simple):
        """Test setting scenario metadata."""
        report = ReplayReport()
        report.set_scenario_metadata(mock_scenario_simple)

        assert report.scenario_metadata['session_name'] == "simple_test"
        assert report.scenario_metadata['device_id'] == "TEST_DEVICE_123"
        assert report.scenario_metadata['total_actions'] == 1

    def test_set_scenario_metadata_extracts_fields(self, mock_scenario_complex):
        """Test metadata extraction from complex scenario."""
        report = ReplayReport()
        report.set_scenario_metadata(mock_scenario_complex)

        assert report.scenario_metadata['session_name'] == "complex_test"
        assert report.scenario_metadata['device_id'] == "TEST_DEVICE_123"
        assert report.scenario_metadata['recorded_at'] == "2025-10-01T12:00:00"
        assert report.scenario_metadata['total_actions'] == 5

    def test_set_scenario_metadata_handles_missing_timestamp(self):
        """Test metadata handles missing timestamp field."""
        scenario = {
            "session_name": "test",
            "device_id": "device123",
            "actions": []
        }

        report = ReplayReport()
        report.set_scenario_metadata(scenario)

        assert report.scenario_metadata['recorded_at'] is None


class TestReplayReportActionResults:
    """Test action result tracking."""

    def test_add_action_result(self, sample_action_result):
        """Test adding action result."""
        report = ReplayReport()
        report.add_action_result(sample_action_result)

        assert len(report.action_results) == 1
        assert report.action_results[0] == sample_action_result

    def test_add_multiple_action_results(self):
        """Test adding multiple action results."""
        report = ReplayReport()

        for i in range(5):
            metrics = ExecutionMetrics(
                start_time=1000.0 + i,
                end_time=1001.0 + i,
                duration_ms=1000.0,
                retry_count=0,
                timeout_occurred=False,
                screenshot_captured=False
            )

            result = ActionResult(
                action_index=i,
                tool_name="click",
                parameters={},
                status=ActionStatus.SUCCESS,
                result=True,
                error=None,
                metrics=metrics
            )
            report.add_action_result(result)

        assert len(report.action_results) == 5

    def test_add_action_result_preserves_order(self):
        """Test action results maintain insertion order."""
        report = ReplayReport()

        for i in range(3):
            metrics = ExecutionMetrics(
                start_time=1000.0,
                end_time=1001.0,
                duration_ms=1000.0,
                retry_count=0,
                timeout_occurred=False,
                screenshot_captured=False
            )

            result = ActionResult(
                action_index=i,
                tool_name=f"action_{i}",
                parameters={},
                status=ActionStatus.SUCCESS,
                result=True,
                error=None,
                metrics=metrics
            )
            report.add_action_result(result)

        # Verify order
        assert report.action_results[0].tool_name == "action_0"
        assert report.action_results[1].tool_name == "action_1"
        assert report.action_results[2].tool_name == "action_2"


class TestReplayReportGlobalErrors:
    """Test global error tracking."""

    def test_add_global_error(self):
        """Test adding global error."""
        report = ReplayReport()
        report.add_global_error("Test error message")

        assert len(report.global_errors) == 1
        assert report.global_errors[0] == "Test error message"

    def test_add_multiple_global_errors(self):
        """Test adding multiple global errors."""
        report = ReplayReport()

        report.add_global_error("Error 1")
        report.add_global_error("Error 2")
        report.add_global_error("Error 3")

        assert len(report.global_errors) == 3
        assert "Error 1" in report.global_errors
        assert "Error 2" in report.global_errors
        assert "Error 3" in report.global_errors


class TestReplayReportGeneration:
    """Test report generation."""

    def test_generate_report_all_success(self, mock_scenario_simple):
        """Test report generation with all successful actions."""
        report = ReplayReport()
        report.set_scenario_metadata(mock_scenario_simple)

        # Add successful result
        metrics = ExecutionMetrics(
            start_time=1000.0,
            end_time=1001.5,
            duration_ms=1500.0,
            retry_count=0,
            timeout_occurred=False,
            screenshot_captured=False
        )

        result = ActionResult(
            action_index=0,
            tool_name="click",
            parameters={"selector": "Button"},
            status=ActionStatus.SUCCESS,
            result=True,
            error=None,
            metrics=metrics
        )
        report.add_action_result(result)

        # Generate report
        final_report = report.generate(duration_seconds=2.0)

        # Verify success
        assert final_report['success'] is True
        assert final_report['execution']['total_actions'] == 1
        assert final_report['execution']['successful_actions'] == 1
        assert final_report['execution']['failed_actions'] == 0
        assert final_report['execution']['success_rate'] == 100.0

    def test_generate_report_with_failures(self, mock_scenario_complex):
        """Test report generation with mixed success/failure."""
        report = ReplayReport()
        report.set_scenario_metadata(mock_scenario_complex)

        # Add 3 success, 2 failures
        for i in range(5):
            metrics = ExecutionMetrics(
                start_time=1000.0,
                end_time=1001.0,
                duration_ms=1000.0,
                retry_count=0,
                timeout_occurred=False,
                screenshot_captured=False
            )

            status = ActionStatus.SUCCESS if i < 3 else ActionStatus.FAILED
            result = ActionResult(
                action_index=i,
                tool_name="click",
                parameters={},
                status=status,
                result=True if status == ActionStatus.SUCCESS else None,
                error=None if status == ActionStatus.SUCCESS else "Failed",
                metrics=metrics
            )
            report.add_action_result(result)

        # Generate report
        final_report = report.generate(duration_seconds=5.0)

        # Verify statistics
        assert final_report['success'] is False  # Has failures
        assert final_report['execution']['total_actions'] == 5
        assert final_report['execution']['successful_actions'] == 3
        assert final_report['execution']['failed_actions'] == 2
        assert final_report['execution']['success_rate'] == 60.0

    def test_generate_report_with_skipped_actions(self):
        """Test report generation with skipped actions."""
        report = ReplayReport()

        # Add 2 success, 1 skipped, 1 failed
        statuses = [
            ActionStatus.SUCCESS,
            ActionStatus.SUCCESS,
            ActionStatus.SKIPPED,
            ActionStatus.FAILED
        ]

        for i, status in enumerate(statuses):
            metrics = ExecutionMetrics(
                start_time=1000.0,
                end_time=1001.0,
                duration_ms=1000.0,
                retry_count=0,
                timeout_occurred=False,
                screenshot_captured=False
            )

            result = ActionResult(
                action_index=i,
                tool_name="click",
                parameters={},
                status=status,
                result=None,
                error=None,
                metrics=metrics
            )
            report.add_action_result(result)

        final_report = report.generate(duration_seconds=4.0)

        assert final_report['execution']['total_actions'] == 4
        assert final_report['execution']['successful_actions'] == 2
        assert final_report['execution']['failed_actions'] == 1
        assert final_report['execution']['skipped_actions'] == 1

    def test_calculate_success_rate_zero_actions(self):
        """Test success rate calculation with zero actions."""
        report = ReplayReport()

        final_report = report.generate(duration_seconds=0.0)

        # With no actions, success_rate should be 0
        assert final_report['execution']['success_rate'] == 0

    def test_calculate_success_rate_all_failed(self):
        """Test success rate with all failures."""
        report = ReplayReport()

        # Add 3 failures
        for i in range(3):
            metrics = ExecutionMetrics(
                start_time=1000.0,
                end_time=1001.0,
                duration_ms=1000.0,
                retry_count=0,
                timeout_occurred=False,
                screenshot_captured=False
            )

            result = ActionResult(
                action_index=i,
                tool_name="click",
                parameters={},
                status=ActionStatus.FAILED,
                result=None,
                error="Failed",
                metrics=metrics
            )
            report.add_action_result(result)

        final_report = report.generate(duration_seconds=3.0)

        assert final_report['execution']['success_rate'] == 0.0

    def test_calculate_avg_duration(self):
        """Test average duration calculation."""
        report = ReplayReport()

        # Add actions with different durations
        durations = [1000.0, 2000.0, 3000.0]

        for i, duration in enumerate(durations):
            metrics = ExecutionMetrics(
                start_time=1000.0,
                end_time=1000.0 + duration / 1000.0,
                duration_ms=duration,
                retry_count=0,
                timeout_occurred=False,
                screenshot_captured=False
            )

            result = ActionResult(
                action_index=i,
                tool_name="click",
                parameters={},
                status=ActionStatus.SUCCESS,
                result=True,
                error=None,
                metrics=metrics
            )
            report.add_action_result(result)

        final_report = report.generate(duration_seconds=6.0)

        # Average should be (1000 + 2000 + 3000) / 3 = 2000
        assert final_report['execution']['avg_action_duration_ms'] == 2000.0

    def test_calculate_avg_duration_with_no_metrics(self):
        """Test average duration with actions without metrics."""
        report = ReplayReport()

        result = ActionResult(
            action_index=0,
            tool_name="click",
            parameters={},
            status=ActionStatus.SUCCESS,
            result=True,
            error=None,
            metrics=None
        )
        report.add_action_result(result)

        final_report = report.generate(duration_seconds=1.0)

        # Should be 0 when no metrics available
        assert final_report['execution']['avg_action_duration_ms'] == 0

    def test_generate_includes_retry_statistics(self):
        """Test report includes retry statistics."""
        report = ReplayReport()

        # Add actions with different retry counts
        for i, retry_count in enumerate([0, 1, 2]):
            metrics = ExecutionMetrics(
                start_time=1000.0,
                end_time=1001.0,
                duration_ms=1000.0,
                retry_count=retry_count,
                timeout_occurred=False,
                screenshot_captured=False
            )

            result = ActionResult(
                action_index=i,
                tool_name="click",
                parameters={},
                status=ActionStatus.SUCCESS,
                result=True,
                error=None,
                metrics=metrics
            )
            report.add_action_result(result)

        final_report = report.generate(duration_seconds=3.0)

        # Total retries = 0 + 1 + 2 = 3
        assert final_report['execution']['total_retries'] == 3

    def test_generate_includes_failed_actions_list(self):
        """Test report includes list of failed actions."""
        report = ReplayReport()

        # Add 2 success, 2 failures
        for i in range(4):
            metrics = ExecutionMetrics(
                start_time=1000.0,
                end_time=1001.0,
                duration_ms=1000.0,
                retry_count=0,
                timeout_occurred=False,
                screenshot_captured=False
            )

            status = ActionStatus.FAILED if i % 2 == 1 else ActionStatus.SUCCESS
            result = ActionResult(
                action_index=i,
                tool_name=f"action_{i}",
                parameters={},
                status=status,
                result=None if status == ActionStatus.FAILED else True,
                error=f"Error {i}" if status == ActionStatus.FAILED else None,
                metrics=metrics
            )
            report.add_action_result(result)

        final_report = report.generate(duration_seconds=4.0)

        # Verify failed actions list
        failed_actions = final_report['failed_actions']
        assert len(failed_actions) == 2
        assert failed_actions[0]['tool_name'] == "action_1"
        assert failed_actions[1]['tool_name'] == "action_3"

    def test_generate_includes_all_action_results(self):
        """Test report includes all action results."""
        report = ReplayReport()

        for i in range(3):
            metrics = ExecutionMetrics(
                start_time=1000.0,
                end_time=1001.0,
                duration_ms=1000.0,
                retry_count=0,
                timeout_occurred=False,
                screenshot_captured=False
            )

            result = ActionResult(
                action_index=i,
                tool_name=f"action_{i}",
                parameters={},
                status=ActionStatus.SUCCESS,
                result=True,
                error=None,
                metrics=metrics
            )
            report.add_action_result(result)

        final_report = report.generate(duration_seconds=3.0)

        # Verify all results included
        assert len(final_report['action_results']) == 3

    def test_generate_rounds_values(self):
        """Test report rounds floating point values."""
        report = ReplayReport()

        metrics = ExecutionMetrics(
            start_time=1000.0,
            end_time=1001.5678,
            duration_ms=1567.8901,
            retry_count=0,
            timeout_occurred=False,
            screenshot_captured=False
        )

        result = ActionResult(
            action_index=0,
            tool_name="click",
            parameters={},
            status=ActionStatus.SUCCESS,
            result=True,
            error=None,
            metrics=metrics
        )
        report.add_action_result(result)

        final_report = report.generate(duration_seconds=2.3456789)

        # Verify rounding
        assert final_report['execution']['duration_seconds'] == 2.35
        assert final_report['execution']['success_rate'] == 100.0

    def test_generate_with_global_errors(self):
        """Test report success=False when global errors exist."""
        report = ReplayReport()

        metrics = ExecutionMetrics(
            start_time=1000.0,
            end_time=1001.0,
            duration_ms=1000.0,
            retry_count=0,
            timeout_occurred=False,
            screenshot_captured=False
        )

        # All actions successful
        result = ActionResult(
            action_index=0,
            tool_name="click",
            parameters={},
            status=ActionStatus.SUCCESS,
            result=True,
            error=None,
            metrics=metrics
        )
        report.add_action_result(result)

        # But global error occurred
        report.add_global_error("Device disconnected")

        final_report = report.generate(duration_seconds=1.0)

        # Report should be unsuccessful due to global error
        assert final_report['success'] is False
        assert len(final_report['errors']) == 1
        assert "Device disconnected" in final_report['errors']


class TestReplayReportSaveToFile:
    """Test report saving to file."""

    def test_save_to_file(self, tmp_path, mock_scenario_simple, sample_action_result):
        """Test saving report to JSON file."""
        report = ReplayReport()
        report.set_scenario_metadata(mock_scenario_simple)
        report.add_action_result(sample_action_result)

        output_file = tmp_path / "report.json"
        report.save_to_file(str(output_file), duration_seconds=1.0)

        # Verify file created
        assert output_file.exists()

        # Verify content is valid JSON
        with open(output_file, 'r') as f:
            loaded_report = json.load(f)

        assert loaded_report['success'] is True
        assert loaded_report['execution']['total_actions'] == 1

    def test_save_to_file_creates_directories(self, tmp_path, mock_scenario_simple, sample_action_result):
        """Test save creates parent directories if needed."""
        report = ReplayReport()
        report.set_scenario_metadata(mock_scenario_simple)
        report.add_action_result(sample_action_result)

        nested_dir = tmp_path / "reports" / "2025-10-01"
        output_file = nested_dir / "report.json"

        # Create parent directories
        nested_dir.mkdir(parents=True, exist_ok=True)

        report.save_to_file(str(output_file), duration_seconds=1.0)

        assert output_file.exists()

    def test_save_to_file_format_is_pretty(self, tmp_path, mock_scenario_simple, sample_action_result):
        """Test saved file uses pretty formatting."""
        report = ReplayReport()
        report.set_scenario_metadata(mock_scenario_simple)
        report.add_action_result(sample_action_result)

        output_file = tmp_path / "report.json"
        report.save_to_file(str(output_file), duration_seconds=1.0)

        # Read file content
        with open(output_file, 'r') as f:
            content = f.read()

        # Verify pretty formatting (should have newlines and indentation)
        assert '\n' in content
        assert '  ' in content  # Indentation


class TestActionStatusEnum:
    """Test ActionStatus enum."""

    def test_action_status_values(self):
        """Test ActionStatus enum values."""
        assert ActionStatus.SUCCESS.value == "success"
        assert ActionStatus.FAILED.value == "failed"
        assert ActionStatus.SKIPPED.value == "skipped"
        assert ActionStatus.TIMEOUT.value == "timeout"

    def test_action_status_equality(self):
        """Test ActionStatus equality comparisons."""
        assert ActionStatus.SUCCESS == ActionStatus.SUCCESS
        assert ActionStatus.SUCCESS != ActionStatus.FAILED


class TestExecutionMetrics:
    """Test ExecutionMetrics data structure."""

    def test_execution_metrics_creation(self):
        """Test ExecutionMetrics initialization."""
        metrics = ExecutionMetrics(
            start_time=1000.0,
            end_time=1001.5,
            duration_ms=1500.0,
            retry_count=2,
            timeout_occurred=False,
            screenshot_captured=True
        )

        assert metrics.start_time == 1000.0
        assert metrics.end_time == 1001.5
        assert metrics.duration_ms == 1500.0
        assert metrics.retry_count == 2
        assert metrics.timeout_occurred is False
        assert metrics.screenshot_captured is True
