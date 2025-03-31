"""
API Key authentication middleware for FastAPI
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import os
from typing import Callable, Dict, Optional, List

class APIKeyMiddleware:
    """
    Middleware for API key authentication in FastAPI applications.
    
    This middleware checks for a valid API key in the request headers
    and rejects requests without a valid key.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        api_key_name: str = "X-API-Key",
        exclude_paths: Optional[List[str]] = None,
        allow_missing_api_key: bool = False
    ):
        """
        Initialize the API key middleware.
        
        Args:
            api_key: The API key to validate against. If None, uses MCP_API_KEY env var.
            api_key_name: The name of the header containing the API key.
            exclude_paths: List of paths to exclude from API key validation.
            allow_missing_api_key: Whether to allow requests without an API key.
        """
        self.api_key = api_key or os.environ.get("MCP_API_KEY", "croissant-mcp-demo-key")
        self.api_key_name = api_key_name
        self.exclude_paths = exclude_paths or ["/health", "/", "/docs", "/openapi.json", "/redoc"]
        self.allow_missing_api_key = allow_missing_api_key
    
    async def __call__(self, request: Request, call_next: Callable):
        """
        Process the request and validate the API key.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.
            
        Returns:
            The response from the next middleware or route handler.
        """
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        api_key = request.headers.get(self.api_key_name)
        
        if api_key == self.api_key:
            return await call_next(request)
        elif api_key is None and self.allow_missing_api_key:
            print(f"Warning: Request to {request.url.path} without API key")
            return await call_next(request)
        else:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid or missing API key"}
            )
