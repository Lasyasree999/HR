"""
HireGenius AI — Interviews Router
=====================================
API endpoints for interview question generation.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database.connection import get_db
from database.models import User
from schemas.interviews import GenerateInterviewRequest
from services.interview_service import InterviewService
from utils.security import get_current_user

router = APIRouter(prefix="/api/interviews", tags=["Interviews"])


@router.post("/generate")
def generate_interview(
    request: GenerateInterviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate interview questions for a candidate-job pairing."""
    return InterviewService.generate_interview(
        db, request.candidate_id, request.job_id,
        request.num_questions, [l.value for l in request.levels]
    )


@router.get("")
def list_interviews(
    job_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all interviews."""
    return InterviewService.list_interviews(db, job_id)


@router.get("/{interview_id}")
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get interview details by ID."""
    return InterviewService.get_interview(db, interview_id)
