"""
HireGenius AI — Ranking Router
=================================
API endpoints for candidate ranking and matching.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from services.ranking_service import RankingService
from utils.security import get_current_user

router = APIRouter(prefix="/api/ranking", tags=["Ranking"])


@router.post("/match/{job_id}")
def match_candidates(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Match and rank all candidates for a specific job."""
    return RankingService.match_candidates_to_job(db, job_id)


@router.get("/job/{job_id}")
def get_rankings(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get pre-computed rankings for a job."""
    return RankingService.get_rankings_for_job(db, job_id)


@router.post("/recommend/{candidate_id}/{job_id}")
def generate_recommendation(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a hiring recommendation for a candidate."""
    return RankingService.generate_recommendation(db, candidate_id, job_id)
