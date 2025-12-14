"""
Performance profiling utilities.

This module provides tools for monitoring and profiling application
performance to identify bottlenecks and optimization opportunities.
"""

import cProfile
import functools
import io
import pstats
import time
from contextlib import contextmanager
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


@contextmanager
def profile_context(print_stats: bool = True, sort_by: str = "cumulative"):
    """
    Context manager for profiling code blocks.

    Args:
        print_stats: Whether to print statistics on exit
        sort_by: Sort key for statistics (default: "cumulative")

    Example:
        with profile_context():
            expensive_operation()
    """
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        yield profiler
    finally:
        profiler.disable()
        if print_stats:
            stats = pstats.Stats(profiler)
            stats.sort_stats(sort_by)
            stats.print_stats(20)  # Print top 20 functions


def profile_function(
    print_stats: bool = True, sort_by: str = "cumulative"
) -> Callable[[F], F]:
    """
    Decorator to profile a function's performance.

    Args:
        print_stats: Whether to print statistics
        sort_by: Sort key for statistics

    Example:
        @profile_function()
        def my_function():
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = cProfile.Profile()
            profiler.enable()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                profiler.disable()
                if print_stats:
                    stats = pstats.Stats(profiler)
                    stats.sort_stats(sort_by)
                    stats.print_stats(10)

        return wrapper  # type: ignore

    return decorator


class Timer:
    """Simple timer context manager for measuring execution time."""

    def __init__(self, label: str = "Operation", verbose: bool = True):
        """
        Initialize timer.

        Args:
            label: Label for the timed operation
            verbose: Whether to print timing information
        """
        self.label = label
        self.verbose = verbose
        self.start_time: float | None = None
        self.elapsed: float | None = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and optionally print result."""
        if self.start_time is not None:
            self.elapsed = time.perf_counter() - self.start_time
            if self.verbose:
                print(f"{self.label}: {self.elapsed:.4f} seconds")

    def get_elapsed(self) -> float:
        """Get elapsed time in seconds."""
        return self.elapsed if self.elapsed is not None else 0.0


def time_function(func: F) -> F:
    """
    Decorator to time function execution.

    Example:
        @time_function
        def my_function():
            ...
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start
            print(f"{func.__name__} took {elapsed:.4f} seconds")

    return wrapper  # type: ignore


def get_memory_usage() -> dict[str, Any]:
    """
    Get current memory usage statistics.

    Returns:
        Dictionary with memory usage information
    """
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()

        return {
            "rss_mb": mem_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": mem_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent(),
        }
    except ImportError:
        return {"error": "psutil not installed"}


def profile_to_string(profiler: cProfile.Profile, top_n: int = 20) -> str:
    """
    Convert profiler output to string.

    Args:
        profiler: cProfile.Profile instance
        top_n: Number of top functions to include

    Returns:
        Formatted statistics string
    """
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")

    stream = io.StringIO()
    stats.print_stats(top_n, stream=stream)
    return stream.getvalue()
