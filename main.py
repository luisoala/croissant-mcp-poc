"""
Main entry point for the Croissant MCP Server
"""
import os
import sys
import uvicorn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from server import asgi_app

if __name__ == "__main__":
    print("Starting Croissant MCP Server...")
    print("Available datasets will be indexed and searchable via MCP")
    print("Server will be available at http://0.0.0.0:8000")
    
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)
