
EC2_HOST="44.242.230.242"
EC2_USER="ubuntu"
REMOTE_DIR="~/croissant-mcp-server"

echo "Testing connection to EC2 instance..."
ssh -o ConnectTimeout=5 ${EC2_USER}@${EC2_HOST} "echo Connection successful"

if [ $? -ne 0 ]; then
    echo "Failed to connect to EC2 instance. Check your SSH configuration."
    exit 1
fi

echo "Creating remote directory..."
ssh ${EC2_USER}@${EC2_HOST} "mkdir -p ${REMOTE_DIR}"

echo "Copying files to EC2 instance..."
scp main_fastmcp_all_interfaces.py ${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/
scp -r src ${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/
scp requirements.txt ${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/

echo "Installing dependencies on EC2 instance..."
ssh ${EC2_USER}@${EC2_HOST} "cd ${REMOTE_DIR} && pip install -r requirements.txt"

echo "Stopping any running MCP server..."
ssh ${EC2_USER}@${EC2_HOST} "pkill -f 'python main_fastmcp' || true"

echo "Starting MCP SDK server on EC2..."
ssh ${EC2_USER}@${EC2_HOST} "cd ${REMOTE_DIR} && nohup python main_fastmcp_all_interfaces.py > server.log 2>&1 &"

echo "Waiting for server to start..."
sleep 5

echo "Testing server connection..."
curl -s -N -H "Accept: text/event-stream" http://${EC2_HOST}:8000/sse | head -n 10

echo "Creating EC2 Cursor configuration..."
cat > mcp_cursor_ec2_sdk.json << EOF
{
  "servers": [
    {
      "name": "croissant-datasets-ec2",
      "url": "http://${EC2_HOST}:8000/sse",
      "auth": {
        "type": "none"
      },
      "enabled": true
    }
  ]
}
EOF

echo "Deployment complete!"
echo "Server is running at http://${EC2_HOST}:8000"
echo "SSE endpoint: http://${EC2_HOST}:8000/sse"
echo "To view logs: ssh ${EC2_USER}@${EC2_HOST} 'tail -f ${REMOTE_DIR}/server.log'"
