"""
Main entry point for the Croissant MCP Server with API key authentication
"""
import os
import sys
import uvicorn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from server_api_key import app

if __name__ == "__main__":
    api_key = os.environ.get("MCP_API_KEY", "croissant-mcp-demo-key")
    
    print("Starting Croissant MCP Server with API key authentication...")
    print("Available datasets will be indexed and searchable via MCP")
    print("Server will be available at http://0.0.0.0:8000")
    print("Access MCP endpoints at http://0.0.0.0:8000/mcp")
    print(f"API Key authentication is enabled (API key: {api_key})")
    print("Set MCP_API_KEY environment variable to change the API key")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
