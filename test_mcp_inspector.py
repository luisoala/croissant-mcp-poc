"""
Test script for verifying the MCP-compliant SSE implementation with the MCP Inspector tool
"""
import asyncio
import aiohttp
import json
import logging
import requests
import sseclient
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8000/sse"
API_KEY = "croissant-mcp-demo-key"

def test_sse_with_requests():
    """Test SSE connection with requests/sseclient"""
    headers = {"Accept": "text/event-stream"}
    
    logger.info(f"Testing SSE connection to {SERVER_URL} with requests/sseclient")
    try:
        response = requests.get(SERVER_URL, headers=headers, stream=True)
        if response.status_code != 200:
            logger.error(f"Failed to connect to SSE endpoint: {response.status_code}")
            return False
        
        client = sseclient.SSEClient(response)
        event_count = 0
        for event in client.events():
            data = json.loads(event.data)
            logger.info(f"Received event: {data}")
            
            if data.get('jsonrpc') != '2.0':
                logger.error("Event missing jsonrpc: 2.0")
                return False
            
            if 'result' not in data and 'error' not in data:
                logger.error("Event missing result or error")
                return False
            
            if 'id' not in data:
                logger.error("Event missing id")
                return False
            
            event_count += 1
            if event_count >= 2:
                break
        
        return event_count > 0
    except Exception as e:
        logger.error(f"Error testing SSE connection: {e}")
        return False

def test_inspector_compatibility():
    """Test compatibility with MCP Inspector tool requirements"""
    logger.info("Testing compatibility with MCP Inspector tool requirements")
    
    # Check if the SSE endpoint follows the MCP specification
    # 1. Endpoint should be at /sse
    # 2. No authentication required
    # 3. JSON-RPC 2.0 format
    
    if not SERVER_URL.endswith('/sse'):
        logger.error("SSE endpoint URL should end with /sse")
        return False
    
    # Test authentication not required
    try:
        response = requests.get(SERVER_URL, headers={"Accept": "text/event-stream"}, stream=True)
        if response.status_code != 200:
            logger.error(f"SSE endpoint requires authentication: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error testing authentication: {e}")
        return False
    
    # Test JSON-RPC 2.0 format
    try:
        client = sseclient.SSEClient(response)
        for event in client.events():
            data = json.loads(event.data)
            if data.get('jsonrpc') != '2.0':
                logger.error("Event missing jsonrpc: 2.0")
                return False
            
            if 'result' not in data and 'error' not in data:
                logger.error("Event missing result or error")
                return False
            
            if 'id' not in data:
                logger.error("Event missing id")
                return False
            
            logger.info("Event format is compatible with MCP Inspector tool")
            return True
    except Exception as e:
        logger.error(f"Error testing JSON-RPC format: {e}")
        return False
    
    return False

def main():
    logger.info("=== Testing MCP-compliant SSE Implementation for Inspector Tool ===")
    
    sse_test = test_sse_with_requests()
    inspector_test = test_inspector_compatibility()
    
    logger.info("=== Test Results ===")
    logger.info(f"SSE Connection (requests): {'✅ PASS' if sse_test else '❌ FAIL'}")
    logger.info(f"Inspector Compatibility: {'✅ PASS' if inspector_test else '❌ FAIL'}")
    
    if sse_test and inspector_test:
        logger.info("✅ All tests passed! The MCP SSE implementation is compatible with the MCP Inspector tool.")
    else:
        logger.error("❌ Some tests failed. Check the server implementation.")

if __name__ == "__main__":
    main()
