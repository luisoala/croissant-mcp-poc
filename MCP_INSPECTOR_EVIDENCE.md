# MCP Inspector Tool Test Results

## Test Command

```javascript
const { MCPInspector } = require('@modelcontextprotocol/inspector');

const inspector = new MCPInspector({
  serverUrl: 'http://localhost:8000/sse',
  apiKey: 'croissant-mcp-demo-key'
});

inspector.connect()
  .then(() => {
    console.log('✅ Successfully connected to MCP server');
    console.log('Server info:', inspector.serverInfo);
    
    inspector.on('message', (message) => {
      console.log('Received message:', message);
    });
    
    setTimeout(() => {
      inspector.disconnect();
      console.log('Disconnected from MCP server');
      process.exit(0);
    }, 10000);
  })
  .catch((error) => {
    console.error('❌ Failed to connect to MCP server:', error.message);
    process.exit(1);
  });
```

## Test Output

```
```
