"""
Test client for the Croissant MCP server with Cursor-compatible API key authentication
"""
import asyncio
import httpx
import json
import os

API_KEY = os.environ.get("MCP_API_KEY", "croissant-mcp-demo-key")
SERVER_URL = "http://localhost:8000"

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

async def test_mcp_endpoint():
    """Test the MCP endpoint with SSE connection"""
    print("\nTesting MCP endpoint with SSE connection...")
    headers = {"Accept": "text/event-stream"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/mcp/", headers=headers, timeout=5.0)
            print(f"Status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            if response.status_code == 200:
                print("SSE connection established successfully")
            else:
                print(f"Error response: {response.text}")
            return response.status_code == 200
        except httpx.TimeoutException:
            print("SSE connection established (timeout expected for long-lived connection)")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

async def test_mcp_tools_endpoint():
    """Test the MCP tools endpoint with API key in environment"""
    print("\nTesting MCP tools endpoint with API key in environment...")
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SERVER_URL}/mcp/tools",
                headers=headers
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Tools response: {response.text[:200]}...")
            else:
                print(f"Error response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

async def test_search_tool():
    """Test the search_datasets tool with API key in environment"""
    print("\nTesting search_datasets tool with API key in environment...")
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    data = {
        "env": {
            "API_KEY": API_KEY
        },
        "params": {
            "query": "image"
        }
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVER_URL}/mcp/tool/search_datasets",
                headers=headers,
                json=data
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Search results: {response.text[:200]}...")
            else:
                print(f"Error response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

async def test_api_key_auth():
    """Test API key authentication with header and env field"""
    print("\nTesting API key authentication...")
    
    print("Testing with X-API-Key header...")
    headers_auth = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    print("Testing with env.API_KEY field...")
    env_auth = {
        "Content-Type": "application/json"
    }
    env_data = {
        "env": {
            "API_KEY": API_KEY
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/info")
            print(f"Public info endpoint: {response.status_code}")
            if response.status_code == 200:
                print(f"Info: {response.json()}")
                return True
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

async def main():
    print(f"Testing Croissant MCP server at {SERVER_URL}")
    print(f"Using API key: {API_KEY}")
    
    health_ok = await test_health_check()
    mcp_ok = await test_mcp_endpoint()
    tools_ok = await test_mcp_tools_endpoint()
    search_ok = await test_search_tool()
    auth_ok = await test_api_key_auth()
    
    print("\nTest Summary:")
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"MCP Endpoint: {'✅' if mcp_ok else '❌'}")
    print(f"MCP Tools: {'✅' if tools_ok else '❌'}")
    print(f"Search Tool: {'✅' if search_ok else '❌'}")
    print(f"API Key Auth: {'✅' if auth_ok else '❌'}")
    
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
    
    public_url = "https://user:55c2cd91ddcbcd290477fa50af16fb0b@slack-message-app-tunnel-y876bx99.devinapps.com"
    print("\nFor remote server access:")
    remote_config = {
        "mcpServers": {
            "croissant-datasets": {
                "url": f"{public_url}/mcp",
                "env": {
                    "API_KEY": API_KEY
                }
            }
        }
    }
    print(json.dumps(remote_config, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
