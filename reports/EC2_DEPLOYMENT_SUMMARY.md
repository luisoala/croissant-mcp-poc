# Croissant MCP Server EC2 Deployment Summary

This guide provides a concise summary of steps to deploy the Croissant MCP Server on your EC2 instance with API key authentication for Cursor integration.

## Quick Deployment Steps

1. **SSH into your EC2 instance**:
   ```bash
   ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-dns
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/luisoala/croissant-mcp-poc.git
   cd croissant-mcp-poc
   ```

3. **Run the deployment script**:
   ```bash
   cd croissant-mcp-integration
   chmod +x croissant-mcp-deploy.sh
   ./croissant-mcp-deploy.sh
   ```

   This script will:
   - Install required dependencies
   - Set up a Python virtual environment
   - Configure API key authentication (default: `croissant-mcp-demo-key`)
   - Create and start a systemd service for the server
   - Display the server URL and Cursor configuration

4. **Verify the server is running**:
   ```bash
   sudo systemctl status croissant-mcp
   ```

5. **Test API key authentication**:
   ```bash
   curl -H "X-API-Key: croissant-mcp-demo-key" http://localhost:8000/info
   ```

## Cursor Integration

Add the following to your Cursor MCP configuration file (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "croissant-datasets": {
      "url": "http://your-ec2-public-dns:8000/mcp",
      "env": {
        "API_KEY": "croissant-mcp-demo-key"
      }
    }
  }
}
```

Replace `your-ec2-public-dns` with your actual EC2 instance's public DNS or IP address.

## Security Group Configuration

Ensure your EC2 security group allows inbound traffic on port 8000:

1. Go to the EC2 console
2. Select your instance
3. Click on the security group
4. Add an inbound rule:
   - Type: Custom TCP
   - Port range: 8000
   - Source: 0.0.0.0/0 (or restrict to specific IPs)

## Troubleshooting

- **Server not starting**: Check logs with `sudo journalctl -u croissant-mcp -f`
- **Cannot connect to server**: Verify security group allows port 8000
- **Authentication issues**: Ensure API key in Cursor config matches server's key
- **Cursor integration issues**: Check that URL format is correct and ends with `/mcp`

## Advanced Configuration

For a production deployment, consider:

1. Using a custom API key:
   ```bash
   ./croissant-mcp-deploy.sh your-custom-api-key
   ```

2. Setting up HTTPS with Nginx and Let's Encrypt (see AWS_DEPLOYMENT_UPDATED.md)

3. Restricting access to specific IP addresses in your security group

For more detailed instructions, refer to the AWS_DEPLOYMENT_UPDATED.md and CURSOR_INTEGRATION_AWS.md files in the repository.
