# Graph Theory Foundations

Graphs are a compact language for describing relationships: roads join
intersections, links join web pages, and dependencies join software packages.
This tutorial introduces the vocabulary and representations needed to reason
about those relationships, then connects each choice to practical complexity
trade-offs.

The accompanying [`graph_demo.py`](graph_demo.py) is a runnable, standard
library-only implementation. It intentionally favors readable code over a
feature-complete graph package; copy it and modify the examples at the bottom
to experiment.

## 1. What is a graph?

A graph is a pair \(G=(V,E)\):

* **Vertices** (or nodes) \(V\) are the objects.
* **Edges** \(E\) are relationships between objects.

For an undirected simple graph, an edge is an unordered pair \(\{u,v\}\).
Thus \(\{u,v\}\) and \(\{v,u\}\) describe the same edge, and self-loops
\(\{u,u\}\) are normally excluded. For example, a triangle has

```text
V = {A, B, C}
E = {{A, B}, {B, C}, {C, A}}
```

The graph is **finite** when \(V\) and \(E\) are finite. Unless stated
otherwise, examples here are finite.

### Variants

* **Undirected graph:** relationships have no direction. “Alice is friends
  with Bob” is naturally undirected.
* **Directed graph (digraph):** an edge is an ordered pair \((u,v)\). It goes
  from `u` (the **tail**) to `v` (the **head**); following a link may not work
  in reverse.
* **Weighted graph:** each edge has a numerical label such as distance,
  cost, capacity, or time. A weight can be positive, zero, or (in some
  algorithms) negative.
* **Multigraph:** multiple distinct edges may join the same endpoints.
  Parallel flights between two airports are a natural example. A multigraph
  may also permit loops, depending on the convention.
* **Simple graph:** undirected, unweighted, no loops, and no parallel edges.
  “Graph” often means simple graph when no qualifiers are given.

These properties combine: a directed weighted multigraph is perfectly
reasonable. The data structure must preserve every distinction the model
needs.

## 2. Degree and neighborhoods

For an undirected graph, the **degree** \(\deg(v)\) is the number of edges
incident to vertex \(v\). A loop contributes two to degree in the usual
undirected convention. In a directed graph, distinguish:

* **in-degree** \(\deg^-(v)\): edges entering `v`;
* **out-degree** \(\deg^+(v)\): edges leaving `v`.

The **neighborhood** of `v`, written \(N(v)\), is the set of vertices adjacent
to it. For a directed graph, use \(N^+(v)\) for outgoing neighbors and
\(N^-(v)\) for incoming neighbors. A vertex of degree zero is **isolated**.

The handshaking lemma says

\[
\sum_{v\in V}\deg(v)=2|E|
\]

for an undirected graph (counting a loop twice). For a digraph,
\(\sum_v\deg^-(v)=\sum_v\deg^+(v)=|E|\). These identities are useful sanity
checks when writing graph code.

## 3. Representations

### Edge list

Store each edge as a record such as `(u, v)` or `(u, v, weight)`.

```python
[("A", "B"), ("B", "C"), ("C", "A")]
```

