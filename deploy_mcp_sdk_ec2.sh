
echo "Stopping any running MCP server..."
pkill -f "python main_fastmcp" || true

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting MCP SDK server on all interfaces..."
nohup python main_fastmcp_all_interfaces.py > server_sdk.log 2>&1 &

echo "Waiting for server to start..."
sleep 5

if pgrep -f "python main_fastmcp_all_interfaces.py" > /dev/null; then
    echo "Server started successfully!"
    echo "Server is running at http://0.0.0.0:8000"
    echo "SSE endpoint: http://0.0.0.0:8000/sse"
    echo "To view logs: tail -f server_sdk.log"
    
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    if [ ! -z "$PUBLIC_IP" ]; then
        echo "Public URL: http://$PUBLIC_IP:8000"
        echo "Public SSE endpoint: http://$PUBLIC_IP:8000/sse"
        
        echo "Creating EC2 Cursor configuration..."
        cat > mcp_cursor_ec2_sdk.json << EOF
{
  "servers": [
    {
      "name": "croissant-datasets-ec2",
      "url": "http://$PUBLIC_IP:8000/sse",
      "auth": {
        "type": "none"
      },
      "enabled": true
    }
  ]
}
EOF
        echo "Created mcp_cursor_ec2_sdk.json with EC2 public IP"
    else
        echo "Could not determine public IP address"
    fi
else
    echo "Failed to start server. Check server_sdk.log for details."
    exit 1
fi
