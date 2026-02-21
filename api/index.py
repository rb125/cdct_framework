import os
import sys

# Ensure the root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from cdct_mcp_server import mcp

# This is the ASGI application that Vercel will use
# It will handle both the /sse endpoint and provide the MCP interface
app = mcp.sse_app()
