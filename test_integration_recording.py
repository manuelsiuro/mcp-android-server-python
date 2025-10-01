#!/usr/bin/env python3
"""
Integration Test Script for Recording Mechanism POC

This script tests the recording mechanism with a real Android device.
Run this after starting the MCP server.

Usage:
    python test_integration_recording.py
"""

import time
import json
from pathlib import Path

# Import server functions (assuming server.py is in same directory)
import server


def test_recording_integration():
    """Test the full recording and replay workflow."""

    print("=" * 60)
    print("RECORDING MECHANISM POC - INTEGRATION TEST")
    print("=" * 60)
    print()

    # Test 1: Check device connection
    print("1. Checking device connection...")
    try:
        device_info = server.connect_device()
        print(f"   ✓ Connected to {device_info['manufacturer']} {device_info['model']}")
        print(f"   ✓ Android {device_info['version']} (SDK {device_info['sdk']})")
    except Exception as e:
        print(f"   ✗ Failed to connect to device: {e}")
        print("   Make sure a device is connected via ADB")
        return False

    print()

    # Test 2: Start recording
    print("2. Starting recording session...")
    result = server.start_recording(
        session_name="integration_test",
        description="POC integration test",
        capture_screenshots=True
    )

    if result.get("status") == "active":
        print(f"   ✓ Recording started: {result['recording_id']}")
        print(f"   ✓ Screenshots: {result['capture_screenshots']}")
    else:
        print(f"   ✗ Failed to start recording: {result}")
        return False

    print()

    # Test 3: Simulate some actions (you'll need to adjust these for your device)
    print("3. Recording test actions...")
    print("   NOTE: Make sure the Contacts app is on screen with a search button visible")
    input("   Press Enter when ready to record actions...")

    # Record action 1: Click search
    print("   - Recording click on search button...")
    click_result = server.click("Search contacts", selector_type="description", timeout=5.0)
    if click_result:
        print("     ✓ Click recorded")
    else:
        print("     ⚠ Click failed (element may not exist)")

    time.sleep(1)

    # Record action 2: Send text
    print("   - Recording text input...")
    text_result = server.send_text("test", clear=True)
    if text_result:
        print("     ✓ Text input recorded")
    else:
        print("     ⚠ Text input failed")

    time.sleep(1)

    # Check status
    status = server.get_recording_status()
    print(f"   ✓ Current status: {status['action_count']} actions recorded")

    print()

    # Test 4: Stop recording
    print("4. Stopping recording...")
    stop_result = server.stop_recording()

    if stop_result.get("status") == "saved":
        print(f"   ✓ Recording saved: {stop_result['scenario_file']}")
        print(f"   ✓ Actions recorded: {stop_result['action_count']}")
        print(f"   ✓ Duration: {stop_result['duration_ms']}ms")
        print(f"   ✓ Screenshots: {stop_result['screenshot_folder']}")
    else:
        print(f"   ✗ Failed to stop recording: {stop_result}")
        return False

    scenario_file = stop_result['scenario_file']

    print()

    # Test 5: Verify JSON structure
    print("5. Verifying scenario JSON...")
    try:
        with open(scenario_file) as f:
            scenario = json.load(f)

        print(f"   ✓ Schema version: {scenario['schema_version']}")
        print(f"   ✓ Session name: {scenario['metadata']['name']}")
        print(f"   ✓ Actions: {len(scenario['actions'])}")

        # Print action details
        for action in scenario['actions']:
            print(f"      - Action {action['id']}: {action['tool']} ({action['params']})")
            if action.get('screenshot'):
                screenshot_exists = Path(action['screenshot']).exists()
                print(f"        Screenshot: {'✓' if screenshot_exists else '✗'} {action['screenshot']}")

    except Exception as e:
        print(f"   ✗ Failed to verify JSON: {e}")
        return False

    print()

    # Test 6: Replay scenario
    print("6. Replaying scenario...")
    print("   NOTE: This will replay the recorded actions")
    input("   Press Enter to continue with replay...")

    replay_result = server.replay_scenario(scenario_file, speed_multiplier=1.0)

    if replay_result.get("status") in ["PASSED", "FAILED"]:
        print(f"   ✓ Replay completed: {replay_result['status']}")
        print(f"   ✓ Actions executed: {replay_result['actions_executed']}")
        print(f"   ✓ Actions passed: {replay_result['actions_passed']}")
        print(f"   ✓ Actions failed: {replay_result['actions_failed']}")
        print(f"   ✓ Duration: {replay_result['duration_ms']}ms")
    else:
        print(f"   ✗ Replay error: {replay_result}")
        return False

    print()
    print("=" * 60)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 60)
    print()
    print(f"Scenario saved to: {scenario_file}")
    print("You can replay it with:")
    print(f"  replay_scenario('{scenario_file}')")
    print()

    return True


if __name__ == "__main__":
    success = test_recording_integration()
    exit(0 if success else 1)
