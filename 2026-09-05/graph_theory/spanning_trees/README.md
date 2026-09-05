# Trees, spanning trees, and minimum spanning trees

This note develops the basic theory and two standard algorithms for weighted
undirected graphs. The accompanying `spanning_trees.py` is executable with
Python 3 and uses only the standard library:

```bash
python3 spanning_trees.py
```

## 1. Trees

A **graph** has vertices (nodes) and edges (links). Here graphs are finite,
undirected, and may have an explicitly supplied set of isolated vertices. A
**path** is a sequence of vertices joined by edges. A graph is **connected**
when every pair of vertices has a path between them. A **cycle** is a closed
path with no repeated vertices except its first/last vertex.

A **tree** is a connected, acyclic, undirected graph. For a graph with `n`
vertices, the following are equivalent:

* it is a tree;
* it is connected and has exactly `n - 1` edges;
* it is acyclic and has exactly `n - 1` edges;
* every two vertices have exactly one simple path;
* adding any missing edge creates a cycle;
* deleting any edge disconnects it (every edge is a bridge).

An induction proof of the edge count is useful: remove a leaf (a degree-one
vertex), apply the induction hypothesis to the remaining tree, then restore
the leaf and its one edge. More generally, a forest with `n` vertices and `c`
connected components has `n - c` edges.

## 2. Spanning trees and forests

Given a connected graph `G = (V, E)`, a **spanning tree** is a subgraph with
all vertices `V` and enough edges to remain connected, but no cycles. Thus it
has exactly `|V| - 1` edges. A graph can have many spanning trees; a complete
graph `K_n` has `n^(n-2)` by Cayley's formula.

If `G` is disconnected, no single spanning tree can connect vertices from
different components. A **spanning forest** contains a spanning tree inside
each connected component and has `|V| - c` edges. Both implementations in the
Python file naturally return a minimum spanning forest for disconnected input,
which is often the useful generalization.

## 3. Minimum spanning trees (MSTs)

Give each edge a numerical weight (cost, distance, latency, etc.). A **minimum
spanning tree** minimizes the sum of its edge weights among all spanning trees.
Negative weights are valid; only comparisons matter. For disconnected graphs,
the analogous minimum spanning forest minimizes each component's total.

An MST need not be unique. It is unique when the edge weights are all distinct,
but distinct weights are sufficient rather than necessary: some ties can exist
without producing alternative optimal trees. A reliable characterization is:
for every cycle, the maximum-weight edge is unique (then it cannot belong to
any MST). Conversely, if a cycle has two or more maximum-weight edges, an MST
can be exchanged to obtain another MST. `unique_mst` in the example checks ties
group-by-group using this exchange idea.

## 4. Cut and cycle properties

For a cut `(S, V-S)`, an edge **crosses** it when one endpoint is in each side.

**Cut property (safe edge).** If an edge is a lightest edge crossing some cut,
then it is safe: at least one MST contains it. If it is the *unique* lightest
edge crossing that cut, every MST contains it. Proof sketch: start with an MST;
if it omits the edge, add it to create a cycle, then remove the cycle edge that
also crosses the cut. The replacement is no heavier.

**Cycle property.** If an edge is strictly heavier than every other edge on a
cycle, it is in no MST. Remove it from an MST if necessary by exchanging it
with a lighter cycle edge. With ties, a maximum edge may occur in some MST but
is not forced out; this is why the strict/unique wording matters.

Kruskal repeatedly applies the cut property to the globally lightest safe edge.
Prim repeatedly applies it to the cut separating the vertices already reached
from the rest of that component.

## 5. Kruskal's algorithm

1. Sort all edges by nondecreasing weight.
2. Start with each vertex in its own component.
3. Scan edges. Add an edge exactly when its endpoints are in different DSU
   components; otherwise skip it because it would make a cycle.
4. Stop after `n - 1` accepted edges in a connected graph.

The edge acceptance rule is the cycle test; the DSU makes it efficient. With
`m` edges and `n` vertices, sorting costs `O(m log m)`, while DSU operations
cost `O(m α(n))` (effectively linear), so the total is `O(m log m)`.

## 6. Prim's algorithm

1. Choose a start vertex and mark it reached.
2. Put all edges leaving the reached set into a min-priority queue.
3. Remove the lightest edge whose far endpoint is unreached, add it, and push
   the new vertex's outgoing edges.
4. Repeat until the component is spanned. Restart from an unreached vertex for
   a spanning forest.

With adjacency lists and a binary heap, Prim runs in `O(m log n)` (often stated
as `O(m log n)` or `O(m log m)` depending on the heap implementation). With a
dense adjacency matrix and a simple array it is `O(n^2)`. The code uses a heap
and deliberately restarts, so isolated vertices are represented correctly.

## 7. Disjoint-set union (DSU)

DSU maintains a partition of vertices under:

* `find(x)`: return the representative of `x`'s component;
* `union(x, y)`: merge components, returning whether a merge occurred.

**Path compression** flattens parent pointers during `find`; **union by rank**
attaches the shallower tree under the deeper tree. Together, a sequence of `q`
operations costs `O(q α(n))`, where `α` is the inverse Ackermann function.
This is why Kruskal can test cycles without repeatedly searching paths.

## 8. Implementation notes and sanity checks

`spanning_trees.py` includes:

* `DisjointSet`, `connected_components`, and `is_forest`;
* `kruskal` and heap-based `prim`;
* `is_spanning_forest` validation;
* `unique_mst` tie detection;
* demonstrations comparing equal MST weights, a disconnected forest, and a
  triangle with three equal MST choices.

The return value is `(chosen_edges, total_weight)`. An empty graph has weight
zero; an isolated vertex contributes no edge. Parallel edges are accepted,
while self-loops are ignored by the algorithms because they cannot help a
spanning tree.
