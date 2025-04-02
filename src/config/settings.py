"""
Configuration settings for the Croissant MCP server
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Security
    API_KEY: str = "demo-key"  # Change in production
    
    # Data settings
    DATA_DIR: Path = Path("data")
    CROISSANT_DIR: Path = Path("samples")
    
    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(exist_ok=True)
settings.CROISSANT_DIR.mkdir(exist_ok=True) 