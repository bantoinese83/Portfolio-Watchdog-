"""
AI-powered features.

This package contains:
- commentary: OpenAI GPT-4 powered natural language explanations
"""

from src.ai.commentary import (
    generate_ai_commentary,
    get_cached_ai_commentary,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

__all__ = [
    "generate_ai_commentary",
    "get_cached_ai_commentary",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
]

