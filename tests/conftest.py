"""
Pytest configuration for test suite.

This file contains fixtures and configuration that applies to all tests.
"""

import pytest
import server


@pytest.fixture(autouse=True)
def reset_recording_state():
    """Reset recording state before and after each test.

    This ensures that recording state doesn't leak between tests,
    preventing test interference when running the full test suite.
    """
    # Reset before test
    server._recording_state = {
        "active": False,
        "session_name": None,
        "device_id": None,
        "actions": [],
        "screenshots_dir": None,
        "action_counter": 0,
        "start_time": None,
        "last_action_time": None
    }

    yield

    # Reset after test
    server._recording_state = {
        "active": False,
        "session_name": None,
        "device_id": None,
        "actions": [],
        "screenshots_dir": None,
        "action_counter": 0,
        "start_time": None,
        "last_action_time": None
    }
