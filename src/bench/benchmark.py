"""Benchmark CLI for sorting algorithms."""
import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import random

from src.algorithms.merge_sort import merge_sort
from src.algorithms.quick_sort import quick_sort, PivotStrategy
from src.bench.datasets import generate_dataset, DatasetType
from src.bench.metrics import measure_sort_performance, Metrics, aggregate_metrics
from src.bench.logging_setup import setup_logging, get_logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Benchmark divide-and-conquer sorting algorithms",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    parser.add_argument(
        "--algorithms",
        type=str,
        default="merge,quick",
        help="Comma-separated list of algorithms (merge, quick)",
    )
    
    parser.add_argument(
        "--pivot",
        type=str,
        default="random",
        choices=["first", "last", "median_of_three", "random"],
        help="Pivot strategy for Quick Sort",
    )
    
    parser.add_argument(
        "--datasets",
        type=str,
        default="sorted,reverse,random,nearly_sorted,duplicates_heavy",
        help="Comma-separated list of dataset types",
    )
    
    parser.add_argument(
        "--sizes",
        type=str,
        default="1000,5000,10000,50000",
        help="Comma-separated list of dataset sizes",
    )
    
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of runs per experiment",
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    
    parser.add_argument(
        "--outdir",
        type=str,
        default="results",
        help="Output directory for results",
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    
    parser.add_argument(
        "--instrument",
        action="store_true",
        help="Count comparisons and swaps",
    )
    
    parser.add_argument(
        "--make-plots",
        action="store_true",
        help="Generate plots after benchmarking",
    )
    
    return parser.parse_args()


def run_benchmark(
    algorithm: str,
    pivot_strategy: Optional[str],
    dataset_type: DatasetType,
    size: int,
    runs: int,
    seed: int,
    instrument: bool,
    logger: Any,
) -> List[Dict[str, Any]]:
    """
    Run benchmark for a single algorithm/dataset/size combination.
    
    Returns:
        List of result dictionaries, one per run
    """
    results: List[Dict[str, Any]] = []
    
    # Get sort function
    if algorithm == "merge":
        sort_func = merge_sort
        sort_kwargs: Dict[str, Any] = {}
    elif algorithm == "quick":
        sort_func = quick_sort
        sort_kwargs = {
            "pivot_strategy": pivot_strategy or "first",
        }
        # Only pass seed for random pivot strategy
        if pivot_strategy == "random":
            sort_kwargs["seed"] = seed
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    for run_idx in range(runs):
        logger.info(
            f"Running {algorithm} on {dataset_type} size={size} run={run_idx+1}/{runs}"
        )
        
        # Generate dataset with unique seed per run
        dataset_seed = seed + run_idx * 1000 if seed is not None else None
        arr = generate_dataset(size, dataset_type, seed=dataset_seed)
        
        # For quick sort with random pivot, use unique seed per run
        if algorithm == "quick" and pivot_strategy == "random":
            sort_kwargs["seed"] = (seed + run_idx * 1000) if seed is not None else None
        
        # Run benchmark
        sorted_arr, metrics = measure_sort_performance(
            sort_func,
            arr,
            instrument=instrument,
            **sort_kwargs,
        )
        
        # Verify correctness
        expected = sorted(arr)
        if sorted_arr != expected:
            logger.error(
                f"Correctness check failed for {algorithm} on {dataset_type} "
                f"size={size} run={run_idx+1}"
            )
            logger.error(f"Expected: {expected[:10]}...")
            logger.error(f"Got: {sorted_arr[:10]}...")
            return []  # Return empty to indicate failure
        
        # Store result
        result = {
            "algorithm": algorithm,
            "pivot": pivot_strategy if algorithm == "quick" else None,
            "dataset": dataset_type,
            "size": size,
            "run": run_idx + 1,
            "time_s": metrics.time_seconds,
            "peak_mem_bytes": metrics.peak_memory_bytes,
            "comparisons": metrics.comparisons if instrument else None,
            "swaps": metrics.swaps if instrument else None,
            "seed": seed,
        }
        results.append(result)
    
    return results


def save_results_csv(results: List[Dict[str, Any]], csv_path: Path) -> None:
    """Save results to CSV file."""
    if not results:
        return
    
    file_exists = csv_path.exists()
    
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)


def save_summary_json(results: List[Dict[str, Any]], json_path: Path) -> None:
    """Save aggregated summary to JSON file."""
    if not results:
        return
    
    # Group by (algorithm, pivot, dataset, size)
    grouped: Dict[tuple, List[Metrics]] = {}
    
    for result in results:
        key = (
            result["algorithm"],
            result.get("pivot"),
            result["dataset"],
            result["size"],
        )
        
        metrics = Metrics()
        metrics.time_seconds = result["time_s"]
        metrics.peak_memory_bytes = result["peak_mem_bytes"]
        metrics.comparisons = result.get("comparisons") or 0
        metrics.swaps = result.get("swaps") or 0
        
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(metrics)
    
    # Aggregate
    summary: Dict[str, Any] = {}
    for key, metrics_list in grouped.items():
        algo, pivot, dataset, size = key
        key_str = f"{algo}_{pivot or 'N/A'}_{dataset}_{size}"
        summary[key_str] = aggregate_metrics(metrics_list)
        summary[key_str]["algorithm"] = algo
        summary[key_str]["pivot"] = pivot
        summary[key_str]["dataset"] = dataset
        summary[key_str]["size"] = size
    
    # Merge with existing summary if it exists
    if json_path.exists():
        with open(json_path, "r") as f:
            existing = json.load(f)
        existing.update(summary)
        summary = existing
    
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)


