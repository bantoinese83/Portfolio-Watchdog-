#!/usr/bin/env python3
"""Test script to diagnose data fetching issues."""

import sys
from src.core.engine import fetch_ohlcv
from src.core.data_fetcher import RAPIDAPI_KEY, fetch_ohlcv_rapidapi

def test_ticker(ticker: str):
    """Test fetching data for a ticker using both methods."""
    print(f"\n{'='*60}")
    print(f"Testing ticker: {ticker}")
    print(f"{'='*60}")
    
    # Test RapidAPI
    print("\n1. Testing RapidAPI...")
    if RAPIDAPI_KEY:
        print("   ✅ RapidAPI key is set")
        try:
            df_rapid = fetch_ohlcv_rapidapi(ticker)
            if df_rapid is not None and not df_rapid.empty:
                print(f"   ✅ RapidAPI success: {len(df_rapid)} rows")
                print(f"   Date range: {df_rapid.index.min()} to {df_rapid.index.max()}")
            else:
                print("   ❌ RapidAPI returned empty/None")
        except Exception as e:
            print(f"   ❌ RapidAPI error: {str(e)[:200]}")
    else:
        print("   ⚠️  RapidAPI key not set (set RAPIDAPI_KEY env var)")
    
    # Test yfinance
    print("\n2. Testing yfinance...")
    try:
        df_yf = fetch_ohlcv(ticker, use_rapidapi=False)
        if not df_yf.empty:
            print(f"   ✅ yfinance success: {len(df_yf)} rows")
            print(f"   Date range: {df_yf.index.min()} to {df_yf.index.max()}")
        else:
            print("   ❌ yfinance returned empty DataFrame")
    except Exception as e:
        print(f"   ❌ yfinance error: {str(e)[:200]}")
    
    # Test with fallback
    print("\n3. Testing with automatic fallback...")
    try:
        df = fetch_ohlcv(ticker, use_rapidapi=True)
        if not df.empty:
            print(f"   ✅ Fallback success: {len(df)} rows")
            print(f"   Date range: {df.index.min()} to {df.index.max()}")
        else:
            print("   ❌ Fallback returned empty DataFrame")
    except Exception as e:
        print(f"   ❌ Fallback error: {str(e)[:200]}")

if __name__ == "__main__":
    tickers = sys.argv[1:] if len(sys.argv) > 1 else ["GOOGL", "AAPL"]
    for ticker in tickers:
        test_ticker(ticker)

