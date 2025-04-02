"""
Dataset tools for the Croissant MCP server
"""
from typing import List, Dict, Any, Optional, TypeVar, Generic
from mcp.tool import tool
from ..models.dataset import Dataset, DatasetPreview, DatasetStats, DataSource, DatasetFormat
from ..config.settings import settings
import json
import os
from datetime import datetime
from pydantic import ValidationError

# Type variable for generic responses
T = TypeVar('T')

class ToolResponse(Generic[T]):
    """Generic response wrapper for tool results"""
    def __init__(self, data: T):
        self.data = data
        self.timestamp = datetime.now().isoformat()

# In-memory dataset storage
datasets: Dict[str, Dataset] = {}

def load_sample_datasets() -> None:
    """Load sample datasets from the samples directory"""
    for filename in os.listdir(settings.CROISSANT_DIR):
        if filename.endswith('_croissant.json'):
            source = filename.split('_')[0]
            try:
                with open(settings.CROISSANT_DIR / filename) as f:
                    data = json.load(f)
                    dataset = Dataset(
                        id=f"{source}_{data.get('name', 'unnamed')}",
                        name=data.get('name', 'Unnamed Dataset'),
                        description=data.get('description', ''),
                        source=DataSource(source.upper()),
                        format=DatasetFormat(data.get('format', 'OTHER')),
                        url=data.get('url', ''),
                        croissant_url=data.get('croissant_url', ''),
                        license=data.get('license'),
                        tags=data.get('tags', []),
                        metadata=data.get('metadata', {}),
                        last_updated=datetime.now().isoformat()
                    )
                    datasets[dataset.id] = dataset
            except ValidationError as e:
                logger.error(f"Validation error loading dataset {filename}: {e}")
            except Exception as e:
                logger.error(f"Error loading dataset {filename}: {e}")

@tool()
async def list_datasets() -> ToolResponse[List[Dataset]]:
    """List all available datasets"""
    return ToolResponse(list(datasets.values()))

@tool()
async def search_datasets(query: str) -> ToolResponse[List[Dataset]]:
    """Search datasets by name, description, or tags"""
    query = query.lower()
    results = [
        dataset for dataset in datasets.values()
        if query in dataset.name.lower() 
        or query in dataset.description.lower()
        or any(query in tag.lower() for tag in dataset.tags)
    ]
    return ToolResponse(results)

@tool()
async def get_dataset_metadata(dataset_id: str) -> ToolResponse[Dataset]:
    """Get detailed metadata for a specific dataset"""
    if dataset_id not in datasets:
        raise ValueError(f"Dataset {dataset_id} not found")
    return ToolResponse(datasets[dataset_id])

@tool()
async def get_dataset_preview(dataset_id: str, rows: int = 5) -> ToolResponse[DatasetPreview]:
    """Get a preview of the dataset"""
    if dataset_id not in datasets:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    # TODO: Implement actual data preview logic
    # For now, return mock data
    preview = DatasetPreview(
        dataset_id=dataset_id,
        preview_data=[{"column1": "value1", "column2": "value2"}],
        total_rows=100,
        columns=["column1", "column2"],
        column_types={"column1": "string", "column2": "string"}
    )
    return ToolResponse(preview)

@tool()
async def get_dataset_stats(dataset_id: str) -> ToolResponse[DatasetStats]:
    """Get basic statistics about the dataset"""
    if dataset_id not in datasets:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    # TODO: Implement actual statistics calculation
    # For now, return mock data
    stats = DatasetStats(
        dataset_id=dataset_id,
        row_count=100,
        column_count=2,
        size_bytes=1024,
        column_stats={
            "column1": {"type": "string", "unique_values": 10},
            "column2": {"type": "string", "unique_values": 5}
        },
        last_updated=datetime.now().isoformat()
    )
    return ToolResponse(stats)

@tool()
async def list_sources() -> ToolResponse[List[str]]:
    """List all data sources"""
    return ToolResponse([source.value for source in DataSource])

@tool()
async def get_source_datasets(source: str) -> ToolResponse[List[Dataset]]:
    """Get all datasets from a specific source"""
    try:
        source_enum = DataSource(source.upper())
    except ValueError:
        raise ValueError(f"Invalid source: {source}")
    
    results = [
        dataset for dataset in datasets.values()
        if dataset.source == source_enum
    ]
    return ToolResponse(results)

@tool()
async def validate_dataset(dataset_id: str) -> ToolResponse[Dict[str, Any]]:
    """Validate a Croissant file against the spec"""
    if dataset_id not in datasets:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    # TODO: Implement actual validation logic
    result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    return ToolResponse(result)

# Load sample datasets on module import
load_sample_datasets() 