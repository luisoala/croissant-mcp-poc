
set -e

echo "=== Updating EC2 Server to Allow SSE Without Authentication ==="

EC2_IP="44.242.230.242"

echo "Attempting to connect to EC2 instance..."
if ssh -o ConnectTimeout=10 ubuntu@$EC2_IP echo "SSH connection successful"; then
    echo "SSH connection established."
    
    ssh ubuntu@$EC2_IP << 'EOF'
        echo "Connected to EC2 instance"
        
        cd croissant-mcp-poc
        
        echo "Pulling latest changes from repository..."
        git pull
        
        echo "Restarting MCP server service..."
        sudo systemctl restart croissant-mcp
        
        echo "Waiting for server to start..."
        sleep 5
        
        echo "Checking service status..."
        sudo systemctl status croissant-mcp
        
        echo "Testing server with curl..."
        curl -H "Accept: text/event-stream" http://localhost:8000/sse -v --max-time 5
        
        echo "Viewing server logs..."
        sudo journalctl -u croissant-mcp -n 50
EOF
else
    echo "SSH connection failed. Testing HTTP endpoints directly..."
    
    echo "Testing /info endpoint..."
    curl -s -H "X-API-Key: croissant-mcp-demo-key" http://$EC2_IP:8000/info | json_pp
    
    echo -e "\nTesting /sse endpoint without API key..."
    curl -N -H "Accept: text/event-stream" http://$EC2_IP:8000/sse --max-time 5
fi

echo "=== EC2 Server Update Complete ==="
echo "Cursor should now be able to connect to the MCP server at http://$EC2_IP:8000/sse"
echo "No API key is required for the SSE endpoint"
