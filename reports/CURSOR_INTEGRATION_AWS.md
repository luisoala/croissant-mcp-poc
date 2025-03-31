# Integrating Croissant MCP Server on AWS with Cursor IDE

This guide explains how to integrate the Croissant MCP Server running on AWS EC2 with Cursor IDE using API key authentication.

## Overview

The Croissant MCP Server provides a Model Context Protocol (MCP) interface for searching and accessing Croissant datasets from various platforms. By deploying it on AWS EC2 and integrating with Cursor IDE, you can:

1. Access the server from anywhere
2. Search for datasets directly from your IDE
3. Get dataset information and metadata
4. Add dataset context to your LLM-powered coding sessions

## Prerequisites

1. The Croissant MCP Server deployed on AWS EC2 (see AWS_DEPLOYMENT_UPDATED.md)
2. Cursor IDE installed on your machine

## Configuration Steps

### 1. Verify the AWS EC2 Server is Running

SSH into your EC2 instance and check the server status:

```bash
sudo systemctl status croissant-mcp
```

The output should show that the service is active and running.

### 2. Test the API Key Authentication

Test the server's API key authentication with curl:

```bash
curl -H "X-API-Key: croissant-mcp-demo-key" http://your-ec2-public-dns:8000/info
```

Replace `your-ec2-public-dns` with your actual EC2 instance's public DNS or IP address, and `croissant-mcp-demo-key` with your configured API key.

You should receive a JSON response with server information.

### 3. Configure Cursor to Use the AWS MCP Server

Create or edit the MCP configuration file in one of these locations:

- **Project-specific**: `.cursor/mcp.json` in your project directory
- **Global**: `~/.cursor/mcp.json` in your home directory

Add the following configuration:

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

Replace:
- `your-ec2-public-dns` with your actual EC2 instance's public DNS or IP address
- `croissant-mcp-demo-key` with the API key configured on your server

**Important**: 
- The `env` field is used to pass the API key to the server
- Do not include the API key in the URL
- Make sure the URL ends with `/mcp` (the MCP endpoint path)
- If you've set up HTTPS, use `https://` instead of `http://`

### 4. Restart Cursor

Restart Cursor to apply the new MCP configuration.

## Using Croissant Dataset Tools in Cursor

Once configured, you can use the following tools in Cursor:

### Basic Dataset Search

Ask Cursor to search for datasets:

- "Search for image datasets"
- "Find datasets about machine learning"
- "Look for datasets from Kaggle"

### Advanced Dataset Search

Request specific filters:

- "Find CSV datasets from Kaggle"
- "Search for datasets with Apache license"
- "Show me datasets about natural language processing with pagination"

### Get Dataset Details

Ask for information about a specific dataset:

- "Tell me about the MNIST dataset"
- "Show details for the CroissantLLM dataset"
- "What's the license for the Titanic dataset?"

## Troubleshooting

If you encounter issues:

1. **Cannot connect to the server**:
   - Check that your EC2 security group allows traffic on port 8000
   - Verify the server is running with `sudo systemctl status croissant-mcp`
   - Check logs with `sudo journalctl -u croissant-mcp`

2. **API Key Authentication Issues**:
   - Verify the API key in your Cursor configuration matches the one on the server
   - Test the API key with curl as shown above
   - Check server logs for authentication errors

3. **Cursor cannot connect to the MCP server**:
   - Ensure the URL in your mcp.json is correct
   - Check that your EC2 instance is publicly accessible
   - Verify the server is running and the MCP endpoint is available

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
   - Use HTTPS for all connections if possible
   - Restrict access to your server as needed
   - Consider using AWS Security Groups to limit access

## Advanced: Customizing the MCP Server

You can customize the MCP server by:

1. Adding more datasets to the index
2. Creating additional search tools
3. Implementing custom resources for specific dataset types
4. Extending the server with additional functionality

See the project documentation for more details on customization options.
