"""
HireGenius AI — Emails Router
================================
API endpoints for AI-generated HR emails.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.connection import get_db
from database.models import User
from schemas.emails import GenerateEmailRequest, EmailUpdate
from services.email_service import EmailService
from utils.security import get_current_user

router = APIRouter(prefix="/api/emails", tags=["Emails"])


@router.post("/generate")
def generate_email(
    request: GenerateEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI-powered HR email."""
    return EmailService.generate_email(
        db, request.candidate_id, request.email_type.value,
        request.job_id, request.additional_context or "",
        current_user.id,
    )


@router.get("")
def list_emails(
    candidate_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all generated emails."""
    return EmailService.get_emails(db, candidate_id)


@router.put("/{email_id}")
def update_email(
    email_id: int,
    update: EmailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Edit a generated email."""
    return EmailService.update_email(db, email_id, update.subject, update.body)
