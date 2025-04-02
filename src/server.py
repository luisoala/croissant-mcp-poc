"""
Main server implementation for the Croissant MCP server
"""
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server import FastMCP
import uvicorn
import logging
import os
import threading
from typing import Dict, List, Any
from functools import wraps
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette
from starlette.routing import Mount

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Croissant MCP Server", port=8000)

# Create Starlette app with CORS middleware
app = Starlette(
    debug=True,
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ],
    routes=[
        Mount("/", app=mcp.sse_app()),
    ],
)

# Decorator to ensure operations are executed in the main thread
def execute_on_main_thread(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return {"error": str(e)}
    return wrapper

@mcp.tool()
@execute_on_main_thread
def list_datasets() -> Dict[str, List[str]]:
    """List all available datasets"""
    return {"datasets": ["dataset1", "dataset2"]}

@mcp.tool()
@execute_on_main_thread
def search_datasets(query: str) -> Dict[str, List[str]]:
    """Search datasets by name, description, or tags"""
    return {"results": [f"Dataset matching {query}"]}

@mcp.tool()
@execute_on_main_thread
def get_dataset_metadata(dataset_id: str) -> Dict[str, Any]:
    """Get detailed metadata for a specific dataset"""
    return {"metadata": {"id": dataset_id, "name": "Sample Dataset"}}

@mcp.tool()
@execute_on_main_thread
def get_dataset_preview(dataset_id: str, rows: int = 5) -> Dict[str, Any]:
    """Get a preview of the dataset"""
    return {"preview": {"data": [{"column1": "value1"}]}}

@mcp.tool()
@execute_on_main_thread
def get_dataset_stats(dataset_id: str) -> Dict[str, Any]:
    """Get basic statistics about the dataset"""
    return {"stats": {"rows": 100, "columns": 5}}

@mcp.tool()
@execute_on_main_thread
def get_current_file_path() -> str:
    """Get the current path of the binary"""
    return os.getcwd()

@mcp.tool()
@execute_on_main_thread
def list_files_with_relative_path(relative_path: str = "") -> List[str]:
    """List all files in the specified relative path in the current directory"""
    base_dir = os.getcwd()
    if ':' in relative_path or '..' in relative_path or '//' in relative_path:
        return []
    if relative_path is None or relative_path == "":
        return os.listdir(base_dir)
    else:
        return os.listdir(os.path.join(base_dir, relative_path))

@mcp.tool()
@execute_on_main_thread
def read_file(relative_path: str) -> str:
    """Read the content of a file"""
    base_dir = os.getcwd()
    if ':' in relative_path or '..' in relative_path or '//' in relative_path:
        return "Invalid relative path"
    if relative_path == "":
        return "Relative path is required"
    with open(os.path.join(base_dir, relative_path), "r") as f:
        return f.read()

@mcp.tool()
@execute_on_main_thread
def write_file(relative_path: str, content: str) -> str:
    """Write content to a file"""
    base_dir = os.getcwd()
    if ':' in relative_path or '..' in relative_path or '//' in relative_path:
        return "Invalid relative path"
    if relative_path == "":
        return "Relative path is required"
    with open(os.path.join(base_dir, relative_path), "w") as f:
        f.write(content)
    return "File written successfully"

@mcp.tool()
@execute_on_main_thread
def read_binary(relative_path: str) -> bytes:
    """Read the content of a binary file"""
    base_dir = os.getcwd()
    if ':' in relative_path or '..' in relative_path or '//' in relative_path:
        return b"Invalid relative path"
    if relative_path == "":
        return b"Relative path is required"
    with open(os.path.join(base_dir, relative_path), "rb") as f:
        return f.read()

@mcp.tool()
@execute_on_main_thread
def write_binary(relative_path: str, content: bytes) -> str:
    """Write content to a binary file"""
    base_dir = os.getcwd()
    if ':' in relative_path or '..' in relative_path or '//' in relative_path:
        return "Invalid relative path"
    if relative_path == "":
        return "Relative path is required"
    with open(os.path.join(base_dir, relative_path), "wb") as f:
        f.write(content)
    return "File written successfully"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
