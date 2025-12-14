# Cache Configuration Guide

This guide explains how to configure and adjust cache TTL (Time-To-Live) values to optimize performance for your use case.

## 📋 Cache Overview

The Portfolio Watchdog uses two types of caches:

1. **Data Cache** - Caches market data from yfinance API
2. **Classification Cache** - Caches ticker classification results

## ⚙️ Adjusting Cache TTLs

### Current Default Values

Located in `cache.py`:

```python
# Global cache instances
_data_cache = TTLCache(ttl_seconds=1800)  # 30 minutes for market data
_classification_cache = TTLCache(ttl_seconds=300)  # 5 minutes for classifications
```

### How to Modify

#### Option 1: Direct Modification in `cache.py`

Edit the TTL values in `cache.py`:

```python
# For longer cache duration (e.g., end-of-day analysis)
_data_cache = TTLCache(ttl_seconds=3600)  # 1 hour
_classification_cache = TTLCache(ttl_seconds=600)  # 10 minutes

# For shorter cache duration (e.g., real-time trading)
_data_cache = TTLCache(ttl_seconds=300)  # 5 minutes
_classification_cache = TTLCache(ttl_seconds=60)  # 1 minute
```

#### Option 2: Environment Variables (Recommended for Production)

Modify `cache.py` to support environment variables:

```python
import os

# Read from environment or use defaults
DATA_CACHE_TTL = int(os.getenv("DATA_CACHE_TTL", "1800"))  # 30 minutes default
CLASS_CACHE_TTL = int(os.getenv("CLASS_CACHE_TTL", "300"))  # 5 minutes default

_data_cache = TTLCache(ttl_seconds=DATA_CACHE_TTL)
_classification_cache = TTLCache(ttl_seconds=CLASS_CACHE_TTL)
```

Then set environment variables:
```bash
export DATA_CACHE_TTL=3600
export CLASS_CACHE_TTL=600
```

#### Option 3: Decorator-Level Configuration

Modify the decorators in `engine.py`:

```python
# In engine.py
@cached_data_fetch(ttl_seconds=3600)  # Change from 1800 to 3600
def fetch_ohlcv(...):
    ...

@cached_classification(ttl_seconds=600)  # Change from 300 to 600
def classify_ticker(...):
    ...
```

## 🎯 Recommended TTL Values by Use Case

### Intraday Trading (Active Monitoring)
- **Data Cache**: 60-300 seconds (1-5 minutes)
- **Classification Cache**: 30-60 seconds (30 seconds - 1 minute)
- **Use Case**: Real-time monitoring, frequent updates needed

### Swing Trading (Daily Analysis)
- **Data Cache**: 1800-3600 seconds (30-60 minutes)
- **Classification Cache**: 300-600 seconds (5-10 minutes)
- **Use Case**: Daily check-ins, moderate update frequency

### End-of-Day Analysis
- **Data Cache**: 3600-7200 seconds (1-2 hours)
- **Classification Cache**: 600-1800 seconds (10-30 minutes)
- **Use Case**: Once or twice daily analysis

### Backtesting/Research
- **Data Cache**: 86400 seconds (24 hours)
- **Classification Cache**: 3600 seconds (1 hour)
- **Use Case**: Historical analysis, no real-time requirements

## 📊 Monitoring Cache Performance

### In the Dashboard

The dashboard shows cache statistics:
- **Cache Size**: Total number of cached items
- **Breakdown**: Data cache vs Classification cache sizes

### Programmatically

```python
from cache import get_cache_stats

stats = get_cache_stats()
print(f"Data Cache: {stats['data_cache_size']} items")
print(f"Classification Cache: {stats['classification_cache_size']} items")
```

### Cache Hit Rate Calculation

To calculate cache hit rate, you would need to add metrics tracking:

```python
# Example: Add to cache.py
class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache: dict[str, tuple[Any, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Any | None:
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, timestamp = self.cache[key]
        if datetime.now() - timestamp > self.ttl:
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return value
    
    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
```

## 🔧 Cache Management

### Clearing Cache

#### From Dashboard
Click the "🗑️ Clear Cache" button in the dashboard

#### Programmatically
```python
from cache import clear_all_caches

clear_all_caches()
```

#### Manual Cache Cleanup
```python
from cache import _data_cache, _classification_cache

_data_cache.cleanup_expired()
_classification_cache.cleanup_expired()
```

## ⚠️ Important Considerations

1. **Market Hours**: During market hours, shorter TTLs ensure fresher data
2. **API Rate Limits**: Longer TTLs reduce API calls but may show stale data
3. **Memory Usage**: Larger caches use more memory (typically minimal impact)
4. **Data Freshness**: Balance between performance and data accuracy

## 🚀 Performance Impact

### Typical Cache Performance

- **Cache Hit**: ~0.01-0.05 seconds (near-instant)
- **Cache Miss**: 0.5-5 seconds (API call + processing)
- **Speedup**: 10-500x faster with cache

### Memory Usage

- **Per Data Cache Entry**: ~50-200 KB (depends on data period)
- **Per Classification Entry**: ~1-5 KB
- **Typical Total**: 1-10 MB for 10-20 tickers

## 📝 Example: Custom Cache Configuration

Create a custom cache configuration file:

```python
# custom_cache_config.py
from cache import TTLCache

# Custom configuration for swing trading
SWING_TRADING_CONFIG = {
    "data_ttl": 3600,  # 1 hour
    "class_ttl": 600,  # 10 minutes
}

# Create custom cache instances
custom_data_cache = TTLCache(ttl_seconds=SWING_TRADING_CONFIG["data_ttl"])
custom_class_cache = TTLCache(ttl_seconds=SWING_TRADING_CONFIG["class_ttl"])
```

## 🔍 Troubleshooting

### Cache Not Working
- Check if cache decorators are applied to functions
- Verify cache TTL hasn't expired
- Check cache statistics in dashboard

### Too Much Stale Data
- Reduce TTL values
- Clear cache more frequently
- Use manual refresh button

### Too Many API Calls
- Increase TTL values
- Check cache hit rates
- Verify cache is being used

### Memory Issues
- Reduce cache TTL (fewer items cached)
- Clear cache periodically
- Monitor cache size in dashboard

