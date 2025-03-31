#!/usr/bin/env python3
"""
Test script for SSE protocol compliance with MCP
"""
import requests
import json
import time
import sys

def test_sse_protocol(url, api_key=None):
    """Test SSE protocol compliance with MCP"""
    headers = {
        "Accept": "text/event-stream",
    }
    
    if api_key:
        headers["X-API-Key"] = api_key
    
    print(f"Connecting to {url} with headers: {headers}")
    
    try:
        with requests.get(url, headers=headers, stream=True) as response:
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            if response.status_code != 200:
                print(f"Error: {response.text}")
                return False
            
            # Read SSE events
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"Received: {decoded_line}")
                    
                    # Check if the response follows JSON-RPC format
                    if decoded_line.startswith("data:"):
                        try:
                            data = json.loads(decoded_line[5:])
                            print(f"Parsed JSON: {data}")
                            
                            # Check if it follows JSON-RPC format
                            if "jsonrpc" in data:
                                print("✅ Response follows JSON-RPC format")
                                return True
                            else:
                                print("❌ Response does not follow JSON-RPC format")
                                print("Expected format: {'jsonrpc': '2.0', 'method': 'xxx', 'params': {...}}")
                        except json.JSONDecodeError:
                            print(f"Invalid JSON: {decoded_line[5:]}")
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_sse_protocol.py <url> [api_key]")
        sys.exit(1)
    
    url = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = test_sse_protocol(url, api_key)
    print(f"Protocol test {'successful' if success else 'failed'}")
    sys.exit(0 if success else 1)
