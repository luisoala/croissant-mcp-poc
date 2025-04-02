"""
Main entry point for the Croissant MCP Server
"""
import os
import sys
import logging
import uvicorn
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.error(f"Failed to load environment variables: {e}")
    sys.exit(1)

# Import the FastAPI app
try:
    from src.server import app
except ImportError as e:
    logger.error(f"Failed to import server app: {e}")
    sys.exit(1)

if __name__ == "__main__":
    try:
        # Get port from environment or default to 8000
        port = int(os.environ.get("PORT", 8000))
        
        logger.info(f"Starting Croissant MCP Server on port {port}...")
        logger.info("Available endpoints:")
        logger.info(f"- Health check: http://0.0.0.0:{port}/health")
        logger.info(f"- MCP endpoints: http://0.0.0.0:{port}/mcp")
        logger.info(f"- SSE events: http://0.0.0.0:{port}/events")
        logger.info(f"- API docs: http://0.0.0.0:{port}/docs")
        
        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
