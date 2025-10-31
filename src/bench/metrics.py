"""Performance metrics collection."""
import time
import tracemalloc
from typing import Dict, Any, Optional, List
import psutil
import os


class Metrics:
    """Container for benchmark metrics."""
    
    def __init__(self) -> None:
        self.time_seconds: float = 0.0
        self.peak_memory_bytes: int = 0
        self.comparisons: int = 0
        self.swaps: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "time_s": self.time_seconds,
            "peak_mem_bytes": self.peak_memory_bytes,
            "comparisons": self.comparisons,
            "swaps": self.swaps,
        }


def measure_sort_performance(
    sort_func,
    arr: List[int],
    *args,
    instrument: bool = False,
    **kwargs,
) -> tuple[List[int], Metrics]:
    """
    Measure performance of a sorting function.
    
    Args:
        sort_func: Sorting function to benchmark
        arr: Input array to sort
        *args: Additional positional arguments for sort_func
        instrument: Whether to count comparisons and swaps
        **kwargs: Additional keyword arguments for sort_func
    
    Returns:
        Tuple of (sorted_array, metrics)
    """
    metrics = Metrics()
    
    # Setup instrumentation
    if instrument:
        counters: Dict[str, int] = {"comparison": 0, "swap": 0}
        
        def instrument_callback(op: str) -> None:
            if op in counters:
                counters[op] += 1
        
        if "instrument" not in kwargs:
            kwargs["instrument"] = instrument_callback
    
    # Measure memory before
    process = psutil.Process(os.getpid())
    tracemalloc.start()
    
    # Measure time
    start_time = time.perf_counter()
    sorted_arr = sort_func(arr, *args, **kwargs)
    end_time = time.perf_counter()
    
    # Measure memory
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss_memory = process.memory_info().rss
    
    metrics.time_seconds = end_time - start_time
    metrics.peak_memory_bytes = max(peak, rss_memory)
    
    if instrument:
        metrics.comparisons = counters.get("comparison", 0)
        metrics.swaps = counters.get("swap", 0)
    
    return sorted_arr, metrics


def aggregate_metrics(metrics_list: List[Metrics]) -> Dict[str, Any]:
    """
    Aggregate metrics across multiple runs.
    
    Args:
        metrics_list: List of Metrics objects from multiple runs
    
    Returns:
        Dictionary with aggregated statistics
    """
    if not metrics_list:
        return {}
    
    times = [m.time_seconds for m in metrics_list]
    memories = [m.peak_memory_bytes for m in metrics_list]
    comparisons = [m.comparisons for m in metrics_list if m.comparisons > 0]
    swaps = [m.swaps for m in metrics_list if m.swaps > 0]
    
    import statistics
    
    result: Dict[str, Any] = {
        "time_mean_s": statistics.mean(times),
        "time_std_s": statistics.stdev(times) if len(times) > 1 else 0.0,
        "time_best_s": min(times),
        "time_worst_s": max(times),
        "memory_mean_bytes": statistics.mean(memories),
        "memory_std_bytes": statistics.stdev(memories) if len(memories) > 1 else 0.0,
        "memory_peak_bytes": max(memories),
        "runs": len(metrics_list),
    }
    
    if comparisons:
        result["comparisons_mean"] = statistics.mean(comparisons)
        result["comparisons_std"] = statistics.stdev(comparisons) if len(comparisons) > 1 else 0.0
    
    if swaps:
        result["swaps_mean"] = statistics.mean(swaps)
        result["swaps_std"] = statistics.stdev(swaps) if len(swaps) > 1 else 0.0
    
    return result

