"""
HireGenius AI — Base Agent
============================
Abstract base class for all AI agents.
Provides shared Groq LLM and embedding capabilities.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ai.groq_client import get_groq_client, GroqClient

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for HireGenius AI agents.
    Each specialized agent inherits from this class and implements
    its own processing logic using the shared Groq LLM.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize the agent.

        Args:
            name: Agent name (e.g., 'Resume Intelligence Agent').
            description: Brief description of agent's purpose.
        """
        self.name = name
        self.description = description
        self.groq: GroqClient = get_groq_client()
        logger.info(f"Initialized agent: {self.name}")

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt that defines the agent's persona and capabilities."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's primary task.

        Args:
            **kwargs: Task-specific parameters.

        Returns:
            Dictionary with the agent's output.
        """
        pass

    def generate(self, prompt: str, temperature: float = 0.5) -> str:
        """Generate a response using the agent's system prompt."""
        return self.groq.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=temperature,
        )

    def generate_json(self, prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        """Generate a structured JSON response."""
        return self.groq.generate_json(
            prompt=prompt,
            system_prompt=self.system_prompt + "\nAlways respond with valid JSON.",
            temperature=temperature,
        )

    def __repr__(self):
        return f"<Agent: {self.name}>"
