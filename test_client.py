"""
Simple HTTP client to test the Croissant MCP server endpoints
"""
import asyncio
import httpx
import json

async def test_server_health():
    """Test the server health endpoint"""
    print("\nTesting server health...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/health")
            print(f"Health check status: {response.status_code}")
            print(f"Response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error checking server health: {e}")
            return False

async def test_mcp_endpoint():
    """Test the MCP endpoint directly"""
    print("\nTesting MCP endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/mcp")
            print(f"MCP endpoint status: {response.status_code}")
            print(f"Response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error checking MCP endpoint: {e}")
            return False

async def test_search_tool():
    """Test the search_datasets tool using direct HTTP request"""
    print("\nTesting search_datasets tool...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/mcp/tools/search_datasets",
                json={"query": "image"}
            )
            print(f"Search tool status: {response.status_code}")
            if response.status_code == 200:
                print(f"Search results: {response.text}")
            else:
                print(f"Error response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error calling search tool: {e}")
            return False

async def test_resources():
    """Test the datasets list resource using direct HTTP request"""
    print("\nTesting datasets list resource...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/mcp/resources/datasets/list"
            )
            print(f"Resource status: {response.status_code}")
            if response.status_code == 200:
                print(f"Datasets: {response.text}")
            else:
                print(f"Error response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error getting resource: {e}")
            return False

async def main():
    print("Testing Croissant MCP server...")
    
    health_ok = await test_server_health()
    
    mcp_ok = await test_mcp_endpoint()
    
    search_ok = await test_search_tool()
    
    resources_ok = await test_resources()
    
    print("\nTest Summary:")
    print(f"Server Health: {'✅' if health_ok else '❌'}")
    print(f"MCP Endpoint: {'✅' if mcp_ok else '❌'}")
    print(f"Search Tool: {'✅' if search_ok else '❌'}")
    print(f"Resources: {'✅' if resources_ok else '❌'}")

if __name__ == "__main__":
    asyncio.run(main())
