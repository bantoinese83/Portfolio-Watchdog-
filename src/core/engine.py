"""
Traffic Light Logic Engine for Portfolio Watchdog.

This module implements the proprietary technical analysis logic that classifies
stocks into three categories: GREEN (Bullish/Trend Healthy), YELLOW (Corrective/Opportunity),
and RED (Breakdown/Kill Switch).

The engine processes daily and weekly OHLCV data to determine:
- Trend structure (200-day moving average)
- Market structure integrity (weekly swing lows)
- Momentum indicators (RSI, price velocity)
- Fibonacci retracement levels
- Hidden bullish divergence patterns
"""

import datetime as dt
import io
import json
import logging
import sys
import time
import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
import yfinance as yf

from src.utils.cache import cached_data_fetch, cached_classification

# Suppress yfinance verbose warnings
logging.getLogger("yfinance").setLevel(logging.ERROR)

# Try to import TA-Lib, fallback to pandas-based RSI if unavailable
try:
    import talib

    HAS_TALIB = True
except (ImportError, ValueError, OSError):
    HAS_TALIB = False


@dataclass(slots=True)
class TrafficLightResult:
    """
    Encapsulates the traffic light classification and diagnostics
    for a single ticker at a single evaluation time.

    Attributes:
        ticker: Stock ticker symbol (uppercase)
        status: Classification status ("GREEN", "YELLOW", or "RED")
        emoji: Visual indicator ("🟢", "🟡", "🔴")
        price: Current closing price
        note: Actionable note explaining the classification
        ai_commentary: AI-generated natural language explanation (optional)
        as_of: Timestamp of the evaluation
    """

    ticker: str
    status: str  # "GREEN", "YELLOW", or "RED"
    emoji: str  # "🟢", "🟡", "🔴"
    price: float
    note: str
    ai_commentary: str = ""  # AI-generated explanation
    as_of: dt.datetime = dt.datetime.now(dt.timezone.utc)


@cached_data_fetch(ttl_seconds=1800)  # Cache for 30 minutes
def fetch_ohlcv(
    ticker: str, period: str = "2y", interval: str = "1d", use_rapidapi: bool = True
) -> pd.DataFrame:
    """
    Fetch OHLCV time series using yfinance with retry logic.

    This function retrieves historical price data from Yahoo Finance.
    The default period of 2 years provides sufficient history for computing
    the 200-day moving average and identifying weekly swing patterns.

    Args:
        ticker: Stock ticker symbol (e.g., "TSLA")
        period: Time period to fetch (default: "2y" for 2 years)
        interval: Data interval (default: "1d" for daily bars)

    Returns:
        DataFrame indexed by datetime with columns:
        ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

    Raises:
        ValueError: If no data is returned for the ticker after retries
    """
    max_retries = 3
    retry_delay = 1  # seconds

    # Try RapidAPI first if configured and enabled
    if use_rapidapi:
        try:
            from src.core.data_fetcher import fetch_ohlcv_rapidapi

            df_rapidapi = fetch_ohlcv_rapidapi(ticker, period, interval)
            if df_rapidapi is not None and not df_rapidapi.empty:
                return df_rapidapi
        except Exception:
            # Fall through to yfinance if RapidAPI fails
            pass

    for attempt in range(max_retries):
        try:
            # Suppress yfinance's verbose output (both stdout and stderr)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Suppress yfinance logger
                yf_logger = logging.getLogger("yfinance")
                old_level = yf_logger.level
                yf_logger.setLevel(logging.CRITICAL)
                
                # Redirect both stdout and stderr to suppress all yfinance messages
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                try:
                    # Redirect both stdout and stderr to suppress all print/error messages
                    sys.stdout = io.StringIO()
                    sys.stderr = io.StringIO()
                    df = yf.download(
                        ticker,
                        period=period,
                        interval=interval,
                        auto_adjust=False,
                        progress=False,
                    )
                except Exception:
                    # Re-raise after restoring streams
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    yf_logger.setLevel(old_level)
                    raise
                finally:
                    # Always restore both streams and logger
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    yf_logger.setLevel(old_level)

            if df.empty or df is None:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                # Provide more helpful error message
                raise ValueError(
                    f"No data returned for {ticker}. "
                    f"This may be due to: invalid ticker symbol, market closed, "
                    f"or API rate limiting. Please verify the ticker and try again later."
                )

            # Handle MultiIndex columns (yfinance sometimes returns these)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)

            df = df.dropna()
            if df.empty:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise ValueError(f"No valid data after processing for {ticker}")

            return df

        except (ValueError, KeyError, AttributeError, TypeError, json.JSONDecodeError) as e:
            # Handle JSON decode errors and other data issues
            error_msg = str(e)
            if isinstance(e, json.JSONDecodeError) or "JSON" in error_msg or "Expecting value" in error_msg:
                # API rate limiting or invalid response - yfinance got empty/invalid JSON
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise ValueError(
                    f"API error for {ticker} (rate limit or invalid response). Please try again later."
                )
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            raise ValueError(f"Failed to fetch data for {ticker}: {error_msg}")
        except Exception as e:
            # Catch all other exceptions (network errors, etc.)
            error_msg = str(e)
            # Also catch JSONDecodeError that might be wrapped
            if "JSONDecodeError" in str(type(e)) or "Expecting value" in error_msg:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise ValueError(
                    f"API error for {ticker} (rate limit or invalid response). Please try again later."
                )
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            raise ValueError(f"Error fetching {ticker}: {error_msg}")

    raise ValueError(f"Failed to fetch data for {ticker} after {max_retries} attempts")


