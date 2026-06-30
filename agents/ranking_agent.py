"""
HireGenius AI — Agent 2: Candidate Ranking Agent
===================================================
Responsible for comparing candidates against job descriptions,
generating match scores, ranking, and providing explanations.
"""

import logging
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from ai.embeddings import compute_similarity

logger = logging.getLogger(__name__)


class RankingAgent(BaseAgent):
    """
    Candidate Ranking Agent.
    Compares candidate resumes against job descriptions using
    semantic similarity + LLM-based analysis for comprehensive scoring.
    """

    def __init__(self):
        super().__init__(
            name="Candidate Ranking Agent",
            description="Ranks candidates against job descriptions with match scores"
        )

    @property
    def system_prompt(self) -> str:
        return """You are an expert Candidate Ranking Agent for enterprise recruitment.
Your job is to evaluate how well a candidate matches a job description.

You must provide:
1. skill_match_score (0-100): How well the candidate's skills match required skills
2. experience_match_score (0-100): How well the experience level matches
3. overall_match_score (0-100): Weighted overall match score
4. recommendation: One of "Strong Hire", "Hire", "Consider", "Reject"
5. explanation: 2-3 sentence explanation of the ranking
6. matching_skills: List of skills that match
7. missing_skills: List of required skills the candidate lacks

Be fair, thorough, and evidence-based. Always respond with valid JSON."""

    def execute(
        self,
        candidate_text: str,
        job_description: str,
        candidate_name: str = "Unknown",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Rank a candidate against a job description.

        Args:
            candidate_text: Candidate's resume text or parsed summary.
            job_description: Job description with requirements.
            candidate_name: Candidate's name.

        Returns:
            Dictionary with match scores, ranking, and explanation.
        """
        # Compute semantic similarity
        semantic_score = compute_similarity(candidate_text, job_description) * 100

        prompt = f"""Evaluate this candidate against the job description.

CANDIDATE ({candidate_name}):
{candidate_text[:2500]}

JOB DESCRIPTION:
{job_description[:2000]}

SEMANTIC SIMILARITY SCORE: {semantic_score:.1f}/100

Based on the above, provide a detailed evaluation as JSON:
{{
    "skill_match_score": <0-100>,
    "experience_match_score": <0-100>,
    "overall_match_score": <0-100>,
    "recommendation": "<Strong Hire|Hire|Consider|Reject>",
    "explanation": "Detailed 2-3 sentence explanation",
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill3", "skill4"]
}}"""

        try:
            result = self.generate_json(prompt)
            # Blend AI score with semantic similarity
            ai_score = result.get("overall_match_score", 50)
            result["overall_match_score"] = round(0.6 * ai_score + 0.4 * semantic_score, 1)
            result["semantic_score"] = round(semantic_score, 1)
            result["candidate_name"] = candidate_name
            return result
        except Exception as e:
            logger.error(f"Ranking failed for {candidate_name}: {e}")
            return {
                "skill_match_score": round(semantic_score, 1),
                "experience_match_score": round(semantic_score, 1),
                "overall_match_score": round(semantic_score, 1),
                "semantic_score": round(semantic_score, 1),
                "recommendation": "Consider",
                "explanation": "Automated ranking based on semantic similarity.",
                "matching_skills": [],
                "missing_skills": [],
                "candidate_name": candidate_name,
            }

    def rank_multiple(
        self,
        candidates: List[Dict[str, Any]],
        job_description: str,
    ) -> List[Dict[str, Any]]:
        """
        Rank multiple candidates against a job description.

        Args:
            candidates: List of dicts with 'name' and 'text' keys.
            job_description: Job description text.

        Returns:
            Sorted list of ranking results (highest score first).
        """
        results = []
        for candidate in candidates:
            result = self.execute(
                candidate_text=candidate.get("text", ""),
                job_description=job_description,
                candidate_name=candidate.get("name", "Unknown"),
            )
            results.append(result)

        # Sort by overall match score (descending)
        results.sort(key=lambda x: x.get("overall_match_score", 0), reverse=True)

        # Add rank numbers
        for i, result in enumerate(results):
            result["rank"] = i + 1

        return results


# Singleton
_ranking_agent = None

def get_ranking_agent() -> RankingAgent:
    global _ranking_agent
    if _ranking_agent is None:
        _ranking_agent = RankingAgent()
    return _ranking_agent
