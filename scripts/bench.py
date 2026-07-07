'''
Running the 3 benchmarks 

Dependencies: 
pip install maude

Examples of use: 

positional arguments:
  {1,2,3}     Benchmark identifier: 1, 2, or 3.
  n           Number of random strings.
'''

import argparse
import random
import string

import maude


BASE_SEED = 20260703
MIN_STRING_LENGTH = 1
MAX_STRING_LENGTH = 12


def generate_random_strings(n: int) -> list[str]:
    '''Generating random strings'''
    if n < 0:
        raise ValueError("The number of strings must be non-negative.")

    # The same value of n always produces the same sequence.
    rng = random.Random(BASE_SEED + n)

    result = []
    for _ in range(n):
        length = rng.randint(MIN_STRING_LENGTH, MAX_STRING_LENGTH)
        value = "".join(
            rng.choices(string.ascii_letters, k=length)
        )
        result.append(value)

    return result


def to_maude_string_sequence(values: list[str]) -> str:
    """Convert Python strings to a space-separated Maude string sequence."""
    return " ".join(f'"{value}"' for value in values)


def to_maude_string_list(values: list[str]) -> str:
    """Convert Python strings to a bracketed Maude string list."""
    return f"[{to_maude_string_sequence(values)}]"


def main(benchmark: int, n: int) -> None:
    module_name = "BENCHMARK"
    if benchmark == 1:
        maude_file = "bench"
    elif benchmark == 2:
        maude_file = "bench2"
    elif benchmark == 3:
        maude_file = "bench3"
    else:
        raise ValueError(
            "The benchmark identifier must be 1, 2, or 3."
        )

    maude.init()

    if not maude.load(maude_file):
        raise RuntimeError(
            f"Could not load the Maude file '{maude_file}'."
        )

    module = maude.getModule(module_name)

    if module is None:
        raise RuntimeError(
            f"Could not find the Maude module '{module_name}'."
        )

    random_strings = generate_random_strings(n)
    maude_sequence = to_maude_string_sequence(random_strings)
    maude_list = to_maude_string_list(random_strings)

    if benchmark == 1:
        term_text = (
            "map(lambda x:String : length(x:String), "
            f"{maude_list})"
        )
    elif benchmark == 2:
        term_text = f"map({maude_list})"
    else:
        term_text = f"map({maude_sequence})"

    term = module.parseTerm(term_text)

    if term is None:
        raise RuntimeError(
            f"Could not parse the Maude term:\n{term_text}"
        )

    term.reduce()
    print(term)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run one of the Maude benchmarks."
    )
    parser.add_argument(
        "benchmark",
        type=int,
        choices=(1, 2, 3),
        help="Benchmark identifier: 1, 2, or 3.",
    )
    parser.add_argument(
        "n",
        type=int,
        help="Number of random strings.",
    )

    args = parser.parse_args()
    main(args.benchmark, args.n)
