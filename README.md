# The Portfolio Watchdog (MVP)

Automated stock analysis dashboard that classifies assets into **Green**, **Yellow**, or **Red** traffic light states based on proprietary technical analysis of daily and weekly OHLCV data.

## 🎯 Overview

The Portfolio Watchdog is a "Set and Forget" dashboard where users input stock tickers and instantly see if the asset is:
- 🟢 **GREEN**: Safe/Trending (Hold / Add)
- 🟡 **YELLOW**: In a Healthy Correction (Watch for Entry / Buy the Dip)
- 🔴 **RED**: Structurally Broken (Exit / Avoid)

## 🏗️ Architecture

- **Frontend**: Streamlit (clean, mobile-responsive, password-protected)
- **Backend**: Python 3.9+ with Pandas, NumPy, TA-Lib
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Data Source**: yfinance (Yahoo Finance API)
- **Authentication**: streamlit-authenticator

## 📋 Prerequisites

- Python 3.9 or higher
- PostgreSQL database (local or remote)
- TA-Lib library (may require OS-level dependencies)

## 🚀 1. Clone & Environment Setup

```bash
git clone https://github.com/your-org/portfolio_watchdog.git
cd portfolio_watchdog

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Alternative: Using Conda

```bash
conda create -n watchdog python=3.11
conda activate watchdog
pip install -r requirements.txt
```

## 📦 2. TA-Lib Installation

TA-Lib may require OS-level dependencies. Installation varies by platform:

### macOS
```bash
brew install ta-lib
pip install TA-Lib
```

### Ubuntu / Debian
```bash
sudo apt-get update
sudo apt-get install -y build-essential
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

