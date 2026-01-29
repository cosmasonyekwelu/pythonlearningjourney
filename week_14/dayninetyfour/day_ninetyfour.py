"""
Day 94: Performance Optimization for Trading Systems
Demonstrates profiling, vectorization with NumPy, and caching.
"""

import time
import cProfile
import pstats
import io
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Callable
from functools import wraps

class TradingProfiler:
    """Advanced profiler for trading system performance analysis."""

    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                execution_time_ms = (end_time - start_time) * 1000
                print(f"DEBUG: Function '{func.__name__}' took {execution_time_ms:.2f}ms")
        return wrapper

    def detailed_profile(self, func: Callable, *args, **kwargs):
        """Run detailed profiling using cProfile."""
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()

        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        print(s.getvalue())
        return result

# --- Optimized Calculation Example ---

def slow_calculation(prices: List[float]):
    """Slow iterative SMA calculation."""
    results = []
    window = 20
    for i in range(len(prices)):
        if i < window:
            results.append(None)
        else:
            avg = sum(prices[i-window:i]) / window
            results.append(avg)
    return results

def optimized_calculation(prices: np.ndarray):
    """Fast vectorized SMA calculation using NumPy."""
    window = 20
    return pd.Series(prices).rolling(window=window).mean().values

def demonstrate_optimization():
    profiler = TradingProfiler()

    # Generate 100,000 price points
    n = 100000
    prices_list = np.random.randn(n).tolist()
    prices_array = np.array(prices_list)

    print(f"--- Benchmarking {n} data points ---")

    print("\nIterative Approach:")
    start = time.time()
    slow_calculation(prices_list)
    print(f"Time: {(time.time() - start)*1000:.2f}ms")

    print("\nVectorized Approach (NumPy/Pandas):")
    start = time.time()
    optimized_calculation(prices_array)
    print(f"Time: {(time.time() - start)*1000:.2f}ms")

    print("\nDetailed Profile of Optimized Version:")
    profiler.detailed_profile(optimized_calculation, prices_array)

if __name__ == "__main__":
    demonstrate_optimization()
