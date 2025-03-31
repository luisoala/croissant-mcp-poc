"""
Middleware for handling Cursor-compatible API key authentication
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
import json

API_KEY = os.environ.get("MCP_API_KEY", "croissant-mcp-demo-key")
API_KEY_ENV_VAR = "API_KEY"  # Environment variable name for Cursor integration

class CursorAPIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling Cursor-compatible API key authentication
    
    This middleware checks for API keys in:
    1. Request headers (X-API-Key)
    2. Query parameters (api_key)
    3. Request body for POST requests (env.API_KEY)
    
    It allows SSE connections to /mcp endpoint without authentication
    """
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc", "/mcp/auth-info"]:
            return await call_next(request)
        
        if request.url.path == "/mcp" and request.headers.get("Accept") == "text/event-stream":
            print("SSE connection from Cursor detected - allowing without header auth")
            return await call_next(request)
        
        api_key = request.headers.get("X-API-Key")
        
        if not api_key and "api_key" in request.query_params:
            api_key = request.query_params["api_key"]
        
        if not api_key and request.method == "POST" and request.url.path.startswith("/mcp"):
            try:
                body = await request.json()
                if "env" in body and API_KEY_ENV_VAR in body["env"]:
                    api_key = body["env"][API_KEY_ENV_VAR]
                    print(f"Found API key in request body env.{API_KEY_ENV_VAR}")
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
