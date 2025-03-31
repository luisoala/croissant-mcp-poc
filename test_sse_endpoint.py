"""
Test script for the Cursor-compatible SSE endpoint with API key authentication
"""
import requests
import json
import time
import sys
import os

BASE_URL = os.environ.get("MCP_SERVER_URL", "http://44.242.230.242:8000")
API_KEY = os.environ.get("MCP_API_KEY", "croissant-mcp-demo-key")

def test_info_endpoint():
    """Test the info endpoint with API key authentication"""
    print("\n=== Testing /info endpoint ===")
    
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/info", headers=headers)
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Server returned:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_sse_endpoint():
    """Test the SSE endpoint with API key authentication"""
    print("\n=== Testing /sse endpoint ===")
    
    headers = {
        "Accept": "text/event-stream",
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.get(f"{BASE_URL}/sse", headers=headers, stream=True)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! SSE connection established.")
            print("Waiting for events...")
            
            event_count = 0
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"Received: {decoded_line}")
                    
                    event_count += 1
                    if event_count >= 5:  # Stop after 5 events
                        break
            
            response.close()
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_sse_endpoint_with_env_api_key():
    """Test the SSE endpoint with API key in env parameter (Cursor format)"""
    print("\n=== Testing /sse endpoint with env.API_KEY ===")
    
    headers = {"Accept": "text/event-stream"}
    params = {"env.API_KEY": API_KEY}
    
    try:
        response = requests.get(f"{BASE_URL}/sse", headers=headers, params=params, stream=True)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! SSE connection established with env.API_KEY.")
            print("Waiting for events...")
            
            event_count = 0
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"Received: {decoded_line}")
                    
                    event_count += 1
                    if event_count >= 5:  # Stop after 5 events
                        break
            
            response.close()
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_sse_endpoint_without_api_key():
    """Test the SSE endpoint without API key (should fail)"""
    print("\n=== Testing /sse endpoint without API key ===")
    
    headers = {"Accept": "text/event-stream"}
    
    try:
        response = requests.get(f"{BASE_URL}/sse", headers=headers)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 403:
            print("Success! Server correctly rejected request without API key.")
            print(f"Error message: {response.text}")
            return True
        else:
            print(f"Unexpected response: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_cursor_mcp_config():
    """Generate a Cursor MCP configuration file"""
    print("\n=== Generating Cursor MCP configuration ===")
    
    config = {
        "mcpServers": {
            "croissant-datasets": {
                "url": f"{BASE_URL}/sse",
                "env": {
                    "API_KEY": API_KEY
                }
            }
        }
    }
    
    config_path = "mcp_cursor_test.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Cursor MCP configuration saved to {config_path}:")
    print(json.dumps(config, indent=2))
    
    print("\nTo use this configuration in Cursor:")
    print(f"1. Copy this file to ~/.cursor/mcp.json")
    print(f"2. Restart Cursor")
    print(f"3. Cursor should connect to the MCP server at {BASE_URL}/sse")
    
    return True

def main():
    """Run all tests"""
    print("=== Testing Cursor-compatible SSE endpoint with API key authentication ===")
    print(f"Server URL: {BASE_URL}")
    print(f"API Key: {API_KEY}")
    
    info_success = test_info_endpoint()
    sse_success = test_sse_endpoint()
    sse_env_success = test_sse_endpoint_with_env_api_key()
    sse_no_key_success = test_sse_endpoint_without_api_key()
    config_success = test_cursor_mcp_config()
    
    print("\n=== Test Summary ===")
    print(f"Info endpoint: {'✅ PASS' if info_success else '❌ FAIL'}")
    print(f"SSE endpoint with X-API-Key: {'✅ PASS' if sse_success else '❌ FAIL'}")
    print(f"SSE endpoint with env.API_KEY: {'✅ PASS' if sse_env_success else '❌ FAIL'}")
    print(f"SSE endpoint without API key: {'✅ PASS' if sse_no_key_success else '❌ FAIL'}")
    print(f"Cursor MCP configuration: {'✅ PASS' if config_success else '❌ FAIL'}")
    
    if info_success and sse_success and sse_env_success and sse_no_key_success and config_success:
        print("\n✅ All tests passed! The server is ready for Cursor integration.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