def resample_to_weekly(df_daily: pd.DataFrame) -> pd.DataFrame:
    """
    Resample daily OHLCV to weekly bars using standard OHLC aggregation rules.

    Weekly bars are essential for identifying major swing lows that define
    market structure. The weekly timeframe filters out daily noise and reveals
    the underlying trend structure.

    Aggregation rules:
    - Weekly open: first open of the week
    - Weekly high: maximum high of the week
    - Weekly low: minimum low of the week
    - Weekly close: last close of the week
    - Volume: sum of daily volumes

    Weeks are grouped by calendar week ending on Friday (W-FRI).

    Args:
        df_daily: Daily OHLCV DataFrame

    Returns:
        Weekly OHLCV DataFrame with same column structure
    """
    ohlc_dict = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }
    weekly = df_daily.resample("W-FRI").agg(ohlc_dict).dropna()
    return weekly


def find_major_weekly_swing_lows(
    df_weekly: pd.DataFrame,
    lookback: int = 2,
    prominence: float | None = None,
) -> pd.DataFrame:
    """
    Detect major weekly swing lows based on local minima in Low prices.

    Optimized using vectorized NumPy operations for better performance.

    A swing low is identified when a bar's Low is strictly lower than both:
    - The previous 'lookback' bars
    - The next 'lookback' bars

    This prevents false signals during healthy corrections by requiring
    a clear local minimum with sufficient context on both sides.

    Optional 'prominence' parameter filters out shallow lows by requiring
    the swing low to be at least 'prominence' percent below the local
    average Low around it. This helps identify "major" swing lows that
    represent significant structural support levels.

    Args:
        df_weekly: Weekly OHLCV DataFrame
        lookback: Number of bars to look back/forward for local minimum (default: 2)
        prominence: Optional minimum percentage drop below local average (default: None)

    Returns:
        DataFrame with added boolean column 'swing_low' marking detected swing lows
    """
    lows = df_weekly["Low"].values
    n = len(lows)

    if n < 2 * lookback + 1:
        # Not enough data for swing detection
        df_weekly = df_weekly.copy()
        df_weekly["swing_low"] = np.zeros(n, dtype=bool)
        return df_weekly

    # Vectorized approach: use rolling windows for better performance
    swing_mask = np.zeros(n, dtype=bool)

    # Use vectorized operations where possible
    for i in range(lookback, n - lookback):
        # Get the low prices before and after the current bar
        past = lows[i - lookback : i]
        future = lows[i + 1 : i + 1 + lookback]

        # Check if current bar's low is lower than all surrounding bars
        past_min, future_min = past.min(), future.min()
        is_local_min = lows[i] < past_min and lows[i] < future_min

        if not is_local_min:
            continue

        # Optional prominence filter: require significant drop below local average
        if prominence is not None:
            # Calculate local average around the swing low
            window = lows[i - lookback : i + 1 + lookback]
            local_mean = window.mean()
            # Calculate percentage drop from local mean
            drawdown_pct = (local_mean - lows[i]) / local_mean * 100.0
            # Only mark as swing low if drop exceeds prominence threshold
            if drawdown_pct < prominence:
                continue

        swing_mask[i] = True

    # Add swing_low column to DataFrame (use view if possible)
    df_weekly = df_weekly.copy()
    df_weekly["swing_low"] = swing_mask
    return df_weekly


