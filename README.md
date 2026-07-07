# MAUDE-LAMBDA

This repository contains rewrite theories that support higher-order programming
in [Maude](https://github.com/maude-lang/Maude). They allow users to write
specifications using standard higher-order functions such as `map`, `filter`,
and `fold`.

We propose two approaches:

- **Higher-order functions via parameterized modules.** This approach builds on
  Maude's advanced [theory and view system](https://maude.lcc.uma.es/maude-manual/maude-manualch7.html). 
  We define module interfaces for iterable data structures, while the function
  to be applied in a higher-order setting is defined within a module.

- **Lambda abstractions.** This approach provides the sorts and constructors
  required to represent lambda abstractions in Maude. These abstractions are
  then used to define the usual higher-order functions.

The approach based on lambda abstractions is closer to common functional
programming practice than the approach based on parameterized modules. However,
this additional flexibility comes with an execution overhead: meta-level
operations are required to perform beta-reduction during function application.

Further details about the implementation are available in
[thi paper](./paper.pdf).

The two approaches are implemented in separate directories:

- `pmodule` contains the Maude files required for the parameterized-module
  approach.
- `lambda` contains the Maude files defining lambda abstractions and the
  corresponding higher-order functions.

Each directory contains a description of the implemented modules, together
with examples of their use. The directory `base` contains common definitions
including the definition of collections and iterators. 

The `scripts` directory contains scripts for benchmarking and comparing the
two approaches.
