"""
Completely redesigned MCP server implementation for Croissant datasets with Cursor-compatible API key authentication
and proper JSON-RPC format for SSE connections
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sse_starlette.sse import EventSourceResponse
import json
import os
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator

from mcp.server.fastmcp import FastMCP

class JsonRpcRequest:
    """JSON-RPC 2.0 request"""
    def __init__(self, method: str, params: Optional[Dict] = None, id: Optional[str] = None):
        self.jsonrpc = "2.0"
        self.method = method
        self.params = params or {}
        self.id = id
        
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
            "id": self.id
        }

class JsonRpcResponse:
    """JSON-RPC 2.0 response"""
    def __init__(self, result: Any, id: Optional[str] = None):
        self.jsonrpc = "2.0"
        self.result = result
        self.id = id
        
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "jsonrpc": self.jsonrpc,
            "result": self.result,
            "id": self.id
        }

class JsonRpcError:
    """JSON-RPC 2.0 error"""
    def __init__(self, code: int, message: str, data: Optional[Any] = None, id: Optional[str] = None):
        self.jsonrpc = "2.0"
        self.error = {
            "code": code,
            "message": message
        }
        if data:
            self.error["data"] = data
        self.id = id
        
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "jsonrpc": self.jsonrpc,
            "error": self.error,
            "id": self.id
        }

from dataset_index import CroissantDatasetIndex
from search import CroissantSearch

API_KEY = os.environ.get("MCP_API_KEY", "croissant-mcp-demo-key")
API_KEY_NAME = "X-API-Key"
API_KEY_ENV_VAR = "API_KEY"  # Environment variable name for Cursor integration

dataset_index = CroissantDatasetIndex()
dataset_index.load_example_datasets()
search_engine = CroissantSearch(dataset_index)

app = FastAPI(title="Croissant MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware for API key authentication"""
    
    async def dispatch(self, request: Request, call_next):
        """Dispatch method for middleware"""
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc", "/mcp/auth-info"]:
            return await call_next(request)
        
        api_key = None
        
        api_key = request.headers.get(API_KEY_NAME)
        
        if not api_key and "api_key" in request.query_params:
            api_key = request.query_params["api_key"]
        
        if not api_key and request.method == "POST":
            try:
                body_bytes = await request.body()
                body = json.loads(body_bytes)
                
                if "env" in body and API_KEY_ENV_VAR in body["env"]:
                    api_key = body["env"][API_KEY_ENV_VAR]
                    print(f"Found API key in request body env.{API_KEY_ENV_VAR}")
                
                async def get_body():
                    return body_bytes
                
                request._body = body_bytes
                request.body = get_body
                
            except Exception as e:
                print(f"Error parsing request body: {e}")
        
        if api_key == API_KEY:
            print(f"Valid API key provided for {request.url.path}")
            return await call_next(request)
        
        if not request.url.path.startswith("/mcp"):
            print(f"Warning: Request to {request.url.path} without API key")
            return await call_next(request)
        
        print(f"Invalid or missing API key for {request.url.path}")
        return JSONResponse(
            status_code=403,
            content={"detail": "Invalid or missing API key"}
        )

app.add_middleware(APIKeyMiddleware)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "Croissant MCP Server"}

@app.get("/info")
async def server_info():
    """Server information endpoint"""
    return {
        "name": "Croissant Dataset Index",
        "version": "0.1.0",
        "description": "MCP server for Croissant datasets across multiple platforms",
        "datasets_count": len(dataset_index.list_datasets()),
        "providers": search_engine.get_available_providers(),
        "auth_method": "api_key",
        "api_key_header": API_KEY_NAME,
        "api_key_env_var": API_KEY_ENV_VAR
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Croissant MCP Server", "docs": "/docs", "mcp": "/mcp"}

@app.get("/mcp/auth-info")
async def mcp_auth_info():
    """Return authentication information for MCP clients"""
    return {
        "auth_method": "api_key",
        "api_key_header": API_KEY_NAME,
        "api_key_env_var": API_KEY_ENV_VAR,
        "default_key": "croissant-mcp-demo-key"
    }

mcp = FastMCP("Croissant Dataset Index")

@mcp.resource("datasets://list")
def list_datasets() -> str:
    """List all available datasets in the index"""
    return json.dumps(dataset_index.list_datasets())

@mcp.resource("datasets://{dataset_id}")
def get_dataset(dataset_id: str) -> str:
    """Get information about a specific dataset"""
    dataset = dataset_index.get_dataset(dataset_id)
    if dataset:
        return json.dumps(dataset)
    return json.dumps({"error": f"Dataset {dataset_id} not found"})

@mcp.tool()
def search_datasets(query: str = "") -> str:
    """
    Basic search for datasets matching the query
    
    Args:
        query: Text to search for in dataset name and description
    """
    results = dataset_index.search(query)
    return json.dumps(results)

@mcp.tool()
def advanced_search(
    query: str = "", 
    provider: str = "", 
    data_format: str = "",
    license_type: str = "",
    keywords: str = "",
    sort_by: str = "relevance",
    page: int = 1,
    page_size: int = 10
) -> str:
    """
    Advanced search for datasets with filtering, sorting, and pagination
    
    Args:
        query: Text to search for in name and description
        provider: Filter by data provider (e.g., "Hugging Face", "Kaggle")
        data_format: Filter by data format (e.g., "csv", "parquet")
        license_type: Filter by license type
        keywords: Comma-separated list of keywords to filter by
        sort_by: Sort results by ("relevance", "name", "provider")
        page: Page number for pagination
        page_size: Number of results per page
    """
    keyword_list = None
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",")]
        
    results, total_count = search_engine.search(
        query=query,
        provider=provider if provider else None,
        data_format=data_format if data_format else None,
        license_type=license_type if license_type else None,
        keywords=keyword_list,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )
    
    return json.dumps({
        "results": results,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size
    })