def generate_plots(results: List[Dict[str, Any]], plots_dir: Path, logger: Any) -> None:
    """Generate plots from results."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
    except ImportError:
        logger.warning("matplotlib not available, skipping plots")
        return
    
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    if not results:
        logger.warning("No results to plot")
        return
    
    # Group results by algorithm and dataset
    algorithms = sorted(set(r["algorithm"] for r in results))
    datasets = sorted(set(r["dataset"] for r in results))
    sizes = sorted(set(r["size"] for r in results))
    
    # Time vs size plots
    fig, axes = plt.subplots(len(datasets), 1, figsize=(10, 5 * len(datasets)))
    if len(datasets) == 1:
        axes = [axes]
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        for algo in algorithms:
            algo_results = [
                r for r in results
                if r["algorithm"] == algo and r["dataset"] == dataset
            ]
            
            if not algo_results:
                continue
            
            # Average time per size
            size_times: Dict[int, List[float]] = {}
            for r in algo_results:
                size = r["size"]
                if size not in size_times:
                    size_times[size] = []
                size_times[size].append(r["time_s"])
            
            avg_times = [sum(size_times[s]) / len(size_times[s]) for s in sizes if s in size_times]
            plot_sizes = [s for s in sizes if s in size_times]
            
            ax.plot(plot_sizes, avg_times, marker="o", label=algo)
        
        ax.set_xlabel("Array Size")
        ax.set_ylabel("Time (seconds)")
        ax.set_title(f"Sorting Time vs Size - {dataset}")
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(plots_dir / "time_vs_size.png", dpi=150)
    plt.close()
    
    # Memory vs size plots
    fig, axes = plt.subplots(len(datasets), 1, figsize=(10, 5 * len(datasets)))
    if len(datasets) == 1:
        axes = [axes]
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        for algo in algorithms:
            algo_results = [
                r for r in results
                if r["algorithm"] == algo and r["dataset"] == dataset
            ]
            
            if not algo_results:
                continue
            
            # Average memory per size
            size_memories: Dict[int, List[int]] = {}
            for r in algo_results:
                size = r["size"]
                if size not in size_memories:
                    size_memories[size] = []
                size_memories[size].append(r["peak_mem_bytes"])
            
            avg_memories = [
                sum(size_memories[s]) / len(size_memories[s])
                for s in sizes if s in size_memories
            ]
            plot_sizes = [s for s in sizes if s in size_memories]
            
            ax.plot(plot_sizes, avg_memories, marker="o", label=algo)
        
        ax.set_xlabel("Array Size")
        ax.set_ylabel("Peak Memory (bytes)")
        ax.set_title(f"Memory Usage vs Size - {dataset}")
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(plots_dir / "memory_vs_size.png", dpi=150)
    plt.close()
    
    logger.info(f"Plots saved to {plots_dir}")


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Setup paths
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    plots_dir = Path("plots")
    
    # Setup logging
    setup_logging(outdir, args.log_level)
    logger = get_logger(__name__)
    
    # Parse arguments
    algorithms = [a.strip() for a in args.algorithms.split(",")]
    datasets = [d.strip() for d in args.datasets.split(",")]
    sizes = [int(s.strip()) for s in args.sizes.split(",")]
    
    # Validate algorithms
    valid_algorithms = {"merge", "quick"}
    for algo in algorithms:
        if algo not in valid_algorithms:
            logger.error(f"Invalid algorithm: {algo}")
            return 1
    
    # Set random seed
    if args.seed is not None:
        random.seed(args.seed)
    
    # Run benchmarks
    all_results: List[Dict[str, Any]] = []
    correctness_failed = False
    
    for algorithm in algorithms:
        pivot_strategy = args.pivot if algorithm == "quick" else None
        
        for dataset_type in datasets:
            for size in sizes:
                try:
                    results = run_benchmark(
                        algorithm,
                        pivot_strategy,
                        dataset_type,  # type: ignore
                        size,
                        args.runs,
                        args.seed,
                        args.instrument,
                        logger,
                    )
                    
                    if not results:
                        correctness_failed = True
                    else:
                        all_results.extend(results)
                        
                except Exception as e:
                    logger.error(
                        f"Error running benchmark: {algorithm}, {dataset_type}, {size}",
                        exc_info=True,
                    )
                    correctness_failed = True
    
    # Save results
    csv_path = outdir / "bench_results.csv"
    json_path = outdir / "summary.json"
    
    if all_results:
        save_results_csv(all_results, csv_path)
        save_summary_json(all_results, json_path)
        logger.info(f"Results saved to {csv_path} and {json_path}")
    
    # Generate plots
    if args.make_plots or all_results:
        generate_plots(all_results, plots_dir, logger)
    
    # Exit with error if correctness failed
    if correctness_failed:
        logger.error("Benchmark failed due to correctness check failures")
        return 1
    
    logger.info("Benchmark completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

