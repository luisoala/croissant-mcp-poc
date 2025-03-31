"""
Test script for verifying the MCP-compliant SSE endpoint
"""
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8001/sse"
API_KEY = "croissant-mcp-demo-key"

async def test_sse_connection():
    """Test SSE connection without authentication"""
    headers = {"Accept": "text/event-stream"}
    
    logger.info(f"Testing SSE connection to {SERVER_URL}")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(SERVER_URL, headers=headers) as response:
                logger.info(f"Status: {response.status}")
                if response.status != 200:
                    logger.error(f"Failed to connect to SSE endpoint: {response.status}")
                    return False
                
                event_count = 0
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
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
                
                logger.info(f"Successfully received {event_count} valid events")
                return event_count > 0
        except Exception as e:
            logger.error(f"Error testing SSE connection: {e}")
            return False

async def test_authentication_required():
    """Test that other endpoints require authentication"""
    logger.info("Testing authentication requirements")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8001/datasets") as response:
                logger.info(f"Datasets endpoint without auth: {response.status}")
                if response.status != 403:
                    logger.error("Datasets endpoint should require authentication")
                    return False
            
            headers = {"X-API-Key": API_KEY}
            async with session.get("http://localhost:8001/datasets", headers=headers) as response:
                logger.info(f"Datasets endpoint with auth: {response.status}")
                if response.status != 200:
                    logger.error("Datasets endpoint authentication failed")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error testing authentication: {e}")
            return False

async def main():
    logger.info("=== Testing MCP-compliant SSE Implementation ===")
    
    sse_test = await test_sse_connection()
    auth_test = await test_authentication_required()
    
    logger.info("=== Test Results ===")
    logger.info(f"SSE Connection (no auth): {'✅ PASS' if sse_test else '❌ FAIL'}")
    logger.info(f"Authentication Requirements: {'✅ PASS' if auth_test else '❌ FAIL'}")
    
    if sse_test and auth_test:
        logger.info("✅ All tests passed! The MCP SSE implementation is compliant with the MCP specification.")
    else:
        logger.error("❌ Some tests failed. Check the server implementation.")

if __name__ == "__main__":
    asyncio.run(main())
