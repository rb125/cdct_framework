# CDCT Framework MCP Server

The CDCT Framework is now accessible as a Model Context Protocol (MCP) server, allowing an LLM to directly interact with the diagnostic tools for evaluation.

## Installation

Ensure you have the `mcp` library installed:

```bash
pip install mcp
```

## Running the Server

To start the MCP server using `stdio` transport (default):

```bash
python cdct_mcp_server.py
```

## Features

The MCP server exposes the following tools to an LLM:

1.  `get_model_score`: Retrieves existing results for a model.
2.  `run_experiment`: Starts a diagnostic battery in the background (Local only).
3.  `list_available_models`: Lists models configured for evaluation.
4.  `list_concepts`: Lists all semantic concepts in the framework.
5.  `server_status`: Checks server health and environment.

## Running the Server (Local)

To start the MCP server using `stdio` transport (default):

```bash
python cdct_mcp_server.py
```

## Running the Server (Vercel / SSE)

If you have deployed this to Vercel (e.g., `https://cdct-framework.vercel.app/`), the server uses the **SSE (Server-Sent Events)** transport.

To use the SSE transport with Claude Desktop or other MCP clients:

```json
{
  "mcpServers": {
    "cdct-framework": {
      "url": "https://cdct-framework.vercel.app/sse"
    }
  }
}
```

**Note for Vercel Deployments:**
- Background tasks like `run_experiment` will not persist changes on Vercel due to the read-only/ephemeral file system.
- Ensure all your `results_jury/*.json` files are committed to the repository if you want them accessible on Vercel.
