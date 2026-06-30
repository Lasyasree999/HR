"""
HireGenius AI — Policies Router
==================================
API endpoints for HR policy management and RAG-based Q&A.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from schemas.policies import PolicyQueryRequest
from services.policy_service import PolicyService
from utils.security import get_current_user

router = APIRouter(prefix="/api/policies", tags=["Policies"])


@router.post("/upload")
async def upload_policy(
    file: UploadFile = File(...),
    title: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload an HR policy document."""
    return await PolicyService.upload_policy(db, file, title)


@router.get("")
def list_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all policies."""
    return PolicyService.get_policies(db)


@router.post("/query")
def query_policy(
    request: PolicyQueryRequest,
    current_user: User = Depends(get_current_user),
):
    """RAG-based policy Q&A."""
    return PolicyService.query_policy(request.question)
