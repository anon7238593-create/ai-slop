# Graph Traversals in Python: BFS, DFS, and What They Enable

This tutorial develops graph traversal from first principles and turns the
ideas into reusable, standard-library-only Python. The companion
[`traversals.py`](traversals.py) is executable:

```bash
python traversals.py
```

It prints representative results and runs assertions as a tiny smoke-test
suite. A graph is represented as an adjacency mapping, such as
`{"A": ["B", "C"], "B": ["A"]}`. Vertices can be any hashable Python values.
Neighbors may be lists, tuples, sets, or generators (the functions consume
each iterable once).

## 1. The shared traversal model

Both BFS and DFS maintain a **discovered/visited** set. On first discovering a
vertex `v` from `u`, record `parent[v] = u`. The parent links form a traversal
tree (or a forest when we restart from multiple roots), and prevent revisiting
cycles.

For a graph with `V` vertices and `E` adjacency entries, a traversal costs
`O(V + E)` time and `O(V)` auxiliary space. This assumes adjacency lists; an
adjacency matrix would make scanning neighbors much more expensive.

## 2. Breadth-first search (BFS)

BFS explores in layers: distance 0, then distance 1, then distance 2, and so
on. A FIFO queue is the essential data structure.

```text
discover start; distance[start] = 0
while queue is not empty:
    u = queue.pop_left()
    for v in neighbors(u):
        if v is undiscovered:
            parent[v] = u
            distance[v] = distance[u] + 1
            enqueue v
```

`bfs()` returns `(order, parent, distance)`. In an unweighted graph,
`distance[v]` is the shortest number of edges from the start to `v`. The
parent tree gives one shortest path:

```python
order, parent, distance = bfs(graph, "A")
path = reconstruct_path(parent, "E")
```

If `E` is unreachable, it is absent from `parent` and the path is `[]`.
Neighbor ordering determines which equally short path is selected, but not the
distance.

### BFS applications

* shortest paths in unweighted networks (links, roads, social graphs);
* level-order processing and “within *k* hops” queries;
* flood fill, maze solving, and multi-source propagation;
* testing bipartiteness by alternating colors;
* Kahn's topological-sort algorithm (BFS over indegrees).

## 3. Depth-first search (DFS)

DFS follows one branch as far as possible before backtracking. The only
algorithmic difference is the worklist: a LIFO stack, either explicit or the
Python call stack.

### Iterative DFS

`dfs_iterative()` uses a list as a stack. It marks a vertex when pushing it,
which ensures each vertex is pushed once. Reversing the neighbor list makes
the demo's output resemble recursive DFS; ordering is otherwise not
significant.

Iterative DFS is preferable for very deep or adversarial graphs because it
does not hit Python's recursion limit.

### Recursive DFS and timestamps

`dfs_recursive()` records:

* `discovered[v]` (also called entry or **discovery** time), when `v` is first
  entered;
* `finished[v]` (exit time), after all descendants have been processed.

For every reached vertex, `discovered[v] < finished[v]`. DFS intervals are
nested: if `u` is an ancestor of `v`, then
`discovered[u] < discovered[v] < finished[v] < finished[u]`.
Timestamps support edge classification, cycle detection, topological sorting,
and ancestor queries. Recursive Python code is clear but usually safe only
when the graph depth is comfortably below the interpreter recursion limit.

## 4. Parent trees and path reconstruction

Parent pointers are not necessarily a unique tree: different neighbor
orders produce different valid trees. They are compact (`O(V)`) and useful for
reconstructing a route after the traversal:

```python
def reconstruct_path(parent, target):
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    return list(reversed(path))
```

The implementation returns an empty path for an unknown target and raises a
`KeyError` for a bad BFS/DFS start vertex, making input mistakes visible.

## 5. Cycle detection

### Undirected graphs

During DFS, an already-visited neighbor is a cycle edge unless it is the
vertex we came from (the parent). `has_cycle_undirected()` applies this rule
component by component. For an undirected edge, store both directions:
`u -> v` and `v -> u`.

### Directed graphs

Use three colors:

* **white**: not discovered;
* **gray**: discovered but not finished (on the active recursion stack);
* **black**: finished.

A directed edge to gray is a back edge and proves a cycle. This is implemented
by `has_cycle_directed()`. Do not use the undirected “ignore parent” rule on a
directed graph.

## 6. Bipartite graphs

A graph is bipartite exactly when its vertices can be split into two sets such
that every edge crosses between sets. BFS/DFS can assign colors `0` and `1`;
every neighbor must receive the opposite color. If an edge joins equal
colors, an odd cycle exists and the graph is not bipartite.

`bipartite_coloring()` returns a coloring dictionary, or `None` for failure.
It starts a fresh search at every unvisited vertex, so disconnected graphs are
handled correctly.

## 7. Connected components

For an undirected graph, run a traversal from an arbitrary unvisited root,
collect its reached vertices, remove them, and repeat. The resulting sets are
the connected components.

`connected_components()` also treats a directed graph as an undirected graph
for **weak** components: each directed edge is temporarily made bidirectional.
This is different from strongly connected components, which require a separate
algorithm such as Kosaraju or Tarjan.

## 8. Topological sorting

A topological order of a directed acyclic graph (DAG) places every edge
`u -> v` with `u` before `v`. `topological_sort()` uses Kahn's algorithm:

1. Compute each vertex's indegree.
2. Queue all zero-indegree vertices.
3. Remove one, append it to the order, and decrement its neighbors.
4. Newly zero-indegree vertices join the queue.

If fewer than `V` vertices are output, a directed cycle prevented progress and
the function raises `ValueError`. The result is not unique. Typical uses are
build systems, package installation, course prerequisites, spreadsheet
dependencies, and task scheduling. DFS finish times provide another
topological-sort implementation: reverse finish order, while rejecting
back-edges.

## 9. Choosing BFS or DFS

| Need | Prefer |
| --- | --- |
| Shortest edge-count path | BFS |
| Layer/level information | BFS |
| Low memory on a narrow graph | DFS |
| Deep graph without recursion risk | Iterative DFS |
| Entry/exit intervals and edge classification | DFS |
| Components or reachability | Either |
| Bipartiteness | Either (this module uses BFS) |
| DAG ordering | Kahn BFS or DFS timestamps |

For weighted shortest paths, ordinary BFS is not enough: use Dijkstra for
nonnegative weights or Bellman–Ford when negative edges are allowed. Traversal
only answers reachability and unweighted distance questions.

## 10. Running the examples

From this directory:

```bash
python traversals.py
```

The demo covers shortest paths, both DFS forms, timestamps, undirected and
directed cycles, bipartite/non-bipartite examples, disconnected components,
and a DAG topological order. All algorithms are importable without installing
anything:

```python
from traversals import bfs, connected_components, topological_sort
```

For production callers, keep adjacency mappings explicit and decide whether
missing isolated vertices should be represented as `{vertex: []}`. The
implementation accepts isolated vertices that appear only as keys or only in
neighbor lists, and it does not mutate the caller's graph.
