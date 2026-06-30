"""
HireGenius AI — Chat Router
==============================
API endpoints for the HR Copilot chatbot.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from schemas.policies import ChatMessage
from ai.groq_client import get_groq_client
from ai.rag_engine import get_rag_engine
from services.candidate_service import CandidateService
from utils.security import get_current_user

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/message")
def chat_message(
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to the HR Copilot.
    The copilot can answer questions about candidates, jobs,
    policies, and provide recruitment intelligence.
    """
    user_msg = message.message.lower()

    # Route to appropriate handler based on intent
    try:
        # Check if it's a candidate search query
        if any(kw in user_msg for kw in ["find", "search", "show", "top", "best", "candidates with"]):
            results = CandidateService.semantic_search(message.message, top_k=5)
            if results:
                candidates_text = "\n".join(
                    f"- {r['metadata'].get('candidate_name', 'Unknown')} "
                    f"(Score: {r['score']:.2f})"
                    for r in results
                )
                groq = get_groq_client()
                response = groq.generate(
                    prompt=f"The user asked: {message.message}\n\n"
                           f"Here are the search results:\n{candidates_text}\n\n"
                           "Provide a helpful, conversational summary of these results.",
                    system_prompt="You are an AI HR Copilot. Summarize search results helpfully.",
                )
                return {
                    "response": response,
                    "sources": results[:3],
                    "suggestions": [
                        "Tell me more about the top candidate",
                        "Compare these candidates",
                        "Generate interview questions for the best match"
                    ]
                }

        # Check if it's a policy question
        if any(kw in user_msg for kw in ["policy", "policies", "rule", "guideline", "referral", "probation"]):
            rag = get_rag_engine()
            result = rag.query(message.message, "policy_index", top_k=3)
            return {
                "response": result.get("answer", "I couldn't find relevant policy information."),
                "sources": result.get("sources", []),
                "suggestions": [
                    "What are the leave policies?",
                    "Explain the hiring process",
                    "What is the probation period?"
                ]
            }

        # General recruitment question
        groq = get_groq_client()
        response = groq.generate(
            prompt=message.message,
            system_prompt=(
                "You are HireGenius AI Copilot, an intelligent HR recruitment assistant. "
                "Help HR managers with candidate insights, hiring decisions, "
                "recruitment best practices, and policy questions. "
                "Be conversational, helpful, and data-driven."
            ),
        )

        return {
            "response": response,
            "sources": [],
            "suggestions": [
                "Show top Python candidates",
                "Who is best suited for AI Engineer role?",
                "What is the referral policy?"
            ]
        }

    except Exception as e:
        return {
            "response": f"I encountered an issue processing your request. Please try again. Error: {str(e)}",
            "sources": [],
            "suggestions": ["Try a different question", "Search for candidates", "Ask about policies"]
        }
