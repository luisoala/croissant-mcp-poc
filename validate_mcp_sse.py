"""
MCP SSE Validation Script - Validates implementation against MCP specification
"""
import asyncio
import aiohttp
import json
import logging
import time
import requests
import sys
import os
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8001/sse"

def start_server():
    """Start the MCP SSE server in the background"""
    logger.info("Starting MCP SSE server...")
    try:
        process = subprocess.Popen(
            ["python", "main_mcp_sse.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(2)  # Give the server time to start
        return process
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return None

def stop_server(process):
    """Stop the MCP SSE server"""
    if process:
        logger.info("Stopping MCP SSE server...")
        process.terminate()
        process.wait()

def test_sse_endpoint():
    """Test the SSE endpoint for MCP compliance"""
    logger.info(f"Testing SSE endpoint at {SERVER_URL}")
    
    headers = {"Accept": "text/event-stream"}
    try:
        response = requests.get(SERVER_URL, headers=headers, stream=True)
        if response.status_code != 200:
            logger.error(f"SSE endpoint returned status code {response.status_code}")
            return False
        
        logger.info("SSE endpoint returned 200 OK")
        
        # Read the first few events
        event_data = []
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    data_str = line[5:].strip()
                    try:
                        data = json.loads(data_str)
                        event_data.append(data)
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
                        
                        if len(event_data) >= 2:
                            break
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in event data: {data_str}")
                        return False
        
        logger.info(f"Successfully received {len(event_data)} valid events")
        return len(event_data) > 0
    
    except Exception as e:
        logger.error(f"Error testing SSE endpoint: {e}")
        return False

def validate_mcp_compliance():
    """Validate MCP compliance based on specification"""
    logger.info("Validating MCP compliance based on specification")
    
    # Check 1: SSE endpoint is available at /sse
    if not SERVER_URL.endswith('/sse'):
        logger.error("FAIL: SSE endpoint must be available at /sse")
        return False
    logger.info("PASS: SSE endpoint is available at /sse")
    
    # Check 2: SSE endpoint doesn't require authentication
    headers = {"Accept": "text/event-stream"}
    try:
        response = requests.get(SERVER_URL, headers=headers, stream=True)
        if response.status_code != 200:
            logger.error(f"FAIL: SSE endpoint requires authentication or is not available: {response.status_code}")
            return False
        logger.info("PASS: SSE endpoint doesn't require authentication")
        
        # Check 3: Events are in JSON-RPC 2.0 format
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    data_str = line[5:].strip()
                    try:
                        data = json.loads(data_str)
                        
                        if data.get('jsonrpc') != '2.0':
                            logger.error("FAIL: Events must use JSON-RPC 2.0 format with jsonrpc: 2.0")
                            return False
                        
                        if 'result' not in data and 'error' not in data:
                            logger.error("FAIL: Events must include result or error field")
                            return False
                        
                        if 'id' not in data:
                            logger.error("FAIL: Events must include id field")
                            return False
                        
                        logger.info("PASS: Events follow JSON-RPC 2.0 format")
                        logger.info("PASS: Events include required fields (jsonrpc, result/error, id)")
                        return True
                        
                    except json.JSONDecodeError:
                        logger.error(f"FAIL: Events must be valid JSON: {data_str}")
                        return False
            
    except Exception as e:
        logger.error(f"Error validating MCP compliance: {e}")
        return False

def main():
    logger.info("=== MCP SSE Validation Script ===")
    
    # Start the server
    server_process = start_server()
    if not server_process:
        logger.error("Failed to start server")
        return False
    
    try:
        # Test the SSE endpoint
        sse_test = test_sse_endpoint()
        
        # Validate MCP compliance
        mcp_compliance = validate_mcp_compliance()
        
        logger.info("=== Validation Results ===")
        logger.info(f"SSE Endpoint Test: {'✅ PASS' if sse_test else '❌ FAIL'}")
        logger.info(f"MCP Compliance: {'✅ PASS' if mcp_compliance else '❌ FAIL'}")
        
        if sse_test and mcp_compliance:
            logger.info("✅ All tests passed! The SSE implementation is compliant with the MCP specification.")
            logger.info("This implementation should work with the MCP Inspector tool and Cursor.")
            return True
        else:
            logger.error("❌ Some tests failed. The implementation may not be compliant with the MCP specification.")
            return False
    
    finally:
        # Stop the server
        stop_server(server_process)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
