# Graph Connectivity

Connectivity asks which vertices can reach one another and which edges or
vertices are essential to that reachability.  This directory contains
standard-library Python implementations in [`connectivity.py`](connectivity.py)
and executable tests in [`test_connectivity.py`](test_connectivity.py).

Run them from this directory:

```bash
python -m unittest -v
python connectivity.py
```

## Basic vocabulary

For a graph \(G=(V,E)\), an **undirected path** is a sequence of incident
edges; a **walk** may repeat vertices and edges.  A graph is connected when
every pair of vertices has a path between them.  Its **connected components**
are maximal connected subgraphs.  A directed graph is strongly connected when
every ordered pair \(u,v\) has a directed path from \(u\) to \(v\); its maximal
subgraphs with this property are **strongly connected components (SCCs)**.
Every vertex belongs to exactly one component.  A vertex with no incident edge
is a singleton component.

The code accepts adjacency mappings.  Vertices can be any hashable values, and
neighbors that occur only in a value (not as a key) are still recognized.
Undirected algorithms expect symmetric adjacency and a simple graph.  The
implementations use sets for answers, so component output order is unspecified.

## Connected components

The usual traversal is:

1. Keep an `unseen` set.
2. Start DFS or BFS at an unseen vertex.
3. Mark every vertex reachable from it; those vertices form one component.
4. Repeat until `unseen` is empty.

Each vertex and edge is inspected at most a constant number of times, so the
time is \(O(|V|+|E|)\), with \(O(|V|)\) auxiliary space.  A DSU is preferable
when edges arrive incrementally; a traversal is preferable when the graph is
already available and path details matter.

## Strongly connected components

### Kosaraju's algorithm

Kosaraju uses two linear-time DFS passes:

1. DFS the original graph and record vertices in **finish order**.
2. Reverse every edge.
3. Process vertices in decreasing finish time on the reversed graph.  Each DFS
   tree is exactly one SCC.

The first pass makes the SCC condensation DAG's sink/source ordering work in
the second pass.  It takes \(O(|V|+|E|)\) time and space, including the
reversed graph.

### Tarjan's algorithm

Tarjan performs one DFS.  Each vertex receives a discovery index and a
`lowlink` value: the smallest discovery index reachable from its DFS subtree
using tree edges and at most one edge back to a vertex currently on the stack.
Push vertices on a stack; when `lowlink[v] == index[v]`, `v` is the root of an
SCC, so pop through `v`.  Every edge is considered once: \(O(V+E)\) time and
\(O(V)\) space.  It is often more memory-efficient than Kosaraju because it
does not need a reverse graph, but both are clear and robust choices.

The supplied `kosaraju_scc` and `tarjan_scc` return equivalent unordered sets.
Recursive DFS is concise; for very deep graphs, replace it with an explicit
stack or raise Python's recursion limit carefully.

## Articulation points and bridges

In an undirected graph:

* An **articulation point** (cut vertex) is a vertex whose removal increases
  the number of connected components.
* A **bridge** (cut edge) is an edge whose removal increases that number.

Run DFS and record `discovery[v]` and `low[v]`, the earliest discovery time
reachable from `v`'s subtree without going through its parent tree edge.  For a
DFS tree edge `(u,v)`:

* `low[v] >= discovery[u]` means `u` separates `v`'s subtree and is an
  articulation point (except that the DFS root uses the special rule: it is a
  cut vertex exactly when it has at least two DFS children).
* `low[v] > discovery[u]` means `(u,v)` is a bridge.

These tests are \(O(V+E)\).  A bridge cannot lie on a cycle; an edge on a cycle
has an alternate route and is therefore not a bridge.  A cut vertex can belong
to several robust regions, so its removal can split them even when no one
incident edge alone is a bridge.

## Biconnected intuition

“Biconnected” is used in two closely related ways.  A 2-vertex-connected graph
has at least three vertices and remains connected after deletion of any one
vertex.  In decomposition algorithms, a **vertex-biconnected component** (block)
is a maximal subgraph with no internal articulation vertex; blocks may meet at
an articulation vertex.  Thus a chain of cycles joined at one vertex produces
one block per cycle, with the shared vertex in each.

During DFS, push each traversed edge onto a stack.  When a child `v` satisfies
`low[v] >= discovery[u]`, pop through `(u,v)`; those edges form one block.
The implementation returns each block as its vertex set and emits isolated
vertices as singleton blocks.  A bridge is itself a two-vertex block under this
decomposition.  For multigraphs, edge IDs rather than endpoint pairs are
needed; this example deliberately assumes simple graphs.

## Disjoint-set union (DSU / union-find)

DSU maintains a partition under:

* `find(x)`: identify the representative of `x`'s set;
* `union(a,b)`: merge two sets;
* `connected(a,b)`: test whether two items are in one set.

**Path compression** flattens find paths, while **union by size/rank** attaches
the smaller tree below the larger.  Across \(m\) operations on \(n\) items the
amortized cost is \(O(m\alpha(n))\), effectively constant; initialization
uses \(O(n)\) space.  `DisjointSetUnion` also supports dynamically adding
hashable items and counting current components.

DSU cannot report a path, articulation points, or directed SCCs: it only
maintains equivalence classes under undirected unions.  It is ideal when edges
are added but never removed, and when only “same component?” queries matter.

## Choosing an approach

| Need | Tool | Typical cost |
| --- | --- | --- |
| Components of a static undirected graph | DFS/BFS | \(O(V+E)\) |
| Components after a stream of undirected unions | DSU | near \(O(1)\) amortized |
| Directed mutual reachability | Kosaraju or Tarjan | \(O(V+E)\) |
| Failure-sensitive vertices/edges | low-link DFS | \(O(V+E)\) |
| Blocks / robust regions | edge-stack low-link DFS | \(O(V+E)\) |

## Applications

* **Networks:** connected components identify disconnected service regions;
  bridges and cut vertices expose single points of failure in roads, power
  grids, communications, and supply chains.
* **Build and dependency systems:** SCCs collapse mutually recursive packages
  into a DAG, which supports topological scheduling of the resulting groups.
* **Compilers:** SCCs find recursive call cycles and data-flow loops.
* **Databases and clustering:** DSU supports online equivalence constraints,
  image connected-component labeling, and Kruskal's minimum spanning tree.
* **Computer vision:** biconnected blocks identify regions resilient to one
  feature/vertex failure; connected components label foreground objects.
* **Social and web graphs:** SCCs capture mutual reachability, while weak
  components (connected components after ignoring direction) reveal broad
  communities.
* **Percolation and simulation:** DSU efficiently tracks whether a newly
  occupied site joins a spanning cluster.

## Correctness checklist and edge cases

Test empty graphs, isolated vertices, disconnected graphs, cycles, trees, a
single SCC, all singleton SCCs, and a graph whose directed edges are absent in
reverse.  The provided tests cover isolated vertices, multiple SCCs, a cycle
with bridge tails, articulation points, blocks, and repeated DSU unions.
For production-scale or adversarially deep input, prefer iterative DFS to avoid
Python recursion depth limits, and validate that undirected adjacency is
symmetrical before using the undirected routines.
