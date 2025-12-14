# Project Structure

This document describes the organized structure of the Portfolio Watchdog codebase.

## Directory Layout

```
portfolio_watchdog/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── config_example.yaml         # Authentication config template
├── config.yaml                 # Authentication config (not in git)
├── README.md                   # Main project documentation
├── PROJECT_STRUCTURE.md        # This file
│
├── src/                        # Source code package
│   ├── __init__.py            # Package initialization
│   │
│   ├── core/                  # Core business logic
│   │   ├── __init__.py
│   │   ├── engine.py         # Traffic light classification engine
│   │   └── data_fetcher.py    # OHLCV data fetching (yfinance/RapidAPI)
│   │
│   ├── database/              # Database layer
│   │   ├── __init__.py
│   │   └── models.py          # SQLAlchemy models and DB operations
│   │
│   ├── ai/                    # AI-powered features
│   │   ├── __init__.py
│   │   └── commentary.py      # OpenAI GPT-4 commentary generation
│   │
│   ├── utils/                 # Utility modules
│   │   ├── __init__.py
│   │   ├── cache.py           # TTL-based caching system
│   │   └── profiler.py        # Performance profiling tools
│   │
│   └── ui/                    # UI components
│       ├── __init__.py
│       └── components.py     # Reusable Streamlit components
│
├── docs/                      # Documentation
│   ├── OPENAI_SETUP.md
│   ├── RAPIDAPI_SETUP.md
│   ├── DATABASE_SETUP.md
│   ├── TROUBLESHOOTING.md
│   └── ... (other docs)
│
├── scripts/                   # Utility scripts
│   ├── generate_password_hash.py
│   └── setup_rapidapi.sh
│
├── tests/                     # Test files
│   ├── test_data_fetch.py
│   ├── test_profiling.py
│   └── example_profile.py
│
└── [config files]             # Docker, deployment, etc.
    ├── Dockerfile
    ├── docker-compose.yml
    ├── Procfile
    └── runtime.txt
```

## Module Organization

### `src/core/`
Core business logic for stock analysis:
- **engine.py**: Implements the traffic light classification algorithm
- **data_fetcher.py**: Handles data fetching from yfinance and RapidAPI

### `src/database/`
Database models and operations:
- **models.py**: SQLAlchemy ORM models (User, WatchlistItem) and helper functions

### `src/ai/`
AI-powered features:
- **commentary.py**: Generates natural language explanations using OpenAI GPT-4

### `src/utils/`
Reusable utility modules:
- **cache.py**: TTL-based caching decorators and cache management
- **profiler.py**: Performance profiling tools and decorators

### `src/ui/`
UI components and styling:
- **components.py**: Reusable Streamlit components and custom CSS

## Import Patterns

All imports use absolute paths from the `src` package:

```python
# Core modules
from src.core.engine import classify_ticker
from src.core.data_fetcher import fetch_ohlcv_rapidapi

# Database
from src.database.models import SessionLocal, init_db

# AI
from src.ai.commentary import generate_ai_commentary

# Utils
from src.utils.cache import get_cache_stats
from src.utils.profiler import Timer

# UI
from src.ui.components import apply_custom_css
```

## Benefits of This Structure

1. **Clear Separation of Concerns**: Each module has a single responsibility
2. **Easy to Navigate**: Related code is grouped together
3. **Scalable**: Easy to add new features in appropriate directories
4. **Maintainable**: Clear organization makes code easier to understand and modify
5. **Testable**: Tests are separated from source code
6. **Professional**: Follows Python packaging best practices

## Adding New Features

### Adding a New Core Feature
Place in `src/core/` and update `src/core/__init__.py`

### Adding a New Database Model
Add to `src/database/models.py` or create a new file in `src/database/`

### Adding a New AI Feature
Create in `src/ai/` and update `src/ai/__init__.py`

### Adding a New Utility
Add to `src/utils/` and update `src/utils/__init__.py`

### Adding a New UI Component
Add to `src/ui/components.py` or create a new file in `src/ui/`

## Running the Application

From the project root:
```bash
streamlit run app.py
```

The application will automatically import from the `src` package structure.