def get_last_major_swing_low(df_weekly: pd.DataFrame) -> float:
    """
    Return the price (Low) of the last detected major weekly swing low.

    This price level represents the most recent structural support. If price
    closes below this level, market structure is considered broken (RED status).

    If no swing lows are detected (edge case), we fall back to the minimum
    low over the last 20 weeks as a conservative estimate of support.

    Args:
        df_weekly: Weekly DataFrame with 'swing_low' column from find_major_weekly_swing_lows

    Returns:
        Float price of the last major swing low
    """
    swings = df_weekly[df_weekly["swing_low"]]
    if not swings.empty:
        # Return the most recent swing low price
        return float(swings["Low"].iloc[-1])
    # Fallback: use minimum low over recent period
    return float(df_weekly["Low"].tail(20).min())


def _calculate_rsi_pandas(close: pd.Series, timeperiod: int = 14) -> pd.Series:
    """
    Calculate RSI using pandas (fallback when TA-Lib is unavailable).

    RSI (Relative Strength Index) is calculated as:
    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss over the period

    Args:
        close: Series of closing prices
        timeperiod: Number of periods for RSI calculation (default: 14)

    Returns:
        Series of RSI values
    """
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=timeperiod).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=timeperiod).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_indicators(df_daily: pd.DataFrame) -> pd.DataFrame:
    """
    Compute technical indicators needed for the traffic light system.

    Optimized to compute all indicators in a single pass and avoid
    unnecessary DataFrame copies.

    This function calculates:
    - 200-day SMA: Long-term trend filter (bullish if price > SMA)
    - 20-day rolling high: Threshold for "healthy correction" detection
    - RSI (14): Momentum oscillator for divergence detection
    - Momentum: Daily price change (positive = rising, negative = falling)

    Args:
        df_daily: Daily OHLCV DataFrame

    Returns:
        DataFrame with added columns: ['sma_200', 'high_20', 'rsi_14', 'momentum']
    """
    # Use assign() to add columns in a single operation (more efficient)
    close = df_daily["Close"]
    high = df_daily["High"]

    df = df_daily.assign(
        # 200-day moving average of closing price (trend filter).
        # This is the primary long-term trend indicator. Price above SMA = bullish trend.
        # We use min_periods=50 to allow calculation even with limited history.
        sma_200=close.rolling(window=200, min_periods=50).mean(),
        # 20-day high to define 'healthy correction' threshold.
        # If price drops below this but stays above swing low, it's a YELLOW correction.
        high_20=high.rolling(window=20, min_periods=5).max(),
        # RSI calculation - use TA-Lib if available, otherwise use pandas-based implementation
        # RSI < 30 is considered oversold, which can signal buying opportunities
        # when combined with price holding above structural support.
        rsi_14=(
            talib.RSI(close, timeperiod=14)
            if HAS_TALIB
            else _calculate_rsi_pandas(close, timeperiod=14)
        ),
        # Approximate numeric momentum as daily price change.
        # Positive momentum means price is rising day-over-day.
        # Negative momentum means price is falling.
        momentum=close.diff(),
    )

    return df.dropna()


