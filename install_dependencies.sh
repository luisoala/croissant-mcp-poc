

echo "Installing dependencies for MCP-compliant SSE server..."
pip install fastapi uvicorn sse-starlette aiohttp

echo "Dependencies installed successfully!"
echo "To run the server, use: python main_mcp_sse.py"
