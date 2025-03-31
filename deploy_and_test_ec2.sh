
set -e

echo "=== Deploying and Testing SSE Fix on EC2 ==="

ssh ubuntu@44.242.230.242 << 'EOF'
  echo "Connected to EC2 instance"
  
  cd croissant-mcp-poc
  
  echo "Pulling latest changes from repository..."
  git pull
  
  chmod +x croissant-mcp-integration/croissant-mcp-deploy.sh
  
  echo "Running deployment script..."
  cd croissant-mcp-integration
  ./croissant-mcp-deploy.sh
  
  echo "Restarting MCP server service..."
  sudo systemctl restart croissant-mcp
  
  sleep 5
  
  echo "Checking service status..."
  sudo systemctl status croissant-mcp
  
  echo "Testing server with curl..."
  curl -H "X-API-Key: croissant-mcp-demo-key" http://localhost:8000/info
  
  echo "Viewing server logs..."
  sudo journalctl -u croissant-mcp -n 50
EOF

echo "=== Deployment and Testing Complete ==="
