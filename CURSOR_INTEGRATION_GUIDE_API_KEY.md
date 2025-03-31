# Integrating Croissant MCP Server with Cursor IDE

This guide explains how to integrate the Croissant MCP Server with Cursor IDE using API key authentication.

## Overview

The Croissant MCP Server provides a Model Context Protocol (MCP) interface for searching and accessing Croissant datasets from various platforms. By integrating it with Cursor IDE, you can:

1. Search for datasets directly from your IDE
2. Get dataset information and metadata
3. Add dataset context to your LLM-powered coding sessions

## Prerequisites

1. The Croissant MCP Server running locally or on a remote server
2. Cursor IDE installed on your machine

## Configuration Steps

### 1. Start the Croissant MCP Server with API Key Authentication

If running locally:

```bash
cd croissant-mcp-poc/croissant-mcp-integration
python main_api_key.py
```

The server will start on http://0.0.0.0:8000 with MCP endpoints available at http://0.0.0.0:8000/mcp.

By default, the server uses the API key `croissant-mcp-demo-key`. You can set a custom API key by setting the `MCP_API_KEY` environment variable:

```bash
MCP_API_KEY=your-custom-api-key python main_api_key.py
```

### 2. Configure Cursor to Use the MCP Server with API Key Authentication

Create or edit the MCP configuration file in one of these locations:

- **Project-specific**: `.cursor/mcp.json` in your project directory
- **Global**: `~/.cursor/mcp.json` in your home directory

Add the following configuration for a local server:

```json
{
  "mcpServers": {
    "croissant-datasets": {
      "url": "http://localhost:8000/mcp",
      "env": {
        "API_KEY": "croissant-mcp-demo-key"
      }
    }
  }
}
```

If you're running the server on a remote machine (like AWS), replace `localhost` with the appropriate IP address or domain name:

```json
{
  "mcpServers": {
    "croissant-datasets": {
      "url": "http://your-server-address:8000/mcp",
      "env": {
        "API_KEY": "croissant-mcp-demo-key"
      }
    }
  }
}
```

Make sure to replace `croissant-mcp-demo-key` with your actual API key if you've set a custom one.

### 3. Restart Cursor

Restart Cursor to apply the new MCP configuration.

## Using Croissant Dataset Tools in Cursor

Once configured, you can use the following tools in Cursor:

### Basic Dataset Search

Ask Cursor to search for datasets:

- "Search for image datasets"
- "Find datasets about machine learning"
- "Look for datasets from Kaggle"

### Advanced Dataset Search

Request specific filters:

- "Find CSV datasets from Kaggle"
- "Search for datasets with Apache license"
- "Show me datasets about natural language processing with pagination"

### Get Dataset Details

Ask for information about a specific dataset:

- "Tell me about the MNIST dataset"
- "Show details for the CroissantLLM dataset"
- "What's the license for the Titanic dataset?"

## Available Tools

The Croissant MCP Server provides the following tools to Cursor:

| Tool | Description |
|------|-------------|
| `search_datasets` | Basic search for datasets matching a query |
| `advanced_search` | Advanced search with filtering, sorting, and pagination |
| `get_search_options` | Get available options for search filters |
| `add_dataset` | Add a new dataset to the index |

## Example Datasets

The server comes pre-loaded with example datasets from:

- Hugging Face: CroissantLLM bilingual dataset
- Kaggle: MNIST handwritten digits
- OpenML: Iris dataset
- Dataverse: Titanic passengers dataset
- MLCommons: PASS image dataset

## Limitations

- Cursor only sends the first 40 tools to the Agent, so if you have many tools, some may not be available
- For remote servers, ensure the server is accessible from your machine

## Troubleshooting

If you encounter issues:

1. Verify the server is running and accessible at http://localhost:8000/mcp or your remote URL
2. Check that your mcp.json configuration is correctly formatted with the proper API key in the `env` field
3. Ensure the server URL in the configuration matches where your server is running
4. Restart Cursor after making configuration changes
5. Check server logs for any errors

### Common Issues

- **403 Forbidden**: This usually means your API key is incorrect. Check that the API key in your mcp.json matches the one used by the server.
- **Connection Refused**: Make sure the server is running and the port is accessible.
- **Tools Not Showing Up**: Remember that Cursor only sends the first 40 tools to the Agent.

## Advanced: Customizing the MCP Server

You can customize the MCP server by:

1. Adding more datasets to the index
2. Creating additional search tools
3. Implementing custom resources for specific dataset types
4. Extending the server with additional functionality

See the project documentation for more details on customization options.
