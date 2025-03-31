"""
Main entry point for the Croissant MCP Server
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from server import mcp

if __name__ == "__main__":
    print("Starting Croissant MCP Server...")
    print("Available datasets will be indexed and searchable via MCP")
    mcp.run()
