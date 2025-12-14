# Quick Start: RapidAPI Setup

## Using Your RapidAPI Key

You've provided a RapidAPI configuration. Here's how to set it up:

### Option 1: Environment Variables (Recommended)

```bash
# Linux/macOS
export RAPIDAPI_KEY="15052fd3b7msh85597e335ff2a7bp169e53jsn5345b8fd7dd1"
export RAPIDAPI_HOST="yahoo-finance166.p.rapidapi.com"

# Windows (PowerShell)
$env:RAPIDAPI_KEY="15052fd3b7msh85597e335ff2a7bp169e53jsn5345b8fd7dd1"
$env:RAPIDAPI_HOST="yahoo-finance166.p.rapidapi.com"
```

### Option 2: .env File

Create a `.env` file in the project root:

```bash
RAPIDAPI_KEY=15052fd3b7msh85597e335ff2a7bp169e53jsn5345b8fd7dd1
RAPIDAPI_HOST=yahoo-finance166.p.rapidapi.com
```

The app will automatically load these via `python-dotenv`.

### How It Works

Once configured, the app will:
1. **Try RapidAPI first** (if key is set)
2. **Fall back to yfinance** if RapidAPI fails or isn't configured
3. **Cache results** for 30 minutes to reduce API calls

### Benefits

- ✅ More reliable than yfinance
- ✅ Different rate limits
- ✅ Automatic fallback
- ✅ No code changes needed

### Verify It's Working

1. Set the environment variables
2. Run the app: `streamlit run app.py`
3. Add a ticker to your watchlist
4. Check if data loads successfully

If RapidAPI is working, you should see successful data fetches even when yfinance has issues.

### MCP Server Configuration

For AI assistant integration, your MCP config is:

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
        "x-api-key: 15052fd3b7msh85597e335ff2a7bp169e53jsn5345b8fd7dd1"
      ]
    }
  }
}
```

This allows AI assistants to access RapidAPI via MCP, but the Python app uses direct API calls.

### Security Note

⚠️ **Important**: The API key shown above should be kept secure. Consider:
- Using environment variables (not hardcoded)
- Rotating keys periodically
- Using different keys for dev/prod

