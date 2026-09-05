# Advanced graph theory: structures, algorithms, and honest limits

This chapter is a practical survey of several graph-theory topics that sit
between textbook definitions and real software.  The examples use an
undirected graph unless stated otherwise.  Vertices are represented by any
hashable Python value and an edge is a pair of vertices.

## 1. Eulerian paths and circuits

An **Eulerian path** (or trail) uses every edge exactly once.  An **Eulerian
circuit** starts and ends at the same vertex.  Vertices may repeat; edges may
not.  This is different from a Hamiltonian path, which constrains vertices.

For a finite connected graph after ignoring isolated vertices:

* it has an Eulerian circuit exactly when every vertex has even degree;
* it has an open Eulerian path exactly when exactly two vertices have odd
  degree;
* zero odd vertices gives a circuit (and a circuit can be viewed as a path);
* more than two odd vertices makes an Euler trail impossible.

The criterion is a theorem, not merely a useful heuristic.  The constructive
algorithm is **Hierholzer's algorithm**: walk unused edges until returning to
the start, then splice in further closed walks.  With adjacency lists and
edge IDs it runs in `O(V + E)` time.  For a directed graph, replace degree
parity with in-degree/out-degree balance and require the appropriate
underlying connectivity.

## 2. Hamiltonian paths and NP-completeness intuition

A **Hamiltonian path** visits every vertex exactly once; a Hamiltonian cycle
also returns to its start.  The local degree checks that solve Euler's
problem do not solve Hamilton's problem: choosing one edge can block a
necessary later choice, so the search has global dependencies.

The decision problem “does this graph contain a Hamiltonian cycle?” is
NP-complete.  Informally:

1. A proposed cycle is a short certificate: check every vertex once and every
   consecutive pair is an edge in polynomial time.
2. A nondeterministic algorithm can guess a certificate, so the problem is in
   NP.
3. Many other NP problems can be transformed into it in polynomial time,
   establishing NP-hardness.

NP-complete does **not** mean “never solvable.”  Small instances, special
   graph families, dynamic programming, integer programming, branch-and-bound,
   and approximation for related optimization problems can all be useful.
   It does mean that no polynomial-time algorithm is known for all instances,
   and a general exact solver can require exponential work.

The included backtracking demo is intentionally bounded.  It is useful for
teaching and for graphs with strong pruning, not for large production inputs.
For `n` vertices, a naive search can explore roughly `O(n!)` paths.

## 3. Graph coloring

A proper **k-coloring** assigns one of `k` colors to each vertex so adjacent
vertices receive different colors.  The smallest feasible `k` is the
chromatic number `χ(G)`.

Facts worth keeping separate:

* bipartite graphs are exactly the 2-colorable graphs (including disconnected
  components);
* every planar graph has a coloring with at most four colors (the four-color
  theorem), while five colors have a simpler proof;
* greedy coloring is fast and often useful, but its answer depends on vertex
  order and can be far from optimal;
* deciding whether `χ(G) ≤ 3` is NP-complete.

A good engineering workflow is to run a fast greedy coloring for an upper
bound, compute easy lower bounds (a clique, an odd cycle, or degree-based
bounds), then use exact search only when the gap matters.

## 4. Planar graph basics

A graph is **planar** if it can be drawn in the plane with no edge crossings
except at shared endpoints.  A particular crossing-free drawing is a
**plane embedding**; planarity is a property of the abstract graph.

For a connected planar simple graph with `V ≥ 3`, Euler's formula is

`V - E + F = 2`,

where `F` counts the outside face as well.  It implies `E ≤ 3V - 6` and
therefore some vertex has degree at most five.  If the graph is triangle-free,
the stronger bound `E ≤ 2V - 4` holds.  The non-planar graphs `K5` and `K3,3`
are the classic obstructions; Kuratowski's theorem characterizes all
non-planar graphs using subdivisions of these two.

