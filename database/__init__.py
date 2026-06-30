"""
HireGenius AI — Database Package
================================
Provides SQLAlchemy models, connection management, and schema utilities.
"""

from .connection import get_db, engine, SessionLocal, Base
from .models import (
    User, Job, Candidate, Resume, Skill,
    Interview, Recommendation, Email, Policy, AnalyticsMetric
)

__all__ = [
    "get_db", "engine", "SessionLocal", "Base",
    "User", "Job", "Candidate", "Resume", "Skill",
    "Interview", "Recommendation", "Email", "Policy", "AnalyticsMetric",
]
