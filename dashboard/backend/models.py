"""
Pydantic models for the dashboard API
"""
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    GENERATED = "generated"
    REFINING = "refining"
    REFINED = "refined"
    VALIDATING = "validating"
    VALIDATED = "validated"
    FAILED = "failed"


class DocumentInfo(BaseModel):
    id: str
    title: str
    status: DocumentStatus
    file_size: Optional[int] = 0
    refined_count: int = 0
    generated_at: Optional[datetime] = None
    elapsed_time: Optional[float] = None
    error_message: Optional[str] = None
    dependencies: List[str] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class GenerationSummary(BaseModel):
    total_documents: int = 10
    completed: int = 0
    in_progress: int = 0
    failed: int = 0
    not_started: int = 0
    overall_progress: float = 0.0
    estimated_time_remaining: Optional[float] = None
    average_document_time: Optional[float] = None
    documents: Dict[str, DocumentInfo] = {}
    generation_started_at: Optional[datetime] = None
    generation_completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class StatusUpdate(BaseModel):
    """WebSocket status update message"""
    type: str = "status_update"
    timestamp: datetime
    document_id: Optional[str] = None
    status: Optional[DocumentStatus] = None
    progress: Optional[float] = None
    message: Optional[str] = None
    summary: Optional[GenerationSummary] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LogEntry(BaseModel):
    """Log entry from orchestrator"""
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR
    message: str
    document_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }