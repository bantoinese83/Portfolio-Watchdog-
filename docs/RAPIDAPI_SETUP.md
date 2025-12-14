# RapidAPI YFinance Integration

## Overview

This guide explains how to use RapidAPI's YFinance API as an alternative data source when the standard yfinance library has issues.

## Setup

### 1. Get RapidAPI Key

1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to "Yahoo Finance API" (or similar)
3. Get your API key from the dashboard

### 2. Configure Environment Variable

Set the RapidAPI key as an environment variable:

```bash
# Linux/macOS
export RAPIDAPI_KEY="your-api-key-here"
export RAPIDAPI_HOST="yahoo-finance166.p.rapidapi.com"

# Windows (PowerShell)
$env:RAPIDAPI_KEY="your-api-key-here"
$env:RAPIDAPI_HOST="yahoo-finance166.p.rapidapi.com"
```

Or create a `.env` file:

```bash
RAPIDAPI_KEY=your-api-key-here
RAPIDAPI_HOST=yahoo-finance166.p.rapidapi.com
```

### 3. Usage

The app will automatically use RapidAPI as a fallback if:
- `RAPIDAPI_KEY` is set
- yfinance fails to fetch data

## MCP Server Configuration

If you want to use RapidAPI via MCP (Model Context Protocol) for AI assistants, add this to your MCP configuration:

```json
{
  "mcpServers": {
    "RapidAPI Hub - YFinance API": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.rapidapi.com",
        "--header",
        "x-api-host: yahoo-finance166.p.rapidapi.com",
        "--header",
        "x-api-key: YOUR_API_KEY_HERE"
      ]
    }
  }
}
```

**Note**: Replace `YOUR_API_KEY_HERE` with your actual RapidAPI key.

## Benefits

- **Reliability**: Alternative data source when yfinance has issues
- **Rate Limits**: Different rate limits than yfinance
- **Consistency**: More reliable API responses
- **Fallback**: Automatic fallback if one source fails

## Current Implementation

The app currently uses:
1. **Primary**: yfinance (standard library)
2. **Fallback**: RapidAPI (if configured)

To enable RapidAPI:
1. Set `RAPIDAPI_KEY` environment variable
2. The app will automatically use it as a fallback

## API Endpoints

The RapidAPI integration uses:
- **Base URL**: `https://yahoo-finance166.p.rapidapi.com`
- **Endpoint**: `/api/v1/historical-data`
- **Method**: GET
- **Headers**: 
  - `X-RapidAPI-Key`: Your API key
  - `X-RapidAPI-Host`: API host

## Troubleshooting

### RapidAPI Not Working

1. Verify API key is correct
2. Check API subscription status
3. Verify rate limits haven't been exceeded
4. Check network connectivity

### Still Using yfinance

If RapidAPI is configured but not being used:
1. Check environment variables are set correctly
2. Verify the API key is valid
3. Check if yfinance is succeeding (no fallback needed)

## Cost Considerations

- RapidAPI may have usage limits based on your subscription
- Free tier typically has limited requests per month
- Check your RapidAPI dashboard for usage and limits

## Security

**Important**: Never commit your API key to version control!

- Use environment variables
- Add `.env` to `.gitignore` (already done)
- Use secure methods to share API keys in production

