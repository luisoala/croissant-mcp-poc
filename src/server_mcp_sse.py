"""
MCP-compliant SSE Server implementation for Croissant datasets
"""
import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY_NAME = "X-API-Key"
API_KEY = os.environ.get("MCP_API_KEY", "croissant-mcp-demo-key")

app = FastAPI(title="Croissant MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATASETS = [
    {
        "id": "imagenet",
        "name": "ImageNet",
        "description": "A large dataset of labeled images for computer vision research",
        "url": "https://www.image-net.org/",
        "format": "croissant",
        "license": "custom",
        "tags": ["images", "classification", "computer vision"]
    },
    {
        "id": "mnist",
        "name": "MNIST",
        "description": "Database of handwritten digits",
        "url": "http://yann.lecun.com/exdb/mnist/",
        "format": "croissant",
        "license": "MIT",
        "tags": ["images", "digits", "classification"]
    },
    {
        "id": "cifar10",
        "name": "CIFAR-10",
        "description": "Dataset of 60,000 32x32 color images in 10 classes",
        "url": "https://www.cs.toronto.edu/~kriz/cifar.html",
        "format": "croissant",
        "license": "MIT",
        "tags": ["images", "classification", "computer vision"]
    }
]

class JsonRpcResult:
    def __init__(self, result: Any, id: str):
        self.result = result
        self.id = id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "result": self.result,
            "id": self.id
        }

class JsonRpcError:
    def __init__(self, code: int, message: str, id: str):
        self.code = code
        self.message = message
        self.id = id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": self.code,
                "message": self.message
            },
            "id": self.id
        }

async def validate_api_key(request: Request) -> bool:
    """Validate API key from various sources"""
    if request.url.path in ["/", "/info", "/sse"]:
        return True

    api_key = request.headers.get(API_KEY_NAME)
    
    if not api_key:
        query_params = dict(request.query_params)
        for key, value in query_params.items():
            if key == "env.API_KEY":
                api_key = value
                break
    
    if api_key == API_KEY:
        logger.info(f"Valid API key provided for {request.url.path}")
        return True
    
    logger.warning(f"Invalid or missing API key for {request.url.path}")
    return False

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Middleware to check for valid API key for protected endpoints only"""
    if request.method == "OPTIONS":
        return await call_next(request)
    
    logger.info(f"Request to {request.url.path}, method: {request.method}")
    
    if request.url.path == "/sse":
        logger.info(f"SSE connection from {request.client.host}")
        return await call_next(request)
        
    is_valid = await validate_api_key(request)
    if is_valid:
        return await call_next(request)
    
    error_response = JsonRpcError(
        code=-32000,
        message="Invalid or missing API key. Provide the API key either:\n"
                "1. As 'X-API-Key' header\n"
                "2. As 'env.API_KEY' query parameter",
        id="1"
    ).to_dict()
    
    return JSONResponse(status_code=403, content=error_response)

@app.get("/")
async def root():
    return {"message": "Croissant MCP Server"}

@app.get("/info")
async def info():
    """Server information endpoint"""
    return {
        "name": "Croissant MCP Server",
        "version": "0.1.0",
        "description": "MCP server for Croissant datasets",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Root endpoint"},
            {"path": "/info", "method": "GET", "description": "Server information"},
            {"path": "/sse", "method": "GET", "description": "MCP SSE endpoint (no authentication required)"},
            {"path": "/datasets", "method": "GET", "description": "List all datasets (requires authentication)"},
            {"path": "/search", "method": "GET", "description": "Search datasets (requires authentication)"}
        ]
    }

@app.get("/datasets")
async def list_datasets():
    return {"datasets": DATASETS}

@app.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    for dataset in DATASETS:
        if dataset["id"] == dataset_id:
            return dataset
    raise HTTPException(status_code=404, detail="Dataset not found")

@app.get("/search")
async def search_datasets(query: str = ""):
    if not query:
        return {"datasets": DATASETS}
    
    results = []
    query = query.lower()
    for dataset in DATASETS:
        if (query in dataset["name"].lower() or 
            query in dataset["description"].lower() or 
            any(query in tag.lower() for tag in dataset["tags"])):
            results.append(dataset)
    
    return {"datasets": results}

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP without authentication"""
    if request.headers.get("Accept") != "text/event-stream":
        return JSONResponse(
            status_code=400,
            content={"detail": "This endpoint requires Accept: text/event-stream header"}
        )
    
    logger.info(f"SSE connection established from: {request.client.host}")
    
    async def event_generator():
        connection_data = JsonRpcResult(
            result={"status": "connected", "server": "Croissant MCP Server"},
            id="connection-1"
        ).to_dict()
        
        yield {
            "event": "message",
            "data": json.dumps(connection_data)
        }
        
        count = 0
        while True:
            count += 1
            heartbeat_data = JsonRpcResult(
                result={"type": "heartbeat", "count": count},
                id=f"heartbeat-{count}"
            ).to_dict()
            
            yield {
                "event": "message",
                "data": json.dumps(heartbeat_data)
            }
            
            await asyncio.sleep(5)
    
    return EventSourceResponse(event_generator())

@app.post("/messages")
async def messages_endpoint(request: Request):
    """Messages endpoint for client-to-server communication"""
    try:
        data = await request.json()
    except Exception as e:
        error_response = JsonRpcError(
            code=-32700,
            message="Parse error",
            id="1"
        ).to_dict()
        return JSONResponse(status_code=400, content=error_response)
    
    if not isinstance(data, dict):
        error_response = JsonRpcError(
            code=-32600,
            message="Invalid Request",
            id="1"
        ).to_dict()
        return JSONResponse(status_code=400, content=error_response)
    
    jsonrpc = data.get("jsonrpc")
    method = data.get("method")
    params = data.get("params", {})
    id_value = data.get("id", "1")
    id = str(id_value) if id_value is not None else "1"
    
    if jsonrpc != "2.0":
        error_response = JsonRpcError(
            code=-32600,
            message="Invalid Request",
            id=str(id) if id is not None else "1"
        ).to_dict()
        return JSONResponse(status_code=400, content=error_response)
    
    if not method:
        error_response = JsonRpcError(
            code=-32600,
            message="Invalid Request",
            id=str(id) if id is not None else "1"
        ).to_dict()
        return JSONResponse(status_code=400, content=error_response)
    
    if method == "search_datasets":
        query = params.get("query", "")
        results = []
        if query:
            query = query.lower()
            for dataset in DATASETS:
                if (query in dataset["name"].lower() or 
                    query in dataset["description"].lower() or 
                    any(query in tag.lower() for tag in dataset["tags"])):
                    results.append(dataset)
        else:
            results = DATASETS
        
        response = JsonRpcResult(
            result={"datasets": results},
            id=str(id) if id is not None else "1"
        ).to_dict()
        return JSONResponse(content=response)
    
    else:
        error_response = JsonRpcError(
            code=-32601,
            message="Method not found",
            id=str(id) if id is not None else "1"
        ).to_dict()
        return JSONResponse(status_code=404, content=error_response)
