"""
HireGenius AI — Analytics Schemas
===================================
Pydantic models for recruitment analytics and dashboard KPIs.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DashboardKPIs(BaseModel):
    """Dashboard overview with key recruitment metrics."""
    total_candidates: int = 0
    active_jobs: int = 0
    shortlisted: int = 0
    interviews_scheduled: int = 0
    hired: int = 0
    rejected: int = 0
    avg_match_score: float = 0.0
    recent_activities: List[Dict[str, Any]] = []
    ai_insights: List[str] = []


class FunnelData(BaseModel):
    """Hiring funnel stage counts."""
    new: int = 0
    screening: int = 0
    interview: int = 0
    offered: int = 0
    hired: int = 0
    rejected: int = 0


class TrendData(BaseModel):
    """Hiring trend data point."""
    period: str
    hired: int = 0
    applied: int = 0
    rejected: int = 0


class SkillDistribution(BaseModel):
    """Skill frequency distribution."""
    skill: str
    count: int
    percentage: float = 0.0


class DepartmentStats(BaseModel):
    """Department-level hiring statistics."""
    department: str
    open_jobs: int = 0
    total_candidates: int = 0
    hired: int = 0
    avg_match_score: float = 0.0


class AnalyticsResponse(BaseModel):
    """Full analytics response with all chart data."""
    funnel: FunnelData
    trends: List[TrendData] = []
    top_skills: List[SkillDistribution] = []
    departments: List[DepartmentStats] = []
    insights: List[str] = []
