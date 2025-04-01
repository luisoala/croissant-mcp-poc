"""
Test script for verifying the MCP SDK server implementation with async response handling
"""
import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8000/sse"
MESSAGES_URL = "http://localhost:8000/messages"
TIMEOUT = 10  # Timeout in seconds
POLL_INTERVAL = 0.5  # Seconds between polling for async responses

def test_sse_connection():
    """Test SSE connection"""
    headers = {"Accept": "text/event-stream"}
    
    logger.info(f"Testing SSE connection to {SERVER_URL}")
    try:
        response = requests.get(SERVER_URL, headers=headers, stream=True)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to connect to SSE endpoint: {response.status_code}")
            return False, None
        
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
        return session_id is not None, session_id
    
    except Exception as e:
        logger.error(f"Error testing SSE connection: {e}")
        return False, None

def test_tools_list_with_polling(session_id=None):
    """Test tools/list endpoint with polling for async responses"""
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
        logger.info(f"Initial status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Immediate response: {json.dumps(data, indent=2)}")
            
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                logger.info(f"Found {len(tools)} tools")
                return True
            
            logger.error("Response missing expected fields")
            return False
            
        elif response.status_code == 202:
            logger.info("Received 202 Accepted, polling for result...")
            
            request_id = None
            try:
                data = response.json()
                if "id" in data:
                    request_id = data["id"]
                    logger.info(f"Request ID: {request_id}")
            except:
                pass
            
            start_time = time.time()
            while (time.time() - start_time) < TIMEOUT:
                time.sleep(POLL_INTERVAL)
                
                logger.info(f"Polling for result...")
                poll_payload = {
                    "jsonrpc": "2.0",
                    "id": request_id or 2,
                    "method": "tools/list"
                }
                
                poll_response = requests.post(url, json=poll_payload, headers=headers, timeout=5)
                logger.info(f"Poll status: {poll_response.status_code}")
                
                if poll_response.status_code == 200:
                    try:
                        data = poll_response.json()
                        logger.info(f"Poll response: {json.dumps(data, indent=2)}")
                        
                        if "result" in data and "tools" in data["result"]:
                            tools = data["result"]["tools"]
                            logger.info(f"Found {len(tools)} tools")
                            return True
                    except Exception as e:
                        logger.error(f"Error parsing poll response: {e}")
                
            logger.error(f"Timed out waiting for tools/list result after {TIMEOUT} seconds")
            return False
            
        else:
            logger.error(f"Failed to list tools: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Error testing tools list: {e}")
        return False

def main():
    logger.info("=== Testing MCP SDK Server Implementation ===")
    
    sse_test, session_id = test_sse_connection()
    
    if session_id:
        logger.info(f"Using session ID: {session_id}")
    else:
        logger.warning("No session ID found, testing without session ID")
    
    tools_test = test_tools_list_with_polling(session_id)
    
    logger.info("=== Test Results ===")
    logger.info(f"SSE Connection: {'✅ PASS' if sse_test else '❌ FAIL'}")
    logger.info(f"Tools List: {'✅ PASS' if tools_test else '❌ FAIL'}")
    
    if sse_test and tools_test:
        logger.info("✅ All tests passed! The MCP SDK server implementation is working correctly.")
    else:
        logger.error("❌ Some tests failed. Check the server implementation.")

if __name__ == "__main__":
    main()
