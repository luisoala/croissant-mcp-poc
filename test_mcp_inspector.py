"""
Test script for verifying MCP-compliant SSE implementation with Inspector tool requirements
"""
import requests
import json
import logging
import time
import sseclient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8001/sse"

def test_sse_with_requests():
    """Test SSE connection using requests and sseclient"""
    logger.info(f"Testing SSE connection to {SERVER_URL} with requests/sseclient")
    
    headers = {"Accept": "text/event-stream"}
    try:
        response = requests.get(SERVER_URL, headers=headers, stream=True)
        if response.status_code != 200:
            logger.error(f"Failed to connect: {response.status_code}")
            return False
        
        client = sseclient.SSEClient(response)
        event_count = 0
        
        for event in client.events():
            try:
                data = json.loads(event.data)
                logger.info(f"Received event: {data}")
                
                # Validate JSON-RPC 2.0 format
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
                if event_count >= 2:  # Get at least 2 events (connection + heartbeat)
                    break
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in event data: {event.data}")
                return False
        
        logger.info(f"Successfully received {event_count} valid events")
        return event_count > 0
        
    except Exception as e:
        logger.error(f"Error testing SSE connection: {e}")
        return False

def test_inspector_compatibility():
    """Test compatibility with MCP Inspector tool requirements"""
    logger.info("Testing compatibility with MCP Inspector tool requirements")
    
    # 1. Check that SSE endpoint is available at /sse
    if not SERVER_URL.endswith('/sse'):
        logger.error("SSE endpoint must be available at /sse")
        return False
    
    # 2. Check that SSE endpoint doesn't require authentication
    headers = {"Accept": "text/event-stream"}
    try:
        response = requests.get(SERVER_URL, headers=headers, stream=True)
        if response.status_code != 200:
            logger.error(f"SSE endpoint requires authentication or is not available: {response.status_code}")
            return False
        
        # 3. Check that events are in JSON-RPC 2.0 format
        client = sseclient.SSEClient(response)
        for event in client.events():
            try:
                data = json.loads(event.data)
                
                if data.get('jsonrpc') != '2.0':
                    logger.error("Events must use JSON-RPC 2.0 format with jsonrpc: 2.0")
                    return False
                
                if 'result' not in data and 'error' not in data:
                    logger.error("Events must include result or error field")
                    return False
                
                if 'id' not in data:
                    logger.error("Events must include id field")
                    return False
                
                logger.info("Event format is compatible with MCP Inspector tool")
                return True
                
            except json.JSONDecodeError:
                logger.error(f"Events must be valid JSON: {event.data}")
                return False
            
    except Exception as e:
        logger.error(f"Error testing Inspector compatibility: {e}")
        return False

def main():
    logger.info("=== Testing MCP-compliant SSE Implementation for Inspector Tool ===")
    
    # Test with requests/sseclient
    requests_test = test_sse_with_requests()
    
    # Test Inspector compatibility
    inspector_test = test_inspector_compatibility()
    
    logger.info("=== Test Results ===")
    logger.info(f"SSE Connection (requests): {'✅ PASS' if requests_test else '❌ FAIL'}")
    logger.info(f"Inspector Compatibility: {'✅ PASS' if inspector_test else '❌ FAIL'}")
    
    if requests_test and inspector_test:
        logger.info("✅ All tests passed! The MCP SSE implementation is compatible with the MCP Inspector tool.")
        return True
    else:
        logger.error("❌ Some tests failed. The implementation may not be compatible with the MCP Inspector tool.")
        return False

if __name__ == "__main__":
    main()
