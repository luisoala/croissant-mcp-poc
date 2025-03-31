"""
Simple MCP client to test the Croissant MCP server
"""
import asyncio
import httpx
from mcp.client.sse import sse_client

async def main():
    print("Connecting to Croissant MCP server...")
    
    try:
        async with sse_client("http://localhost:8000") as client:
            print("Listing available resources...")
            try:
                resources = await client.list_resources()
                print(f"Available resources: {resources}")
            except Exception as e:
                print(f"Error listing resources: {e}")
            
            print("Listing available tools...")
            try:
                tools = await client.list_tools()
                print(f"Available tools: {tools}")
            except Exception as e:
                print(f"Error listing tools: {e}")
            
            print("Reading datasets list resource...")
            try:
                content = await client.get_resource("datasets://list")
                print(f"Datasets: {content}")
            except Exception as e:
                print(f"Error reading resource: {e}")
            
            print("Testing search tool...")
            try:
                search_result = await client.call_tool("search_datasets", {"query": "image"})
                print(f"Search results: {search_result}")
            except Exception as e:
                print(f"Error calling tool: {e}")
        
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")

if __name__ == "__main__":
    asyncio.run(main())
