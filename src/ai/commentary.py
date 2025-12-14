"""
AI-powered commentary generation for traffic light classifications.

Uses OpenAI GPT-4 to generate human-readable explanations for stock classifications.
"""

import os
from typing import Optional

from src.utils.cache import cached_data_fetch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Use mini for cost efficiency, can upgrade to gpt-4


def generate_ai_commentary(
    ticker: str,
    status: str,
    emoji: str,
    price: float,
    note: str,
    indicators: Optional[dict] = None,
) -> str:
    """
    Generate AI-powered natural language explanation for a traffic light classification.

    Args:
        ticker: Stock ticker symbol
        status: Traffic light status (GREEN, YELLOW, RED)
        emoji: Status emoji (🟢, 🟡, 🔴)
        price: Current stock price
        note: Technical note from classification
        indicators: Optional dict with technical indicators (RSI, SMA, etc.)

    Returns:
        Natural language explanation of the classification, or fallback to note if API fails
    """
    if not OPENAI_API_KEY:
        # Fallback to technical note if OpenAI not configured
        return note

    try:
        # Import OpenAI (lazy import to avoid errors if not installed)
        try:
            from openai import OpenAI
        except ImportError:
            return note

        client = OpenAI(api_key=OPENAI_API_KEY)

        # Build context about the stock
        context_parts = [
            f"Stock: {ticker}",
            f"Current Price: ${price:.2f}",
            f"Status: {status} {emoji}",
            f"Technical Analysis: {note}",
        ]

        if indicators:
            indicator_text = ", ".join(
                [f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}" 
                 for k, v in indicators.items() if v is not None]
            )
            if indicator_text:
                context_parts.append(f"Key Indicators: {indicator_text}")

        context = "\n".join(context_parts)

        # Create the prompt
        prompt = f"""You are a professional financial analyst providing clear, concise explanations of stock technical analysis.

Given the following stock analysis:

{context}

Provide a brief (2-3 sentences), professional explanation of what this {status} classification means for {ticker}. 
- Explain the technical situation in plain language
- Mention what investors should watch for
- Keep it actionable and easy to understand
- Do NOT provide investment advice, just explain the technical analysis
- Be specific about the indicators and what they mean

Format your response as a clear, concise explanation without bullet points or markdown. Start directly with the explanation."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional financial analyst explaining technical stock analysis in clear, accessible language.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.7,
        )

        commentary = response.choices[0].message.content.strip()
        return commentary if commentary else note

    except Exception:
        # Fallback to technical note on any error
        return note


@cached_data_fetch(ttl_seconds=1800)  # Cache AI commentary for 30 minutes
def get_cached_ai_commentary(
    ticker: str,
    status: str,
    price: float,
    note: str,
    indicators: Optional[dict] = None,
) -> str:
    """
    Cached wrapper for AI commentary generation.

    This ensures we don't make redundant API calls for the same classification.
    """
    return generate_ai_commentary(ticker, status, "", price, note, indicators)

