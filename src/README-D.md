# Croissant MCP Server

A Model Context Protocol (MCP) server for indexing and providing access to Croissant datasets.

## Features

- API key authentication
- Dataset indexing and search
- Support for multiple data sources (Dataverse, HuggingFace, Kaggle, OpenML)
- Dataset preview and statistics
- Dataset validation
- Real-time updates via SSE

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Running the Server

### Local Development
```bash
python main.py
```

### EC2 Deployment
1. SSH into your EC2 instance
2. Clone the repository
3. Run the deployment script:
```bash
chmod +x deploy.sh
./deploy.sh
```
4. The server will be available at `http://your-ec2-ip:8000`

## MCP Configuration

You can configure the MCP server in two ways:

### Project-specific Configuration
Create `.cursor/mcp.json` in your project directory:
```json
{
  "mcpServers": {
    "croissant-mcp": {
      "url": "http://your-ec2-ip:8000/sse",
      "transport": "sse",
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

### Global Configuration
Create `~/.cursor/mcp.json` in your home directory:
```json
{
  "mcpServers": {
    "croissant-mcp": {
      "url": "http://your-ec2-ip:8000/sse",
      "transport": "sse",
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

### Important Notes
- The server must be accessible from your local machine
- Only the first 40 tools will be available to the Agent
- Tool usage requires approval by default (can be enabled in Yolo mode)
- Resources are not yet supported in Cursor
- The SSE endpoint (`/sse`) is used for real-time communication, while `/mcp` handles MCP protocol messages
- API key can be specified in the `env` field (recommended) or directly in the root of the server configuration
- The server will check for the API key in both the `X-API-Key` header and environment variables

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
- `get_dataset_preview(dataset_id: str, rows: int = 5)` - Get dataset preview
- `get_dataset_stats(dataset_id: str)` - Get dataset statistics

### Dataset Operations
- `validate_dataset(dataset_id: str)` - Validate a Croissant file

## Security

### API Key Authentication (Optional)
- API key authentication is optional and can be enabled by setting the `API_KEY` environment variable
- When enabled, all endpoints require API key authentication via the `X-API-Key` header
- To enable API key authentication:
  1. Set the API key in the `.env` file:
     ```
     API_KEY=your-secret-api-key-here
     ```
  2. When configuring the MCP server in Cursor, use the same API key:
     ```json
     {
       "mcpServers": {
         "croissant-mcp": {
           "url": "http://your-ec2-ip:8000/sse",
           "api_key": "your-secret-api-key-here",
           "transport": "sse"
         }
       }
     }
     ```
- In production, it's recommended to:
  - Use a strong, randomly generated API key
  - Never commit the actual API key to version control
  - Enable API key authentication for security

### CORS
- CORS is enabled (configure allowed origins in production)
- Default allows all origins (`*`) for development
- In production, configure specific allowed origins in the server settings

## Development

### Stack
- FastAPI
- MCP SDK
- SSE-Starlette
- Pydantic

### Project Structure
```
src/
├── models/         # Data models
├── tools/          # MCP tools
├── config/         # Configuration
└── server.py       # Main server implementation
```

### Adding New Tools
1. Create a new tool function in `src/tools/`
2. Decorate with `@tool()`
3. Add type hints and docstrings
4. Register in `src/server.py`

## License

MIT
