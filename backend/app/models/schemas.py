from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    file_id: str
    name: str
    chunks_indexed: int
    status: str


class DocumentResponse(BaseModel):
    file_id: str
    name: str
    uploaded_at: datetime
    chunks: int
    status: str


class DocumentChunkResponse(BaseModel):
    file_id: str
    source: str
    chunk_index: int
    content: str


class DeleteDocumentResponse(BaseModel):
    deleted: bool
    file_id: str


class SourceResponse(BaseModel):
    chunk: str
    source: str
    score: float


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
    session_id: str