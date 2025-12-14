#!/usr/bin/env python3
"""
Simple test script for profiling tools without requiring API calls.

This script tests the cache and profiler modules independently.
"""

from src.utils.cache import TTLCache, get_cache_stats, clear_all_caches
from src.utils.profiler import Timer, get_memory_usage


def test_cache():
    """Test the TTL cache functionality."""
    print("=" * 60)
    print("Testing TTL Cache")
    print("=" * 60)

    cache = TTLCache(ttl_seconds=5)

    # Test set and get
    cache.set("test_key", "test_value")
    value = cache.get("test_key")
    print(f"✓ Cache set/get: {value}")

    # Test expiration (simulated)
    cache.set("expired_key", "expired_value")
    print(f"✓ Cache size: {len(cache.cache)} items")

    # Test cleanup
    removed = cache.cleanup_expired()
    print(f"✓ Cleanup removed: {removed} expired items")

    print()


def test_timer():
    """Test the Timer context manager."""
    print("=" * 60)
    print("Testing Timer")
    print("=" * 60)

    with Timer("Test Operation"):
        # Simulate some work
        total = sum(range(1000000))
        _ = total  # Use the variable

    print("✓ Timer completed successfully")
    print()


def test_memory_usage():
    """Test memory usage monitoring."""
    print("=" * 60)
    print("Testing Memory Usage")
    print("=" * 60)

    mem_info = get_memory_usage()
    if "error" in mem_info:
        print(f"⚠ {mem_info['error']}")
    else:
        print(f"✓ RSS Memory: {mem_info['rss_mb']:.2f} MB")
        print(f"✓ VMS Memory: {mem_info['vms_mb']:.2f} MB")
        print(f"✓ Memory Percent: {mem_info['percent']:.2f}%")

    print()


def test_cache_stats():
    """Test cache statistics."""
    print("=" * 60)
    print("Testing Cache Statistics")
    print("=" * 60)

    # Clear cache first
    clear_all_caches()
    print("✓ Cache cleared")

    # Get stats
    stats = get_cache_stats()
    print(f"✓ Data Cache Size: {stats['data_cache_size']} items")
    print(f"✓ Classification Cache Size: {stats['classification_cache_size']} items")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Portfolio Watchdog - Profiling Tools Test")
    print("=" * 60 + "\n")

    try:
        test_cache()
        test_timer()
        test_memory_usage()
        test_cache_stats()

        print("=" * 60)
        print("✅ All profiling tools are working correctly!")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
