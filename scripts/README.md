This directory contains some useful scripts to benchmark the two
implementations proposed here. In the benchmark files, we define a simple map
from a list of strings into a set containing the (different) sizes of the
strings:

- `bench.maude`: Using lambdas
- `bench2.maude`: Using iterables (parametrized modules)
- `bench3.maude`: Defining the map directly in Maude (without using our theories)

The script `bench.py` can be used to run the three instances: 

```
usage: bench.py [-h] {1,2,3} n

Run one of the Maude benchmarks.

positional arguments:
  {1,2,3}     Benchmark identifier: 1, 2, or 3.
  n           Number of random strings.

```
To run this script, you need the 
[Language bindings for Maude](https://github.com/fadoss/maude-bindings):

```
pip install maude
```

The script `bench.sh` uses [hyperfine](https://github.com/sharkdp/hyperfine) to
test different instances. Once this script is executed, `plot.py` can be used
to generate a plot from the results. This script requires
[Matplotlib](https://matplotlib.org/)

