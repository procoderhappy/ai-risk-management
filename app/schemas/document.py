"""
Document-related Pydantic schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentBase(BaseModel):
    filename: str
    file_type: Optional[str] = None


class DocumentUpload(BaseModel):
    filename: str
    content: bytes
    content_type: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: Optional[int]
    file_type: Optional[str]
    processed: bool
    processing_status: ProcessingStatus
    uploaded_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentAnalysisResponse(BaseModel):
    id: int
    document_id: int
    analysis_type: str
    results: Dict[str, Any]
    confidence: Optional[float]
    processing_time: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentProcessingRequest(BaseModel):
    document_id: int
    analysis_types: List[str] = ["sentiment", "entity_extraction", "classification"]


class DocumentSearchRequest(BaseModel):
    query: str
    file_types: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 10


class DocumentSearchResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    per_page: int