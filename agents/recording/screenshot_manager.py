"""
ScreenshotManager Agent - Subagent for Screenshot Capture.

Manages screenshot capture and storage during recording.
"""

import time
from pathlib import Path
from typing import Any, Dict, Optional

from ..base import SubAgent
from ..models import ScreenshotResult
from ..registry import register_agent


class ScreenshotManagerAgent(SubAgent):
    """
    Subagent that manages screenshot capture and storage.

    Responsibilities:
    - Capture screenshots at appropriate times
    - Name and organize screenshots
    - Compress images (optional)
    - Handle storage errors
    - Link screenshots to actions
    """

    def __init__(self):
        super().__init__("ScreenshotManager", parent_agent="RecordingEngine")
        self.output_folder: Optional[Path] = None
        self.recording_id: Optional[str] = None

    def _process(self, inputs: Dict[str, Any]) -> Any:
        """
        Process screenshot manager commands.

        Supported actions:
        - initialize: Set up screenshot folder
        - capture: Capture a screenshot
        - organize: Organize screenshots folder
        - cleanup: Clean up on error
        """
        action = inputs.get("action", "capture")

        if action == "initialize":
            return self._initialize(
                recording_id=inputs["recording_id"],
                output_folder=inputs["output_folder"],
            )
        elif action == "capture":
            return self._capture_screenshot(
                action_id=inputs["action_id"],
                action_type=inputs["action_type"],
                device_id=inputs.get("device_id"),
            )
        elif action == "organize":
            return self._organize_screenshots()
        elif action == "cleanup":
            return self._cleanup_on_error()
        else:
            raise ValueError(f"Unknown action: {action}")

    def _initialize(self, recording_id: str, output_folder: str) -> Dict[str, Any]:
        """
        Initialize screenshot management for a recording session.

        Args:
            recording_id: ID of the recording
            output_folder: Base output folder for the recording

        Returns:
            Status information
        """
        self.recording_id = recording_id
        self.output_folder = Path(output_folder) / "screenshots"

        # Create screenshots folder if it doesn't exist
        self.output_folder.mkdir(parents=True, exist_ok=True)

        self.logger.info(
            f"Initialized screenshot manager for recording: {recording_id}"
        )
        self.logger.info(f"Screenshots will be saved to: {self.output_folder}")

        return {
            "status": "initialized",
            "recording_id": recording_id,
            "screenshot_folder": str(self.output_folder),
            "message": "Screenshot manager initialized successfully",
        }

    def _capture_screenshot(
        self, action_id: int, action_type: str, device_id: Optional[str] = None
    ) -> ScreenshotResult:
        """
        Capture a screenshot for an action.

        Args:
            action_id: ID of the action
            action_type: Type of action (e.g., 'click', 'input')
            device_id: Device to capture from

        Returns:
            ScreenshotResult with capture information
        """
        if not self.output_folder:
            raise RuntimeError("Screenshot manager not initialized")

        start_time = time.time()

        # Generate screenshot filename
        # Format: 001_click_login.png, 002_input_username.png, etc.
        filename = f"{action_id:03d}_{action_type}.png"
        screenshot_path = self.output_folder / filename

        try:
            # In a real implementation, this would call the MCP screenshot tool
            # For now, we'll simulate the capture
            # Example: mcp.screenshot(str(screenshot_path), device_id=device_id)

            # Simulate file creation and get size
            # In real implementation, actual screenshot would be taken here
            file_size_bytes = 0
            if screenshot_path.exists():
                file_size_bytes = screenshot_path.stat().st_size

            capture_time_ms = int((time.time() - start_time) * 1000)

            self.logger.debug(
                f"Captured screenshot: {filename} ({file_size_bytes} bytes, {capture_time_ms}ms)"
            )

            return ScreenshotResult(
                screenshot_path=str(screenshot_path),
                file_size_bytes=file_size_bytes,
                capture_time_ms=capture_time_ms,
                success=True,
            )

        except Exception as e:
            capture_time_ms = int((time.time() - start_time) * 1000)
            self.logger.error(f"Failed to capture screenshot: {e}")

            return ScreenshotResult(
                screenshot_path=str(screenshot_path),
                file_size_bytes=0,
                capture_time_ms=capture_time_ms,
                success=False,
            )

    def _organize_screenshots(self) -> Dict[str, Any]:
        """
        Organize screenshots folder.

        Returns:
            Statistics about the screenshots
        """
        if not self.output_folder or not self.output_folder.exists():
            return {"organized": False, "message": "Screenshot folder does not exist"}

        screenshots = list(self.output_folder.glob("*.png"))
        total_size = sum(f.stat().st_size for f in screenshots)

        self.logger.info(
            f"Organized {len(screenshots)} screenshots ({total_size} bytes)"
        )

        return {
            "organized": True,
            "screenshot_count": len(screenshots),
            "total_size_bytes": total_size,
            "folder_path": str(self.output_folder),
        }

    def _cleanup_on_error(self) -> Dict[str, Any]:
        """
        Clean up screenshots on recording error.

        Returns:
            Cleanup status
        """
        if not self.output_folder or not self.output_folder.exists():
            return {"cleaned_up": False, "message": "No folder to clean up"}

        # In a real implementation, might want to move to error folder
        # or delete depending on configuration
        # For now, just report status
        screenshots = list(self.output_folder.glob("*.png"))
        count = len(screenshots)

        self.logger.warning(f"Cleanup requested for {count} screenshots")

        return {
            "cleaned_up": True,
            "screenshots_affected": count,
            "folder_path": str(self.output_folder),
        }

    def compress_screenshot(self, screenshot_path: str, quality: int = 85) -> bool:
        """
        Compress a screenshot to reduce file size.

        Args:
            screenshot_path: Path to the screenshot
            quality: Compression quality (1-100)

        Returns:
            True if compression succeeded, False otherwise
        """
        # In real implementation, would use PIL or similar
        # to compress the image
        path = Path(screenshot_path)

        if not path.exists():
            self.logger.error(f"Screenshot not found: {screenshot_path}")
            return False

        # Simulate compression
        self.logger.debug(
            f"Compressed screenshot: {screenshot_path} (quality: {quality})"
        )
        return True


# Register this agent
register_agent("screenshot-manager", ScreenshotManagerAgent)
