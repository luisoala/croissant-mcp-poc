"""
Croissant MCP Server with Cursor-compatible SSE endpoint and API key authentication
"""
import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable
from fastapi import FastAPI, Request, Response, HTTPException, Depends
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

class JsonRpcResponse:
    """Base class for JSON-RPC 2.0 responses"""
    def __init__(self, id: Optional[str] = None):
        self.jsonrpc = "2.0"
        self.id = id or "1"  # Default ID if none provided

    def to_dict(self) -> Dict[str, Any]:
        return {"jsonrpc": self.jsonrpc, "id": self.id}

class JsonRpcResult(JsonRpcResponse):
    """JSON-RPC 2.0 success response"""
    def __init__(self, result: Any, id: Optional[str] = None):
        super().__init__(id)
        self.result = result

    def to_dict(self) -> Dict[str, Any]:
        response = super().to_dict()
        response["result"] = self.result
        return response

class JsonRpcError(JsonRpcResponse):
    """JSON-RPC 2.0 error response"""
    def __init__(self, code: int, message: str, data: Any = None, id: Optional[str] = None):
        super().__init__(id)
        self.error = {
            "code": code,
            "message": message
        }
        if data:
            self.error["data"] = data

    def to_dict(self) -> Dict[str, Any]:
        response = super().to_dict()
        response["error"] = self.error
        return response

async def validate_api_key(request: Request) -> bool:
    """
    Validate API key from various sources:
    1. X-API-Key header
    2. api_key query parameter
    3. env.API_KEY in request body
    4. Authorization header (Bearer token)
    5. API_KEY in cookies
    """
    api_key_header = request.headers.get(API_KEY_NAME)
    if api_key_header and api_key_header == API_KEY:
        logger.info(f"Valid API key provided in header for {request.url.path}")
        return True

    api_key_param = request.query_params.get("api_key")
    if api_key_param and api_key_param == API_KEY:
        logger.info(f"Valid API key provided in query parameter for {request.url.path}")
        return True
    
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        if token == API_KEY:
            logger.info(f"Valid API key provided in Authorization header for {request.url.path}")
            return True

    api_key_cookie = request.cookies.get("API_KEY")
    if api_key_cookie and api_key_cookie == API_KEY:
        logger.info(f"Valid API key provided in cookie for {request.url.path}")
        return True

    env_api_key = request.query_params.get("env.API_KEY")
    if env_api_key and env_api_key == API_KEY:
        logger.info(f"Valid API key provided in env.API_KEY query parameter for {request.url.path}")
        return True
        
    api_key_env = request.query_params.get("API_KEY")
    if api_key_env and api_key_env == API_KEY:
        logger.info(f"Valid API key provided in API_KEY query parameter for {request.url.path}")
        return True
    
    logger.warning(f"Invalid or missing API key for {request.url.path}")
    return False

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Middleware to check for valid API key"""
    if request.method == "OPTIONS":
        return await call_next(request)
    
    if request.url.path == "/":
        return await call_next(request)
    
    if request.url.path == "/info":
        is_valid = await validate_api_key(request)
        if is_valid:
            logger.info(f"Valid API key provided for {request.url.path}")
        else:
            logger.info(f"No valid API key for {request.url.path}, but allowing access")
        return await call_next(request)
    
    is_valid = await validate_api_key(request)
    if is_valid:
        return await call_next(request)
    else:
        if request.url.path.startswith("/mcp") or request.url.path == "/sse":
            error_response = JsonRpcError(
                code=-32000, 
                message="Invalid or missing API key",
                id="1"  # Default ID
            ).to_dict()
            return JSONResponse(status_code=403, content=error_response)
        else:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid or missing API key"}
            )

@app.get("/")
async def root():
    return {"message": "Croissant MCP Server"}

@app.get("/info")
async def info():
    return {
        "name": "Croissant MCP Server",
        "version": "0.1.0",
        "description": "MCP server for Croissant datasets",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Root endpoint"},
            {"path": "/info", "method": "GET", "description": "Server information"},
            {"path": "/sse", "method": "GET", "description": "MCP SSE endpoint for Cursor"},
            {"path": "/mcp", "method": "POST", "description": "MCP JSON-RPC endpoint"},
            {"path": "/datasets", "method": "GET", "description": "List all datasets"},
            {"path": "/datasets/{dataset_id}", "method": "GET", "description": "Get dataset by ID"},
            {"path": "/search", "method": "GET", "description": "Search datasets"}
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
    """SSE endpoint for Cursor MCP integration"""
    logger.info(f"SSE connection from Cursor to {request.url.path}")
    
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

@app.get("/mcp")
@app.get("/mcp/")
async def mcp_sse(request: Request):
    """Legacy SSE endpoint for MCP"""
    if request.headers.get("Accept") != "text/event-stream":
        return JSONResponse(
            status_code=400,
            content={"detail": "This endpoint requires Accept: text/event-stream header"}
        )
    
    logger.info(f"SSE connection from client to {request.url.path} - redirecting to /sse")
    
    return Response(
        status_code=307,
        headers={"Location": "/sse"}
    )

@app.post("/mcp")
@app.post("/mcp/")
async def mcp_jsonrpc(request: Request):
    """JSON-RPC endpoint for MCP"""
    try:
        data = await request.json()
    except Exception as e:
        error_response = JsonRpcError(
            code=-32700,
            message="Parse error",
            data=str(e)
        ).to_dict()
        return JSONResponse(status_code=400, content=error_response)
    
    if not isinstance(data, dict):
        error_response = JsonRpcError(
            code=-32600,
            message="Invalid Request",
            data="Request must be a JSON object"
        ).to_dict()
        return JSONResponse(status_code=400, content=error_response)
    
    jsonrpc = data.get("jsonrpc")
    method = data.get("method")
    params = data.get("params", {})
    id = data.get("id")
    
    if jsonrpc != "2.0":
        error_response = JsonRpcError(
            code=-32600,
            message="Invalid Request",
            data="jsonrpc field must be '2.0'",
            id=id
        ).to_dict()
        return JSONResponse(status_code=400, content=error_response)
    
    if not method:
        error_response = JsonRpcError(
            code=-32600,
            message="Invalid Request",
            data="method field is required",
            id=id
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
            id=id
        ).to_dict()
        return JSONResponse(content=response)
    
    elif method == "get_dataset":
        dataset_id = params.get("id")
        if not dataset_id:
            error_response = JsonRpcError(
                code=-32602,
                message="Invalid params",
                data="id parameter is required",
                id=id
            ).to_dict()
            return JSONResponse(status_code=400, content=error_response)
        
        for dataset in DATASETS:
            if dataset["id"] == dataset_id:
                response = JsonRpcResult(
                    result={"dataset": dataset},
                    id=id
                ).to_dict()
                return JSONResponse(content=response)
        
        error_response = JsonRpcError(
            code=-32001,
            message="Dataset not found",
            id=id
        ).to_dict()
        return JSONResponse(status_code=404, content=error_response)
    
    else:
        error_response = JsonRpcError(
            code=-32601,
            message="Method not found",
            data=f"Method '{method}' is not supported",
            id=id
        ).to_dict()
        return JSONResponse(status_code=404, content=error_response)
