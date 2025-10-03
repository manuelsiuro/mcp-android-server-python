"""
Unit Tests for ReplayEngine Module

Tests scenario loading, action execution orchestration,
error handling, and report generation.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock, call
import json
import time
from pathlib import Path

from replay.replay_engine import ReplayEngine
from replay.execution_context import ReplayConfig
from replay.replay_report import ActionStatus


class TestReplayEngineInitialization:
    """Test ReplayEngine initialization."""

    def test_initialization_with_defaults(self):
        """Test ReplayEngine initializes with default configuration."""
        engine = ReplayEngine()

        assert engine.device_id is None
        assert isinstance(engine.config, ReplayConfig)
        assert engine.dispatcher is not None
        assert engine.context is not None
        assert engine.report is not None

    def test_initialization_with_device_id(self):
        """Test ReplayEngine initialization with device_id."""
        engine = ReplayEngine(device_id="device123")

        assert engine.device_id == "device123"
        assert engine.context.device_id == "device123"

    def test_initialization_with_custom_config(self, replay_config_fast):
        """Test ReplayEngine initialization with custom config."""
        engine = ReplayEngine(device_id="device123", config=replay_config_fast)

        assert engine.config == replay_config_fast
        assert engine.context.config == replay_config_fast


class TestReplayEngineScenarioLoading:
    """Test scenario file loading and validation."""

    def test_load_scenario_valid(self, tmp_scenario_file, mock_scenario_simple):
        """Test loading valid scenario file."""
        engine = ReplayEngine()

        scenario = engine.load_scenario(tmp_scenario_file)

        assert scenario['session_name'] == mock_scenario_simple['session_name']
        assert scenario['device_id'] == mock_scenario_simple['device_id']
        assert len(scenario['actions']) == 1

    def test_load_scenario_missing_file(self):
        """Test loading non-existent scenario file raises FileNotFoundError."""
        engine = ReplayEngine()

        with pytest.raises(FileNotFoundError, match="Scenario not found"):
            engine.load_scenario("/nonexistent/scenario.json")

    def test_load_scenario_invalid_json(self, tmp_invalid_json_file):
        """Test loading invalid JSON raises JSONDecodeError."""
        engine = ReplayEngine()

        with pytest.raises(json.JSONDecodeError):
            engine.load_scenario(tmp_invalid_json_file)

    def test_load_scenario_missing_required_fields(self, tmp_missing_fields_file):
        """Test loading scenario with missing fields raises ValueError."""
        engine = ReplayEngine()

        with pytest.raises(ValueError, match="Invalid scenario format"):
            engine.load_scenario(tmp_missing_fields_file)

    def test_load_scenario_missing_session_name(self, tmp_path):
        """Test scenario without session_name fails validation."""
        scenario_file = tmp_path / "no_session.json"
        scenario_file.write_text(json.dumps({
            "device_id": "device123",
            "actions": []
        }))

        engine = ReplayEngine()

        with pytest.raises(ValueError, match="Invalid scenario format"):
            engine.load_scenario(str(scenario_file))

    def test_load_scenario_missing_device_id(self, tmp_path):
        """Test scenario without device_id fails validation."""
        scenario_file = tmp_path / "no_device.json"
        scenario_file.write_text(json.dumps({
            "session_name": "test",
            "actions": []
        }))

        engine = ReplayEngine()

        with pytest.raises(ValueError, match="Invalid scenario format"):
            engine.load_scenario(str(scenario_file))

    def test_load_scenario_missing_actions(self, tmp_path):
        """Test scenario without actions array fails validation."""
        scenario_file = tmp_path / "no_actions.json"
        scenario_file.write_text(json.dumps({
            "session_name": "test",
            "device_id": "device123"
        }))

        engine = ReplayEngine()

        with pytest.raises(ValueError, match="missing 'actions' field"):
            engine.load_scenario(str(scenario_file))

    def test_load_scenario_actions_not_list(self, tmp_path):
        """Test scenario with non-list actions fails validation."""
        scenario_file = tmp_path / "invalid_actions.json"
        scenario_file.write_text(json.dumps({
            "session_name": "test",
            "device_id": "device123",
            "actions": "not a list"
        }))

        engine = ReplayEngine()

        with pytest.raises(ValueError, match="'actions' must be a list"):
            engine.load_scenario(str(scenario_file))

    def test_load_scenario_preserves_metadata(self, tmp_scenario_file_complex, mock_scenario_complex):
        """Test loading scenario preserves all metadata."""
        engine = ReplayEngine()

        scenario = engine.load_scenario(tmp_scenario_file_complex)

        assert scenario['session_name'] == mock_scenario_complex['session_name']
        assert scenario['device_id'] == mock_scenario_complex['device_id']
        assert scenario['timestamp'] == mock_scenario_complex['timestamp']
        assert scenario['description'] == mock_scenario_complex['description']


class TestReplayEngineSingleActionExecution:
    """Test single action execution."""

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_replay_single_action_success(
        self, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file, replay_config_fast
    ):
        """Test replaying scenario with single successful action."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay
        engine = ReplayEngine(device_id="device123", config=replay_config_fast)
        report = engine.replay(tmp_scenario_file)

        # Verify execution
        assert mock_context.execute_with_retry.call_count == 1
        assert report['success'] is True
        assert report['execution']['total_actions'] == 1
        assert report['execution']['successful_actions'] == 1
        assert report['execution']['failed_actions'] == 0

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_replay_single_action_failure(
        self, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file, replay_config_fast
    ):
        """Test replaying scenario with single failing action."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.FAILED
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay
        engine = ReplayEngine(device_id="device123", config=replay_config_fast)
        report = engine.replay(tmp_scenario_file)

        # Verify failure recorded
        assert report['success'] is False
        assert report['execution']['total_actions'] == 1
        assert report['execution']['successful_actions'] == 0
        assert report['execution']['failed_actions'] == 1


class TestReplayEngineMultipleActionExecution:
    """Test multiple action sequence execution."""

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_replay_multiple_actions_all_success(
        self, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file_complex, replay_config_fast
    ):
        """Test replaying scenario with multiple successful actions."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay
        engine = ReplayEngine(device_id="device123", config=replay_config_fast)
        report = engine.replay(tmp_scenario_file_complex)

        # Verify all actions executed
        assert mock_context.execute_with_retry.call_count == 5
        assert report['execution']['total_actions'] == 5
        assert report['execution']['successful_actions'] == 5
        assert report['execution']['failed_actions'] == 0

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_replay_multiple_actions_with_failures(
        self, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file_complex
    ):
        """Test replaying scenario with mixed success/failure actions."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()

        # Create results: success, fail, success, fail, success
        results = []
        for i in range(5):
            mock_result = MagicMock()
            mock_result.status = ActionStatus.SUCCESS if i % 2 == 0 else ActionStatus.FAILED
            results.append(mock_result)

        mock_context.execute_with_retry.side_effect = results
        mock_context_cls.return_value = mock_context

        # Execute replay with continue_on_error
        config = ReplayConfig(stop_on_error=False, wait_for_screen_on=False)
        engine = ReplayEngine(device_id="device123", config=config)
        report = engine.replay(tmp_scenario_file_complex)

        # Verify all actions attempted
        assert mock_context.execute_with_retry.call_count == 5
        assert report['execution']['total_actions'] == 5
        assert report['execution']['successful_actions'] == 3
        assert report['execution']['failed_actions'] == 2


class TestReplayEngineStopOnError:
    """Test stop_on_error configuration."""

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_replay_with_stop_on_error_true(
        self, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file_complex
    ):
        """Test replay stops after first error when stop_on_error=True."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()

        # Create results: success, fail (should stop here)
        results = []
        success_result = MagicMock()
        success_result.status = ActionStatus.SUCCESS
        results.append(success_result)

        fail_result = MagicMock()
        fail_result.status = ActionStatus.FAILED
        results.append(fail_result)

        mock_context.execute_with_retry.side_effect = results
        mock_context_cls.return_value = mock_context

        # Execute replay with stop_on_error=True
        config = ReplayConfig(stop_on_error=True, wait_for_screen_on=False)
        engine = ReplayEngine(device_id="device123", config=config)
        report = engine.replay(tmp_scenario_file_complex)

        # Verify stopped after 2 actions (1 success, 1 failure)
        assert mock_context.execute_with_retry.call_count == 2
        assert report['execution']['total_actions'] == 2
        assert report['execution']['successful_actions'] == 1
        assert report['execution']['failed_actions'] == 1

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_replay_continue_on_error(
        self, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file_complex
    ):
        """Test replay continues despite errors when stop_on_error=False."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()

        # All fail
        fail_result = MagicMock()
        fail_result.status = ActionStatus.FAILED
        mock_context.execute_with_retry.return_value = fail_result
        mock_context_cls.return_value = mock_context

        # Execute replay with stop_on_error=False
        config = ReplayConfig(stop_on_error=False, wait_for_screen_on=False)
        engine = ReplayEngine(device_id="device123", config=config)
        report = engine.replay(tmp_scenario_file_complex)

        # Verify all 5 actions attempted despite failures
        assert mock_context.execute_with_retry.call_count == 5
        assert report['execution']['failed_actions'] == 5


class TestReplayEngineDelayHandling:
    """Test timing delays between actions."""

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    @patch('replay.replay_engine.time.sleep')
    def test_apply_delay_with_speed_multiplier_1x(
        self, mock_sleep, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file_complex
    ):
        """Test delays applied correctly with speed_multiplier=1.0."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay
        config = ReplayConfig(speed_multiplier=1.0, wait_for_screen_on=False)
        engine = ReplayEngine(device_id="device123", config=config)
        engine.replay(tmp_scenario_file_complex)

        # Verify sleep called with correct delays
        # Scenario has delays: 2000ms, 2000ms, 1000ms, 2000ms
        # With speed_multiplier=1.0: 2.0s, 2.0s, 1.0s, 2.0s
        sleep_calls = [call(2.0), call(2.0), call(1.0), call(2.0)]
        mock_sleep.assert_has_calls(sleep_calls, any_order=False)

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    @patch('replay.replay_engine.time.sleep')
    def test_apply_delay_with_speed_multiplier_2x(
        self, mock_sleep, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file_complex
    ):
        """Test delays reduced with speed_multiplier=2.0 (2x faster)."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay with 2x speed
        config = ReplayConfig(speed_multiplier=2.0, wait_for_screen_on=False)
        engine = ReplayEngine(device_id="device123", config=config)
        engine.replay(tmp_scenario_file_complex)

        # Verify sleep called with halved delays
        # Original: 2000ms, 2000ms, 1000ms, 2000ms
        # With speed_multiplier=2.0: 1.0s, 1.0s, 0.5s, 1.0s
        sleep_calls = [call(1.0), call(1.0), call(0.5), call(1.0)]
        mock_sleep.assert_has_calls(sleep_calls, any_order=False)

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    @patch('replay.replay_engine.time.sleep')
    def test_apply_delay_with_speed_multiplier_half(
        self, mock_sleep, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file_complex
    ):
        """Test delays increased with speed_multiplier=0.5 (0.5x slower)."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay with 0.5x speed
        config = ReplayConfig(speed_multiplier=0.5, wait_for_screen_on=False)
        engine = ReplayEngine(device_id="device123", config=config)
        engine.replay(tmp_scenario_file_complex)

        # Verify sleep called with doubled delays
        # Original: 2000ms, 2000ms, 1000ms, 2000ms
        # With speed_multiplier=0.5: 4.0s, 4.0s, 2.0s, 4.0s
        sleep_calls = [call(4.0), call(4.0), call(2.0), call(4.0)]
        mock_sleep.assert_has_calls(sleep_calls, any_order=False)

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    @patch('replay.replay_engine.time.sleep')
    def test_no_delay_for_last_action(
        self, mock_sleep, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file_complex
    ):
        """Test no delay applied after last action."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay
        config = ReplayConfig(speed_multiplier=1.0, wait_for_screen_on=False)
        engine = ReplayEngine(device_id="device123", config=config)
        engine.replay(tmp_scenario_file_complex)

        # Verify sleep called exactly 4 times (not 5)
        # 5 actions = 4 delays between them
        assert mock_sleep.call_count == 4


class TestReplayEngineDevicePreparation:
    """Test device preparation before replay."""

    @patch('replay.replay_engine.server')
    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_ensure_device_ready_screen_on(
        self, mock_context_cls, mock_dispatcher_cls, mock_server, tmp_scenario_file
    ):
        """Test device screen turned on when wait_for_screen_on=True."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay
        config = ReplayConfig(wait_for_screen_on=True)
        engine = ReplayEngine(device_id="device123", config=config)
        engine.replay(tmp_scenario_file)

        # Verify screen_on called
        mock_server.screen_on.assert_called_once_with("device123")

    @patch('replay.replay_engine.server')
    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_skip_device_ready_when_disabled(
        self, mock_context_cls, mock_dispatcher_cls, mock_server, tmp_scenario_file
    ):
        """Test device preparation skipped when wait_for_screen_on=False."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay
        config = ReplayConfig(wait_for_screen_on=False)
        engine = ReplayEngine(device_id="device123", config=config)
        engine.replay(tmp_scenario_file)

        # Verify screen_on NOT called
        mock_server.screen_on.assert_not_called()


class TestReplayEngineReportGeneration:
    """Test execution report generation."""

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_report_contains_scenario_metadata(
        self, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file, mock_scenario_simple
    ):
        """Test report includes scenario metadata."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay
        engine = ReplayEngine()
        report = engine.replay(tmp_scenario_file)

        # Verify scenario metadata present
        assert 'scenario' in report
        assert report['scenario']['session_name'] == mock_scenario_simple['session_name']
        assert report['scenario']['device_id'] == mock_scenario_simple['device_id']
        assert report['scenario']['total_actions'] == 1

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_report_contains_execution_statistics(
        self, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file_complex
    ):
        """Test report includes execution statistics."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS
        mock_context.execute_with_retry.return_value = mock_result
        mock_context_cls.return_value = mock_context

        # Execute replay
        config = ReplayConfig(wait_for_screen_on=False)
        engine = ReplayEngine(config=config)
        report = engine.replay(tmp_scenario_file_complex)

        # Verify execution statistics
        assert 'execution' in report
        assert 'duration_seconds' in report['execution']
        assert 'total_actions' in report['execution']
        assert 'successful_actions' in report['execution']
        assert 'failed_actions' in report['execution']
        assert 'success_rate' in report['execution']

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_report_tracks_duration_accurately(
        self, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file
    ):
        """Test report duration is accurate."""
        # Setup mocks
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_result = MagicMock()
        mock_result.status = ActionStatus.SUCCESS

        def slow_execute(*args, **kwargs):
            time.sleep(0.1)
            return mock_result

        mock_context.execute_with_retry.side_effect = slow_execute
        mock_context_cls.return_value = mock_context

        # Execute replay
        config = ReplayConfig(wait_for_screen_on=False)
        engine = ReplayEngine(config=config)

        start = time.time()
        report = engine.replay(tmp_scenario_file)
        end = time.time()

        actual_duration = end - start
        reported_duration = report['execution']['duration_seconds']

        # Verify duration is approximately correct
        assert abs(reported_duration - actual_duration) < 0.1


class TestReplayEngineErrorHandling:
    """Test error handling and recovery."""

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_replay_handles_global_exception(
        self, mock_context_cls, mock_dispatcher_cls, tmp_scenario_file
    ):
        """Test replay handles unexpected exceptions gracefully."""
        # Setup mocks to raise exception
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_context.execute_with_retry.side_effect = Exception("Unexpected error")
        mock_context_cls.return_value = mock_context

        # Execute replay - should not crash
        engine = ReplayEngine()
        report = engine.replay(tmp_scenario_file)

        # Verify error recorded
        assert report['success'] is False
        assert len(report['errors']) > 0
        assert "Unexpected error" in report['errors'][0]

    @patch('replay.replay_engine.ActionDispatcher')
    @patch('replay.replay_engine.ExecutionContext')
    def test_replay_continues_after_scenario_load_failure(
        self, mock_context_cls, mock_dispatcher_cls
    ):
        """Test replay handles scenario load failure."""
        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        mock_context = MagicMock()
        mock_context_cls.return_value = mock_context

        # Execute replay with invalid path
        engine = ReplayEngine()
        report = engine.replay("/nonexistent/scenario.json")

        # Verify error recorded and report generated
        assert report['success'] is False
        assert 'errors' in report
        assert len(report['errors']) > 0
