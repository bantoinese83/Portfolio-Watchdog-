# OpenAI API Setup for AI Commentary

## Overview

The Portfolio Watchdog now includes AI-powered natural language explanations for each stock classification using OpenAI GPT-4.

## Setup Instructions

### 1. Get OpenAI API Key

1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Navigate to [API Keys](https://platform.openai.com/api-keys)
3. Create a new API key
4. Copy the key (starts with `sk-...`)

### 2. Configure API Key

**Option 1: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Option 2: .env File**
Add to your `.env` file:
```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini  # Optional: defaults to gpt-4o-mini
```

### 3. Install Dependencies

```bash
pip install openai==1.54.3
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Model Options

### Recommended: GPT-4o-mini (Default)
- **Cost**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **Speed**: Fast
- **Quality**: Excellent for this use case
- **Best for**: Production use, cost-effective

### Alternative: GPT-4
- **Cost**: ~$30 per 1M input tokens, ~$60 per 1M output tokens
- **Speed**: Slower
- **Quality**: Highest quality
- **Best for**: When you need maximum quality

### Change Model

Set in `.env`:
```bash
OPENAI_MODEL=gpt-4  # Use GPT-4 instead of mini
```

Or via environment variable:
```bash
export OPENAI_MODEL=gpt-4
```

## How It Works

1. **Classification**: The system classifies each ticker (GREEN/YELLOW/RED)
2. **AI Commentary**: OpenAI generates a natural language explanation
3. **Caching**: Commentary is cached for 30 minutes to reduce API calls
4. **Fallback**: If OpenAI is unavailable, shows technical note instead

## Example Output

**Without AI**:
> "Price is in a correction below 20-day high but structure is intact above swing low."

**With AI**:
> "GOOGL is currently in a YELLOW status, indicating a healthy correction phase. The stock is trading below its recent 20-day high, which suggests a pullback, but importantly, the price remains above the key weekly swing low support level. This means the overall structure is still intact. Investors should watch for potential entry opportunities as the stock may be setting up for a bounce, especially if it holds above the swing low and RSI begins to recover from oversold levels."

## Cost Estimation

### Per Classification:
- **Input tokens**: ~150-200 tokens
- **Output tokens**: ~50-100 tokens
- **Cost per classification**: ~$0.0001 - $0.0002 (with GPT-4o-mini)

### Monthly Estimate (100 classifications/day):
- **Daily cost**: ~$0.01 - $0.02
- **Monthly cost**: ~$0.30 - $0.60

### With Caching:
- Caching reduces API calls by ~90%
- **Actual monthly cost**: ~$0.03 - $0.06

## Features

✅ **Automatic**: Works automatically for all classifications
✅ **Cached**: Results cached for 30 minutes
✅ **Graceful Fallback**: Shows technical note if API unavailable
✅ **Cost-Effective**: Uses GPT-4o-mini by default
✅ **Customizable**: Can switch to GPT-4 or other models

## Troubleshooting

### "AI Analysis" shows technical note instead of AI commentary

**Possible causes**:
1. OpenAI API key not set
2. API key invalid or expired
3. Rate limit exceeded
4. Network error

**Solutions**:
1. Check `.env` file has `OPENAI_API_KEY` set
2. Verify API key at [OpenAI Platform](https://platform.openai.com/api-keys)
3. Check API usage at [OpenAI Usage](https://platform.openai.com/usage)
4. Check network connectivity

### High API costs

**Solutions**:
1. Ensure caching is working (check cache stats in UI)
2. Use GPT-4o-mini instead of GPT-4
3. Increase cache TTL in `.env`: `DATA_CACHE_TTL=3600` (1 hour)

### Slow response times

**Solutions**:
1. Use GPT-4o-mini (faster than GPT-4)
2. Ensure caching is enabled
3. Check OpenAI API status

## Security

⚠️ **Important**: Never commit your API key to version control!

- ✅ Use `.env` file (already in `.gitignore`)
- ✅ Use environment variables
- ✅ Rotate keys periodically
- ❌ Never hardcode in source code
- ❌ Never share keys publicly

## API Rate Limits

OpenAI has rate limits based on your tier:
- **Free tier**: 3 requests/minute
- **Tier 1**: 500 requests/minute
- **Tier 2**: 5000 requests/minute

With caching, you should stay well within limits even on the free tier.

## Support

For issues or questions:
1. Check OpenAI API status: https://status.openai.com/
2. Review OpenAI docs: https://platform.openai.com/docs
3. Check application logs for error messages