def check_hidden_bullish_divergence(
    closes: pd.Series,
    rsis: pd.Series,
    swing_low_price: float,
    oversold_level: float = 30.0,
    lookback_bars: int = 60,
) -> bool:
    """
    Detect a simplified form of hidden bullish divergence.

    Hidden bullish divergence occurs when:
    - Price retests or slightly undercuts the prior weekly swing low,
      but holds above it on a closing basis (structure intact)
    - RSI prints an oversold reading (< 30) and then forms a higher low
      while price holds the low zone

    This pattern suggests that selling pressure is weakening even though
    price is testing support, which can signal a potential reversal or
    "sniper" entry opportunity during corrections.

    This is a simplified, rule-based approximation intended to flag
    potential entry opportunities during YELLOW (corrective) phases.

    Args:
        closes: Series of closing prices
        rsis: Series of RSI values (must align with closes index)
        swing_low_price: The structural support level to test against
        oversold_level: RSI threshold for oversold condition (default: 30.0)
        lookback_bars: Number of recent bars to analyze (default: 60)

    Returns:
        True if hidden bullish divergence pattern is detected, False otherwise
    """
    if closes.empty or rsis.empty:
        return False

    # Focus on recent price action
    recent_closes = closes.tail(lookback_bars)
    recent_rsis = rsis.reindex_like(recent_closes).dropna()
    if recent_rsis.empty:
        return False

    # Identify the most recent RSI oversold point
    oversold_idx = recent_rsis[recent_rsis < oversold_level].index
    if not oversold_idx.size:
        return False

    # Get the oversold bar nearest to the present
    last_oversold_idx = oversold_idx[-1]

    # Require that price at that bar is close to the prior swing low (within 5%)
    # This ensures we're testing structural support, not just any low
    price_at_oversold = closes.loc[last_oversold_idx]
    if price_at_oversold > swing_low_price * 1.05:
        # More than 5% above swing low: not a "retest" of support
        return False

    # Look for a subsequent higher RSI low while price holds the low zone
    # This is the divergence: RSI improving while price holds support
    rsis_after = recent_rsis[recent_rsis.index > last_oversold_idx]
    if rsis_after.empty:
        return False

    # Simple rule: any RSI after oversold must be above the oversold value
    # while price does not close significantly below the swing low (within 3%)
    oversold_rsi = recent_rsis.loc[last_oversold_idx]
    min_price = swing_low_price * 0.97
    return any(
        rsi_val > oversold_rsi and closes.loc[t] >= min_price
        for t, rsi_val in rsis_after.items()
    )


