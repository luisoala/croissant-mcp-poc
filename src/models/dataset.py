"""
Dataset models for the Croissant MCP server
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class DataSource(str, Enum):
    DATAVERSE = "dataverse"
    HUGGINGFACE = "huggingface"
    KAGGLE = "kaggle"
    OPENML = "openml"

class DatasetFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    NUMPY = "numpy"
    OTHER = "other"

class Dataset(BaseModel):
    """Base dataset model"""
    id: str = Field(..., description="Unique identifier for the dataset")
    name: str = Field(..., description="Name of the dataset")
    description: str = Field(..., description="Description of the dataset")
    source: DataSource = Field(..., description="Source of the dataset")
    format: DatasetFormat = Field(..., description="Format of the dataset")
    url: str = Field(..., description="URL to the dataset")
    croissant_url: str = Field(..., description="URL to the Croissant file")
    license: Optional[str] = Field(None, description="License information")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the dataset")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    row_count: Optional[int] = Field(None, description="Number of rows in the dataset")
    size_bytes: Optional[int] = Field(None, description="Size of the dataset in bytes")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")

class DatasetPreview(BaseModel):
    """Dataset preview model"""
    dataset_id: str
    preview_data: List[Dict[str, Any]]
    total_rows: int
    columns: List[str]
    column_types: Dict[str, str]

class DatasetStats(BaseModel):
    """Dataset statistics model"""
    dataset_id: str
    row_count: int
    column_count: int
    size_bytes: int
    column_stats: Dict[str, Dict[str, Any]]
    last_updated: str 