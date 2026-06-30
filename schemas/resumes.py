"""
HireGenius AI — Resume Schemas
================================
Pydantic models for resume upload, parsing, and embedding responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ResumeUploadResponse(BaseModel):
    """Response after successful resume upload."""
    id: int
    candidate_id: int
    file_name: str
    uploaded_at: datetime
    status: str = "uploaded"

    class Config:
        from_attributes = True


class BulkUploadResponse(BaseModel):
    """Response after bulk resume upload."""
    uploaded: int
    failed: int
    results: List[Dict[str, Any]]


class ResumeParsedResponse(BaseModel):
    """Parsed resume data extracted by AI."""
    id: int
    candidate_id: int
    file_name: str
    parsed_data: Dict[str, Any]
    raw_text_preview: Optional[str] = None

    class Config:
        from_attributes = True


class ResumeParseResult(BaseModel):
    """Structured data extracted from a resume."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    certifications: List[str] = []
    total_years_experience: Optional[float] = None
    summary: Optional[str] = None
