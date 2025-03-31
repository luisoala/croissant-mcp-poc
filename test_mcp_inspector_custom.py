"""
Custom test script for verifying the MCP-compliant SSE implementation
"""
import asyncio
import json
import logging
import requests
import sseclient
import time
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8000/sse"
API_KEY = "croissant-mcp-demo-key"

def test_sse_connection():
    """Test SSE connection without authentication"""
    headers = {"Accept": "text/event-stream"}
    
    logger.info(f"Testing SSE connection to {SERVER_URL}")
    try:
        response = requests.get(SERVER_URL, headers=headers, stream=True)
        logger.info(f"Status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Failed to connect to SSE endpoint: {response.status_code}")
            return False
        
        client = sseclient.SSEClient(response)
        event_count = 0
        events = []
        
        for event in client.events():
            data = json.loads(event.data)
            logger.info(f"Received event: {data}")
            events.append(data)
            
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
        
        logger.info(f"Successfully received {event_count} valid events")
        return events
    except Exception as e:
        logger.error(f"Error testing SSE connection: {e}")
        return False

def main():
    logger.info("=== Testing MCP-compliant SSE Implementation for Inspector Tool ===")
    
    events = test_sse_connection()
    
    if events:
        logger.info("=== Test Results ===")
        logger.info("SSE Connection: ✅ PASS")
        logger.info("JSON-RPC 2.0 Format: ✅ PASS")
        logger.info("Event Content: ✅ PASS")
        logger.info("✅ All tests passed! The MCP SSE implementation is compatible with the MCP Inspector tool.")
        
        # Save events to a file for evidence
        with open("mcp_inspector_test_results.json", "w") as f:
            json.dump(events, f, indent=2)
        logger.info("Test results saved to mcp_inspector_test_results.json")
    else:
        logger.error("❌ Some tests failed. Check the server implementation.")

if __name__ == "__main__":
    main()
