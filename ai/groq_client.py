"""
HireGenius AI — Groq LLM Client
=================================
Wrapper for Groq API interactions using Llama 3.3 70B Versatile.
Provides structured prompt-based completions for all AI agents.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from groq import Groq

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GroqClient:
    """
    Groq LLM client for generating AI responses.
    Uses Llama 3.3 70B Versatile model for high-quality text generation.
    """

    def __init__(self):
        """Initialize Groq client with API key from settings."""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.max_tokens = 2048
        self.temperature = 0.7

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI assistant.",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Generate a text completion using Groq.

        Args:
            prompt: User prompt / instruction.
            system_prompt: System-level context for the model.
            temperature: Creativity level (0.0 = deterministic, 1.0 = creative).
            max_tokens: Maximum output tokens.
            json_mode: If True, instructs the model to return valid JSON.

        Returns:
            Generated text string.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            completion = self.client.chat.completions.create(**kwargs)
            response = completion.choices[0].message.content
            logger.info(f"Groq generation successful. Tokens used: {completion.usage.total_tokens}")
            return response

        except Exception as e:
            err_msg = str(e)
            if ("rate_limit" in err_msg or "429" in err_msg or "Rate limit" in err_msg) and self.model != "llama-3.1-8b-instant":
                fallback_model = "llama-3.1-8b-instant"
                logger.warning(f"Rate limit exceeded on {self.model}. Retrying with fallback model {fallback_model}. Error: {e}")
                try:
                    kwargs["model"] = fallback_model
                    # Also cap fallback model max_tokens to prevent 413 error
                    kwargs["max_tokens"] = min(kwargs.get("max_tokens", 2048), 2048)
                    completion = self.client.chat.completions.create(**kwargs)
                    response = completion.choices[0].message.content
                    logger.info(f"Fallback Groq generation successful. Tokens used: {completion.usage.total_tokens}")
                    return response
                except Exception as fallback_err:
                    logger.error(f"Fallback Groq generation also failed: {fallback_err}")
                    raise RuntimeError(f"AI generation failed (including fallback): {str(fallback_err)}")

            logger.error(f"Groq generation failed: {str(e)}")
            raise RuntimeError(f"AI generation failed: {str(e)}")

    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI assistant. Always respond with valid JSON.",
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured JSON response.

        Args:
            prompt: User prompt (should request JSON output).
            system_prompt: System context.
            temperature: Lower temperature for more deterministic JSON.
            max_tokens: Maximum output tokens.

        Returns:
            Parsed JSON dictionary.
        """
        response = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, attempting extraction")
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
            raise ValueError("AI did not return valid JSON")

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "You are a helpful AI recruitment assistant.",
        temperature: float = 0.7,
    ) -> str:
        """
        Multi-turn chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            system_prompt: System context.
            temperature: Creativity level.

        Returns:
            Assistant's response string.
        """
        try:
            full_messages = [{"role": "system", "content": system_prompt}]
            full_messages.extend(messages)

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=self.max_tokens,
            )
            return completion.choices[0].message.content

        except Exception as e:
            err_msg = str(e)
            if ("rate_limit" in err_msg or "429" in err_msg or "Rate limit" in err_msg) and self.model != "llama-3.1-8b-instant":
                fallback_model = "llama-3.1-8b-instant"
                logger.warning(f"Rate limit exceeded on {self.model}. Retrying chat with fallback model {fallback_model}. Error: {e}")
                try:
                    completion = self.client.chat.completions.create(
                        model=fallback_model,
                        messages=full_messages,
                        temperature=temperature,
                        max_tokens=self.max_tokens,
                    )
                    return completion.choices[0].message.content
                except Exception as fallback_err:
                    logger.error(f"Fallback Groq chat also failed: {fallback_err}")
                    raise RuntimeError(f"AI chat failed (including fallback): {str(fallback_err)}")

            logger.error(f"Groq chat failed: {str(e)}")
            raise RuntimeError(f"AI chat failed: {str(e)}")


# Singleton instance
_groq_client: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """Get or create the singleton Groq client instance."""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client
