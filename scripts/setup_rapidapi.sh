#!/bin/bash
# Quick setup script for RapidAPI integration

echo "Setting up RapidAPI for Portfolio Watchdog..."
echo ""

# Set RapidAPI key (replace with your actual key)
# Get your key from: https://rapidapi.com/
export RAPIDAPI_KEY="${RAPIDAPI_KEY:-your-rapidapi-key-here}"
export RAPIDAPI_HOST="${RAPIDAPI_HOST:-yahoo-finance166.p.rapidapi.com}"

# Create .env file
cat > .env << EOF
# RapidAPI Configuration
RAPIDAPI_KEY=${RAPIDAPI_KEY}
RAPIDAPI_HOST=${RAPIDAPI_HOST}

# Database (defaults to SQLite)
# DATABASE_URL=sqlite:///portfolio_watchdog.db

# Cache TTL (optional)
# DATA_CACHE_TTL=1800
# CLASS_CACHE_TTL=300
EOF

echo "✅ RapidAPI configured!"
echo "✅ Created .env file with your API key"
echo ""
echo "You can now run: streamlit run app.py"
echo ""
echo "The app will use RapidAPI as the primary data source."

