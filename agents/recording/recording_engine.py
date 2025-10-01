"""
RecordingEngine Agent - Primary Agent for Recording System.

Orchestrates the recording process and manages recording state.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ..base import PrimaryAgent
from ..models import (
    Action,
    AgentError,
    RecordingConfig,
    RecordingResult,
    RecordingSession,
    Severity,
)
from ..registry import register_agent


class RecordingEngineAgent(PrimaryAgent):
    """
    Primary agent that orchestrates Android UI scenario recording.

    Responsibilities:
    - Initialize recording session
    - Manage recording lifecycle (start/stop/pause)
    - Coordinate subagents (ActionInterceptor, ScreenshotManager)
    - Serialize recorded data to JSON
    - Handle recording errors and recovery
    """

    def __init__(self):
        super().__init__("RecordingEngine")
        self.active_sessions: Dict[str, RecordingSession] = {}

    def _validate_inputs(self, inputs: Dict[str, Any]) -> list[AgentError]:
        """Validate recording inputs"""
        errors = []

        # For start_recording
        if "action" in inputs and inputs["action"] == "start":
            if "session_name" not in inputs:
                errors.append(
                    AgentError(
                        severity=Severity.CRITICAL,
                        message="session_name is required for start action",
                        context=inputs,
                    )
                )

        # For stop_recording
        elif "action" in inputs and inputs["action"] == "stop":
            if "recording_id" not in inputs:
                errors.append(
                    AgentError(
                        severity=Severity.CRITICAL,
                        message="recording_id is required for stop action",
                        context=inputs,
                    )
                )

        return errors

    def _process(self, inputs: Dict[str, Any]) -> Any:
        """
        Main processing logic for recording operations.

        Supports actions: start, stop, pause, resume, status
        """
        action = inputs.get("action", "start")

        if action == "start":
            return self._start_recording(
                session_name=inputs["session_name"],
                description=inputs.get("description"),
                device_id=inputs.get("device_id"),
                config=self._parse_config(inputs.get("config", {})),
            )
        elif action == "stop":
            return self._stop_recording(inputs["recording_id"])
        elif action == "pause":
            return self._pause_recording(inputs["recording_id"])
        elif action == "resume":
            return self._resume_recording(inputs["recording_id"])
        elif action == "status":
            return self._get_status(inputs["recording_id"])
        else:
            raise ValueError(f"Unknown action: {action}")

    def _parse_config(self, config_dict: Dict[str, Any]) -> RecordingConfig:
        """Parse configuration dictionary into RecordingConfig"""
        return RecordingConfig(
            capture_screenshots=config_dict.get("capture_screenshots", True),
            capture_hierarchy=config_dict.get("capture_hierarchy", True),
            auto_delays=config_dict.get("auto_delays", True),
            output_folder=config_dict.get("output_folder"),
        )

    def _start_recording(
        self,
        session_name: str,
        description: Optional[str],
        device_id: Optional[str],
        config: RecordingConfig,
    ) -> Dict[str, Any]:
        """
        Start a new recording session.

        Args:
            session_name: Name for this recording session
            description: Optional description
            device_id: Target device (None for default)
            config: Recording configuration

        Returns:
            Dictionary with recording_id and status
        """
        # Generate unique recording ID
        recording_id = str(uuid.uuid4())

        # Create output folder if not specified
        if not config.output_folder:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            config.output_folder = f"scenarios/{session_name}_{timestamp}"

        # Create output directory
        output_path = Path(config.output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create screenshots folder
        screenshots_path = output_path / "screenshots"
        screenshots_path.mkdir(exist_ok=True)

        # Initialize recording session
        session = RecordingSession(
            recording_id=recording_id,
            session_name=session_name,
            description=description,
            device_id=device_id,
            config=config,
            actions=[],
            start_time=datetime.now(),
            status="active",
        )

        # Store active session
        self.active_sessions[recording_id] = session

        self.logger.info(
            f"Started recording session: {session_name} (ID: {recording_id})"
        )

        # Initialize subagents (in real implementation would use Task tool)
        # For now, just prepare the session structure

        return {
            "recording_id": recording_id,
            "session_name": session_name,
            "output_folder": str(output_path),
            "screenshot_folder": str(screenshots_path),
            "status": "active",
            "message": f"Recording session '{session_name}' started successfully",
        }

    def _stop_recording(self, recording_id: str) -> RecordingResult:
        """
        Stop a recording session and save to JSON.

        Args:
            recording_id: ID of the recording to stop

        Returns:
            RecordingResult with file paths and statistics
        """
        if recording_id not in self.active_sessions:
            raise ValueError(f"Recording ID not found: {recording_id}")

        session = self.active_sessions[recording_id]
        session.status = "stopped"

        # Calculate duration
        duration_ms = int((datetime.now() - session.start_time).total_seconds() * 1000)

        # Build scenario JSON structure
        scenario = {
            "schema_version": "1.0",
            "metadata": {
                "name": session.session_name,
                "description": session.description or "",
                "created_at": session.start_time.isoformat(),
                "device_id": session.device_id,
                "action_count": len(session.actions),
                "duration_ms": duration_ms,
            },
            "actions": [self._action_to_dict(action) for action in session.actions],
        }

        # Save scenario JSON
        output_path = Path(session.config.output_folder)
        scenario_file = output_path / "scenario.json"

        with open(scenario_file, "w") as f:
            json.dump(scenario, f, indent=2)

        self.logger.info(f"Saved recording to: {scenario_file}")

        # Clean up active session
        del self.active_sessions[recording_id]

        screenshot_folder = str(output_path / "screenshots")

        return RecordingResult(
            recording_id=recording_id,
            session_file=str(scenario_file),
            screenshot_folder=screenshot_folder,
            actions_captured=len(session.actions),
            duration_ms=duration_ms,
            status="success",
            warnings=[],
        )

    def _action_to_dict(self, action: Action) -> Dict[str, Any]:
        """Convert Action object to dictionary for JSON serialization"""
        return {
            "id": action.id,
            "timestamp": action.timestamp,
            "tool": action.tool,
            "params": action.params,
            "result": action.result,
            "delay_before_ms": action.delay_before_ms,
            "delay_after_ms": action.delay_after_ms,
            "screenshot_path": action.screenshot_path,
            "ui_hierarchy": action.ui_hierarchy,
            "error": action.error,
        }

    def _pause_recording(self, recording_id: str) -> Dict[str, Any]:
        """Pause an active recording"""
        if recording_id not in self.active_sessions:
            raise ValueError(f"Recording ID not found: {recording_id}")

        session = self.active_sessions[recording_id]
        session.status = "paused"

        self.logger.info(f"Paused recording: {recording_id}")

        return {
            "recording_id": recording_id,
            "status": "paused",
            "message": "Recording paused successfully",
        }

    def _resume_recording(self, recording_id: str) -> Dict[str, Any]:
        """Resume a paused recording"""
        if recording_id not in self.active_sessions:
            raise ValueError(f"Recording ID not found: {recording_id}")

        session = self.active_sessions[recording_id]
        session.status = "active"

        self.logger.info(f"Resumed recording: {recording_id}")

        return {
            "recording_id": recording_id,
            "status": "active",
            "message": "Recording resumed successfully",
        }

    def _get_status(self, recording_id: str) -> Dict[str, Any]:
        """Get status of a recording session"""
        if recording_id not in self.active_sessions:
            raise ValueError(f"Recording ID not found: {recording_id}")

        session = self.active_sessions[recording_id]
        duration_ms = int((datetime.now() - session.start_time).total_seconds() * 1000)

        return {
            "recording_id": recording_id,
            "session_name": session.session_name,
            "status": session.status,
            "actions_captured": len(session.actions),
            "duration_ms": duration_ms,
            "output_folder": session.config.output_folder,
        }

    def add_action(self, recording_id: str, action: Action) -> None:
        """
        Add a captured action to the recording.

        Called by ActionInterceptor subagent.

        Args:
            recording_id: ID of the active recording
            action: The captured action to add
        """
        if recording_id not in self.active_sessions:
            raise ValueError(f"Recording ID not found: {recording_id}")

        session = self.active_sessions[recording_id]
        session.actions.append(action)

        self.logger.debug(f"Added action {action.id} to recording {recording_id}")


# Register this agent
register_agent("recording-engine", RecordingEngineAgent)
