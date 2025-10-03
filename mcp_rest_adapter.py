#!/usr/bin/env python3
"""
REST API Adapter for MCP Android Server

This adapter exposes the MCP Android server tools via HTTP REST API endpoints,
allowing the web interface to communicate with the MCP server.

The adapter runs on port 8000 and proxies requests to the MCP server.
"""

import asyncio
import json
import re
import subprocess
import sys
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="MCP Android REST Adapter", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP server process
mcp_process: Optional[subprocess.Popen] = None


class ToolRequest(BaseModel):
    """Request model for tool execution"""
    parameters: Dict[str, Any] = {}


class ToolResponse(BaseModel):
    """Response model for tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None


# Cache for tool name to function name mapping
_tool_mapping: Optional[Dict[str, str]] = None

def _build_tool_mapping() -> Dict[str, str]:
    """Build mapping from MCP tool names to actual function names"""
    server_path = '/Users/manuel.siuro/www/mcp-android-server-python/server.py'
    with open(server_path, 'r') as f:
        content = f.read()

    # Find all @mcp.tool(name="...") followed by def function_name
    pattern = r'@mcp\.tool\(name="([^"]+)"[^\)]*\)\s*\n\s*def\s+([a-z_]+)\s*\('
    matches = re.findall(pattern, content)

    return dict(matches)


async def call_mcp_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call an MCP tool by importing and executing it directly.

    This is a workaround since FastMCP doesn't expose REST endpoints.
    We import the server module and call the tool functions directly.
    """
    global _tool_mapping

    try:
        # Build tool mapping if not cached
        if _tool_mapping is None:
            _tool_mapping = _build_tool_mapping()

        # Import the server module
        sys.path.insert(0, '/Users/manuel.siuro/www/mcp-android-server-python')
        import server

        # Get the actual function name from mapping
        func_name = _tool_mapping.get(tool_name)
        if not func_name:
            raise ValueError(f"Tool '{tool_name}' not found in mapping. Available tools: {list(_tool_mapping.keys())[:10]}")

        # Get the tool function
        if not hasattr(server, func_name):
            raise ValueError(f"Function '{func_name}' not found in server module")

        tool_func = getattr(server, func_name)

        # Call the tool function with parameters
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**parameters)
        else:
            result = tool_func(**parameters)

        return {
            "success": True,
            "data": result,
            "error": None
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "data": None,
            "error": f"{str(e)}\n{traceback.format_exc()}"
        }


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "MCP Android REST Adapter",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, request: ToolRequest) -> ToolResponse:
    """
    Execute an MCP tool by name with given parameters.

    Args:
        tool_name: Name of the MCP tool to execute
        request: Tool request containing parameters

    Returns:
        ToolResponse with execution result
    """
    try:
        result = await call_mcp_tool(tool_name, request.parameters)
        return ToolResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    try:
        sys.path.insert(0, '/Users/manuel.siuro/www/mcp-android-server-python')
        import server

        # Get all functions decorated with @mcp.tool
        tools = []
        for name in dir(server):
            attr = getattr(server, name)
            if callable(attr) and not name.startswith('_'):
                # Check if it's likely a tool function
                if hasattr(attr, '__doc__'):
                    tools.append({
                        "name": name,
                        "description": attr.__doc__.split('\n')[0] if attr.__doc__ else ""
                    })

        return {"tools": tools}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("🚀 Starting MCP Android REST Adapter on port 8000...")
    print("📡 This adapter bridges the web interface to the MCP server")
    print("🔧 Available at: http://localhost:8000")
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
