"""
HireGenius AI — Interview Schemas
====================================
Pydantic models for interview question generation and evaluation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class InterviewLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class GenerateInterviewRequest(BaseModel):
    """Request to generate interview questions for a candidate-job pairing."""
    candidate_id: int
    job_id: int
    levels: List[InterviewLevel] = [
        InterviewLevel.beginner,
        InterviewLevel.intermediate,
        InterviewLevel.advanced
    ]
    num_questions: int = Field(default=5, ge=1, le=20)


class InterviewQuestion(BaseModel):
    """A single interview question with metadata."""
    question: str
    category: str  # technical, hr, scenario
    level: str
    expected_answer_points: List[str] = []
    scoring_weight: float = 1.0


class InterviewResponse(BaseModel):
    """Full interview question set with evaluation criteria."""
    id: int
    candidate_id: int
    job_id: int
    technical_questions: List[Dict[str, Any]]
    hr_questions: List[Dict[str, Any]]
    scenario_questions: List[Dict[str, Any]]
    evaluation_criteria: List[Dict[str, Any]]
    scoring_rubric: List[Dict[str, Any]]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
