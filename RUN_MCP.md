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
2.  `run_experiment`: Starts a diagnostic battery in the background.
3.  `list_available_models`: Lists models configured for evaluation.
4.  `list_concepts`: Lists all semantic concepts in the framework.

## Integration with Claude Desktop

To use this with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cdct-framework": {
      "command": "python",
      "args": ["/path/to/cdct_framework/cdct_mcp_server.py"]
    }
  }
}
```

Replace `/path/to/cdct_framework/` with the actual absolute path to your project directory.
