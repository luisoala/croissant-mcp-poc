"""
Croissant MCP Server using the official MCP SDK
"""
import logging
import json
import mcp.types as types
from typing import Dict, Any, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("croissant-mcp-server")

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

get_imagenet_tool = types.Tool(
    name="get_imagenet_dataset",
    description="Get information about the ImageNet dataset: A large dataset of labeled images for computer vision research",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

get_mnist_tool = types.Tool(
    name="get_mnist_dataset",
    description="Get information about the MNIST dataset: Database of handwritten digits",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

get_cifar10_tool = types.Tool(
    name="get_cifar10_dataset",
    description="Get information about the CIFAR-10 dataset: Dataset of 60,000 32x32 color images in 10 classes",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

search_tool = types.Tool(
    name="search_datasets",
    description="Search for datasets by name, description, or tags",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string"
            }
        },
        "required": ["query"]
    }
)

server = Server("Croissant MCP Server")

@server.list_tools()
def list_tools() -> List[types.Tool]:
    """List available Croissant dataset tools."""
    return [get_imagenet_tool, get_mnist_tool, get_cifar10_tool, search_tool]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls for Croissant datasets."""
    logger.info(f"Calling tool {name} with arguments {arguments}")
    
    try:
        if name == "get_imagenet_dataset":
            dataset = next(d for d in DATASETS if d["id"] == "imagenet")
            return [types.TextContent(type="text", text=json.dumps(dataset, indent=2))]
            
        elif name == "get_mnist_dataset":
            dataset = next(d for d in DATASETS if d["id"] == "mnist")
            return [types.TextContent(type="text", text=json.dumps(dataset, indent=2))]
            
        elif name == "get_cifar10_dataset":
            dataset = next(d for d in DATASETS if d["id"] == "cifar10")
            return [types.TextContent(type="text", text=json.dumps(dataset, indent=2))]
            
        elif name == "search_datasets":
            query = arguments.get("query", "").lower()
            results = []
            
            if query:
                for dataset in DATASETS:
                    if (query in dataset["name"].lower() or 
                        query in dataset["description"].lower() or 
                        any(query in tag.lower() for tag in dataset["tags"])):
                        results.append(dataset)
            else:
                results = DATASETS
            
            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
        
        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool {name}")]
    
    except Exception as e:
        logger.error(f"Tool error: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def get_initialization_options() -> InitializationOptions:
    """Get server initialization options."""
    return InitializationOptions(
        server_name="Croissant MCP Server",
        server_version="0.1.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(resources_changed=True),
            experimental_capabilities={},
        ),
    )
