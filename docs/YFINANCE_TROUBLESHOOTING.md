# yfinance API Troubleshooting Guide

## Common Issues

### JSONDecodeError: "Expecting value: line 1 column 1 (char 0)"

This error occurs when yfinance receives an empty or invalid response from Yahoo Finance API. Common causes:

1. **Rate Limiting**: Yahoo Finance may rate-limit requests
2. **Network Issues**: Temporary connectivity problems
3. **API Changes**: Yahoo Finance API structure may have changed
4. **Invalid Ticker**: Ticker symbol may not exist or be delisted

### Solutions Implemented

1. **Retry Logic**: The app automatically retries failed requests (3 attempts with exponential backoff)
2. **Error Suppression**: Verbose yfinance error messages are suppressed in the console
3. **Graceful Handling**: Failed tickers show "❌ Error" status in the UI instead of crashing
4. **Caching**: Successful fetches are cached to reduce API calls

### What You'll See

- **In Console**: Minimal error output (errors are suppressed)
- **In UI**: Failed tickers show:
  - Status: "❌ Error"
  - Note: Brief error description
  - Price: "N/A"

### Manual Solutions

If you're experiencing persistent API failures:

1. **Wait and Retry**: Yahoo Finance may be rate-limiting. Wait a few minutes and refresh
2. **Check Internet Connection**: Ensure stable network connectivity
3. **Verify Ticker Symbols**: Make sure ticker symbols are valid (e.g., "AAPL" not "APPL")
4. **Clear Cache**: Use the "Clear Cache" button to force fresh data fetches
5. **Reduce Watchlist Size**: Fewer concurrent requests may help avoid rate limits

### Alternative Data Sources

If yfinance continues to have issues, consider:

1. **Polygon.io**: Professional API (requires API key)
2. **Alpha Vantage**: Free tier available (requires API key)
3. **IEX Cloud**: Developer-friendly API (requires API key)

### Technical Details

The app uses:
- **Retry Logic**: 3 attempts with 1s, 2s, 3s delays
- **Error Suppression**: stdout redirection during yfinance calls
- **Caching**: 30-minute TTL for successful fetches
- **Graceful Degradation**: App continues working even if some tickers fail

### Monitoring

Check the dashboard for:
- Cache statistics (fewer cache hits = more API calls)
- Error rates (how many tickers are failing)
- Success patterns (which tickers work consistently)

If all tickers are failing, it's likely a network or API-wide issue.