This is compact and excellent for iterating over all edges, sorting by weight
(as in Kruskal's algorithm), or loading data. Testing whether a particular
edge exists takes \(O(E)\) time without an auxiliary index. In a multigraph,
each parallel edge appears as its own record.

### Adjacency list

Map each vertex to the vertices (or edge records) directly reachable from it:

```python
{
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4)],
    "C": [("A", 2)],
}
```

For an undirected graph, insert both directions. For a directed graph, insert
only the tail-to-head direction. Adjacency lists use \(O(V+E)\) space and
make neighbor iteration efficient, so breadth-first search and depth-first
search run in \(O(V+E)\). Membership is \(O(\deg(v))\) with a list; a set can
make expected membership \(O(1)\), at the cost of extra memory and ordering.

### Adjacency matrix

Use a \(V\times V\) table. Entry \(A[u][v]\) is 1 (or `True`) when an edge
exists, 0 otherwise. For weights, store the weight and choose a clear
“no-edge” sentinel such as `None` or infinity.

Matrices use \(O(V^2)\) space and give \(O(1)\) edge-existence lookup and
weight lookup. Iterating over all neighbors costs \(O(V)\), even when the
vertex has few neighbors. A matrix is often ideal for dense graphs or
algorithms based on matrix multiplication. A basic matrix cannot represent
parallel edges without storing a collection or an aggregate (minimum,
maximum, count, and so on) in each cell.

### Complexity summary

Here \(V=|V|\), \(E=|E|\), and \(d(v)\) is the degree:

| Operation | Edge list | Adjacency list | Matrix |
| --- | ---: | ---: | ---: |
| Space | \(O(E)\) | \(O(V+E)\) | \(O(V^2)\) |
| Is edge `(u, v)` present? | \(O(E)\) | \(O(d(u))\) (or expected \(O(1)\) with sets) | \(O(1)\) |
| Enumerate neighbors of `u` | \(O(E)\) | \(O(d(u))\) | \(O(V)\) |
| Add an edge | \(O(1)\) append | expected \(O(1)\) | \(O(1)\) |
| Remove an edge | \(O(E)\) to find it | \(O(d(u))\) | \(O(1)\) |

“\(O(1)\)” for a list insertion assumes no duplicate check and ignores
resizing details. In practice, choose based on workload: sparse traversal
usually favors lists, while frequent pair queries or dense data favors a
matrix.

## 4. Useful graph properties

* **Order** is \(|V|\); **size** is \(|E|\).
* A graph is **simple** when it has no loops or parallel edges.
* It is **connected** when every pair of vertices has an undirected path.
  A directed graph is **strongly connected** when directed paths exist both
  ways between every pair; it is **weakly connected** when ignoring direction
  leaves a connected graph.
* A **path** is a sequence of vertices joined by edges. Its **length** is
  usually its number of edges (or the sum of weights in a weighted setting).
  A **cycle** starts and ends at the same vertex without repeating vertices
  otherwise.
* A graph with no cycles is **acyclic**. A directed acyclic graph (DAG) has
  a **topological ordering**, an ordering in which every edge points forward.
* A **tree** is a connected undirected acyclic graph. For \(V>0\), it has
  exactly \(V-1\) edges. A **forest** is a disjoint union of trees.
* A graph is **bipartite** if its vertices can be split into two groups so
  every edge crosses between groups. Equivalently, it has no odd cycle.
* A **complete graph** has every possible edge; \(K_n\) has
  \(n(n-1)/2\) undirected edges.
* The **distance** between vertices is the shortest path length. The graph's
  **diameter** is the maximum finite distance within a connected component.

Properties often determine algorithms: topological sorting requires a DAG,
two-coloring tests bipartiteness, and Dijkstra's algorithm requires
non-negative edge weights.

## 5. Isomorphism intuition

Two graphs are **isomorphic** when they have the same structure after
renaming vertices. Formally, there is a bijection \(f:V_1\to V_2\) such that
\(\{u,v\}\) is an edge exactly when \(\{f(u),f(v)\}\) is an edge (and weights
or directions are preserved when present).

For example, edges `{("red", "blue"), ("blue", "green")}` and
`{(1, 2), (2, 3)}` describe the same three-vertex path. Names do not matter;
adjacency does. Equal vertex count, edge count, and sorted degree sequence are
quick necessary checks, but not sufficient in general: different graphs can
share all of them. Finding an isomorphism is a deeper matching problem, so
real systems use canonical labeling, refinement, or specialized algorithms
rather than trying every permutation blindly.

## 6. Run the examples

From this directory:

```bash
python3 graph_demo.py
```

The script builds a weighted undirected graph, prints all three
representations, reports degrees and neighborhoods, and demonstrates a
directed graph and a multigraph. It uses only Python's standard library.

