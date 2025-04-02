#!/bin/bash

# Exit on error and undefined variables
set -euo pipefail

# Enable debug mode if requested
if [[ "${DEBUG:-false}" == "true" ]]; then
    set -x
fi

# Configuration
EC2_HOST="${EC2_HOST:-your-ec2-host}"
EC2_USER="${EC2_USER:-ubuntu}"
APP_DIR="/home/ubuntu/croissant-mcp"
PORT="${PORT:-8000}"
MCP_API_KEY="${MCP_API_KEY:-}"
GITHUB_REPO="${GITHUB_REPO:-your-org/croissant-mcp-poc}"
GITHUB_BRANCH="${GITHUB_BRANCH:-clean-implementation}"

# Check required environment variables
if [[ -z "$EC2_HOST" || "$EC2_HOST" == "your-ec2-host" ]]; then
    echo "Error: EC2_HOST not set"
    exit 1
fi

if [[ -z "$MCP_API_KEY" ]]; then
    echo "Warning: MCP_API_KEY not set, using default demo key"
fi

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
handle_error() {
    log "Error on line $1"
    exit 1
}

trap 'handle_error $LINENO' ERR

log "Starting deployment to $EC2_HOST..."

# Create app directory and clone repo on EC2
log "Setting up application directory and cloning repository..."
ssh ${EC2_USER}@${EC2_HOST} "mkdir -p ${APP_DIR} && \
    cd ${APP_DIR} && \
    git clone -b ${GITHUB_BRANCH} https://github.com/${GITHUB_REPO}.git . || \
    (git fetch origin && git checkout ${GITHUB_BRANCH})"

# Install dependencies and start server
log "Setting up Python environment and starting server..."
ssh ${EC2_USER}@${EC2_HOST} "cd ${APP_DIR} && \
    python3 -m venv venv && \
    source venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    sudo systemctl stop croissant-mcp || true && \
    sudo tee /etc/systemd/system/croissant-mcp.service << EOF
[Unit]
Description=Croissant MCP Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=${APP_DIR}
Environment=\"PATH=${APP_DIR}/venv/bin\"
Environment=\"PORT=${PORT}\"
Environment=\"MCP_API_KEY=${MCP_API_KEY}\"
ExecStart=${APP_DIR}/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT}
Restart=always
RestartSec=5
StartLimitInterval=60s
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload && \
    sudo systemctl enable croissant-mcp && \
    sudo systemctl start croissant-mcp"

# Configure nginx with SSL
log "Configuring Nginx..."
ssh ${EC2_USER}@${EC2_HOST} "sudo tee /etc/nginx/sites-available/croissant-mcp << EOF
server {
    listen 80;
    server_name _;

    # Redirect HTTP to HTTPS
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;

    location / {
        proxy_pass http://localhost:${PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Deny access to . files
    location ~ /\. {
        deny all;
    }
}
EOF

    # Generate self-signed certificate if not exists
    if [[ ! -f /etc/ssl/certs/nginx-selfsigned.crt ]]; then
        sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/ssl/private/nginx-selfsigned.key \
            -out /etc/ssl/certs/nginx-selfsigned.crt \
            -subj \"/CN=\${EC2_HOST}\"
    fi

    sudo ln -sf /etc/nginx/sites-available/croissant-mcp /etc/nginx/sites-enabled/ && \
    sudo rm -f /etc/nginx/sites-enabled/default && \
    sudo nginx -t && \
    sudo systemctl restart nginx"

log "Deployment complete!"
log "Server should be running at https://${EC2_HOST}"
log "Note: Using self-signed SSL certificate. Replace with valid certificate in production." 