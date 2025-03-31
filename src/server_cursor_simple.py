"""
Simplified MCP server implementation for Croissant datasets with Cursor-compatible API key authentication
"""
from mcp.server.fastmcp import FastMCP
import os
import json
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
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
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc", "/mcp/auth-info"]:
            return await call_next(request)
        
        if (request.url.path == "/mcp" or request.url.path == "/mcp/") and request.headers.get("Accept") == "text/event-stream":
            print(f"SSE connection from Cursor detected at {request.url.path}")
            
            if not hasattr(request.state, "sse_api_key_checked"):
                request.state.sse_api_key_checked = True
                
                api_key_param = None
                if "api_key" in request.query_params:
                    api_key_param = request.query_params["api_key"]
                    if api_key_param == API_KEY:
                        print(f"Valid API key found in query parameters for SSE connection to {request.url.path}")
                        request.state.has_valid_api_key = True
                        return await call_next(request)
                
                api_key_header = request.headers.get(API_KEY_NAME)
                if api_key_header == API_KEY:
                    print(f"Valid API key found in headers for SSE connection to {request.url.path}")
                    request.state.has_valid_api_key = True
                    return await call_next(request)
                
                print(f"Invalid or missing API key for SSE connection to {request.url.path}")
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Invalid or missing API key for SSE connection"}
                )
            
            if hasattr(request.state, "has_valid_api_key") and request.state.has_valid_api_key:
                return await call_next(request)
        
        api_key = request.headers.get(API_KEY_NAME)
        
        if not api_key and "api_key" in request.query_params:
            api_key = request.query_params["api_key"]
        
        if not api_key and request.method == "POST" and request.url.path.startswith("/mcp"):
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
    return {"status": "ok", "service": "Croissant MCP Server"}

@app.get("/info")
async def server_info():
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

try:
    class RedirectMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            original_path = request.url.path
            
            if request.url.path == "/mcp/" and request.headers.get("Accept") == "text/event-stream":
                print(f"Handling SSE connection to /mcp/ directly")
                
                api_key = request.headers.get(API_KEY_NAME)
                if not api_key and "api_key" in request.query_params:
                    api_key = request.query_params["api_key"]
                
                if api_key != API_KEY:
                    print(f"Invalid or missing API key for SSE connection to /mcp/")
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Invalid or missing API key for SSE connection"}
                    )
                
                print(f"Valid API key provided for SSE connection to /mcp/")
                
                from fastapi import FastAPI
                from mcp.server.fastmcp import FastMCP
                
                from starlette.responses import Response
                from sse_starlette.sse import EventSourceResponse
                
                async def event_generator():
                    yield {"data": json.dumps({"message": "Connected to Croissant MCP Server"})}
                
                return EventSourceResponse(event_generator())
            
            response = await call_next(request)
            return response
    
    app.add_middleware(RedirectMiddleware)
    
    mcp_app = mcp.sse_app()
    
    app.mount("/mcp", mcp_app)
    
    print("MCP server mounted at /mcp with Cursor-compatible API key authentication")
    print(f"API Key: {API_KEY}")
    print(f"API Key Header: {API_KEY_NAME}")
    print(f"API Key Environment Variable: {API_KEY_ENV_VAR}")
except Exception as e:
    print(f"Error mounting MCP server: {e}")
