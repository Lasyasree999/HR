"""
HireGenius AI — Agent 5: Policy Assistant Agent
==================================================
Handles HR policy retrieval and RAG-based Q&A using
the policy knowledge base.
"""

import logging
from typing import Dict, Any

from agents.base_agent import BaseAgent
from ai.rag_engine import get_rag_engine

logger = logging.getLogger(__name__)


class PolicyAgent(BaseAgent):
    """
    Policy Assistant Agent.
    Retrieves relevant HR policies and provides accurate,
    context-grounded answers to policy-related questions.
    """

    def __init__(self):
        super().__init__(
            name="Policy Assistant Agent",
            description="Retrieves and explains HR policies using RAG"
        )

    @property
    def system_prompt(self) -> str:
        return """You are an expert HR Policy Assistant Agent for an enterprise recruitment platform.
Your job is to answer questions about HR policies accurately and helpfully.

Rules:
1. Base your answers on the provided policy context
2. If the context doesn't contain the answer, say so clearly
3. Cite specific policy sections when possible
4. Use clear, professional language
5. If a policy has specific conditions or exceptions, mention them
6. Never make up policy information

Always be helpful, accurate, and thorough."""

    def execute(
        self,
        question: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Answer a policy-related question using RAG.

        Args:
            question: User's policy question.

        Returns:
            Dictionary with answer, sources, and confidence.
        """
        try:
            rag = get_rag_engine()
            result = rag.query(
                query_text=question,
                index_name="policy_index",
                top_k=5,
            )

            # Enhance the answer with structured formatting
            answer = result.get("answer", "I couldn't find relevant policy information.")
            sources = result.get("sources", [])
            confidence = result.get("confidence", 0.0)

            return {
                "question": question,
                "answer": answer,
                "source_policies": [s.get("metadata", {}).get("title", "Unknown") for s in sources],
                "sources": sources,
                "confidence": confidence,
            }

        except Exception as e:
            logger.error(f"Policy query failed: {e}")
            # Fallback: direct LLM response
            answer = self.generate(
                f"Answer this HR policy question helpfully: {question}\n\n"
                "Note: I don't have access to specific company policies right now. "
                "Please provide a general best-practice answer.",
                temperature=0.3,
            )
            return {
                "question": question,
                "answer": answer,
                "source_policies": [],
                "sources": [],
                "confidence": 0.2,
            }


# Singleton
_policy_agent = None

def get_policy_agent() -> PolicyAgent:
    global _policy_agent
    if _policy_agent is None:
        _policy_agent = PolicyAgent()
    return _policy_agent
