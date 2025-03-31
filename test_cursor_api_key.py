"""
Test script for verifying API key handling in the Cursor SSE endpoint
"""
import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8000/mcp"
API_KEY = "croissant-mcp-demo-key"

async def test_with_header():
    """Test SSE connection with X-API-Key header"""
    headers = {
        "Accept": "text/event-stream",
        "X-API-Key": API_KEY
    }
    
    logger.info(f"Testing connection with X-API-Key header")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(SERVER_URL, headers=headers) as response:
                logger.info(f"Status: {response.status}")
                return response.status == 200
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

async def test_with_query_param():
    """Test SSE connection with env.API_KEY query parameter"""
    headers = {"Accept": "text/event-stream"}
    url = f"{SERVER_URL}?env.API_KEY={API_KEY}"
    
    logger.info(f"Testing connection with env.API_KEY query parameter")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                logger.info(f"Status: {response.status}")
                return response.status == 200
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

async def test_with_invalid_key():
    """Test SSE connection with invalid API key"""
    headers = {
        "Accept": "text/event-stream",
        "X-API-Key": "invalid-key"
    }
    
    logger.info(f"Testing connection with invalid API key")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(SERVER_URL, headers=headers) as response:
                logger.info(f"Status: {response.status}")
                return response.status == 403
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

async def main():
    logger.info("=== Testing Cursor API Key Authentication ===")
    
    header_test = await test_with_header()
    query_test = await test_with_query_param()
    invalid_test = await test_with_invalid_key()
    
    logger.info("=== Test Results ===")
    logger.info(f"X-API-Key header: {'✅ PASS' if header_test else '❌ FAIL'}")
    logger.info(f"env.API_KEY query: {'✅ PASS' if query_test else '❌ FAIL'}")
    logger.info(f"Invalid API key: {'✅ PASS' if invalid_test else '❌ FAIL'}")
    
    if header_test and query_test and invalid_test:
        logger.info("✅ All tests passed! API key authentication is working correctly.")
    else:
        logger.error("❌ Some tests failed. Check the server implementation.")

if __name__ == "__main__":
    asyncio.run(main())
