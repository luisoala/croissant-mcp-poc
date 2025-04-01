"""
Main entry point for the Croissant MCP Server using the FastMCP server
Configured to bind to all interfaces (0.0.0.0) for external access
"""
import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_server import server
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("croissant-mcp-server")

if __name__ == "__main__":
    port = 8000
    
    mcp_server = FastMCP(
        server_name="Croissant MCP Server",
        server_version="0.1.0",
        server=server,
        port=port,
        host="0.0.0.0"  # Explicitly bind to all interfaces
    )
    
    logger.info(f"Starting Croissant MCP Server at http://0.0.0.0:{port}")
    logger.info(f"MCP SSE endpoint: http://0.0.0.0:{port}/sse")
    
    mcp_server.run(transport="sse")
