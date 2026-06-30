"""
HireGenius AI — Job Schemas
============================
Pydantic models for job creation, update, listing, and AI description generation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    open = "open"
    closed = "closed"
    on_hold = "on_hold"


class JobCreate(BaseModel):
    """Request model for creating a new job posting."""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    required_skills: Optional[str] = None
    experience_range: Optional[str] = None
    department: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    status: JobStatus = JobStatus.open


class JobUpdate(BaseModel):
    """Request model for updating an existing job posting."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    required_skills: Optional[str] = None
    experience_range: Optional[str] = None
    department: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    status: Optional[JobStatus] = None


class JobResponse(BaseModel):
    """Job posting response with all details."""
    id: int
    title: str
    description: str
    required_skills: Optional[str] = None
    experience_range: Optional[str] = None
    department: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    status: JobStatus
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    candidate_count: Optional[int] = 0

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Paginated list of jobs."""
    jobs: List[JobResponse]
    total: int
    page: int = 1
    per_page: int = 20


class GenerateJDRequest(BaseModel):
    """Request for AI-generated job description."""
    title: str = Field(..., min_length=3)
    department: Optional[str] = None
    required_skills: Optional[str] = None
    experience_range: Optional[str] = None
