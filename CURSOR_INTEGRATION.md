# Integrating Croissant MCP Server with Cursor

This guide explains how to integrate the Croissant MCP Server with Cursor to enable dataset search and context capabilities in your IDE.

## Prerequisites

1. The Croissant MCP Server running locally or on a remote server
2. Cursor IDE installed on your machine

## Configuration Steps

### 1. Start the Croissant MCP Server

Run the server using:

```bash
python main.py
```

The server will start on http://0.0.0.0:8000 with MCP endpoints available at http://0.0.0.0:8000/mcp.

### 2. Configure Cursor to Use the MCP Server

Create or edit the MCP configuration file in one of these locations:

- **Project-specific**: `.cursor/mcp.json` in your project directory
- **Global**: `~/.cursor/mcp.json` in your home directory

Add the following configuration:

```json
{
  "mcpServers": {
    "croissant-datasets": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

If you're running the server on a remote machine, replace `localhost` with the appropriate IP address or domain name.

### 3. Restart Cursor

Restart Cursor to apply the new MCP configuration.

## Using Croissant Dataset Tools in Cursor

Once configured, you can use the following tools in Cursor:

1. **Basic Dataset Search**:
   - Ask Cursor to "search for image datasets" or "find datasets about machine learning"

2. **Advanced Dataset Search**:
   - Request specific filters like "find CSV datasets from Kaggle" or "search for datasets with Apache license"

3. **Get Dataset Details**:
   - Ask for information about a specific dataset by name

## Available Tools

The Croissant MCP Server provides the following tools to Cursor:

- `search_datasets`: Basic search for datasets matching a query
- `advanced_search`: Advanced search with filtering, sorting, and pagination
- `get_search_options`: Get available options for search filters
- `add_dataset`: Add a new dataset to the index

## Limitations

- Cursor only sends the first 40 tools to the Agent, so if you have many tools, some may not be available
- For remote servers, ensure the server is accessible from your machine

## Troubleshooting

If you encounter issues:

1. Verify the server is running and accessible at http://localhost:8000/mcp
2. Check that your mcp.json configuration is correctly formatted
3. Ensure the server URL in the configuration matches where your server is running
4. Restart Cursor after making configuration changes
