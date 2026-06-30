"""
HireGenius AI — Policy Schemas
================================
Pydantic models for HR policy upload, listing, and RAG-based Q&A.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PolicyUploadResponse(BaseModel):
    """Response after policy document upload."""
    id: int
    title: str
    file_name: Optional[str]
    is_embedded: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True


class PolicyResponse(BaseModel):
    """Policy document details."""
    id: int
    title: str
    file_name: Optional[str]
    content_preview: Optional[str] = None
    is_embedded: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True


class PolicyQueryRequest(BaseModel):
    """RAG-based policy question."""
    question: str = Field(..., min_length=5)


class PolicyQueryResponse(BaseModel):
    """RAG-generated answer to a policy question."""
    question: str
    answer: str
    source_policies: List[str] = []
    confidence: float = 0.0


class ChatMessage(BaseModel):
    """Chat message for HR Copilot."""
    message: str = Field(..., min_length=1)
    context: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response from HR Copilot."""
    response: str
    sources: List[Dict[str, Any]] = []
    suggestions: List[str] = []
