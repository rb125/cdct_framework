import os
import sys

# Ensure the root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from cdct_mcp_server import mcp
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport

# Initialize FastAPI
app = FastAPI()

# Enable CORS for Elastic's web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# We use a persistent transport instance
sse = SseServerTransport("/messages")

@app.get("/sse")
async def handle_sse(request: Request):
    """
    This is the endpoint Elastic will connect to.
    It MUST return text/event-stream.
    """
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await mcp.server.connect_via_sse(read_stream, write_stream)

@app.post("/messages")
async def handle_messages(request: Request):
    """
    This handles the tool calls (POST requests) from Elastic.
    """
    return await sse.handle_post_message(request.scope, request.receive, request._send)

@app.get("/")
async def health():
    return {"status": "ok", "mcp_enabled": True}