### Windows
Download the TA-Lib installer from [ta-lib.org](http://ta-lib.org/install.html) or use a pre-built wheel:
```bash
pip install TA-Lib
```

If installation fails, consult the [TA-Lib documentation](https://ta-lib.org/) for your platform.

## 🔐 3. Configure Authentication

1. Copy the example config file:
```bash
cp config_example.yaml config.yaml
```

2. Generate hashed passwords using Python:
```python
import streamlit_authenticator as stauth

# Replace with your desired password
passwords = ["your_plain_password_here"]
hashed = stauth.Hasher(passwords).generate()
print(hashed[0])  # Copy this string
```

3. Edit `config.yaml`:
   - Replace `$2b$12$examplehashedpasswordstring` with your generated hash
   - Update the `cookie.key` to a random secret string (use a password generator)
   - Add additional users as needed

**Example `config.yaml`:**
```yaml
credentials:
  usernames:
    demo_user:
      email: demo@example.com
      name: Demo User
      password: "$2b$12$YourGeneratedHashHere..."

cookie:
  name: "portfolio_watchdog_cookie"
  key: "CHANGE_THIS_TO_RANDOM_SECRET_KEY"
  expiry_days: 7

preauthorized:
  emails: []
```

## 🗄️ 4. Database Setup

### Option A: SQLite (Recommended for Development)

**No setup required!** The app uses SQLite by default for easy development.

The database file `portfolio_watchdog.db` will be created automatically in the project directory when you first run the app.

### Option B: PostgreSQL (Recommended for Production)

#### Create Database and User

```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE portfolio_watchdog;
CREATE USER watchdog_user WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE portfolio_watchdog TO watchdog_user;
```

#### Set Environment Variable

```bash
# Linux/macOS
export DATABASE_URL="postgresql://watchdog_user:strongpassword@localhost:5432/portfolio_watchdog"

# Windows (PowerShell)
$env:DATABASE_URL="postgresql://watchdog_user:strongpassword@localhost:5432/portfolio_watchdog"
```

**Note**: 
- Tables are created automatically at app startup via `init_db()` in `db.py`
- No manual schema creation is required
- For development, SQLite works perfectly and requires no setup

### Alternative: Using .env file

Create a `.env` file in the project root:
```
DATABASE_URL=postgresql://watchdog_user:strongpassword@localhost:5432/portfolio_watchdog
AUTH_CONFIG_PATH=config.yaml
```

Then install `python-dotenv` (already in requirements.txt) and the app will load these variables automatically.

## 🏃 5. Running Locally

```bash
streamlit run app.py
```

Open the URL shown in your terminal (default `http://localhost:8501`).

### First Login

1. Use the username and password you configured in `config.yaml`
2. The app will automatically create your user record in the database
3. Add tickers to your watchlist to see traffic light status

## 📊 6. Data Source Configuration

The engine uses the `yfinance` package to fetch OHLCV data from Yahoo Finance. **No authentication is required** for basic use cases.

### Switching to Polygon.io (Optional)

If you prefer Polygon.io for more reliable data:

1. Create a [Polygon account](https://polygon.io/) and generate an API key
2. Store the key as an environment variable:
   ```bash
   export POLYGON_API_KEY="your_polygon_key"
   ```
3. Implement a `fetch_ohlcv_polygon(ticker: str, ...)` function in `engine.py`
4. Modify `classify_ticker()` to use Polygon instead of yfinance

## 🚢 7. Deployment

### Option A: Heroku-style Deployment

1. **Add a `Procfile`:**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Add `runtime.txt` (optional):**
   ```
   python-3.11.0
   ```

3. **Configure environment variables in Heroku:**
   ```bash
   heroku config:set DATABASE_URL="postgresql://..."
   heroku config:set AUTH_CONFIG_PATH="config.yaml"
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

### Option B: AWS (Containerized)

1. **Create a `Dockerfile`:**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   # Install TA-Lib dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       wget \
       && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
       && tar -xzf ta-lib-0.4.0-src.tar.gz \
       && cd ta-lib/ \
       && ./configure --prefix=/usr \
       && make \
       && make install \
       && cd .. \
       && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8501
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and push to ECR:**
   ```bash
   docker build -t portfolio-watchdog .
   docker tag portfolio-watchdog:latest <account>.dkr.ecr.<region>.amazonaws.com/portfolio-watchdog:latest
   docker push <account>.dkr.ecr.<region>.amazonaws.com/portfolio-watchdog:latest
   ```

3. **Deploy to ECS Fargate** behind an Application Load Balancer
4. **Configure environment variables** in the ECS task definition

### Option C: Docker Compose (Local/Development)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: portfolio_watchdog
      POSTGRES_USER: watchdog_user
      POSTGRES_PASSWORD: strongpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      DATABASE_URL: postgresql://watchdog_user:strongpassword@db:5432/portfolio_watchdog
      AUTH_CONFIG_PATH: config.yaml
    depends_on:
      - db
    volumes:
      - ./config.yaml:/app/config.yaml

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

## ⏰ 8. Automation & Scheduling

The logic engine is deterministic and stateless for a given ticker, so the application can re-compute status on demand.

### Option A: Background Worker (Recommended for Production)

Use a scheduled task (cron, ECS scheduled task, or AWS Lambda + EventBridge) that:

1. Iterates through distinct tickers in `watchlist_items`
2. Calls `classify_ticker()` for each ticker
3. Persists snapshot results to a separate `ticker_snapshots` table (optional, for historical tracking)

**Example Lambda function:**
```python
import os
from db import SessionLocal, WatchlistItem
from engine import classify_ticker

def lambda_handler(event, context):
    db = SessionLocal()
    try:
        # Get all unique tickers from all watchlists
        tickers = db.query(WatchlistItem.ticker).distinct().all()
        for (ticker,) in tickers:
            result = classify_ticker(ticker)
            # Store result in snapshot table or send notification
    finally:
        db.close()
```

### Option B: On-Demand Refresh

Keep the current on-demand architecture and rely on Streamlit reruns. The underlying yfinance calls will fetch fresh data each session when users click "Refresh Data".

## 📚 9. Notes on Logic

### Swing Lows
Implemented in `find_major_weekly_swing_lows()` with adjustable `lookback` and `prominence` parameters to reduce false signals:
- `lookback=2`: Requires 2 weeks on each side to confirm a swing low
- `prominence=3.0`: Swing low must be at least 3% below local average

### Fibonacci Retracement
The 61.8% level is calculated from the recent swing low to the recent high over the last 60 daily bars. Price within 3% of this level triggers a note in YELLOW status.

### RSI Divergence
A simplified hidden bullish divergence heuristic is implemented in `check_hidden_bullish_divergence()`. It detects:
- RSI oversold (< 30) while price tests structural support
- Subsequent RSI improvement while price holds above support

### Tuning Parameters
You can adjust thresholds and windows in `engine.py` to better match your proprietary strategy:
- `oversold_level`: RSI threshold (default: 30.0)
- `lookback_bars`: Bars to analyze for divergence (default: 60-80)
- `prominence`: Minimum swing low prominence (default: 3.0%)

## 🧪 Testing

### Manual Testing
1. Add a few tickers to your watchlist (e.g., TSLA, AAPL, MSFT)
2. Verify traffic light status updates correctly
3. Test adding/removing tickers
4. Verify authentication and logout

### Unit Testing (Future Enhancement)
Create `tests/` directory and add tests for:
- `engine.py` functions (swing low detection, divergence checks)
- Database operations (add/remove tickers)
- Classification logic with mock data

## 📖 Code Documentation

All functions, classes, and complex logic blocks are thoroughly commented. Key areas:
- **Swing Low Detection**: Explains the algorithm to prevent false signals
- **Divergence Checks**: Documents the hidden bullish divergence logic
- **Database Models**: SQLAlchemy models with relationship explanations
- **Traffic Light Logic**: Step-by-step classification rules

## 🐛 Troubleshooting

### "No data returned for {ticker}"
- Check internet connection
- Verify ticker symbol is correct
- yfinance may be rate-limited; wait a few minutes

### "Authentication config file not found"
- Ensure `config.yaml` exists (copy from `config_example.yaml`)
- Check `AUTH_CONFIG_PATH` environment variable

### "Database connection failed"
- Verify PostgreSQL is running
- Check `DATABASE_URL` environment variable
- Ensure database and user exist

### TA-Lib import errors
- Install OS-level TA-Lib library first (see section 2)
- Verify installation with: `python -c "import talib; print(talib.__version__)"`

## 📝 License

[Add your license here]

## 👥 Contributing

[Add contribution guidelines if applicable]

## 📧 Support

For issues or questions, please [open an issue](https://github.com/your-org/portfolio_watchdog/issues) or contact the development team.

