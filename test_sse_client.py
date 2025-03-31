"""
Simple SSE client to test communication with the MCP server
"""
import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "croissant-mcp-demo-key"
SERVER_URL = "http://localhost:8000/sse"

async def test_sse_connection():
    """Test SSE connection with various API key formats"""
    
    test_cases = [
        {
            "name": "env.API_KEY as query param",
            "url": f"{SERVER_URL}?env.API_KEY={API_KEY}",
            "headers": {"Accept": "text/event-stream"}
        },
        {
            "name": "URL encoded env.API_KEY",
            "url": f"{SERVER_URL}?env%2EAPI_KEY={API_KEY}",
            "headers": {"Accept": "text/event-stream"}
        },
        {
            "name": "X-API-Key header",
            "url": SERVER_URL,
            "headers": {
                "Accept": "text/event-stream",
                "X-API-Key": API_KEY
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test in test_cases:
            logger.info(f"\nTesting {test['name']}...")
            logger.info(f"URL: {test['url']}")
            logger.info(f"Headers: {test['headers']}")
            
            try:
                async with session.get(test['url'], headers=test['headers']) as response:
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
                                if event_count >= 3:  # Get 3 events then move to next test
                                    break
                    else:
                        error_text = await response.text()
                        logger.error(f"Error response: {error_text}")
            
            except Exception as e:
                logger.error(f"Connection error: {e}")
            
            logger.info("Test complete\n" + "="*50)

async def main():
    """Run the SSE connection tests"""
    logger.info("Starting SSE connection tests...")
    await test_sse_connection()

if __name__ == "__main__":
    asyncio.run(main())
