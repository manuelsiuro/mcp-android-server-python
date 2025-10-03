# Action History Feature - Testing Guide

## Critical Bug Fixed ✅

**Issue Found**: Missing `datetime` import caused `NameError` when recording actions.
**Status**: FIXED - All imports added, error handling improved, debug logging enhanced.

## Prerequisites

- Backend server must be **RESTARTED** for Python changes to take effect
- Frontend build is optional (changes were backend-only)
- Android device connected via ADB
- MCP Android server accessible

## How to Restart the Backend Server

### Method 1: Kill and Restart

```bash
# Find the backend process
ps aux | grep "uvicorn\|python.*main.py"

# Kill the process (replace PID with actual process ID)
kill <PID>

# Navigate to backend directory
cd /Users/manuel.siuro/www/mcp-android-server-python/web-interface/backend

# Start server (choose one method)

# Option A: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 3001

# Option B: Using Python module
python main.py

# Option C: If you have a start script
./start-backend.sh
```

### Method 2: Restart Script (if available)

```bash
cd /Users/manuel.siuro/www/mcp-android-server-python/web-interface/backend
./restart.sh
```

## Verify Server is Running with New Code

After restarting, check the server logs for these startup messages:

```
✅ Found MCP config: /path/to/mcp-android-server-python/.claude/mcp-servers.json
```

## Testing Plan

### Test 1: Direct MCP Tool Call (Easiest to test first)

1. **Using curl**:
```bash
curl -X POST http://localhost:3001/api/mcp/tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "check_adb",
    "parameters": {}
  }'
```

2. **Check backend logs** for:
```
🔧 MCP Tool Call: check_adb
   Parameters: {}
✅ Recorded MCP tool action: check_adb
📊 Action history now contains 1 actions
```

3. **Check action history API**:
```bash
curl http://localhost:3001/api/actions/history
```

Expected response:
```json
{
  "actions": [
    {
      "id": "uuid-here",
      "timestamp": "2025-10-03T...",
      "type": "mcp_tool",
      "tool": "check_adb",
      "params": {},
      "result": {
        "success": true,
        "data": {...},
        "execution_time_ms": 123
      }
    }
  ]
}
```

### Test 2: Web Interface - Show History Button

1. Open web interface: `http://localhost:3001`
2. Click **"Show History"** button in header
3. Action History panel should appear at bottom-right
4. Initially shows: "No actions recorded yet" with help text

### Test 3: Claude WebSocket Tool Execution

1. In web interface, type a Claude prompt: `"Check which Android devices are connected"`
2. Claude should execute `mcp__mcp-android__check_adb` tool
3. **Check backend logs** for:
```
🔍 DEBUG: Received message type: tool_use
🔧 Detected tool use: mcp__mcp-android__check_adb (ID: toolu_...)
🔍 DEBUG: Received message type: tool_result
✅ Recorded action: mcp__mcp-android__check_adb - Success
📊 Action history now contains 1 actions
```

4. **Check Action History panel** - should show the recorded action with:
   - Tool name badge (green)
   - Timestamp
   - Success/Failed indicator
   - Expandable Parameters section
   - Expandable Result section

### Test 4: Multiple Actions

1. Ask Claude: `"Take a screenshot of the device"`
2. Ask Claude: `"Show me the UI hierarchy"`
3. Action History should now show multiple actions
4. Footer should say: "3 actions recorded"

## Debugging

### If Actions Still Not Appearing

1. **Check server was restarted**:
```bash
# Server logs should show recent startup timestamp
tail -f /path/to/backend.log
```

2. **Check for Python errors in logs**:
```bash
# Look for NameError, ImportError, or other exceptions
grep -i "error\|exception\|traceback" backend.log
```

3. **Test action history endpoint directly**:
```bash
# This should return current action count (even if 0)
curl http://localhost:3001/api/actions/history
```

4. **Check frontend is polling correctly**:
- Open browser DevTools → Network tab
- Should see `GET /api/actions/history` requests every 3 seconds

### Debug Logging

The implementation now includes extensive debug logging:

**For WebSocket (Claude execution)**:
```
🔍 DEBUG: Received message type: <type>
🔧 Detected tool use: <tool_name> (ID: <id>)
✅ Recorded action: <tool> - Success/Failed
📊 Action history now contains X actions
```

**For Direct MCP calls**:
```
🔧 MCP Tool Call: <tool_name>
   Parameters: {...}
✅ Recorded MCP tool action: <tool_name>
📊 Action history now contains X actions
```

**For Errors**:
```
❌ Error recording tool use: <error>
❌ Error recording tool result: <error>
⚠️  Received tool_result for unknown tool_use_id: <id>
```

## Expected Behavior After Fix

✅ **MCP Tool Proxy**: All direct tool calls should be recorded immediately
✅ **Claude WebSocket**: Tool uses should be detected and recorded when Claude executes them
✅ **Error Handling**: Failed actions are recorded with error details
✅ **Debug Visibility**: All tool executions are logged to console
✅ **UI Updates**: Action History panel auto-refreshes every 3 seconds
✅ **Limit Enforcement**: Only last 100 actions are kept

## Known Issues & Limitations

1. **Claude CLI Message Format**: If actions still don't appear from Claude, the stream-json format may differ from expectations. Check debug logs for actual message types received.

2. **Thread Safety**: The current implementation uses a simple list without locking. For production, consider using `asyncio.Lock`.

3. **Persistence**: Actions are stored in-memory only. Server restart clears history. For production, consider Redis or database storage.

## Bug Fixes Applied

### Critical Fixes:
1. ✅ Added missing `datetime` import
2. ✅ Added missing `uuid` import
3. ✅ Added missing `time` import
4. ✅ Consolidated all imports at top of file

### Enhancements:
1. ✅ Added comprehensive error handling with try/catch
2. ✅ Added debug logging for all message types
3. ✅ Added action count logging
4. ✅ Added unknown tool_use_id warnings
5. ✅ Added full stack traces for errors
6. ✅ Protected recording logic to not break tool execution

## Contact & Support

If issues persist after following this guide:
1. Collect backend server logs
2. Check browser console for errors
3. Verify MCP Android server is running and accessible
4. Test with `curl` commands to isolate frontend vs backend issues
