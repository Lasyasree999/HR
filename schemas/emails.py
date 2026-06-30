"""
HireGenius AI — Email Schemas
===============================
Pydantic models for AI-generated HR email communications.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EmailType(str, Enum):
    interview_invite = "interview_invite"
    rejection = "rejection"
    offer = "offer"
    followup = "followup"
    reminder = "reminder"


class GenerateEmailRequest(BaseModel):
    """Request to generate an HR email."""
    candidate_id: int
    email_type: EmailType
    job_id: Optional[int] = None
    additional_context: Optional[str] = None


class EmailResponse(BaseModel):
    """Generated email response."""
    id: int
    candidate_id: Optional[int]
    email_type: EmailType
    subject: str
    body: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class EmailListResponse(BaseModel):
    """List of generated emails."""
    emails: List[EmailResponse]
    total: int


class EmailUpdate(BaseModel):
    """Request to edit a generated email."""
    subject: Optional[str] = None
    body: Optional[str] = None
