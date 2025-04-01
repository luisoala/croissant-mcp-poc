"""
Fixed MCP SDK Server implementation for Croissant datasets
Uses proper async handling for tools/list endpoint
"""
import os
import sys
import logging
import asyncio

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
        host="127.0.0.1"  # Explicitly bind to localhost
    )
    
    logger.info(f"Starting Croissant MCP Server with MCP SDK")
    logger.info(f"Available at http://localhost:{port}")
    logger.info(f"SSE endpoint: http://localhost:{port}/sse")
    
    mcp_server.run(transport="sse")
