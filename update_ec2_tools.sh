

echo "Updating EC2 server with MCP-compliant tools implementation..."

echo "Stopping any running server..."
sudo pkill -f "python3 main_mcp_sse.py"

echo "Updating code from repository..."
cd ~/croissant-mcp-poc
git pull

echo "Copying latest server files..."
cp -f croissant-mcp-integration/src/server_mcp_sse.py ~/server_mcp_sse.py
cp -f croissant-mcp-integration/main_mcp_sse.py ~/main_mcp_sse.py
cp -f croissant-mcp-integration/test_mcp_tools.py ~/test_mcp_tools.py

echo "Installing dependencies..."
pip install fastapi uvicorn sse-starlette aiohttp

echo "Starting the server..."
cd ~
nohup python3 main_mcp_sse.py > server.log 2>&1 &

echo "Server updated and started!"
echo "You can check the server logs with: tail -f ~/server.log"
