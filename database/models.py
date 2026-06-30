"""
HireGenius AI — SQLAlchemy ORM Models
======================================
All 10 database tables mapped as SQLAlchemy ORM models.
Mirrors the schema defined in schema.sql.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime,
    Enum, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from .connection import Base


class User(Base):
    """
    User model for HR managers and administrators.
    Supports role-based access control (admin / hr_manager).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(
        Enum("admin", "hr_manager", name="user_role"),
        nullable=False, default="hr_manager"
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    jobs = relationship("Job", back_populates="creator", lazy="dynamic")
    emails = relationship("Email", back_populates="creator", lazy="dynamic")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Job(Base):
    """
    Job posting model with description, requirements, and status tracking.
    Each job can have multiple candidates applied to it.
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(Text)
    experience_range = Column(String(50))
    department = Column(String(100), index=True)
    salary_range = Column(String(100))
    location = Column(String(200))
    status = Column(
        Enum("open", "closed", "on_hold", name="job_status"),
        nullable=False, default="open"
    )
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    creator = relationship("User", back_populates="jobs")
    candidates = relationship("Candidate", back_populates="job", lazy="dynamic")
    interviews = relationship("Interview", back_populates="job", lazy="dynamic")
    recommendations = relationship("Recommendation", back_populates="job", lazy="dynamic")

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', status='{self.status}')>"


class Candidate(Base):
    """
    Candidate model storing personal information and AI-computed match scores.
    Linked to a specific job opening.
    """
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(30))
    summary = Column(Text)
    match_score = Column(Float, default=0.0)
    status = Column(
        Enum("new", "screening", "interview", "offered", "hired", "rejected",
             name="candidate_status"),
        nullable=False, default="new"
    )
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    job = relationship("Job", back_populates="candidates")
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="candidate", cascade="all, delete-orphan")
    emails = relationship("Email", back_populates="candidate", lazy="dynamic")

    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.name}', score={self.match_score})>"


class Resume(Base):
    """
    Resume model storing uploaded files, extracted text, and parsed structured data.
    Tracks whether the resume has been embedded in the vector store.
    """
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    raw_text = Column(Text)
    parsed_data = Column(JSON)
    is_embedded = Column(Boolean, nullable=False, default=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")

    def __repr__(self):
        return f"<Resume(id={self.id}, file='{self.file_name}', embedded={self.is_embedded})>"


class Skill(Base):
    """
    Skill model storing individual skills extracted from candidate resumes.
    Includes proficiency level and years of experience.
    """
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), nullable=False, index=True)
    proficiency = Column(
        Enum("beginner", "intermediate", "advanced", "expert",
             name="skill_proficiency"),
        default="intermediate"
    )
    years_experience = Column(Integer, default=0)

    # Relationships
    candidate = relationship("Candidate", back_populates="skills")

    def __repr__(self):
        return f"<Skill(id={self.id}, name='{self.skill_name}', level='{self.proficiency}')>"


class Interview(Base):
    """
    Interview model storing AI-generated questions, evaluation criteria,
    and scoring rubrics for candidate-job pairings.
    """
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    technical_questions = Column(JSON)
    hr_questions = Column(JSON)
    scenario_questions = Column(JSON)
    evaluation_criteria = Column(JSON)
    scoring_rubric = Column(JSON)
    status = Column(
        Enum("pending", "completed", "cancelled", name="interview_status"),
        nullable=False, default="pending"
    )
    scheduled_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")

    def __repr__(self):
        return f"<Interview(id={self.id}, status='{self.status}')>"


class Recommendation(Base):
    """
    Hiring recommendation model with AI-generated decisions and reasoning.
    Decisions: strong_hire, hire, consider, reject.
    """
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    decision = Column(
        Enum("strong_hire", "hire", "consider", "reject",
             name="recommendation_decision"),
        nullable=False
    )
    reasoning = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="recommendations")
    job = relationship("Job", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(id={self.id}, decision='{self.decision}')>"


class Email(Base):
    """
    Email model storing AI-generated HR communications.
    Types: interview_invite, rejection, offer, followup, reminder.
    """
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="SET NULL"))
    email_type = Column(
        Enum("interview_invite", "rejection", "offer", "followup", "reminder",
             name="email_type_enum"),
        nullable=False
    )
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(
        Enum("draft", "sent", name="email_status"),
        nullable=False, default="draft"
    )
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="emails")
    creator = relationship("User", back_populates="emails")

    def __repr__(self):
        return f"<Email(id={self.id}, type='{self.email_type}', status='{self.status}')>"


class Policy(Base):
    """
    HR policy document model for RAG-based policy Q&A.
    Stores document content and tracks embedding status.
    """
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    file_name = Column(String(255))
    file_path = Column(String(500))
    content = Column(Text)
    is_embedded = Column(Boolean, nullable=False, default=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Policy(id={self.id}, title='{self.title}', embedded={self.is_embedded})>"


class AnalyticsMetric(Base):
    """
    Analytics model storing recruitment KPI data points.
    Used for dashboard visualizations and trend analysis.
    """
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(String(255), nullable=False)
    category = Column(String(100), index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"))
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Analytics(id={self.id}, metric='{self.metric_name}')>"
