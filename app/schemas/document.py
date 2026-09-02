from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class DocumentCreate(BaseModel):
    name: str
    file_type: str
    size: int


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    size: int
    page_count: Optional[int] = None
    created_at: datetime
    text: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    total: int
    items: List[DocumentResponse]


class DocumentStats(BaseModel):
    total_documents: int
    storage_used_bytes: int
    storage_used_mb: float