This folder does not pretend that a few inequalities are a planarity tester:
the edge bound is necessary but not sufficient.  Linear-time planarity tests
exist (for example, Boyer–Myrvold), but implementing one correctly is a
separate project.  The demo reports Euler bounds and detects explicit
crossings only for a supplied geometric drawing.

## 5. Random graphs

The Erdős–Rényi model `G(n,p)` includes each of the `n choose 2` possible
edges independently with probability `p`.  The expected number of edges is
`p n(n-1)/2`; the degree of one vertex has a binomial distribution.

Sharp threshold phenomena make this model useful for intuition:

* around `p ≈ (log n)/n`, connectivity becomes likely;
* around `p ≈ 1/n`, a giant component emerges;
* increasing `p` usually shrinks distances and raises clustering only in
  comparison with very sparse graphs (other random models control clustering
  differently).

A simulation is evidence about a model, not proof about one observed network.
Use a fixed random seed for reproducible teaching examples and report the
number of trials, not just one attractive sample.

## 6. Centrality

Centrality asks what “important” means, and different definitions answer
different questions:

* **degree centrality:** many immediate neighbors;
* **closeness:** small average shortest-path distance to reachable vertices;
* **betweenness:** lies on many shortest paths, often acting as a broker;
* **eigenvector centrality:** connected to other high-scoring vertices.

Disconnected graphs require care: raw closeness can be undefined or misleading
when distances are infinite.  Betweenness has normalization conventions that
vary between libraries.  Centrality is descriptive, not automatically causal:
high score may reflect data collection, popularity, or a particular time slice.

## 7. PageRank intuition

PageRank models a random surfer.  At each step it follows an outgoing link
with probability `d` and teleports uniformly with probability `1-d`.  In
column-vector notation, the stationary vector satisfies

`r = d P r + (1-d) u`.

Teleportation makes the Markov chain ergodic in the usual implementation and
prevents dangling pages from trapping all probability.  Rank is relative:
changing the graph, damping factor, personalization vector, or treatment of
directed edges changes the result.  PageRank is not a universal measure of
truth, quality, or influence, and link farms/adversarial links can manipulate
it.

The Python demo uses power iteration, redistributes dangling mass uniformly,
and stops on an L1-difference tolerance.  It is pedagogical, not a sparse
matrix implementation for web-scale graphs.

## 8. Spectral concepts

The adjacency matrix `A` records edges (`A[i,j]=1` for a simple graph).
Eigenvalues and eigenvectors reveal global structure:

* the largest adjacency eigenvalue is tied to growth and eigenvector
  centrality;
* the graph Laplacian `L = D - A` is positive semidefinite;
* the multiplicity of Laplacian eigenvalue zero equals the number of connected
  components;
* the second-smallest Laplacian eigenvalue (algebraic connectivity) measures
  how difficult it is to separate a connected graph;
* a Fiedler vector can suggest a spectral partition by its sign.

The bundled power iteration estimates only a dominant eigenvector and can
converge slowly or fail to identify a unique direction when eigenvalues tie.
Without NumPy, the example stays small and uses ordinary Python lists.

## 9. Approximation and heuristic cautions

An approximation algorithm has a provable guarantee relative to an optimum;
a heuristic is simply a practical rule with no universal guarantee.  Do not
call a greedy coloring or nearest-neighbor tour “an approximation algorithm”
unless its ratio and assumptions are established.

Common cautions:

* compare against an exact optimum on small instances;
* state whether the objective is minimized or maximized and define ties;
* test adversarial and random cases, not only friendly examples;
* distinguish worst-case guarantees from average-case behavior;
* preserve reproducible seeds and disclose timeouts;
* centrality and PageRank scores are model outputs, not causal conclusions.

## Running the explorations

The script requires only Python 3.9+ and the standard library:

```bash
python3 explore.py
python3 explore.py --seed 7 --random-trials 200
```

It demonstrates Euler construction, bounded Hamiltonian search, coloring,
random-graph statistics, centrality, PageRank, and a small spectral estimate.
The assertions are deliberately small sanity checks; they are not a
replacement for a graph library or a proof.
