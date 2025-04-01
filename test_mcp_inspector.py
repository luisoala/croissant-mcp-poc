"""
Test script for verifying MCP SDK server implementation using MCP Inspector
"""
import requests
import json
import logging
import time
import sys
from typing import Dict, Any, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8000/sse"
MESSAGES_URL = "http://localhost:8000/messages"
TIMEOUT = 10  # Timeout in seconds
POLL_INTERVAL = 0.5  # Seconds between polling for async responses

def test_sse_connection() -> Tuple[bool, Optional[str]]:
    """Test SSE connection and get session ID"""
    headers = {"Accept": "text/event-stream"}
    
    logger.info(f"Testing SSE connection to {SERVER_URL}")
    try:
        response = requests.get(SERVER_URL, headers=headers, stream=True)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to connect to SSE endpoint: {response.status_code}")
            return False, None
        
        session_id = None
        events = []
        
        for i, line in enumerate(response.iter_lines(decode_unicode=True)):
            if line:
                logger.info(f"Line {i+1}: {line}")
                
                if line.startswith("event:"):
                    event_type = line[6:].strip()
                    events.append({"type": event_type})
                
                if "session_id=" in line and line.startswith("data:"):
                    session_id = line.split("session_id=")[1].strip()
                    logger.info(f"Found session ID: {session_id}")
                    break
            
            if i >= 10:
                break
        
        response.close()
        
        return session_id is not None, session_id
    
    except Exception as e:
        logger.error(f"Error testing SSE connection: {e}")
        return False, None

def test_list_tools(session_id: Optional[str] = None) -> Tuple[bool, List[Dict[str, Any]]]:
    """Test listing tools via the messages endpoint"""
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
                return True, tools
            
            logger.error("Response missing expected fields")
            return False, []
            
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
                            return True, tools
                    except Exception as e:
                        logger.error(f"Error parsing poll response: {e}")
            
            logger.error(f"Timed out waiting for tools/list result after {TIMEOUT} seconds")
            return False, []
            
        else:
            logger.error(f"Failed to list tools: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            return False, []
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return False, []

def test_call_tool(session_id: Optional[str] = None, tool_name: str = "search_datasets") -> bool:
    """Test calling a tool via the messages endpoint"""
    headers = {"Content-Type": "application/json"}
    
    url = MESSAGES_URL
    if session_id:
        url = f"{url}?session_id={session_id}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": {"query": "mnist"}
        }
    }
    
    logger.info(f"Testing tool call {tool_name} at {url}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        logger.info(f"Initial status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Immediate response: {json.dumps(data, indent=2)}")
            
            if "result" in data and "content" in data["result"]:
                logger.info(f"Tool call successful")
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
                    "id": request_id or 4,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": {"query": "mnist"}
                    }
                }
                
                poll_response = requests.post(url, json=poll_payload, headers=headers, timeout=5)
                logger.info(f"Poll status: {poll_response.status_code}")
                
                if poll_response.status_code == 200:
                    try:
                        data = poll_response.json()
                        logger.info(f"Poll response: {json.dumps(data, indent=2)}")
                        
                        if "result" in data and "content" in data["result"]:
                            logger.info(f"Tool call successful")
                            return True
                    except Exception as e:
                        logger.error(f"Error parsing poll response: {e}")
            
            logger.error(f"Timed out waiting for tools/call result after {TIMEOUT} seconds")
            return False
            
        else:
            logger.error(f"Failed to call tool: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Error calling tool: {e}")
        return False

def main():
    logger.info("=== Testing MCP Server with MCP Inspector ===")
    
    sse_success, session_id = test_sse_connection()
    
    if not sse_success:
        logger.error("Failed to connect to SSE endpoint.")
        sys.exit(1)
    
    logger.info(f"Using session ID: {session_id}")
    
    tools_success, tools = test_list_tools(session_id)
    
    if not tools_success:
        logger.error("Failed to list tools.")
        sys.exit(1)
    
    logger.info(f"Found {len(tools)} tools:")
    for i, tool in enumerate(tools):
        logger.info(f"  {i+1}. {tool.get('name')}: {tool.get('description')}")
    
    tool_call_success = test_call_tool(session_id)
    
    logger.info("=== MCP Inspector Test Results ===")
    logger.info(f"SSE Connection: {'✅ PASS' if sse_success else '❌ FAIL'}")
    logger.info(f"Tools Listing: {'✅ PASS' if tools_success else '❌ FAIL'}")
    logger.info(f"Tool Calling: {'✅ PASS' if tool_call_success else '❌ FAIL'}")
    
    if sse_success and tools_success and tool_call_success:
        logger.info("✅ All tests passed! MCP server implementation is working correctly.")
    else:
        logger.error("❌ Some tests failed. MCP server implementation may not be working correctly.")

if __name__ == "__main__":
    main()
