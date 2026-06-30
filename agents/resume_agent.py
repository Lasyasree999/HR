"""
HireGenius AI — Agent 1: Resume Intelligence Agent
=====================================================
Responsible for parsing resumes, extracting structured data
(name, email, phone, skills, experience, education, certifications).
"""

import logging
from typing import Dict, Any, List

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResumeAgent(BaseAgent):
    """
    Resume Intelligence Agent.
    Parses raw resume text and extracts structured candidate information
    using Groq LLM with guided JSON output.
    """

    def __init__(self):
        super().__init__(
            name="Resume Intelligence Agent",
            description="Parses resumes and extracts structured candidate data"
        )

    @property
    def system_prompt(self) -> str:
        return """You are an expert Resume Intelligence Agent for an enterprise recruitment platform.
Your job is to analyze raw resume text and extract structured information accurately.

You MUST extract the following fields:
1. name - Full name of the candidate
2. email - Email address
3. phone - Phone number
4. skills - List of technical and soft skills
5. experience - List of work experiences with company, title, duration, description
6. education - List of educational qualifications with institution, degree, field, year
7. certifications - List of professional certifications
8. total_years_experience - Estimated total years of work experience (as a number)
9. summary - A brief 2-3 sentence professional summary

Be thorough and accurate. If a field is not found in the resume, return an empty value.
Always respond with valid JSON."""

    def execute(self, resume_text: str, **kwargs) -> Dict[str, Any]:
        """
        Parse a resume and extract structured data.

        Args:
            resume_text: Raw text content of the resume.

        Returns:
            Dictionary with extracted candidate information.
        """
        prompt = f"""Analyze the following resume text and extract structured information.

RESUME TEXT:
{resume_text[:4000]}

Return a JSON object with these exact fields:
{{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "+1-234-567-8900",
    "skills": ["Python", "Machine Learning", "SQL", ...],
    "experience": [
        {{
            "company": "Company Name",
            "title": "Job Title",
            "duration": "Jan 2020 - Dec 2022",
            "years": 2,
            "description": "Key responsibilities and achievements"
        }}
    ],
    "education": [
        {{
            "institution": "University Name",
            "degree": "Bachelor's/Master's/PhD",
            "field": "Computer Science",
            "year": "2020"
        }}
    ],
    "certifications": ["AWS Certified", "PMP", ...],
    "total_years_experience": 5.0,
    "summary": "Brief professional summary"
}}"""

        try:
            result = self.generate_json(prompt)
            logger.info(f"Resume parsed successfully: {result.get('name', 'Unknown')}")
            return result
        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            return {
                "name": "",
                "email": "",
                "phone": "",
                "skills": [],
                "experience": [],
                "education": [],
                "certifications": [],
                "total_years_experience": 0,
                "summary": "Failed to parse resume",
                "error": str(e),
            }

    def extract_skills(self, resume_text: str) -> List[str]:
        """Extract just the skills from a resume."""
        prompt = f"""Extract all technical and professional skills from this resume.
Return a JSON object with a single key "skills" containing a list of skill strings.

RESUME TEXT:
{resume_text[:3000]}"""

        try:
            result = self.generate_json(prompt)
            return result.get("skills", [])
        except Exception:
            return []


# Singleton
_resume_agent = None

def get_resume_agent() -> ResumeAgent:
    global _resume_agent
    if _resume_agent is None:
        _resume_agent = ResumeAgent()
    return _resume_agent
