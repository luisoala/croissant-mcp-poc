

set -e

echo "=== Croissant MCP Server Deployment ==="
echo "This script will deploy the Croissant MCP Server with API key authentication"
echo "for Cursor IDE integration."
echo ""

echo "Updating system packages..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

echo "Cloning repository..."
if [ -d "croissant-mcp-poc" ]; then
  echo "Repository already exists, updating..."
  cd croissant-mcp-poc
  git pull
else
  git clone https://github.com/luisoala/croissant-mcp-poc.git
  cd croissant-mcp-poc
fi


echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
else
  pip install fastapi uvicorn pydantic sse-starlette
fi

echo "Configuring API key..."
API_KEY=${1:-"croissant-mcp-demo-key"}
echo "MCP_API_KEY=$API_KEY" > .env
chmod 600 .env

echo "Creating systemd service..."
sudo bash -c "cat > /etc/systemd/system/croissant-mcp.service << EOF
[Unit]
Description=Croissant MCP Server
After=network.target

[Service]
User=\$(whoami)
WorkingDirectory=\$(pwd)
EnvironmentFile=\$(pwd)/.env
ExecStart=\$(pwd)/venv/bin/python main_cursor_simple.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

echo "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable croissant-mcp
sudo systemctl restart croissant-mcp

PUBLIC_HOSTNAME=$(curl -s http://169.254.169.254/latest/meta-data/public-hostname)
if [ -z "$PUBLIC_HOSTNAME" ]; then
  PUBLIC_HOSTNAME=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
fi

echo ""
echo "=== Deployment Complete ==="
echo "Croissant MCP Server deployed successfully!"
echo "Server running at: http://$PUBLIC_HOSTNAME:8000"
echo "MCP endpoint: http://$PUBLIC_HOSTNAME:8000/mcp"
echo "API Key: $API_KEY"
echo ""
echo "Add the following to your Cursor MCP configuration (~/.cursor/mcp.json):"
echo '{
  "mcpServers": {
    "croissant-datasets": {
      "url": "http://'"$PUBLIC_HOSTNAME"':8000/mcp",
      "env": {
        "API_KEY": "'"$API_KEY"'"
      }
    }
  }
}'

echo ""
echo "To check server status: sudo systemctl status croissant-mcp"
echo "To view logs: sudo journalctl -u croissant-mcp -f"
echo ""
echo "Test the server with: curl -H \"X-API-Key: $API_KEY\" http://$PUBLIC_HOSTNAME:8000/info"
