# Croissant MCP Server POC

A Model Context Protocol (MCP) server POC for indexing and providing access to Croissant datasets.

## Interact w MCP server at your MCP client (e.g. Cursor)

Copy paste following (dont worry about "your-api-key", just copy paste as you see below) into the mcp.jsonof your MCP client:

```json
{
  "mcpServers": {
    "croissant-mcp": {
      "url": "http://54.188.239.243:8000/sse",
      "transport": "sse",
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```
## Available Endpoints

- `/health` - Health check endpoint
- `/mcp` - MCP endpoints
- `/events` - SSE events for real-time updates
- `/docs` - API documentation

## Available Tools

### Dataset Discovery
- `list_datasets()` - List all available datasets
- `search_datasets(query: str)` - Search datasets by name, description, or tags
- `list_sources()` - List all data sources
- `get_source_datasets(source: str)` - Get datasets from a specific source

### Data Access
- `get_dataset_metadata(dataset_id: str)` - Get detailed metadata

### Adding New Tools
1. Create a new tool function in `src/tools/`
2. Decorate with `@tool()`
3. Add type hints and docstrings
4. Register in `src/server.py`
