#!/usr/bin/env bash

set -euo pipefail

MIN_N="${1:-10}"
MAX_N="${2:-300}"
RUNS="${3:-10}"
STEP="${4:-50}"

RESULTS_DIR="benchmark-results"

if ! command -v hyperfine >/dev/null 2>&1; then
    echo "Error: hyperfine is not installed."
    echo "On Ubuntu/Debian, try: sudo apt install hyperfine"
    echo "With Cargo, try: cargo install hyperfine"
    exit 1
fi

if [[ ! -f "bench.py" ]]; then
    echo "Error: bench.py was not found in the current directory."
    exit 1
fi

mkdir -p "$RESULTS_DIR"

for ((n = MIN_N; n <= MAX_N; n += STEP)); do
    echo
    echo "=================================================="
    echo "Benchmarking with N = $n"
    echo "=================================================="

    hyperfine \
        --warmup 3 \
        --runs "$RUNS" \
        --export-json "$RESULTS_DIR/results-${n}.json" \
        --export-markdown "$RESULTS_DIR/results-${n}.md" \
        "python bench.py 1 $n" \
        "python bench.py 2 $n" \
        "python bench.py 3 $n" 
done

echo
echo "Results saved in: $RESULTS_DIR/"
