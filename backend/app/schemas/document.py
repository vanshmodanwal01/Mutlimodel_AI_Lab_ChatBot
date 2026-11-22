from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    document_id: str
    session_id: str
    filename: str
    file_type: str
    file_size: int
    chunks_created: int
    processing_status: str
    created_at: datetime


class DocumentItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    filename: str
    file_type: str
    file_size: int
    processing_status: str
    chunk_count: int = 0
    created_at: datetime


class DocumentListResponse(BaseModel):
    session_id: str
    documents: List[DocumentItem]


class DocumentDeleteResponse(BaseModel):
    document_id: str
    success: bool
    message: str
