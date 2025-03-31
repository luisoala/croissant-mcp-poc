"""
Test script for verifying the MCP-compliant tools implementation
"""
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8000/messages"
API_KEY = "croissant-mcp-demo-key"

async def test_tools_list():
    """Test tools/list endpoint"""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    logger.info(f"Testing tools/list endpoint at {SERVER_URL}")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(SERVER_URL, json=payload, headers=headers) as response:
                logger.info(f"Status: {response.status}")
                if response.status != 200:
                    logger.error(f"Failed to get tools list: {response.status}")
                    return False
                
                data = await response.json()
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

async def test_tools_call(tool_name: str, arguments: Optional[Dict[str, Any]] = None):
    """Test tools/call endpoint"""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    
    logger.info(f"Testing tools/call endpoint for tool {tool_name} at {SERVER_URL}")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(SERVER_URL, json=payload, headers=headers) as response:
                logger.info(f"Status: {response.status}")
                if response.status != 200:
                    logger.error(f"Failed to call tool: {response.status}")
                    return False
                
                data = await response.json()
                logger.info(f"Response: {json.dumps(data, indent=2)}")
                
                if "result" not in data:
                    logger.error("Response missing result field")
                    return False
                
                if "content" not in data["result"]:
                    logger.error("Result missing content field")
                    return False
                
                return True
        except Exception as e:
            logger.error(f"Error testing tool call: {e}")
            return False

async def main():
    logger.info("=== Testing MCP-compliant Tools Implementation ===")
    
    tools_list_test = await test_tools_list()
    get_dataset_test = await test_tools_call("get_mnist_dataset")
    search_datasets_test = await test_tools_call("search_datasets", {"query": "images"})
    
    logger.info("=== Test Results ===")
    logger.info(f"Tools List: {'✅ PASS' if tools_list_test else '❌ FAIL'}")
    logger.info(f"Get Dataset Tool: {'✅ PASS' if get_dataset_test else '❌ FAIL'}")
    logger.info(f"Search Datasets Tool: {'✅ PASS' if search_datasets_test else '❌ FAIL'}")
    
    if tools_list_test and get_dataset_test and search_datasets_test:
        logger.info("✅ All tests passed! The MCP tools implementation is working correctly.")
    else: 
        logger.error("❌ Some tests failed. Check the server implementation.")

if __name__ == "__main__":
    asyncio.run(main())
