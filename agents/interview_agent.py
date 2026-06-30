"""
HireGenius AI — Agent 3: Interview Intelligence Agent
========================================================
Generates interview questions (technical, HR, scenario) with
evaluation criteria and scoring rubrics.
"""

import logging
from typing import Dict, Any, List

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class InterviewAgent(BaseAgent):
    """
    Interview Intelligence Agent.
    Generates customized interview questions based on the job description
    and candidate profile, with evaluation criteria and scoring rubrics.
    """

    def __init__(self):
        super().__init__(
            name="Interview Intelligence Agent",
            description="Generates interview questions, evaluation criteria, and scoring rubrics"
        )

    @property
    def system_prompt(self) -> str:
        return """You are an expert Interview Intelligence Agent for enterprise recruitment.
Your job is to generate high-quality, role-specific interview questions.

Generate questions in three categories:
1. Technical Questions - Test domain knowledge and technical skills
2. HR Questions - Assess cultural fit, teamwork, communication
3. Scenario Questions - Evaluate problem-solving and decision-making

For each question, provide:
- The question text
- Difficulty level (beginner/intermediate/advanced)
- Expected answer key points
- Scoring weight

Also generate:
- Evaluation criteria: What the interviewer should look for
- Scoring rubric: How to score responses (1-5 scale)

Always respond with valid JSON."""

    def execute(
        self,
        job_title: str,
        job_description: str,
        candidate_skills: List[str] = None,
        num_questions: int = 5,
        levels: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate interview questions for a candidate-job pairing.

        Args:
            job_title: Title of the job.
            job_description: Full job description.
            candidate_skills: Candidate's skills for targeted questions.
            num_questions: Number of questions per category.
            levels: Difficulty levels to include.

        Returns:
            Dictionary with questions, criteria, and rubric.
        """
        if levels is None:
            levels = ["beginner", "intermediate", "advanced"]
        if candidate_skills is None:
            candidate_skills = []

        skills_str = ", ".join(candidate_skills[:15]) if candidate_skills else "Not specified"

        prompt = f"""Generate comprehensive interview questions for the following role.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_description[:2000]}

CANDIDATE'S SKILLS: {skills_str}

DIFFICULTY LEVELS: {', '.join(levels)}
QUESTIONS PER CATEGORY: {num_questions}

Return JSON with this exact structure:
{{
    "technical_questions": [
        {{
            "question": "Question text",
            "level": "beginner|intermediate|advanced",
            "expected_points": ["point 1", "point 2"],
            "scoring_weight": 1.0
        }}
    ],
    "hr_questions": [
        {{
            "question": "Question text",
            "level": "intermediate",
            "expected_points": ["point 1", "point 2"],
            "scoring_weight": 1.0
        }}
    ],
    "scenario_questions": [
        {{
            "question": "Scenario-based question text",
            "level": "advanced",
            "expected_points": ["point 1", "point 2"],
            "scoring_weight": 1.5
        }}
    ],
    "evaluation_criteria": [
        {{
            "criterion": "Technical Knowledge",
            "description": "What to evaluate",
            "weight": 30
        }}
    ],
    "scoring_rubric": [
        {{
            "score": 5,
            "label": "Exceptional",
            "description": "Exceeds expectations in all areas"
        }},
        {{
            "score": 4,
            "label": "Strong",
            "description": "Meets all expectations"
        }},
        {{
            "score": 3,
            "label": "Adequate",
            "description": "Meets most expectations"
        }},
        {{
            "score": 2,
            "label": "Below Average",
            "description": "Needs improvement"
        }},
        {{
            "score": 1,
            "label": "Unsatisfactory",
            "description": "Does not meet expectations"
        }}
    ]
}}"""

        try:
            result = self.generate_json(prompt)
            logger.info(f"Generated interview questions for: {job_title}")
            return result
        except Exception as e:
            logger.error(f"Interview generation failed: {e}")
            return self._fallback_questions(job_title)

    def _fallback_questions(self, job_title: str) -> Dict[str, Any]:
        """Provide fallback questions if AI generation fails."""
        return {
            "technical_questions": [
                {"question": f"Describe your experience relevant to the {job_title} role.",
                 "level": "intermediate", "expected_points": [], "scoring_weight": 1.0}
            ],
            "hr_questions": [
                {"question": "Tell me about a time you worked effectively in a team.",
                 "level": "intermediate", "expected_points": [], "scoring_weight": 1.0}
            ],
            "scenario_questions": [
                {"question": "How would you handle a tight deadline with conflicting priorities?",
                 "level": "intermediate", "expected_points": [], "scoring_weight": 1.0}
            ],
            "evaluation_criteria": [
                {"criterion": "Technical Skills", "description": "Core competencies", "weight": 40},
                {"criterion": "Communication", "description": "Clarity and articulation", "weight": 30},
                {"criterion": "Problem Solving", "description": "Analytical thinking", "weight": 30},
            ],
            "scoring_rubric": [
                {"score": 5, "label": "Exceptional", "description": "Exceeds all expectations"},
                {"score": 3, "label": "Adequate", "description": "Meets expectations"},
                {"score": 1, "label": "Unsatisfactory", "description": "Below expectations"},
            ],
        }


# Singleton
_interview_agent = None

def get_interview_agent() -> InterviewAgent:
    global _interview_agent
    if _interview_agent is None:
        _interview_agent = InterviewAgent()
    return _interview_agent
