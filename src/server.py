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
import json
import glob
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

# Constants
SAMPLES_DIR = "samples"
CROISSANT_FILES = ["openml_test_croissant.json", "kaggle_test_croissant.json", 
                   "hf_test_croissant.json", "dataverse_test_croissant.json"]

def load_croissant_file(filename: str) -> Dict:
    """Helper function to load a Croissant JSON file"""
    file_path = os.path.join(SAMPLES_DIR, filename)
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        return {}

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
    datasets = []
    for filename in CROISSANT_FILES:
        data = load_croissant_file(filename)
        if data and 'name' in data:
            datasets.append(data['name'])
    return {"datasets": datasets}

@mcp.tool()
@execute_on_main_thread
def search_datasets(query: str) -> Dict[str, List[str]]:
    """Search datasets by name, description, or tags"""
    results = []
    query = query.lower()
    
    for filename in CROISSANT_FILES:
        data = load_croissant_file(filename)
        if not data:
            continue
            
        # Search in name
        if 'name' in data and query in data['name'].lower():
            results.append(data['name'])
            continue
            
        # Search in description
        if 'description' in data and query in data['description'].lower():
            results.append(data['name'])
            continue
            
        # Search in keywords/tags if they exist
        if 'keywords' in data:
            if any(query in keyword.lower() for keyword in data['keywords']):
                results.append(data['name'])
                
    return {"results": results}

@mcp.tool()
@execute_on_main_thread
def get_dataset_metadata(dataset_id: str) -> Dict[str, Any]:
    """Get detailed metadata for a specific dataset"""
    for filename in CROISSANT_FILES:
        data = load_croissant_file(filename)
        if data and data.get('name') == dataset_id:
            return {
                "metadata": {
                    "id": dataset_id,
                    "name": data.get('name'),
                    "description": data.get('description'),
                    "keywords": data.get('keywords', []),
                    "creators": data.get('creators', []),
                    "license": data.get('license', ''),
                    "source": filename.split('_')[0]  # e.g., 'openml', 'kaggle', etc.
                }
            }
    return {"metadata": {"id": dataset_id, "error": "Dataset not found"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
