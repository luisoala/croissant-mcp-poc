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
    echo "Usage: $0 {start|stop|restart|status|deploy|cleanup}"
    echo "  start   - Start the server"
    echo "  stop    - Stop the server"
    echo "  restart - Restart the server"
    echo "  status  - Check server status"
    echo "  deploy  - Deploy the server"
    echo "  cleanup - Remove all installed files and configurations"
    exit 1
}

# Function to cleanup all installed files and configurations
cleanup_server() {
    echo "Starting cleanup..."
    
    # Stop the service if running
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "Stopping service..."
        sudo systemctl stop $SERVICE_NAME
    fi
    
    # Disable and remove systemd service
    echo "Removing systemd service..."
    sudo systemctl disable $SERVICE_NAME
    sudo rm -f /etc/systemd/system/$SERVICE_NAME.service
    sudo systemctl daemon-reload
    
    # Remove Nginx configuration
    echo "Removing Nginx configuration..."
    sudo rm -f /etc/nginx/sites-enabled/$APP_NAME
    sudo rm -f /etc/nginx/sites-available/$APP_NAME
    
    # Remove SSL certificates
    echo "Removing SSL certificates..."
    sudo rm -f /etc/nginx/ssl/croissant-mcp.crt
    sudo rm -f /etc/nginx/ssl/croissant-mcp.key
    
    # Remove application directory
    echo "Removing application directory..."
    sudo rm -rf $APP_DIR
    
    # Remove log files
    echo "Removing log files..."
    sudo rm -f /var/log/croissant-mcp.log
    sudo rm -f /var/log/croissant-mcp.error.log
    
    # Reload Nginx
    echo "Reloading Nginx..."
    sudo systemctl reload nginx
    
    echo "Cleanup complete!"
}

# Main deployment function
deploy_server() {
    echo "Starting deployment..."

    # Create application directory
    sudo mkdir -p $APP_DIR
    sudo chown -R $USER:$USER $APP_DIR

    # Copy application files
    echo "Copying application files..."
    cp -r ./* $APP_DIR/

    # Create and activate virtual environment
    echo "Setting up virtual environment..."
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate

    # Install git if not present
    if ! command -v git &> /dev/null; then
        echo "Installing git..."
        sudo apt-get update
        sudo apt-get install -y git
    fi

    # Install nginx if not present
    if ! command -v nginx &> /dev/null; then
        echo "Installing nginx..."
        sudo apt-get update
        sudo apt-get install -y nginx
    fi

    # Install dependencies
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install wheel setuptools
    pip install -r requirements.txt

    # Verify installation
    echo "Verifying installation..."
    if ! python3 -c "import mcp" &> /dev/null; then
        echo "Error: mcp package not found after installation"
        echo "Attempting to install directly from git..."
        pip install git+https://github.com/modelcontextprotocol/python-sdk.git
    fi

    # Create systemd service file
    echo "Creating systemd service..."
    sudo tee /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Croissant MCP Server
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="PYTHONPATH=$APP_DIR"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/bin/bash -c 'source $VENV_DIR/bin/activate && $VENV_DIR/bin/uvicorn src.server:app --host 0.0.0.0 --port 8000 --log-level debug'
Restart=on-failure
RestartSec=5
StandardOutput=append:/var/log/croissant-mcp.log
StandardError=append:/var/log/croissant-mcp.error.log

[Install]
WantedBy=multi-user.target
EOF

    # Create log files with proper permissions
    sudo touch /var/log/croissant-mcp.log /var/log/croissant-mcp.error.log
    sudo chown $USER:$USER /var/log/croissant-mcp.log /var/log/croissant-mcp.error.log

    # Create Nginx configuration directory if it doesn't exist
    echo "Setting up Nginx configuration..."
    sudo mkdir -p /etc/nginx/sites-available
    sudo mkdir -p /etc/nginx/sites-enabled

    # Create Nginx configuration
    sudo tee $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name _;

    # Redirect all HTTP traffic to HTTPS
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    # SSL configuration
    ssl_certificate /etc/nginx/ssl/croissant-mcp.crt;
    ssl_certificate_key /etc/nginx/ssl/croissant-mcp.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings for SSE
        proxy_read_timeout 300;
        proxy_send_timeout 300;
        proxy_connect_timeout 300;
    }
}
EOF

    # Create SSL directory and generate self-signed certificate
    echo "Setting up SSL..."
    sudo mkdir -p /etc/nginx/ssl
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/croissant-mcp.key \
        -out /etc/nginx/ssl/croissant-mcp.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    sudo chmod 600 /etc/nginx/ssl/croissant-mcp.key
    sudo chmod 644 /etc/nginx/ssl/croissant-mcp.crt

    # Enable Nginx site and remove default site
    echo "Configuring Nginx..."
    sudo ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default

    # Test Nginx configuration
    echo "Testing Nginx configuration..."
    sudo nginx -t

    # Reload Nginx
    echo "Reloading Nginx..."
    sudo systemctl reload nginx

    # Reload systemd and start service
    echo "Starting service..."
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    sudo systemctl restart $SERVICE_NAME

    # Check service status and logs
    echo "Checking service status..."
    sudo systemctl status $SERVICE_NAME
    
    echo "Checking service logs..."
    sudo journalctl -u $SERVICE_NAME -n 50

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
    cleanup)
        cleanup_server
        ;;
    *)
        show_usage
        ;;
esac

exit 0 