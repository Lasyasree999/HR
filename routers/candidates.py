"""
HireGenius AI — Candidates Router
=====================================
API endpoints for candidate management, search, and AI analysis.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database.connection import get_db
from database.models import User
from schemas.candidates import CandidateSearchRequest, CandidateCompareRequest
from services.candidate_service import CandidateService
from utils.security import get_current_user

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


@router.get("")
def list_candidates(
    job_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all candidates with optional filters."""
    return CandidateService.get_candidates(db, job_id=job_id, status=status)


@router.get("/{candidate_id}")
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed candidate profile."""
    return CandidateService.get_candidate(db, candidate_id)


@router.get("/{candidate_id}/summary")
def get_candidate_summary(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI executive summary for a candidate."""
    return CandidateService.generate_summary(db, candidate_id)


@router.post("/{candidate_id}/skill-gap")
def skill_gap_analysis(
    candidate_id: int,
    job_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Perform skill gap analysis against a job."""
    return CandidateService.skill_gap_analysis(db, candidate_id, job_id)


@router.post("/compare")
def compare_candidates(
    request: CandidateCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compare multiple candidates for a job."""
    return CandidateService.compare_candidates(db, request.candidate_ids, request.job_id)


@router.post("/search")
def search_candidates(
    request: CandidateSearchRequest,
    current_user: User = Depends(get_current_user),
):
    """Semantic search for candidates."""
    return CandidateService.semantic_search(request.query, request.top_k)


@router.put("/{candidate_id}/status")
def update_candidate_status(
    candidate_id: int,
    status: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update candidate hiring status."""
    return CandidateService.update_status(db, candidate_id, status)

