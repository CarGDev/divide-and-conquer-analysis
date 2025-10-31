#!/bin/bash
# Run benchmarks script

set -e

echo "Running sorting algorithm benchmarks..."

python -m src.bench.benchmark \
    --algorithms merge,quick \
    --datasets sorted,reverse,random,nearly_sorted,duplicates_heavy \
    --sizes 1000,5000,10000,50000 \
    --runs 5 \
    --seed 42 \
    --instrument \
    --outdir results \
    --log-level INFO \
    --make-plots

echo "Benchmarks completed. Check results/ and plots/ directories."

