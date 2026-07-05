#!/usr/bin/env python3

import argparse
import csv
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt


RESULT_FILE_PATTERN = re.compile(r"results-(\d+)\.json$")
COMMAND_PATTERN = re.compile(r"\bbench\.py\s+([123])\s+(\d+)\b")


def extract_benchmark_number(command: str) -> int:
    """
    Extract the benchmark identifier from a command such as:

        python bench.py 2 100
    """
    match = COMMAND_PATTERN.search(command)

    if match is None:
        raise ValueError(
            f"Could not identify the benchmark in command: {command!r}"
        )

    return int(match.group(1))


def read_hyperfine_file(path: Path) -> tuple[int, dict[int, dict]]:
    """
    Read one Hyperfine JSON file.

    Returns:
        N and a dictionary mapping benchmark identifiers to their results.
    """
    filename_match = RESULT_FILE_PATTERN.fullmatch(path.name)

    if filename_match is None:
        raise ValueError(
            f"Unexpected result filename: {path.name!r}"
        )

    n = int(filename_match.group(1))

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    results = data.get("results")

    if not isinstance(results, list):
        raise ValueError(
            f"The file {path} does not contain a valid Hyperfine "
            "'results' list."
        )

    benchmarks = {}

    for result in results:
        command = result.get("command", "")
        benchmark = extract_benchmark_number(command)

        if "mean" not in result:
            raise ValueError(
                f"No mean execution time was found for {command!r} "
                f"in {path}."
            )

        benchmarks[benchmark] = result

    missing = {1, 2, 3} - benchmarks.keys()

    if missing:
        raise ValueError(
            f"The file {path} is missing benchmark(s): "
            f"{sorted(missing)}"
        )

    return n, benchmarks


def collect_results(
    results_directory: Path,
) -> list[dict[str, float]]:
    """
    Collect and normalize all Hyperfine results.

    Benchmark 3 is used as the baseline.
    """
    files = list(results_directory.glob("results-*.json"))

    if not files:
        raise FileNotFoundError(
            f"No files matching 'results-*.json' were found in "
            f"{results_directory}."
        )

    collected = []

    for path in files:
        n, benchmarks = read_hyperfine_file(path)

        mean_1 = float(benchmarks[1]["mean"])
        mean_2 = float(benchmarks[2]["mean"])
        mean_3 = float(benchmarks[3]["mean"])

        if mean_3 <= 0:
            raise ValueError(
                f"Invalid baseline execution time in {path}: {mean_3}"
            )

        collected.append(
            {
                "n": n,
                "mean_1": mean_1,
                "mean_2": mean_2,
                "mean_3": mean_3,
                "relative_1": mean_1 / mean_3,
                "relative_2": mean_2 / mean_3,
            }
        )

    collected.sort(key=lambda row: row["n"])
    return collected


def write_csv(results: list[dict[str, float]], output_path: Path) -> None:
    """Write the collected and normalized results to a CSV file."""
    fieldnames = [
        "n",
        "mean_imp1_seconds",
        "mean_imp2_seconds",
        "mean_imp3_seconds",
        "imp1_relative_to_imp3",
        "imp2_relative_to_imp3",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in results:
            writer.writerow(
                {
                    "n": row["n"],
                    "mean_imp1_seconds": row["mean_1"],
                    "mean_imp2_seconds": row["mean_2"],
                    "mean_imp3_seconds": row["mean_3"],
                    "imp1_relative_to_imp3": row["relative_1"],
                    "imp2_relative_to_imp3": row["relative_2"],
                }
            )


def create_plot(
    results: list[dict[str, float]],
    output_prefix: Path,
    show_plot: bool,
) -> None:
    """Create the relative-performance plot."""
    n_values = [row["n"] for row in results]
    relative_1 = [row["relative_1"] for row in results]
    relative_2 = [row["relative_2"] for row in results]

    fig, axis = plt.subplots(figsize=(8, 5))

    axis.plot(
        n_values,
        relative_1,
        marker="o",
        linewidth=1.8,
        label="imp1 / imp3",
    )

    axis.plot(
        n_values,
        relative_2,
        marker="s",
        linewidth=1.8,
        label="imp2 / imp3",
    )

    # Benchmark 3 is not plotted as a series, but this line shows
    # the baseline against which imp1 and imp2 are normalized.
    axis.axhline(
        y=1.0,
        linestyle="--",
        linewidth=1,
        label="imp3 baseline",
    )

    axis.set_xlabel("Number of strings ($N$)")
    axis.set_ylabel("Relative execution time")
    axis.set_title("Execution time relative to imp3")
    axis.grid(True, linestyle=":", linewidth=0.7)
    axis.legend()
    axis.set_ylim(bottom=0)

    fig.tight_layout()

    png_path = output_prefix.with_suffix(".png")
    pdf_path = output_prefix.with_suffix(".pdf")

    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")

    print(f"PNG plot written to: {png_path}")
    print(f"PDF plot written to: {pdf_path}")

    if show_plot:
        plt.show()
    else:
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Plot Hyperfine execution times relative to benchmark 3."
        )
    )

    parser.add_argument(
        "results_directory",
        nargs="?",
        type=Path,
        default=Path("benchmark-results"),
        help=(
            "Directory containing results-N.json files "
            "(default: benchmark-results)."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("relative-performance"),
        help=(
            "Output filename prefix "
            "(default: relative-performance)."
        ),
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the plot interactively.",
    )

    args = parser.parse_args()

    results = collect_results(args.results_directory)

    csv_path = args.output.with_suffix(".csv")
    write_csv(results, csv_path)
    create_plot(results, args.output, args.show)

    print(f"CSV data written to: {csv_path}")


if __name__ == "__main__":
    main()