@mcp.tool()
def get_search_options() -> str:
    """Get available options for search filters"""
    options = {
        "providers": search_engine.get_available_providers(),
        "formats": search_engine.get_available_formats(),
        "licenses": search_engine.get_available_licenses(),
        "keywords": search_engine.get_all_keywords(),
        "sort_options": ["relevance", "name", "provider"]
    }
    return json.dumps(options)

@mcp.tool()
def add_dataset(dataset_id: str, metadata: str) -> str:
    """Add a new dataset to the index"""
    try:
        metadata_dict = json.loads(metadata)
        dataset_index.add_dataset(dataset_id, metadata_dict)
        return json.dumps({"success": True, "message": f"Dataset {dataset_id} added to index"})
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON metadata"})

@mcp.prompt()
def dataset_search_prompt() -> str:
    """Prompt for searching datasets"""
    return """
    You can search for Croissant datasets across multiple platforms:
    
    Basic Search:
    - Search for datasets by topic, name, or description
    
    Advanced Search:
    - Filter by provider (Hugging Face, Kaggle, OpenML, Dataverse)
    - Filter by data format (CSV, Parquet, etc.)
    - Filter by license type
    - Filter by keywords
    - Sort results by relevance, name, or provider
    - Paginate through results
    
    Examples:
    - "Search for image datasets"
    - "Find datasets from Kaggle about machine learning"
    - "Show me datasets with CSV format"
    """

async def generate_sse_events(request: Request) -> AsyncGenerator[Dict, None]:
    """Generate SSE events with proper JSON-RPC format"""
    yield {
        "data": json.dumps({
            "jsonrpc": "2.0",
            "id": "connection-established",
            "result": {
                "status": "connected",
                "server": "Croissant MCP Server",
                "message": "Connected to Croissant MCP Server"
            }
        })
    }
    
    counter = 0
    while True:
        await asyncio.sleep(30)  # Send heartbeat every 30 seconds
        counter += 1
        yield {
            "data": json.dumps({
                "jsonrpc": "2.0",
                "id": f"heartbeat-{counter}",
                "result": {
                    "type": "heartbeat",
                    "timestamp": counter
                }
            })
        }

@app.get("/mcp/sse")
async def mcp_sse(request: Request):
    """SSE endpoint for MCP with proper JSON-RPC format"""
    api_key = request.headers.get(API_KEY_NAME)
    if not api_key and "api_key" in request.query_params:
        api_key = request.query_params["api_key"]
    
    if api_key != API_KEY:
        return JSONResponse(
            status_code=403,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32000,
                    "message": "Invalid or missing API key"
                }
            }
        )
    
    print(f"Valid API key provided for SSE connection to /mcp/sse")
    return EventSourceResponse(generate_sse_events(request))

@app.post("/mcp/jsonrpc")
async def mcp_jsonrpc(request: Request):
    """JSON-RPC endpoint for MCP"""
    try:
        body = await request.json()
        
        if "jsonrpc" not in body or body["jsonrpc"] != "2.0":
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: missing or invalid jsonrpc version"
                    }
                }
            )
        
        if "method" not in body:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: missing method"
                    }
                }
            )
        
        method = body["method"]
        params = body.get("params", {})
        request_id = body.get("id")
        
        if method == "search_datasets":
            result = search_datasets(**params)
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": json.loads(result)
                }
            )
        elif method == "advanced_search":
            result = advanced_search(**params)
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": json.loads(result)
                }
            )
        elif method == "get_search_options":
            result = get_search_options()
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": json.loads(result)
                }
            )
        elif method == "list_datasets":
            result = list_datasets()
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": json.loads(result)
                }
            )
        elif method == "get_dataset":
            if "dataset_id" not in params:
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: missing dataset_id"
                        }
                    }
                )
            result = get_dataset(params["dataset_id"])
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": json.loads(result)
                }
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            )
    except Exception as e:
        print(f"Error processing JSON-RPC request: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        )

try:
    mcp_app = mcp.sse_app()
    
    app.mount("/mcp", mcp_app)
    app.mount("/mcp/", mcp_app)
    
    print("MCP server mounted at /mcp and /mcp/ with Cursor-compatible API key authentication")
    print(f"API Key: {API_KEY}")
    print(f"API Key Header: {API_KEY_NAME}")
    print(f"API Key Environment Variable: {API_KEY_ENV_VAR}")
    print("Custom SSE endpoint available at /mcp/sse")
    print("Custom JSON-RPC endpoint available at /mcp/jsonrpc")
except Exception as e:
    print(f"Error mounting MCP server: {e}")
