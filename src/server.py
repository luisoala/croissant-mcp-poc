"""
Minimal MCP server implementation for Croissant datasets
"""
import asyncio
import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Croissant MCP Server",
    description="MCP server for Croissant datasets",
    version="1.0.0"
)

# Initialize MCP
mcp = FastMCP("Croissant MCP")

# API key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
API_KEY = "demo-key"  # Change in production

async def verify_api_key(api_key: Optional[str] = Depends(api_key_header)):
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key

# Dataset model
class Dataset(BaseModel):
    id: str
    name: str
    description: str
    format: str
    license: str
    provider: str

# In-memory dataset storage
datasets: Dict[str, Dataset] = {}

# MCP Resources
@mcp.resource("datasets://list")
async def list_datasets() -> List[Dataset]:
    """List all available datasets"""
    return list(datasets.values())

@mcp.resource("datasets://{dataset_id}")
async def get_dataset(dataset_id: str) -> Dataset:
    """Get a specific dataset by ID"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return datasets[dataset_id]

# MCP Tools
@mcp.tool()
async def search_datasets(query: str) -> List[Dataset]:
    """Search datasets by name or description"""
    query = query.lower()
    return [
        dataset for dataset in datasets.values()
        if query in dataset.name.lower() or query in dataset.description.lower()
    ]

@mcp.tool()
async def add_dataset(dataset: Dataset) -> Dataset:
    """Add a new dataset"""
    if dataset.id in datasets:
        raise HTTPException(status_code=400, detail="Dataset ID already exists")
    datasets[dataset.id] = dataset
    return dataset

# SSE endpoint for real-time updates
@app.get("/events")
async def events(request: Request):
    """SSE endpoint for real-time updates"""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            yield {
                "event": "dataset_count",
                "data": str(len(datasets))
            }
            await asyncio.sleep(1)
    
    return EventSourceResponse(event_generator())

# Mount MCP routes
app.include_router(mcp.app, prefix="/mcp")

# Load example datasets
def load_example_datasets():
    """Load example datasets on startup"""
    example_datasets = [
        Dataset(
            id="mnist",
            name="MNIST Handwritten Digits",
            description="A large collection of handwritten digits",
            format="numpy",
            license="CC BY-SA 3.0",
            provider="Yann LeCun"
        ),
        Dataset(
            id="iris",
            name="Iris Flower Dataset",
            description="A dataset for classification of iris flowers",
            format="csv",
            license="CC0",
            provider="UCI"
        ),
        Dataset(
            id="titanic",
            name="Titanic Passenger Dataset",
            description="Passenger information from the Titanic disaster",
            format="csv",
            license="CC0",
            provider="Kaggle"
        ),
        Dataset(
            id="croissant-llm",
            name="CroissantLLM Bilingual Dataset",
            description="A bilingual dataset for language model training",
            format="jsonl",
            license="MIT",
            provider="Croissant"
        )
    ]
    for dataset in example_datasets:
        datasets[dataset.id] = dataset

# Load example datasets on startup
load_example_datasets()
