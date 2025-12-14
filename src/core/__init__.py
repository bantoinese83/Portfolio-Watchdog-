"""
Core engine and data fetching modules.

This package contains:
- engine: Traffic light classification logic
- data_fetcher: OHLCV data fetching (yfinance and RapidAPI)
"""

from src.core.engine import TrafficLightResult, classify_ticker, fetch_ohlcv
from src.core.data_fetcher import (
    fetch_ohlcv_rapidapi,
    fetch_ohlcv_with_fallback,
    RAPIDAPI_KEY,
    RAPIDAPI_HOST,
)

__all__ = [
    "TrafficLightResult",
    "classify_ticker",
    "fetch_ohlcv",
    "fetch_ohlcv_rapidapi",
    "fetch_ohlcv_with_fallback",
    "RAPIDAPI_KEY",
    "RAPIDAPI_HOST",
]

