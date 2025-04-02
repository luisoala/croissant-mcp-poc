"""
Test script to verify MCP implementation using the MCP Inspector
"""
import asyncio
import json
from mcp.client import Client
from mcp.transport import StdioTransport
from mcp.inspector import Inspector

async def test_mcp_server():
    # Create MCP client
    transport = StdioTransport()
    client = Client(transport)
    
    try:
        # Connect to server
        await client.connect()
        print("Connected to MCP server")
        
        # Initialize inspector
        inspector = Inspector(client)
        
        # Test list resources
        resources = await inspector.list_resources()
        print("\nAvailable resources:")
        print(json.dumps(resources, indent=2))
        
        # Test reading a resource
        dataset = await inspector.read_resource("datasets://mnist")
        print("\nMNIST dataset:")
        print(json.dumps(dataset, indent=2))
        
        # Test search tool
        search_result = await inspector.invoke_tool("search_datasets", {"query": "digits"})
        print("\nSearch results:")
        print(json.dumps(search_result, indent=2))
        
        # Test add dataset tool
        new_dataset = {
            "id": "test",
            "name": "Test Dataset",
            "description": "A test dataset",
            "format": "csv",
            "license": "MIT",
            "provider": "Test"
        }
        add_result = await inspector.invoke_tool("add_dataset", new_dataset)
        print("\nAdd dataset result:")
        print(json.dumps(add_result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 