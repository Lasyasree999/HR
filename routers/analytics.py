"""
HireGenius AI — Analytics Router
====================================
API endpoints for recruitment analytics and KPIs.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from services.analytics_service import AnalyticsService
from utils.security import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard KPIs and overview."""
    return AnalyticsService.get_dashboard_kpis(db)


@router.get("/funnel")
def get_funnel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get hiring funnel data."""
    return AnalyticsService.get_funnel_data(db)


@router.get("/trends")
def get_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get hiring trends."""
    return AnalyticsService.get_trends(db)


@router.get("/skills")
def get_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get top skills distribution."""
    return AnalyticsService.get_top_skills(db)


@router.get("/departments")
def get_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get department hiring statistics."""
    return AnalyticsService.get_department_stats(db)


@router.get("/insights")
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI-generated recruitment insights."""
    return AnalyticsService.get_ai_insights(db)
