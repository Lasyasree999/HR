"""
HireGenius AI — Jobs Router
==============================
API endpoints for job posting management.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.connection import get_db
from database.models import User
from schemas.jobs import JobCreate, JobUpdate, GenerateJDRequest
from services.job_service import JobService
from utils.security import get_current_user

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("")
def list_jobs(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all jobs with optional filters."""
    return JobService.get_jobs(db, status=status, department=department, search=search)


@router.post("")
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job posting."""
    job = JobService.create_job(db, job_data, current_user.id)
    return {"id": job.id, "title": job.title, "status": job.status, "message": "Job created successfully"}


@router.get("/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get job details by ID."""
    job = JobService.get_job(db, job_id)
    return {
        "id": job.id, "title": job.title, "description": job.description,
        "required_skills": job.required_skills, "experience_range": job.experience_range,
        "department": job.department, "salary_range": job.salary_range,
        "location": job.location, "status": job.status,
        "created_at": job.created_at.isoformat(), "updated_at": job.updated_at.isoformat(),
    }


@router.put("/{job_id}")
def update_job(
    job_id: int,
    update_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a job posting."""
    job = JobService.update_job(db, job_id, update_data)
    return {"id": job.id, "title": job.title, "message": "Job updated successfully"}


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a job posting."""
    JobService.delete_job(db, job_id)
    return {"message": "Job deleted successfully"}


@router.post("/{job_id}/generate-description")
def generate_description(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an AI-powered job description for an existing job."""
    job = JobService.get_job(db, job_id)
    result = JobService.generate_description(
        title=job.title,
        department=job.department,
        required_skills=job.required_skills,
        experience_range=job.experience_range,
    )
    return result


@router.post("/generate-description")
def generate_new_description(
    request: GenerateJDRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate an AI-powered job description for a new role."""
    return JobService.generate_description(
        title=request.title,
        department=request.department,
        required_skills=request.required_skills,
        experience_range=request.experience_range,
    )
