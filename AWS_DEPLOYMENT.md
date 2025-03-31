# Deploying Croissant MCP Server on AWS

This guide explains how to deploy the Croissant MCP Server on an AWS EC2 instance for remote access from Cursor IDE.

## Prerequisites

1. An AWS account with permissions to create EC2 instances
2. Basic knowledge of AWS EC2 and security groups
3. SSH access to your AWS instance

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

## Step 5: Run the Server

```bash
# Start the server
python main.py
```

The server will start on port 8000. You can access it at:
- http://your-ec2-public-dns:8000/
- http://your-ec2-public-dns:8000/mcp (MCP endpoint)

## Step 6: Configure for Production (Optional)

For a production deployment, you should:

1. Set up a systemd service to run the server as a background service
2. Configure a reverse proxy with Nginx or Apache
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
ExecStart=/home/ubuntu/croissant-mcp-poc/croissant-mcp-integration/venv/bin/python main.py
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

## Step 7: Configure Cursor to Use the Remote MCP Server

In Cursor, create or edit the MCP configuration file:

- **Project-specific**: `.cursor/mcp.json` in your project directory
- **Global**: `~/.cursor/mcp.json` in your home directory

Add the following configuration:

```json
{
  "mcpServers": {
    "croissant-datasets": {
      "url": "http://your-ec2-public-dns:8000/mcp"
    }
  }
}
```

Replace `your-ec2-public-dns` with your actual EC2 instance's public DNS or IP address.

## Troubleshooting

1. **Cannot connect to the server**:
   - Check that your security group allows traffic on port 8000
   - Verify the server is running with `ps aux | grep python`

2. **Server crashes**:
   - Check the logs with `journalctl -u croissant-mcp` if using systemd
   - Verify all dependencies are installed correctly

3. **Cursor cannot connect to the MCP server**:
   - Ensure the URL in your mcp.json is correct
   - Check that your EC2 instance is publicly accessible
   - Verify the server is running and the MCP endpoint is available
