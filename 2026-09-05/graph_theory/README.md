# Graph Theory Playground

This directory is a practical, self-contained tour of graph theory. Each
topic has two goals:

1. Explain the mathematical ideas, assumptions, correctness intuition, and
   complexity in Markdown.
2. Provide standard-library Python code that can be read, run, modified, and
   used as a small laboratory.

The examples intentionally favor clarity over production-level optimization.
They use ordinary dictionaries, lists, sets, heaps, and recursion so that the
connection between the mathematics and the implementation remains visible.

## Topic map

| Topic | Main ideas | Python material |
| --- | --- | --- |
| [Foundations](foundations/) | Graph models, representations, degrees, neighborhoods, variants, complexity | `graph_demo.py` |
| [Traversals](traversals/) | BFS, DFS, parent trees, timestamps, cycles, bipartiteness, components, topological sort | `traversals.py` |
| [Shortest paths](shortest_paths/) | BFS paths, Dijkstra, Bellman-Ford, DAG paths, Floyd-Warshall, negative cycles | `shortest_paths.py` |
| [Connectivity](connectivity/) | Components, SCCs, DSU, articulation points, bridges, biconnected blocks | `connectivity.py`, `test_connectivity.py` |
| [Spanning trees](spanning_trees/) | Trees, forests, MSTs, cuts, cycles, Kruskal, Prim, DSU | `spanning_trees.py` |
| [Flow and matching](flow_and_matching/) | Residual networks, augmenting paths, Edmonds-Karp, min-cut, bipartite matching | `flow_matching.py`, tests |
| [Advanced topics](advanced/) | Eulerian and Hamiltonian structure, coloring, planarity, random graphs, centrality, PageRank, spectra | `explore.py` |

## Suggested path

Start with **Foundations** to learn the vocabulary and compare adjacency
lists, matrices, and edge lists. Read **Traversals** next: BFS and DFS are the
building blocks for many later algorithms.

Move to **Shortest paths** and **Spanning trees** for optimization problems.
Then study **Connectivity** to understand how graph structure changes when
vertices or edges are removed. **Flow and matching** introduces a powerful
optimization model. Finish with **Advanced topics**, where some problems are
easy to solve, some are computationally difficult, and some are best explored
with heuristics or approximations.

## Running the experiments

The scripts are designed to run without third-party packages. From a topic
directory, use the command shown by its README. Typical commands are:

```sh
python3 graph_demo.py
python3 traversals.py
python3 shortest_paths.py
python3 -m unittest -v
```

Most scripts include assertions or demonstrations. They are intentionally
small enough to edit interactively: change the vertices, add an edge, alter a
weight, or construct a counterexample and observe what changes.

## Shared conventions

- Vertices are usually hashable Python values, commonly strings or integers.
- An adjacency list maps a vertex to its outgoing neighbors.
- Weighted edges are represented as `(neighbor, weight)` pairs or explicit
  edge records, as explained by each topic.
- Unless a topic says otherwise, arithmetic uses Python integers.
- A Boolean result is represented by `True`/`False` in Python and often as
  `1`/`0` when printed by the example language.
- Unreachable vertices are represented by an omitted distance or `None`,
  depending on the function's documented return value.
- Algorithms validate important preconditions, but the examples are not a
  substitute for an industrial graph library.

## How to study each topic

For each folder, read the Markdown before the code. Identify:

1. The exact graph model and input assumptions.
2. The invariant maintained by the algorithm.
3. Why the algorithm terminates and why its result is correct.
4. The time and space complexity.
5. Which edge cases can invalidate a tempting implementation.

Then run the Python file and change one thing at a time. Useful experiments
include disconnected graphs, parallel edges, self-loops, negative weights,
ties, multiple shortest paths, cycles, and empty inputs.

## Scope and limitations

The collection aims to be broad and educational rather than exhaustive in the
research sense. It does not replace a textbook: proofs are often presented as
invariants and correctness sketches, and implementations omit concerns such
as persistence, concurrency, huge inputs, and specialized data structures.
Those omissions are deliberate so the core ideas stay approachable.
