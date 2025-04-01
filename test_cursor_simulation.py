"""
Script to simulate Cursor's interaction with the MCP server
This helps verify the integration without needing direct access to Cursor's UI
"""
import requests
import json
import logging
import time
import sys
from typing import Dict, Any, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8001/sse"
MESSAGES_URL = "http://localhost:8001/messages"
TIMEOUT = 10  # Timeout in seconds
POLL_INTERVAL = 0.5  # Seconds between polling for async responses

def connect_to_sse() -> Tuple[bool, Optional[str]]:
    """Connect to SSE endpoint and get session ID (simulates Cursor's initial connection)"""
    headers = {"Accept": "text/event-stream"}
    
    logger.info(f"Connecting to SSE endpoint: {SERVER_URL}")
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
        
        has_endpoint_event = any(e.get("type") == "endpoint" for e in events)
        
        if not has_endpoint_event:
            logger.warning("Missing 'endpoint' event in SSE stream")
        
        return session_id is not None, session_id
    
    except Exception as e:
        logger.error(f"Error connecting to SSE endpoint: {e}")
        return False, None

def list_tools(session_id: Optional[str] = None) -> Tuple[bool, List[Dict[str, Any]]]:
    """List tools (simulates Cursor's tool discovery)"""
    headers = {"Content-Type": "application/json"}
    
    url = MESSAGES_URL
    if session_id:
        url = f"{url}?session_id={session_id}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    logger.info(f"Listing tools at {url}")
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

def call_tool(tool_name: str, arguments: Dict[str, Any], session_id: Optional[str] = None) -> Tuple[bool, Any]:
    """Call a tool (simulates Cursor's tool usage)"""
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
            "arguments": arguments
        }
    }
    
    logger.info(f"Calling tool {tool_name} at {url}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        logger.info(f"Initial status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Immediate response: {json.dumps(data, indent=2)}")
            
            if "result" in data and "content" in data["result"]:
                content = data["result"]["content"]
                return True, content
            
            logger.error("Response missing expected fields")
            return False, None
            
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
                        "arguments": arguments
                    }
                }
                
                poll_response = requests.post(url, json=poll_payload, headers=headers, timeout=5)
                logger.info(f"Poll status: {poll_response.status_code}")
                
                if poll_response.status_code == 200:
                    try:
                        data = poll_response.json()
                        logger.info(f"Poll response: {json.dumps(data, indent=2)}")
                        
                        if "result" in data and "content" in data["result"]:
                            content = data["result"]["content"]
                            return True, content
                    except Exception as e:
                        logger.error(f"Error parsing poll response: {e}")
                
            logger.error(f"Timed out waiting for tools/call result after {TIMEOUT} seconds")
            return False, None
            
        else:
            logger.error(f"Failed to call tool: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            return False, None
        
    except Exception as e:
        logger.error(f"Error calling tool: {e}")
        return False, None

def main():
    logger.info("=== Simulating Cursor's interaction with MCP server ===")
    
    sse_success, session_id = connect_to_sse()
    
    if not sse_success:
        logger.error("Failed to connect to SSE endpoint. Cursor would not be able to use this server.")
        sys.exit(1)
    
    logger.info(f"Using session ID: {session_id}")
    
    tools_success, tools = list_tools(session_id)
    
    if not tools_success:
        logger.error("Failed to list tools. Cursor would show 'No tools available'.")
        sys.exit(1)
    
    logger.info(f"Found {len(tools)} tools:")
    for i, tool in enumerate(tools):
        logger.info(f"  {i+1}. {tool.get('name')}: {tool.get('description')}")
    
    if tools:
        search_tool = next((t for t in tools if t.get("name") == "search_datasets"), None)
        
        if search_tool:
            logger.info("Calling search_datasets tool...")
            call_success, result = call_tool("search_datasets", {"query": "image"}, session_id)
            
            if call_success:
                logger.info("Tool call successful!")
                logger.info(f"Result: {json.dumps(result, indent=2)}")
            else:
                logger.error("Tool call failed. Cursor would show an error message.")
        else:
            first_tool = tools[0]
            tool_name = first_tool.get('name')
            if tool_name:
                logger.info(f"Calling {tool_name} tool...")
                call_success, result = call_tool(tool_name, {}, session_id)
                
                if call_success:
                    logger.info("Tool call successful!")
                    logger.info(f"Result: {json.dumps(result, indent=2)}")
                else:
                    logger.error("Tool call failed. Cursor would show an error message.")
            else:
                logger.error("Tool missing name property. Cannot call tool.")
    
    logger.info("=== Cursor Integration Test Results ===")
    logger.info(f"SSE Connection: {'✅ PASS' if sse_success else '❌ FAIL'}")
    logger.info(f"Tools Listing: {'✅ PASS' if tools_success else '❌ FAIL'}")
    logger.info(f"Tool Calling: {'✅ PASS' if 'call_success' in locals() and call_success else '❌ FAIL'}")
    
    if sse_success and tools_success and ('call_success' in locals() and call_success):
        logger.info("✅ All tests passed! Cursor should be able to use this MCP server correctly.")
        logger.info("The server should appear in Cursor's MCP tab as 'croissant-datasets'")
        logger.info("Tools should be listed and callable from Cursor")
    else:
        logger.error("❌ Some tests failed. Cursor integration may not work correctly.")

if __name__ == "__main__":
    main()
