import os
import sys
import json
from typing import Any

# Ensure the root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from cdct_mcp_server import mcp
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport

# Initialize FastAPI
app = FastAPI(title="CDCT MCP Gateway")

# Enable CORS for Agent Builders (Elastic/Claude)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize the MCP SSE transport
# We'll manage the lifecycle manually to ensure header compatibility
sse = SseServerTransport("/messages")

@app.get("/sse")
async def handle_sse(request: Request):
    """
    Explicitly handle the SSE connection with the correct Content-Type.
    """
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        # Delegate the stream to the MCP server
        await mcp.server.connect_via_sse(read_stream, write_stream)
        
    # The connect_sse helper handles the StreamingResponse internally, 
    # but we can wrap it if needed for custom headers.
    return Response(status_code=200)

@app.post("/messages")
async def handle_messages(request: Request):
    """
    Handle MCP JSON-RPC messages.
    """
    # Force application/json if the header is missing or malformed
    return await sse.handle_post_message(request.scope, request.receive, request._send)

@app.get("/")
async def health():
    return {
        "status": "online",
        "mcp_endpoints": {
            "sse": "/sse",
            "messages": "/messages"
        }
    }

# Fallback to the FastMCP auto-generated SSE app if the manual one is too restrictive
# But we'll try the manual routing first for better header control.
# app = mcp.sse_app()
