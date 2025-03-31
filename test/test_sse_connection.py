#!/usr/bin/env python3
"""
Test script for SSE connection to MCP server
"""
import requests
import json
import time
import sys

def test_sse_connection(url, api_key=None):
    """Test SSE connection to MCP server"""
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
                    
                    # If we receive a valid event, consider the test successful
                    if decoded_line.startswith("data:"):
                        try:
                            data = json.loads(decoded_line[5:])
                            print(f"Parsed JSON: {data}")
                            return True
                        except json.JSONDecodeError:
                            print(f"Invalid JSON: {decoded_line[5:]}")
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_sse_connection.py <url> [api_key]")
        sys.exit(1)
    
    url = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = test_sse_connection(url, api_key)
    print(f"Test {'successful' if success else 'failed'}")
    sys.exit(0 if success else 1)
