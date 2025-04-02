#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="croissant-mcp"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="$APP_NAME.service"
NGINX_CONF="$APP_NAME.conf"

# Create application directory
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Copy application files
cp -r ./* $APP_DIR/

# Create and activate virtual environment
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install dependencies
pip install -r $APP_DIR/requirements.txt

# Create systemd service file
cat << EOF | sudo tee /etc/systemd/system/$SERVICE_NAME
[Unit]
Description=Croissant MCP Server
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
cat << EOF | sudo tee /etc/nginx/sites-available/$NGINX_CONF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/$NGINX_CONF /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME
sudo systemctl restart nginx

# Check service status
sudo systemctl status $SERVICE_NAME

echo "Deployment complete! The server should be running on port 8000."
echo "You can check the logs with: sudo journalctl -u $SERVICE_NAME -f" 