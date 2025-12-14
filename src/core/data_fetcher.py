"""
Alternative data fetching methods for Portfolio Watchdog.

This module provides fallback data sources when yfinance has issues.
Supports RapidAPI YFinance API as an alternative.
"""

import os
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from src.utils.cache import cached_data_fetch

# Load environment variables from .env file
load_dotenv()

# RapidAPI configuration (optional - set via environment variables)
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "yahoo-finance166.p.rapidapi.com")
RAPIDAPI_BASE_URL = "https://yahoo-finance166.p.rapidapi.com"


@cached_data_fetch(ttl_seconds=1800)  # Cache for 30 minutes (same as yfinance)
def fetch_ohlcv_rapidapi(
    ticker: str, period: str = "2y", interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """
    Fetch OHLCV data using RapidAPI YFinance endpoint.

    This is an alternative to yfinance when the standard API has issues.

    Args:
        ticker: Stock ticker symbol
        period: Time period (e.g., "2y" for 2 years)
        interval: Data interval (e.g., "1d" for daily)

    Returns:
        DataFrame with OHLCV data, or None if API key not configured or request fails
    """
    if not RAPIDAPI_KEY:
        return None

    try:
        # Use the get-chart endpoint for OHLCV data
        url = f"{RAPIDAPI_BASE_URL}/api/stock/get-chart"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST,
        }
        
        # Map interval to RapidAPI format
        interval_map = {
            "1d": "1d",
            "1wk": "1wk",
            "1mo": "1mo",
        }
        rapid_interval = interval_map.get(interval, "1d")
        
        # Map period to range
        range_map = {
            "2y": "2y",
            "1y": "1y",
            "6mo": "6mo",
            "1mo": "1mo",
            "5d": "5d",
        }
        rapid_range = range_map.get(period, "2y")
        
        params = {
            "symbol": ticker,
            "interval": rapid_interval,
            "range": rapid_range,
            "region": "US",
        }

        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        
        # Handle RapidAPI chart response format
        if isinstance(data, dict):
            # Check for top-level error
            if data.get("error"):
                return None
            
            # Chart endpoint returns: {"chart": {"result": [...], "error": ...}}
            chart = data.get("chart", {})
            if isinstance(chart, dict):
                # Check for error
                if chart.get("error"):
                    return None
                
                # Get result array
                result = chart.get("result", [])
                if isinstance(result, list) and len(result) > 0:
                    # Result contains chart data objects
                    chart_data = result[0] if isinstance(result[0], dict) else {}
                    # Get timestamps and indicators (OHLCV)
                    timestamps = chart_data.get("timestamp", [])
                    indicators = chart_data.get("indicators", {})
                    quote = indicators.get("quote", [])
                    
                    if quote and isinstance(quote, list) and len(quote) > 0:
                        quote_data = quote[0]  # First quote object
                        # Extract OHLCV arrays
                        opens = quote_data.get("open", [])
                        highs = quote_data.get("high", [])
                        lows = quote_data.get("low", [])
                        closes = quote_data.get("close", [])
                        volumes = quote_data.get("volume", [])
                        
                        # Get adjclose if available
                        adjclose_list = []
                        adjclose_data = indicators.get("adjclose", [])
                        if adjclose_data and isinstance(adjclose_data, list) and len(adjclose_data) > 0:
                            adjclose_list = adjclose_data[0].get("adjclose", [])
                        
                        if timestamps and len(timestamps) > 0 and len(closes) > 0:
                            # Build DataFrame from arrays
                            rows = []
                            for i, ts in enumerate(timestamps):
                                if i < len(closes) and closes[i] is not None:
                                    date = pd.to_datetime(ts, unit="s")
                                    row = {
                                        "Date": date,
                                        "Open": float(opens[i]) if i < len(opens) and opens[i] is not None else float(closes[i]),
                                        "High": float(highs[i]) if i < len(highs) and highs[i] is not None else float(closes[i]),
                                        "Low": float(lows[i]) if i < len(lows) and lows[i] is not None else float(closes[i]),
                                        "Close": float(closes[i]),
                                        "Volume": int(volumes[i]) if i < len(volumes) and volumes[i] is not None else 0,
                                    }
                                    # Use adjclose if available, otherwise use close
                                    if adjclose_list and i < len(adjclose_list) and adjclose_list[i] is not None:
                                        row["Adj Close"] = float(adjclose_list[i])
                                    else:
                                        row["Adj Close"] = row["Close"]
                                    rows.append(row)
                            
                            if rows:
                                df = pd.DataFrame(rows)
                                df = df.set_index("Date")
                                df = df.sort_index()
                                
                                # Ensure required columns exist
                                required_cols = ["Open", "High", "Low", "Close", "Volume", "Adj Close"]
                                if all(col in df.columns for col in required_cols):
                                    return df.dropna()
        
        return None
    except Exception:
        # Silently fail - will fall back to yfinance
        return None


def fetch_ohlcv_with_fallback(
    ticker: str, period: str = "2y", interval: str = "1d"
) -> pd.DataFrame:
    """
    Fetch OHLCV data with fallback to RapidAPI if yfinance fails.

    Args:
        ticker: Stock ticker symbol
        period: Time period
        interval: Data interval

    Returns:
        DataFrame with OHLCV data

    Raises:
        ValueError: If all data sources fail
    """
    # Try RapidAPI first if configured
    if RAPIDAPI_KEY:
        df = fetch_ohlcv_rapidapi(ticker, period, interval)
        if df is not None and not df.empty:
            return df

    # Fall back to yfinance (import here to avoid circular imports)
    from src.core.engine import fetch_ohlcv

    return fetch_ohlcv(ticker, period, interval, use_rapidapi=False)
