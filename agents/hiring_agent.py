"""
HireGenius AI — Agent 4: Hiring Recommendation Agent
=======================================================
Analyzes candidate profiles and generates hiring recommendations
with detailed reasoning (Strong Hire / Hire / Consider / Reject).
"""

import logging
from typing import Dict, Any

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class HiringAgent(BaseAgent):
    """
    Hiring Recommendation Agent.
    Produces comprehensive hiring recommendations based on
    candidate analysis, match scores, and organizational fit.
    """

    def __init__(self):
        super().__init__(
            name="Hiring Recommendation Agent",
            description="Generates hiring recommendations with detailed reasoning"
        )

    @property
    def system_prompt(self) -> str:
        return """You are an expert Hiring Recommendation Agent for enterprise recruitment.
Your job is to analyze a candidate's full profile and provide a definitive hiring recommendation.

Your recommendation MUST be one of:
- "Strong Hire" - Exceptional candidate, exceeds all requirements
- "Hire" - Good candidate, meets requirements well
- "Consider" - Meets some requirements, has potential but gaps exist
- "Reject" - Does not meet key requirements

Provide detailed reasoning covering:
1. Skills alignment
2. Experience relevance
3. Education & certifications
4. Cultural fit potential
5. Growth potential
6. Risk factors

Be objective, fair, and data-driven. Always respond with valid JSON."""

    def execute(
        self,
        candidate_name: str,
        candidate_summary: str,
        job_title: str,
        job_description: str,
        match_score: float = 0.0,
        skills: list = None,
        experience: list = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a hiring recommendation for a candidate.

        Args:
            candidate_name: Candidate's name.
            candidate_summary: AI-generated candidate summary or resume text.
            job_title: Job title being applied for.
            job_description: Full job description.
            match_score: Pre-computed match score.
            skills: List of candidate's skills.
            experience: List of experience entries.

        Returns:
            Dictionary with decision, reasoning, and confidence.
        """
        skills_str = ", ".join(skills[:20]) if skills else "Not extracted"
        exp_str = str(experience[:5]) if experience else "Not extracted"

        prompt = f"""Analyze this candidate and provide a hiring recommendation.

CANDIDATE: {candidate_name}
MATCH SCORE: {match_score:.1f}/100

CANDIDATE PROFILE:
{candidate_summary[:2500]}

SKILLS: {skills_str}

EXPERIENCE: {exp_str}

JOB TITLE: {job_title}
JOB DESCRIPTION:
{job_description[:1500]}

Return JSON:
{{
    "decision": "Strong Hire|Hire|Consider|Reject",
    "confidence_score": <0.0-1.0>,
    "reasoning": "Detailed paragraph explaining the recommendation",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "risk_factors": ["risk 1"],
    "salary_justification": "Brief note on salary range fit",
    "growth_potential": "Assessment of candidate's growth trajectory"
}}"""

        try:
            result = self.generate_json(prompt)
            result["candidate_name"] = candidate_name
            result["job_title"] = job_title
            logger.info(
                f"Recommendation for {candidate_name}: {result.get('decision')}"
            )
            return result
        except Exception as e:
            logger.error(f"Recommendation failed for {candidate_name}: {e}")
            return {
                "decision": "Consider",
                "confidence_score": 0.3,
                "reasoning": "Unable to generate detailed recommendation. Manual review recommended.",
                "strengths": [],
                "weaknesses": [],
                "risk_factors": ["Automated analysis incomplete"],
                "candidate_name": candidate_name,
                "job_title": job_title,
            }


# Singleton
_hiring_agent = None

def get_hiring_agent() -> HiringAgent:
    global _hiring_agent
    if _hiring_agent is None:
        _hiring_agent = HiringAgent()
    return _hiring_agent
