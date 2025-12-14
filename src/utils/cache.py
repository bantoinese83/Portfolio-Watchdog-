"""
Caching utilities for performance optimization.

This module provides caching mechanisms to reduce redundant API calls
and expensive computations, significantly improving application performance.
"""

import functools
import hashlib
import os
import pickle
from datetime import datetime, timedelta
from typing import Any, Callable, TypeVar

# Type variable for generic function typing
F = TypeVar("F", bound=Callable[..., Any])


def _make_cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate a cache key from function arguments."""
    # Create a stable hash of the arguments
    key_data = pickle.dumps((args, sorted(kwargs.items())))
    return hashlib.md5(key_data).hexdigest()


class TTLCache:
    """
    Time-To-Live cache with automatic expiration.

    Caches function results for a specified duration, automatically
    invalidating entries after the TTL expires.
    """

    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize TTL cache.

        Args:
            ttl_seconds: Time to live in seconds (default: 300 = 5 minutes)
        """
        self.cache: dict[str, tuple[Any, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Any | None:
        """Get value from cache if not expired."""
        if key not in self.cache:
            return None

        value, timestamp = self.cache[key]
        if datetime.now() - timestamp > self.ttl:
            del self.cache[key]
            return None

        return value

    def set(self, key: str, value: Any) -> None:
        """Store value in cache with current timestamp."""
        self.cache[key] = (value, datetime.now())

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

    def cleanup_expired(self) -> int:
        """
        Remove expired entries and return count of removed items.

        Returns:
            Number of expired entries removed
        """
        now = datetime.now()
        expired_keys = [
            key
            for key, (_, timestamp) in self.cache.items()
            if now - timestamp > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)


# Global cache instances
# TTL values can be customized via environment variables or direct modification
# See CACHE_CONFIG.md for configuration options
DATA_CACHE_TTL = int(os.getenv("DATA_CACHE_TTL", "1800"))  # 30 minutes default
CLASS_CACHE_TTL = int(os.getenv("CLASS_CACHE_TTL", "300"))  # 5 minutes default

_data_cache = TTLCache(ttl_seconds=DATA_CACHE_TTL)
_classification_cache = TTLCache(ttl_seconds=CLASS_CACHE_TTL)


def cached_data_fetch(ttl_seconds: int = 1800) -> Callable[[F], F]:
    """
    Decorator to cache expensive data fetch operations.

    Uses the global data cache instance for consistent stats tracking.

    Args:
        ttl_seconds: Cache TTL in seconds (default: 1800 = 30 minutes)

    Returns:
        Decorated function with caching
    """

    def decorator(func: F) -> F:
        # Use global data cache if TTL matches, otherwise create new instance
        if ttl_seconds == DATA_CACHE_TTL:
            cache = _data_cache
        else:
            cache = TTLCache(ttl_seconds=ttl_seconds)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = f"{func.__name__}:{_make_cache_key(*args, **kwargs)}"
            cached_value = cache.get(cache_key)

            if cached_value is not None:
                return cached_value

            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper  # type: ignore

    return decorator


def cached_classification(ttl_seconds: int = 300) -> Callable[[F], F]:
    """
    Decorator to cache ticker classification results.

    Uses the global classification cache instance for consistent stats tracking.

    Args:
        ttl_seconds: Cache TTL in seconds (default: 300 = 5 minutes)

    Returns:
        Decorated function with caching
    """

    def decorator(func: F) -> F:
        # Use global classification cache if TTL matches, otherwise create new instance
        if ttl_seconds == CLASS_CACHE_TTL:
            cache = _classification_cache
        else:
            cache = TTLCache(ttl_seconds=ttl_seconds)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Use ticker as primary cache key
            ticker = args[0] if args else kwargs.get("ticker", "")
            cache_key = f"{func.__name__}:{ticker.upper()}"
            cached_value = cache.get(cache_key)

            if cached_value is not None:
                return cached_value

            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper  # type: ignore

    return decorator


def get_cache_stats() -> dict[str, int]:
    """
    Get statistics about cache usage.

    Returns:
        Dictionary with cache statistics
    """
    return {
        "data_cache_size": len(_data_cache.cache),
        "classification_cache_size": len(_classification_cache.cache),
    }


def clear_all_caches() -> None:
    """Clear all cache instances."""
    _data_cache.clear()
    _classification_cache.clear()
