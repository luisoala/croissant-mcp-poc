# Deploying Croissant MCP Server on AWS EC2 with Cursor Integration

This guide explains how to deploy the Croissant MCP Server on an AWS EC2 instance with API key authentication for Cursor IDE integration.

## Prerequisites

1. An AWS account with permissions to create EC2 instances
2. Basic knowledge of AWS EC2 and security groups
3. SSH access to your AWS instance
4. Cursor IDE installed on your machine

## Step 1: Launch an EC2 Instance

1. Log in to the AWS Management Console
2. Navigate to EC2 service
3. Click "Launch Instance"
4. Choose an Ubuntu Server (20.04 LTS or newer)
5. Select an instance type (t2.micro is sufficient for testing)
6. Configure instance details as needed
7. Add storage (default 8GB is sufficient)
8. Configure security group:
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 80) from anywhere
   - Allow HTTPS (port 443) from anywhere
   - Allow custom TCP (port 8000) from anywhere
9. Review and launch the instance
10. Create or select an existing key pair for SSH access

## Step 2: Connect to Your EC2 Instance

```bash
ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-dns
```

## Step 3: Install Dependencies

```bash
# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install git
sudo apt install -y git
```

## Step 4: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/luisoala/croissant-mcp-poc.git
cd croissant-mcp-poc/croissant-mcp-integration

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 5: Configure API Key Authentication

Create a configuration file for the API key:

```bash
# Create a .env file for API key configuration
echo "MCP_API_KEY=croissant-mcp-demo-key" > .env

# Make sure the file is readable only by the owner
chmod 600 .env
```

You can change the API key to a more secure value if needed.

## Step 6: Run the Server with API Key Authentication

```bash
# Start the server with API key authentication
source .env && python main_cursor_simple.py
```

The server will start on port 8000 with API key authentication enabled. You can access it at:
- http://your-ec2-public-dns:8000/ (Server info)
- http://your-ec2-public-dns:8000/mcp (MCP endpoint)

## Step 7: Configure for Production

For a production deployment, you should:

1. Set up a systemd service to run the server as a background service
2. Configure a reverse proxy with Nginx for HTTPS
3. Set up SSL/TLS with Let's Encrypt

### Example systemd Service

Create a file at `/etc/systemd/system/croissant-mcp.service`:

```ini
[Unit]
Description=Croissant MCP Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/croissant-mcp-poc/croissant-mcp-integration
EnvironmentFile=/home/ubuntu/croissant-mcp-poc/croissant-mcp-integration/.env
ExecStart=/home/ubuntu/croissant-mcp-poc/croissant-mcp-integration/venv/bin/python main_cursor_simple.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable croissant-mcp
sudo systemctl start croissant-mcp
```

### Setting up Nginx as a Reverse Proxy (Optional but Recommended)

Install Nginx:

```bash
sudo apt install -y nginx
```

Create a Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/croissant-mcp
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-ec2-public-dns;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /mcp {
        proxy_pass http://localhost:8000/mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # For SSE connections
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/croissant-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Setting up SSL/TLS with Let's Encrypt (Optional but Recommended)

Install Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

Obtain and install a certificate:

```bash
sudo certbot --nginx -d your-ec2-public-dns
```

Follow the prompts to complete the setup.

## Step 8: Configure Cursor to Use the Remote MCP Server with API Key

In Cursor, create or edit the MCP configuration file:

- **Project-specific**: `.cursor/mcp.json` in your project directory
- **Global**: `~/.cursor/mcp.json` in your home directory

Add the following configuration:

```json
{
  "mcpServers": {
    "croissant-datasets": {
      "url": "http://your-ec2-public-dns/mcp",
      "env": {
        "API_KEY": "croissant-mcp-demo-key"
      }
    }
  }
}
```

If you've set up HTTPS with Let's Encrypt, use `https://` instead of `http://`.

Replace:
- `your-ec2-public-dns` with your actual EC2 instance's public DNS or IP address
- `croissant-mcp-demo-key` with the API key you configured in the `.env` file

## Step 9: Test the Integration

1. Restart Cursor to apply the new MCP configuration
2. In Cursor, try using the Croissant dataset tools:
   - "Search for image datasets"
   - "Find datasets about machine learning"
   - "Look for datasets from Kaggle"

## Deployment Script

For convenience, here's a deployment script you can use to set up the server on your EC2 instance:

```bash
#!/bin/bash
# croissant-mcp-deploy.sh

# Update system
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# Clone repository
git clone https://github.com/luisoala/croissant-mcp-poc.git
cd croissant-mcp-poc/croissant-mcp-integration

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "MCP_API_KEY=croissant-mcp-demo-key" > .env
chmod 600 .env

# Create systemd service
sudo bash -c 'cat > /etc/systemd/system/croissant-mcp.service << EOF
[Unit]
Description=Croissant MCP Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/croissant-mcp-poc/croissant-mcp-integration
EnvironmentFile=/home/ubuntu/croissant-mcp-poc/croissant-mcp-integration/.env
ExecStart=/home/ubuntu/croissant-mcp-poc/croissant-mcp-integration/venv/bin/python main_cursor_simple.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF'

# Enable and start service
sudo systemctl enable croissant-mcp
sudo systemctl start croissant-mcp

# Print status
echo "Croissant MCP Server deployed successfully!"
echo "Server running at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-hostname):8000"
echo "MCP endpoint: http://$(curl -s http://169.254.169.254/latest/meta-data/public-hostname):8000/mcp"
echo "API Key: croissant-mcp-demo-key"
echo ""
echo "Add the following to your Cursor MCP configuration:"
echo '{
  "mcpServers": {
    "croissant-datasets": {
      "url": "http://'"$(curl -s http://169.254.169.254/latest/meta-data/public-hostname)"':8000/mcp",
      "env": {
        "API_KEY": "croissant-mcp-demo-key"
      }
    }
  }
}'
```

Save this script as `croissant-mcp-deploy.sh` on your EC2 instance, make it executable with `chmod +x croissant-mcp-deploy.sh`, and run it with `./croissant-mcp-deploy.sh`.

## Troubleshooting

1. **Cannot connect to the server**:
   - Check that your security group allows traffic on port 8000
   - Verify the server is running with `ps aux | grep python`
   - Check systemd logs with `journalctl -u croissant-mcp`

2. **API Key Authentication Issues**:
   - Verify the API key in your Cursor configuration matches the one in the `.env` file
   - Check server logs for authentication errors
   - Test the API key with curl: `curl -H "X-API-Key: croissant-mcp-demo-key" http://your-ec2-public-dns:8000/info`

3. **Cursor cannot connect to the MCP server**:
   - Ensure the URL in your mcp.json is correct and doesn't include credentials in the URL
   - Check that your EC2 instance is publicly accessible
   - Verify the server is running and the MCP endpoint is available
   - Check for SSE connection errors in Cursor

4. **SSE Connection Issues**:
   - If using Nginx, ensure the proxy settings for SSE connections are correct
   - Check for CORS issues in the server logs
   - Verify the server is properly handling SSE connections

## Security Considerations

1. **API Key Security**:
   - Use a strong, unique API key
   - Consider implementing API key rotation
   - Store the API key securely

2. **Network Security**:
   - Restrict SSH access to your IP address only
   - Consider using a VPC and private subnets
   - Use HTTPS for all connections

3. **Server Hardening**:
   - Keep the system updated
   - Use a firewall to restrict access
   - Consider using AWS Security Groups to limit access
