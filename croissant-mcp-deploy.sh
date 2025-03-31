

set -e

echo "=== Croissant MCP Server Deployment ==="
echo "This script will deploy the Croissant MCP Server with API key authentication"
echo "for Cursor IDE integration."
echo ""

echo "Updating system packages..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

echo "Checking repository status..."
if git remote -v 2>/dev/null | grep -q "luisoala/croissant-mcp-poc"; then
  echo "Already in the repository, updating..."
  git pull
else
  echo "Cloning repository..."
  if [ -d "croissant-mcp-poc" ]; then
    echo "Repository directory exists, entering and updating..."
    cd croissant-mcp-poc
    git pull
  else
    git clone https://github.com/luisoala/croissant-mcp-poc.git
    cd croissant-mcp-poc
  fi
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
ExecStart=\$(pwd)/venv/bin/python main_cursor_sse.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

echo "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable croissant-mcp
sudo systemctl restart croissant-mcp

echo "Detecting public IP address..."
PUBLIC_HOSTNAME=""

if [ -z "$PUBLIC_HOSTNAME" ]; then
  PUBLIC_HOSTNAME=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/public-hostname)
fi

if [ -z "$PUBLIC_HOSTNAME" ]; then
  PUBLIC_HOSTNAME=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/public-ipv4)
fi

if [ -z "$PUBLIC_HOSTNAME" ]; then
  PUBLIC_HOSTNAME=$(curl -s --connect-timeout 3 http://checkip.amazonaws.com)
  PUBLIC_HOSTNAME=$(echo "$PUBLIC_HOSTNAME" | tr -d '\n')
fi

if [ -z "$PUBLIC_HOSTNAME" ]; then
  PUBLIC_HOSTNAME=$(curl -s --connect-timeout 3 https://ifconfig.me)
fi

if [ -z "$PUBLIC_HOSTNAME" ]; then
  PUBLIC_HOSTNAME=$(curl -s --connect-timeout 3 https://api.ipify.org)
fi

if [ -z "$PUBLIC_HOSTNAME" ]; then
  echo "Could not automatically detect public IP address."
  echo "Please enter your EC2 instance's public IP address:"
  read -p "> " PUBLIC_HOSTNAME
  
  if [ -z "$PUBLIC_HOSTNAME" ]; then
    echo "No IP address provided. Using 'your-ec2-public-ip' as a placeholder."
    PUBLIC_HOSTNAME="your-ec2-public-ip"
  fi
fi

echo "Using public address: $PUBLIC_HOSTNAME"

echo ""
echo "=== Deployment Complete ==="
echo "Croissant MCP Server deployed successfully!"
echo "Server running at: http://$PUBLIC_HOSTNAME:8000"
echo "SSE endpoint: http://$PUBLIC_HOSTNAME:8000/sse"
echo "API Key: $API_KEY"
echo ""
echo "Add the following to your Cursor MCP configuration (~/.cursor/mcp.json):"
echo '{
  "mcpServers": {
    "croissant-datasets": {
      "url": "http://'"$PUBLIC_HOSTNAME"':8000/sse",
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
echo "Test the SSE endpoint with: curl -H \"Accept: text/event-stream\" -H \"X-API-Key: $API_KEY\" http://$PUBLIC_HOSTNAME:8000/sse"
