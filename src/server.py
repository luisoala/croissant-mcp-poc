"""
Main server implementation for the Croissant MCP server
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server.types import Tool
from typing import Dict, List, Optional, Any, TypeVar, Generic
import os
from dotenv import load_dotenv
import signal
import sys

from .config.settings import settings
from .tools import dataset_tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional API Key security
API_KEY = os.getenv("API_KEY")
if API_KEY:
    from fastapi.security import APIKeyHeader
    api_key_header = APIKeyHeader(name="X-API-Key")

    async def get_api_key(api_key: str = Security(api_key_header)):
        if api_key != API_KEY:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        return api_key

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting up Croissant MCP Server...")
    # Load datasets
    dataset_tools.load_sample_datasets()
    # Initialize MCP server
    mcp = FastMCP("Croissant MCP Server")
    yield
    # Shutdown
    logger.info("Shutting down Croissant MCP Server...")
    # Cleanup resources
    dataset_tools.datasets.clear()

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Croissant MCP Server",
    description="MCP server for Croissant datasets",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# SSE endpoint for real-time updates
@app.get("/events")
async def events(request: Request):
    """SSE endpoint for real-time updates with ping/pong"""
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    logger.info("Client disconnected")
                    break
                
                # Send ping every 30 seconds
                yield {
                    "event": "ping",
                    "data": "ping"
                }
                
                # Send dataset count
                yield {
                    "event": "dataset_count",
                    "data": str(len(dataset_tools.datasets))
                }
                
                # Wait before next update
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"Error in SSE connection: {e}")
            yield {
                "event": "error",
                "data": str(e)
            }
    
    return EventSourceResponse(
        event_generator(),
        ping=30000,  # Send ping every 30 seconds
        ping_message_factory=lambda: "ping"
    )

# Mount MCP routes
app.include_router(mcp.app, prefix="/mcp")

# Global state for graceful shutdown
shutdown_event = asyncio.Event()

@app.get("/shutdown")
async def shutdown_server():
    """Endpoint to gracefully shutdown the server"""
    shutdown_event.set()
    return {"message": "Server shutting down..."}

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    print("Starting up server...")
    # Add any startup initialization here

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    print("Shutting down server...")
    # Add any cleanup code here

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    config = uvicorn.Config(
        "src.server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        timeout_graceful_shutdown=5
    )
    
    server = uvicorn.Server(config)
    
    # Handle shutdown signal
    def handle_shutdown(sig, frame):
        print("Received shutdown signal")
        shutdown_event.set()
    
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("Received keyboard interrupt")
        shutdown_event.set()
    finally:
        print("Server shutdown complete")
