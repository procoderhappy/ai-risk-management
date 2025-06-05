"""
Configuration management for AI Risk Management System
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Risk Management & Compliance System"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite:///./risk_management.db"
    
    # AI/ML Configuration
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_TOKENS: int = 4096
    EMBEDDING_DIMENSION: int = 384
    VECTOR_DB_PATH: str = "./data/vector_db"
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".docx", ".txt", ".csv", ".xlsx"]
    UPLOAD_DIR: str = "./data/uploads"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Regional Compliance
    SUPPORTED_REGIONS: List[str] = ["US", "EU", "UK", "APAC"]
    DEFAULT_REGION: str = "US"
    
    # Performance
    CACHE_TTL: int = 3600  # 1 hour
    MAX_WORKERS: int = 4
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        if v == "your-secret-key-change-in-production":
            raise ValueError("Please change the default secret key")
        return v
    
    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()