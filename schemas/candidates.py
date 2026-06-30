"""
HireGenius AI — Candidate Schemas
===================================
Pydantic models for candidate profiles, rankings, comparisons, and search.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CandidateStatus(str, Enum):
    new = "new"
    screening = "screening"
    interview = "interview"
    offered = "offered"
    hired = "hired"
    rejected = "rejected"


class CandidateCreate(BaseModel):
    """Request model for creating a candidate record."""
    name: str = Field(..., min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_id: Optional[int] = None


class CandidateResponse(BaseModel):
    """Candidate profile response with AI-computed data."""
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    match_score: float = 0.0
    status: CandidateStatus
    job_id: Optional[int] = None
    skills: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    """Paginated list of candidates."""
    candidates: List[CandidateResponse]
    total: int


class CandidateRankingResponse(BaseModel):
    """Ranked candidate with match details."""
    rank: int
    candidate_id: int
    candidate_name: str
    match_score: float
    skill_match: float
    experience_match: float
    recommendation: str
    explanation: Optional[str] = None


class CandidateCompareRequest(BaseModel):
    """Request to compare multiple candidates."""
    candidate_ids: List[int] = Field(..., min_length=2, max_length=10)
    job_id: int


class CandidateCompareResponse(BaseModel):
    """Comparison result for multiple candidates."""
    candidates: List[Dict[str, Any]]
    insights: str
    recommendation: str


class CandidateSearchRequest(BaseModel):
    """Semantic search request for candidates."""
    query: str = Field(..., min_length=3)
    top_k: int = Field(default=10, ge=1, le=50)
    job_id: Optional[int] = None


class CandidateSummaryResponse(BaseModel):
    """AI-generated executive summary for a candidate."""
    candidate_id: int
    candidate_name: str
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    suitability: str
    overall_rating: str


class SkillGapResponse(BaseModel):
    """Skill gap analysis result."""
    candidate_id: int
    current_skills: List[str]
    missing_skills: List[str]
    learning_paths: List[Dict[str, str]]
    growth_suggestions: List[str]
