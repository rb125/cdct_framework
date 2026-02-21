import os
import sys

# Ensure the root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from cdct_mcp_server import mcp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize the MCP SSE application directly as the Vercel app
# This is the most robust way to avoid "Invalid Host header" errors on Vercel
app = mcp.sse_app()

# Add CORS support (some MCP clients are web-based)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# No need for AllowedHostsMiddleware here as the root app on Vercel
# handles the Host header implicitly.
