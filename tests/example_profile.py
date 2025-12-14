#!/usr/bin/env python3
"""
Example script demonstrating performance profiling tools.

This script shows how to use the profiling utilities to measure
and optimize application performance.
"""

from src.utils.cache import clear_all_caches, get_cache_stats
from src.core.engine import classify_ticker
from src.utils.profiler import Timer, get_memory_usage, profile_context


def example_timing():
    """Example of using Timer for simple performance measurement."""
    print("=" * 60)
    print("Example: Timing Ticker Classification")
    print("=" * 60)

    with Timer("First Classification (No Cache)"):
        result1 = classify_ticker("TSLA")

    print(f"Result: {result1.status} - {result1.emoji}")
    print()

    with Timer("Second Classification (Cached)"):
        result2 = classify_ticker("TSLA")

    print(f"Result: {result2.status} - {result2.emoji}")
    print()


def example_profiling():
    """Example of detailed profiling with cProfile."""
    print("=" * 60)
    print("Example: Detailed Profiling")
    print("=" * 60)

    with profile_context(print_stats=True, sort_by="cumulative"):
        # Profile multiple operations
        result1 = classify_ticker("AAPL")
        result2 = classify_ticker("MSFT")
        result3 = classify_ticker("GOOGL")

    print(f"Results: {result1.status}, {result2.status}, {result3.status}")
    print()


def example_cache_stats():
    """Example of monitoring cache statistics."""
    print("=" * 60)
    print("Example: Cache Statistics")
    print("=" * 60)

    # Clear cache first
    clear_all_caches()
    print("Cache cleared")
    print()

    # Classify some tickers
    tickers = ["TSLA", "AAPL", "MSFT", "GOOGL", "AMZN"]
    for ticker in tickers:
        classify_ticker(ticker)

    # Check cache stats
    stats = get_cache_stats()
    print(f"Data Cache Size: {stats['data_cache_size']} items")
    print(f"Classification Cache Size: {stats['classification_cache_size']} items")
    print()

    # Classify again (should use cache)
    print("Classifying again (should use cache)...")
    with Timer("Cached Classification"):
        for ticker in tickers:
            classify_ticker(ticker)

    print()


def example_memory_usage():
    """Example of monitoring memory usage."""
    print("=" * 60)
    print("Example: Memory Usage")
    print("=" * 60)

    mem_before = get_memory_usage()
    print(f"Memory Before: {mem_before}")

    # Perform operations
    _ = [classify_ticker(f"TICKER{i}") for i in range(5)]

    mem_after = get_memory_usage()
    print(f"Memory After: {mem_after}")

    if "rss_mb" in mem_before and "rss_mb" in mem_after:
        diff = mem_after["rss_mb"] - mem_before["rss_mb"]
        print(f"Memory Increase: {diff:.2f} MB")
    print()


def example_parallel_vs_sequential():
    """Compare parallel vs sequential processing."""
    print("=" * 60)
    print("Example: Parallel vs Sequential")
    print("=" * 60)

    from concurrent.futures import ThreadPoolExecutor, as_completed

    tickers = ["TSLA", "AAPL", "MSFT", "GOOGL", "AMZN"]

    # Sequential
    print("Sequential Processing:")
    with Timer("Sequential"):
        _ = [classify_ticker(t) for t in tickers]
    print()

    # Clear cache to ensure fair comparison
    clear_all_caches()

    # Parallel
    print("Parallel Processing:")
    with Timer("Parallel"):
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ticker = {
                executor.submit(classify_ticker, ticker): ticker for ticker in tickers
            }
            _ = [future.result() for future in as_completed(future_to_ticker)]
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Portfolio Watchdog - Performance Profiling Examples")
    print("=" * 60 + "\n")

    try:
        example_timing()
        example_cache_stats()
        example_memory_usage()
        # Uncomment for detailed profiling (produces verbose output)
        # example_profiling()
        # example_parallel_vs_sequential()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
