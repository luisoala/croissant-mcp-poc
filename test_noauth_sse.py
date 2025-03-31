"""
Test script to verify the SSE endpoint can be accessed without authentication
"""
import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8000/sse"

async def test_sse_connection():
    """Test SSE connection without API key"""
    
    headers = {"Accept": "text/event-stream"}
    
    logger.info(f"Connecting to {SERVER_URL} without API key...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(SERVER_URL, headers=headers) as response:
                logger.info(f"Response status: {response.status}")
                
                if response.status == 200:
                    event_count = 0
                    async for line in response.content:
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line:
                            logger.info(f"Received: {decoded_line}")
                            if decoded_line.startswith('data:'):
                                try:
                                    data = json.loads(decoded_line[5:])
                                    logger.info(f"Parsed data: {json.dumps(data, indent=2)}")
                                except json.JSONDecodeError:
                                    logger.error("Failed to parse JSON data")
                            
                            event_count += 1
                            if event_count >= 3:  # Get 3 events then exit
                                break
                    
                    logger.info("Test successful: SSE connection established without API key")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Error response: {error_text}")
                    return False
        
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

async def main():
    """Run the SSE connection test"""
    logger.info("Starting SSE connection test...")
    success = await test_sse_connection()
    
    if success:
        logger.info("✅ Test passed: SSE endpoint can be accessed without API key")
    else:
        logger.error("❌ Test failed: Could not access SSE endpoint without API key")

if __name__ == "__main__":
    asyncio.run(main())
