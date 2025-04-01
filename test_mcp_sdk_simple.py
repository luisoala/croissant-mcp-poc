"""
Simple test script for verifying the MCP SDK server implementation
"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8000/sse"
MESSAGES_URL = "http://localhost:8000/messages"

def test_sse_connection():
    """Test SSE connection"""
    headers = {"Accept": "text/event-stream"}
    
    logger.info(f"Testing SSE connection to {SERVER_URL}")
    try:
        response = requests.get(SERVER_URL, headers=headers, stream=True)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to connect to SSE endpoint: {response.status_code}")
            return False
        
        session_id = None
        for i, line in enumerate(response.iter_lines(decode_unicode=True)):
            if line:
                logger.info(f"Line {i+1}: {line}")
                if "session_id=" in line and line.startswith("data:"):
                    session_id = line.split("session_id=")[1].strip()
                    logger.info(f"Found session ID: {session_id}")
                    break
            
            if i >= 5:
                break
        
        response.close()
        return session_id is not None
    
    except Exception as e:
        logger.error(f"Error testing SSE connection: {e}")
        return False

def test_tools_list(session_id=None):
    """Test tools/list endpoint"""
    headers = {"Content-Type": "application/json"}
    
    url = MESSAGES_URL
    if session_id:
        url = f"{url}?session_id={session_id}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    logger.info(f"Testing tools/list at {url}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to list tools: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            return False
        
        data = response.json()
        logger.info(f"Response: {json.dumps(data, indent=2)}")
        
        if "result" not in data:
            logger.error("Response missing result field")
            return False
        
        if "tools" not in data["result"]:
            logger.error("Result missing tools field")
            return False
        
        tools = data["result"]["tools"]
        logger.info(f"Found {len(tools)} tools")
        
        return len(tools) > 0
    
    except Exception as e:
        logger.error(f"Error testing tools list: {e}")
        return False

def main():
    logger.info("=== Testing MCP SDK Server Implementation ===")
    
    sse_test = test_sse_connection()
    
    session_id = None
    if sse_test:
        headers = {"Accept": "text/event-stream"}
        try:
            response = requests.get(SERVER_URL, headers=headers, stream=True)
            for line in response.iter_lines(decode_unicode=True):
                if line and "session_id=" in line and line.startswith("data:"):
                    session_id = line.split("session_id=")[1].strip()
                    logger.info(f"Using session ID: {session_id}")
                    break
            response.close()
        except:
            pass
    
    tools_test = test_tools_list(session_id)
    
    logger.info("=== Test Results ===")
    logger.info(f"SSE Connection: {'✅ PASS' if sse_test else '❌ FAIL'}")
    logger.info(f"Tools List: {'✅ PASS' if tools_test else '❌ FAIL'}")
    
    if sse_test and tools_test:
        logger.info("✅ All tests passed! The MCP SDK server implementation is working correctly.")
    else:
        logger.error("❌ Some tests failed. Check the server implementation.")

if __name__ == "__main__":
    main()
