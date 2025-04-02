"""
Main server implementation for the Croissant MCP server
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from mcp.server.fastmcp import FastMCP
from modelcontextprotocol.server.fastapi import FastMCP as ModelContextProtocolFastMCP
from modelcontextprotocol.server.sse import SSEServerTransport
from modelcontextprotocol.server.types import Tool
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv

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

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