@cached_classification(ttl_seconds=300)  # Cache for 5 minutes
def classify_ticker(
    ticker: str,
    df_daily: pd.DataFrame | None = None,
    df_weekly: pd.DataFrame | None = None,
) -> TrafficLightResult:
    """
    Core traffic light classifier implementing the proprietary trading logic.

    This function implements the three-tier classification system:

    1) 🟢 GREEN (Trend Healthy / Bullish):
       - Close > 200-day SMA (price above long-term trend)
       - Momentum positive (price rising)
       - User Action: "Hold / Add"

    2) 🟡 YELLOW (Healthy Correction / The Opportunity Zone):
       - Close below 20-day high (correction in progress)
       - Close above last major weekly swing low (structure intact)
       - "Sniper" checks for entry opportunities:
         - Price near 61.8% Fibonacci retracement
         - Hidden bullish divergence (RSI oversold while price holds low)
       - User Action: "Watch for Entry (Buy the Dip)"

    3) 🔴 RED (Breakdown / The Kill Switch):
       - Close below last major weekly swing low (structure broken)
       - OR Close < 200-day MA with negative velocity (trend reversal)
       - User Action: "Exit / Avoid (Trend is Dead)"

    Args:
        ticker: Stock ticker symbol
        df_daily: Optional pre-fetched daily data (for testing/caching)
        df_weekly: Optional pre-fetched weekly data (for testing/caching)

    Returns:
        TrafficLightResult with classification, price, and actionable note
    """
    # Fetch data if not provided (allows for testing with mock data)
    if df_daily is None:
        df_daily = fetch_ohlcv(ticker)
    if df_weekly is None:
        df_weekly = resample_to_weekly(df_daily)

    # Detect weekly swing lows to define structural support
    # lookback=2 means we need 2 weeks on each side to confirm a swing low
    # prominence=3.0 means the swing low must be at least 3% below local average
    df_weekly_swings = find_major_weekly_swing_lows(
        df_weekly, lookback=2, prominence=3.0
    )
    last_swing_low_price = get_last_major_swing_low(df_weekly_swings)

    # Compute daily indicators (SMA, RSI, momentum, etc.)
    df_ind = compute_indicators(df_daily)
    latest = df_ind.iloc[-1]
    prev = df_ind.iloc[-2] if len(df_ind) >= 2 else latest

    # Extract key values for classification
    close = float(latest["Close"])
    sma_200 = float(latest["sma_200"])
    high_20 = float(latest["high_20"])
    momentum = float(latest["momentum"])
    prev_momentum = float(prev["momentum"])

    note_parts: list[str] = []

    # 3) RED: structural breakdown or crash below 200-day MA with negative momentum
    is_below_swing_low = close < last_swing_low_price
    is_below_sma_with_negative_momentum = (
        close < sma_200 and momentum < 0 and prev_momentum < 0
    )

    if is_below_swing_low:
        # Structure broken: price closed below last major support
        status, emoji = "RED", "🔴"
        note_parts.append(
            "Price closed below last major weekly swing low (structure broken)."
        )
    elif is_below_sma_with_negative_momentum:
        # Trend reversal: below 200-day MA with persistent negative momentum
        status, emoji = "RED", "🔴"
        note_parts.append(
            "Price is below 200-day MA with persistent negative momentum."
        )
    elif close > sma_200 and momentum > 0:
        # 1) GREEN: above 200-day MA with positive momentum
        status, emoji = "GREEN", "🟢"
        note_parts.append(
            "Trend is healthy: price above 200-day MA and momentum positive."
        )
    elif close < high_20 and close > last_swing_low_price:
        # 2) YELLOW: correction zone but structure intact
        status, emoji = "YELLOW", "🟡"
        note_parts.append(
            "Price is in a correction below 20-day high but structure is intact above swing low."
        )

        # "Sniper" checks for opportunity zone
        swing_low = last_swing_low_price
        swing_high = float(df_ind["High"].tail(60).max())
        if swing_high > swing_low:
            # 61.8% Fibonacci retracement level
            fib_61_8 = swing_high - 0.618 * (swing_high - swing_low)
            # Check if price is within 3% of the 61.8% level
            if abs(close - fib_61_8) / swing_high < 0.03:
                note_parts.append(
                    "Price is testing 61.8% Fibonacci retracement support."
                )

        # Hidden bullish divergence check using RSI and price around last swing
        if check_hidden_bullish_divergence(
            closes=df_ind["Close"],
            rsis=df_ind["rsi_14"],
            swing_low_price=swing_low,
            oversold_level=30.0,
            lookback_bars=80,
        ):
            note_parts.append(
                "RSI oversold while price holds above swing low (hidden bullish divergence)."
            )
    else:
        # Fallback: treat as RED if neither clearly green nor in controlled correction
        status, emoji = "RED", "🔴"
        note_parts.append("Trend is weak and outside defined healthy correction zone.")

    note = " ".join(note_parts) if note_parts else "No specific note."
    
    # Generate AI commentary (with fallback to note if OpenAI not configured)
    ai_commentary = ""
    try:
        from src.ai.commentary import get_cached_ai_commentary
        
        # Prepare indicator data for AI context
        indicators = {
            "RSI": float(latest.get("rsi_14", 0)),
            "200-day SMA": sma_200,
            "20-day High": high_20,
            "Momentum": momentum,
            "Swing Low": last_swing_low_price,
        }
        
        ai_commentary = get_cached_ai_commentary(
            ticker=ticker.upper(),
            status=status,
            price=close,
            note=note,
            indicators=indicators,
        )
    except Exception:
        # If AI commentary fails, use technical note
        ai_commentary = note
    
    return TrafficLightResult(
        ticker=ticker.upper(),
        status=status,
        emoji=emoji,
        price=close,
        note=note,
        ai_commentary=ai_commentary,
        as_of=df_ind.index[-1].to_pydatetime(),
    )
