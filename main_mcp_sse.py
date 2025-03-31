"""
Main entry point for the Croissant MCP Server with MCP-compliant SSE endpoint
"""
import os
import sys
import uvicorn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from server_mcp_sse import app

if __name__ == "__main__":
    api_key = os.environ.get("MCP_API_KEY", "croissant-mcp-demo-key")
    port = 8001  # Using port 8001 to avoid conflicts
    
    print("Starting Croissant MCP Server with MCP-compliant SSE endpoint...")
    print(f"Available at http://localhost:{port}")
    print(f"SSE endpoint (no authentication required): http://localhost:{port}/sse")
    print(f"API Key authentication is enabled for other endpoints (API key: {api_key})")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
