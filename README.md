# Divide-and-Conquer Sorting Algorithms Benchmark

A comprehensive Python project for benchmarking merge sort and quick sort algorithms across different dataset types and sizes, with detailed performance metrics, logging, and visualization.

## Project Overview

This project implements two divide-and-conquer sorting algorithms (Merge Sort and Quick Sort) and provides a benchmarking framework to evaluate their performance across various dataset characteristics:

- **Merge Sort**: Stable, O(n log n) worst-case time complexity
- **Quick Sort**: In-place, O(n log n) average-case with configurable pivot strategies

The benchmark suite measures:
- Wall-clock time (using `time.perf_counter`)
- Peak memory usage (using `tracemalloc` and `psutil`)
- Comparison and swap counts (when instrumentation is enabled)
- Correctness verification (comparing against Python's `sorted()`)

## Project Structure

```
.
├── src/
│   ├── algorithms/
│   │   ├── merge_sort.py      # Merge sort implementation
│   │   └── quick_sort.py       # Quick sort with pivot strategies
│   └── bench/
│       ├── benchmark.py         # Main CLI benchmark runner
│       ├── datasets.py          # Dataset generators
│       ├── metrics.py           # Performance measurement utilities
│       └── logging_setup.py     # Logging configuration
├── tests/
│   └── test_sorts.py            # Comprehensive test suite
├── scripts/
│   └── run_benchmarks.sh        # Convenience script to run benchmarks
├── results/                     # Auto-created: CSV, JSON, logs
├── plots/                       # Auto-created: PNG visualizations
├── pyproject.toml               # Project configuration and dependencies
├── .gitignore
└── README.md                    # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd divide-and-conquer-analysis
```

2. Install dependencies:
```bash
pip install -e .
```

Or install from `pyproject.toml`:
```bash
pip install -e ".[dev]"  # Includes dev dependencies (mypy, ruff, black)
```

## Quick Start

### Run a Simple Benchmark

```bash
python -m src.bench.benchmark \
    --algorithms merge,quick \
    --datasets sorted,reverse,random \
    --sizes 1000,5000,10000 \
    --runs 5 \
    --seed 42 \
    --instrument \
    --make-plots
```

### Use the Convenience Script

```bash
./scripts/run_benchmarks.sh
```

## CLI Usage

The benchmark CLI (`src.bench.benchmark`) supports the following arguments:

### Required Arguments

None (all have defaults)

### Optional Arguments

- `--algorithms`: Comma-separated list of algorithms to benchmark
  - Options: `merge`, `quick`
  - Default: `merge,quick`

- `--pivot`: Pivot strategy for Quick Sort
  - Options: `first`, `last`, `median_of_three`, `random`
  - Default: `random`

- `--datasets`: Comma-separated list of dataset types
  - Options: `sorted`, `reverse`, `random`, `nearly_sorted`, `duplicates_heavy`
  - Default: `sorted,reverse,random,nearly_sorted,duplicates_heavy`

- `--sizes`: Comma-separated list of dataset sizes
  - Default: `1000,5000,10000,50000`
  - Example: `--sizes 1000,5000,10000,50000,100000`

- `--runs`: Number of runs per experiment (for statistical significance)
  - Default: `5`

- `--seed`: Random seed for reproducibility
  - Default: `42`

- `--outdir`: Output directory for results
  - Default: `results`

- `--log-level`: Logging level
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`
  - Default: `INFO`

- `--instrument`: Enable counting of comparisons and swaps
  - Flag (no value)

- `--make-plots`: Generate plots after benchmarking
  - Flag (no value)

### Example CLI Commands

**Basic benchmark with default settings:**
```bash
python -m src.bench.benchmark
```

**Full benchmark with all options:**
```bash
python -m src.bench.benchmark \
    --algorithms merge,quick \
    --pivot random \
    --datasets sorted,reverse,random,nearly_sorted,duplicates_heavy \
    --sizes 1000,5000,10000,50000 \
    --runs 5 \
    --seed 42 \
    --instrument \
    --outdir results \
    --log-level INFO \
    --make-plots
```

**Compare pivot strategies:**
```bash
for pivot in first last median_of_three random; do
    python -m src.bench.benchmark \
        --algorithms quick \
        --pivot $pivot \
        --datasets random \
        --sizes 10000,50000 \
        --runs 10 \
        --seed 42
done
```

**Quick performance check:**
```bash
python -m src.bench.benchmark \
    --algorithms merge,quick \
    --datasets random \
    --sizes 10000 \
    --runs 3 \
    --make-plots
```

## Output Files

### Results Directory (`results/`)

- **`bench_results.csv`**: Detailed results in CSV format
  - Columns: `algorithm`, `pivot`, `dataset`, `size`, `run`, `time_s`, `peak_mem_bytes`, `comparisons`, `swaps`, `seed`
  - One row per run

- **`summary.json`**: Aggregated statistics per (algorithm, dataset, size) combination
  - Includes: mean, std, best, worst times and memory
  - Comparison and swap statistics (if instrumentation enabled)

- **`bench.log`**: Rotating log file (max 10MB, 5 backups)
  - Contains: system info, run metadata, progress logs, errors

### Plots Directory (`plots/`)

- **`time_vs_size.png`**: Line chart showing sorting time vs array size
  - Separate subplot for each dataset type
  - One line per algorithm

- **`memory_vs_size.png`**: Line chart showing memory usage vs array size
  - Separate subplot for each dataset type
  - One line per algorithm

## Reproducing Results

### Generate a Plot

After running benchmarks:
```bash
python -m src.bench.benchmark \
    --algorithms merge,quick \
    --datasets random \
    --sizes 1000,5000,10000,50000 \
    --runs 5 \
    --seed 42 \
    --make-plots
```

Plots will be automatically generated in `plots/` directory.

### Generate CSV from Scratch

```bash
python -m src.bench.benchmark \
    --algorithms merge \
    --datasets sorted,reverse,random \
    --sizes 1000,5000 \
    --runs 3 \
    --seed 42 \
    --outdir results
```

Check `results/bench_results.csv` for the output.

## Logging

Logging is configured via `src.bench.logging_setup.py`:

- **Console output**: Formatted with timestamp, level, and message
- **File output**: Detailed logs with function names and line numbers
- **Rotation**: Log files rotate at 10MB, keeping 5 backups
- **Metadata**: Logs include Python version, OS, architecture, and git commit (if available)

### Log Levels

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages

### Example Log Output

```
2024-01-15 10:30:00 - __main__ - INFO - ================================================================================
2024-01-15 10:30:00 - __main__ - INFO - Benchmark session started
2024-01-15 10:30:00 - __main__ - INFO - Python version: 3.10.5
2024-01-15 10:30:00 - __main__ - INFO - Platform: macOS-13.0
2024-01-15 10:30:00 - __main__ - INFO - Running merge on random size=1000 run=1/5
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

The test suite includes:

1. **Unit Tests**:
   - Empty arrays
   - Single element arrays
   - Already sorted arrays
   - Reverse sorted arrays
   - Random arrays
   - Arrays with duplicates
   - Large arrays
   - Instrumentation tests

2. **Property Tests**:
   - Comparison with Python's `sorted()` on random arrays
   - Multiple sizes and pivot strategies

## Code Quality

### Type Checking

```bash
mypy src/ tests/
```

### Linting

```bash
ruff check src/ tests/
```

### Formatting

```bash
ruff format src/ tests/
```

Or using black:

```bash
black src/ tests/
```

## Algorithm Details

### Merge Sort

- **Time Complexity**: O(n log n) worst-case, average-case, best-case
- **Space Complexity**: O(n)
- **Stability**: Stable
- **Implementation**: Recursive divide-and-conquer with merging

### Quick Sort

- **Time Complexity**: O(n log n) average-case, O(n²) worst-case
- **Space Complexity**: O(log n) average-case (recursion stack)
- **Stability**: Not stable (in-place implementation)
- **Pivot Strategies**:
  - `first`: Always use first element (O(n²) on sorted arrays)
  - `last`: Always use last element (O(n²) on reverse sorted arrays)
  - `median_of_three`: Use median of first, middle, last
  - `random`: Random pivot (good average performance)

## Dataset Types

1. **sorted**: Array already in ascending order `[0, 1, 2, ..., n-1]`
2. **reverse**: Array in descending order `[n-1, n-2, ..., 0]`
3. **random**: Random integers from `[0, 10*n)` range
4. **nearly_sorted**: Sorted array with ~1% of elements swapped
5. **duplicates_heavy**: Array with many duplicate values (only `n/10` distinct values)

## Performance Considerations

- Benchmarks use `time.perf_counter()` for high-resolution timing
- Memory measurement uses both `tracemalloc` and `psutil` for accuracy
- Multiple runs per experiment reduce variance
- Seeded randomness ensures reproducibility

## Contributing

1. Follow Python type hints (checked with mypy)
2. Maintain test coverage
3. Run linting before committing
4. Update README for significant changes

## License

[Specify your license here]

## Performance Analysis

See **[ANALYSIS.md](ANALYSIS.md)** for a comprehensive comparison and analysis of the algorithms, including:

- Detailed performance metrics across sorted, reverse sorted, and random datasets
- Execution time and memory usage comparisons
- Operation counts (comparisons and swaps)
- Discussion of discrepancies between theoretical analysis and practical performance
- Explanations for observed performance characteristics

The analysis document includes:
- Performance tables for all dataset types
- Theoretical vs practical performance analysis
- Scalability analysis
- Recommendations for algorithm selection

## Acknowledgments

- Algorithms based on standard divide-and-conquer implementations
- Benchmarking framework inspired by best practices in performance testing

