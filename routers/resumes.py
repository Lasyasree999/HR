"""
HireGenius AI — Resumes Router
=================================
API endpoints for resume upload and management.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database.connection import get_db
from database.models import User
from services.resume_service import ResumeService
from utils.security import get_current_user

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a single resume file (PDF or DOCX)."""
    result = await ResumeService.upload_resume(db, file, job_id)
    return result


@router.post("/bulk-upload")
async def bulk_upload(
    files: List[UploadFile] = File(...),
    job_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload multiple resume files in bulk."""
    result = await ResumeService.bulk_upload(db, files, job_id)
    return result


@router.get("/{resume_id}")
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get parsed resume details."""
    resume = ResumeService.get_resume(db, resume_id)
    return {
        "id": resume.id,
        "candidate_id": resume.candidate_id,
        "file_name": resume.file_name,
        "parsed_data": resume.parsed_data,
        "is_embedded": resume.is_embedded,
        "raw_text_preview": resume.raw_text[:500] if resume.raw_text else None,
        "uploaded_at": resume.uploaded_at.isoformat(),
    }
