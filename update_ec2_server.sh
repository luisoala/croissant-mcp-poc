set -e

echo "=== Updating EC2 Server with Cursor-compatible SSE Endpoint ==="

EC2_IP="44.242.230.242"

ssh ubuntu@$EC2_IP << 'EOF'
  echo "Connected to EC2 instance"
  
  cd croissant-mcp-poc
  
  echo "Pulling latest changes from repository..."
  git pull
  
  echo "Updating systemd service to use the new SSE endpoint server..."
  sudo sed -i 's/main_cursor_fixed_v2.py/main_cursor_sse.py/g' /etc/systemd/system/croissant-mcp.service
  
  echo "Reloading systemd daemon..."
  sudo systemctl daemon-reload
  
  echo "Restarting MCP server service..."
  sudo systemctl restart croissant-mcp
  
  echo "Waiting for server to start..."
  sleep 5
  
  echo "Checking service status..."
  sudo systemctl status croissant-mcp
  
  echo "Testing server with curl..."
  curl -H "X-API-Key: croissant-mcp-demo-key" http://localhost:8000/info
  
  echo "Testing SSE endpoint with curl..."
  curl -H "Accept: text/event-stream" -H "X-API-Key: croissant-mcp-demo-key" http://localhost:8000/mcp -v
  
  echo "Viewing server logs..."
  sudo journalctl -u croissant-mcp -n 50
EOF

echo "=== EC2 Server Update Complete ==="
echo "The server is now running with the Cursor-compatible SSE endpoint"
echo "Cursor should be configured to use: http://$EC2_IP:8000/mcp"
echo "with API_KEY: croissant-mcp-demo-key"

cat > mcp_cursor_ec2.json << EOF
{
  "mcpServers": {
    "croissant-datasets": {
      "url": "http://$EC2_IP:8000/mcp",
      "env": {
        "API_KEY": "croissant-mcp-demo-key"
      }
    }
  }
}
EOF

echo "Cursor MCP configuration saved to mcp_cursor_ec2.json"
echo "To use this configuration in Cursor:"
echo "1. Copy this file to ~/.cursor/mcp.json"
echo "2. Restart Cursor"
echo "3. Cursor should connect to the MCP server at http://$EC2_IP:8000/mcp"
