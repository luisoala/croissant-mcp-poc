#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="croissant-mcp"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="$APP_NAME"
NGINX_CONFIG="/etc/nginx/sites-available/$APP_NAME"

# Function to check if server is running
check_server_running() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        return 0
    else
        return 1
    fi
}

# Function to stop the server
stop_server() {
    echo "Stopping $SERVICE_NAME service..."
    sudo systemctl stop $SERVICE_NAME
    echo "Service stopped successfully"
}

# Function to start the server
start_server() {
    echo "Starting $SERVICE_NAME service..."
    sudo systemctl start $SERVICE_NAME
    echo "Service started successfully"
}

# Function to restart the server
restart_server() {
    echo "Restarting $SERVICE_NAME service..."
    sudo systemctl restart $SERVICE_NAME
    echo "Service restarted successfully"
}

# Function to check server status
check_status() {
    echo "Checking $SERVICE_NAME service status..."
    sudo systemctl status $SERVICE_NAME
}

# Function to show usage
show_usage() {
    echo "Usage: $0 {start|stop|restart|status|deploy}"
    echo "  start   - Start the server"
    echo "  stop    - Stop the server"
    echo "  restart - Restart the server"
    echo "  status  - Check server status"
    echo "  deploy  - Deploy the server"
    exit 1
}

# Main deployment function
deploy_server() {
    # Create application directory
    sudo mkdir -p $APP_DIR
    sudo chown -R $USER:$USER $APP_DIR

    # Copy application files
    cp -r ./* $APP_DIR/

    # Create and activate virtual environment
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate

    # Install git if not present
    if ! command -v git &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y git
    fi

    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt

    # Create systemd service file
    sudo tee /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Croissant MCP Server
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/uvicorn src.server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Create Nginx configuration
    sudo tee $NGINX_CONFIG << EOF
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
    }
}
EOF

    # Enable Nginx site
    sudo ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx

    # Enable and start the service
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    sudo systemctl restart $SERVICE_NAME

    # Check service status
    sudo systemctl status $SERVICE_NAME

    echo "Deployment complete! The server should be running on http://localhost:8000"
}

# Handle command line arguments
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        check_status
        ;;
    deploy)
        deploy_server
        ;;
    *)
        show_usage
        ;;
esac

exit 0 