import os
import sys

# Ensure the root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from cdct_mcp_server import mcp
from fastapi import FastAPI
from starlette.responses import JSONResponse

# Initialize FastAPI
app = FastAPI(title="CDCT MCP Gateway")

# Mount the MCP SSE application
# FastMCP.sse_app() returns a Starlette/FastAPI compatible app
mcp_app = mcp.sse_app()
app.mount("/mcp", mcp_app)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "CDCT MCP Server",
        "endpoints": {
            "mcp_sse": "/mcp/sse",
            "mcp_messages": "/mcp/messages"
        }
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
