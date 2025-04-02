# Croissant MCP Server

A minimal MCP server that indexes Croissant datasets and exposes them via tools and resources to LLM tools and agents. The server uses Server-Sent Events (SSE) for real-time updates and runs on port 8000.

## Features

- FastAPI-based MCP server
- SSE support for real-time updates
- API key authentication
- Dataset indexing and search
- Deployable to EC2
- Nginx reverse proxy configuration

## Setup

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running Locally

```bash
python main.py
```

The server will start on http://0.0.0.0:8000

## Available Endpoints

- Health check: `/health`
- MCP endpoints: `/mcp`
- SSE events: `/events`
- API docs: `/docs`

## Deployment to EC2

1. Update the `deploy_ec2.sh` script with your EC2 host:
```bash
EC2_HOST="your-ec2-host"
```

2. Make sure you have SSH access to your EC2 instance:
```bash
ssh-copy-id ubuntu@your-ec2-host
```

3. Run the deployment script:
```bash
./deploy_ec2.sh
```

The script will:
- Copy the application files to EC2
- Set up a Python virtual environment
- Install dependencies
- Configure systemd service
- Set up Nginx reverse proxy

## Security

- The server requires an API key for authentication
- Set the `MCP_API_KEY` environment variable or use the default demo key
- All endpoints except `/health` require authentication
- Nginx is configured to handle SSL (you'll need to add your SSL certificates)

## Development

The server is built with:
- FastAPI for the web framework
- MCP SDK for LLM tool integration
- SSE-Starlette for real-time updates
- Pydantic for data validation

## License

MIT
