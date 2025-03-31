"""
Test client for the Croissant MCP server with API key authentication
"""
import asyncio
import httpx
import json

API_KEY = "croissant-mcp-demo-key"
API_KEY_NAME = "X-API-Key"

SERVER_URL = "https://croissant-mcp-server.loca.lt"

async def test_health_check():
    """Test the server health endpoint (no auth required)"""
    print("\nTesting health check endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

async def test_mcp_endpoint_no_auth():
    """Test the MCP endpoint without authentication (should fail)"""
    print("\nTesting MCP endpoint without authentication...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/mcp")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return response.status_code == 403  # Should return 403 Forbidden
        except Exception as e:
            print(f"Error: {e}")
            return False

async def test_mcp_endpoint_with_auth():
    """Test the MCP endpoint with authentication"""
    print("\nTesting MCP endpoint with authentication...")
    headers = {API_KEY_NAME: API_KEY}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/mcp", headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

async def test_search_tool_with_auth():
    """Test the search_datasets tool with authentication"""
    print("\nTesting search_datasets tool with authentication...")
    headers = {API_KEY_NAME: API_KEY}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVER_URL}/mcp/tools/search_datasets",
                headers=headers,
                json={"query": "image"}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Search results: {response.text}")
            else:
                print(f"Error response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

async def test_auth_info():
    """Test the auth info endpoint"""
    print("\nTesting auth info endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/mcp/auth-info")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

async def main():
    print(f"Testing Croissant MCP server at {SERVER_URL}")
    print(f"Using API key: {API_KEY}")
    
    health_ok = await test_health_check()
    
    mcp_no_auth_ok = await test_mcp_endpoint_no_auth()
    
    mcp_with_auth_ok = await test_mcp_endpoint_with_auth()
    
    search_ok = await test_search_tool_with_auth()
    
    auth_info_ok = await test_auth_info()
    
    print("\nTest Summary:")
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"MCP No Auth (should fail): {'✅' if mcp_no_auth_ok else '❌'}")
    print(f"MCP With Auth: {'✅' if mcp_with_auth_ok else '❌'}")
    print(f"Search Tool: {'✅' if search_ok else '❌'}")
    print(f"Auth Info: {'✅' if auth_info_ok else '❌'}")
    
    print("\nCursor Integration:")
    print("Add the following to your ~/.cursor/mcp.json file:")
    cursor_config = {
        "mcpServers": {
            "croissant-datasets": {
                "url": f"{SERVER_URL}/mcp",
                "env": {
                    "API_KEY": API_KEY
                }
            }
        }
    }
    print(json.dumps(cursor_config, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
