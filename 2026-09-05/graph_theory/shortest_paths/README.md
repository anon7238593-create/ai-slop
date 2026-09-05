# Shortest paths

Shortest-path modeling starts by making the state space explicit. A vertex is
an object or state, and a directed edge is one legal transition. An edge
weight is the cost, time, distance, risk, or other quantity being minimized.
For an undirected graph, store both directions. Decide whether parallel edges
and self-loops are meaningful, and include isolated vertices when their
unreachable status matters.

The reusable implementations in `shortest_paths.py` use adjacency lists:

```python
graph = {"A": [("B", 3), ("C", 1)], "B": [("D", 2)], "C": [("D", 5)], "D": []}
```

Run the built-in experiments with:

```bash
python3 shortest_paths.py
```

## Choosing an algorithm

| Situation | Algorithm | Typical complexity |
|---|---|---|
| Unweighted (or every edge costs one) | BFS | `O(V + E)` |
| Weighted, all weights nonnegative | Dijkstra with a binary heap | `O((V + E) log V)` |
| Negative edges, but no reachable negative cycle | Bellman–Ford | `O(VE)` |
| DAG, including negative edges | Topological-order relaxation | `O(V + E)` |
| Distances between every pair | Floyd–Warshall | `O(V^3)` time, `O(V^2)` space |

`V` is the number of vertices and `E` the number of directed edges. The
adjacency-list implementations do not need a dense matrix, except
Floyd–Warshall, which intentionally creates one.

## BFS for unweighted graphs

BFS explores a source's frontier in layers. The first time it discovers a
vertex, it has found a path with the fewest edges: every earlier layer is
closer, and the queue processes layers in order. Store `distance[v]` and a
predecessor to reconstruct one shortest path. Missing dictionary entries mean
unreachable vertices; the source has distance zero.

For 0/1 edge weights, a related specialized technique is 0–1 BFS using a
deque. Ordinary BFS is correct only when every transition has the same cost
(or when the graph has deliberately been expanded to model costs).

## Dijkstra

Dijkstra repeatedly finalizes the unsettled vertex with smallest tentative
distance, then relaxes its outgoing edges. Relaxation asks whether
`distance[u] + w(u,v)` improves `distance[v]`. Nonnegative weights make the
greedy choice safe: a later route through any unsettled vertex cannot reduce a
finalized value. The implementation uses stale heap entries rather than a
decrease-key operation, which is simpler and still has the stated bound.

It must not be used with negative edges. The script explicitly raises
`ValueError` rather than silently returning a potentially wrong answer.

## Bellman–Ford and negative cycles

After at most `V - 1` edges, every simple shortest path has been considered.
Bellman–Ford scans every edge that many times, relaxing improvements. An extra
scan that still improves an edge proves a negative cycle reachable from the
source. Such a cycle makes the minimum cost undefined (`-infinity`) for every
vertex reachable after the cycle. Unreachable negative cycles do not affect a
single-source run.

Bellman–Ford supports negative edges, but not a meaningful finite answer for
paths whose cost can decrease forever. The implementation reports a reachable
negative cycle.

## DAG shortest paths

A DAG has a topological order in which every edge points forward. Once a
vertex is processed in that order, all possible predecessors have already
been processed, so one relaxation pass is enough. This remains correct with
negative edge weights because acyclicity, rather than nonnegativity, supplies
the ordering argument. The function can accept an order or compute one and
reject cyclic input.

## Floyd–Warshall

Floyd–Warshall maintains `d[i][j]`, initially zero for `i == j`, direct-edge
weights, and infinity otherwise. At iteration `k`, it permits vertices
`0..k` as intermediate vertices:

`d[i][j] = min(d[i][j], d[i][k] + d[k][j])`.

The invariant is that the table contains the best route with only processed
intermediates. A negative diagonal entry after the algorithm indicates a
negative cycle. The implementation also stores a `next_hop` table so paths
can be reconstructed, and returns an empty path for unreachable pairs.

## Reconstruction and edge cases

Single-source algorithms return predecessor maps. Follow predecessors from the
target back to the source and reverse the result; `reconstruct_path` returns
`[]` for an unreachable target and detects malformed predecessor cycles.
Floyd–Warshall instead stores the first next vertex and uses
`reconstruct_floyd_path`.

Important cases covered by the runnable demo include an isolated source,
unreachable vertices, tied shortest routes, zero-weight edges, negative edges,
negative-cycle rejection, and rejection of negative edges by Dijkstra.
Floating-point weights are accepted, but integer costs are preferable when
exact equality is important. A graph with no edges still gives a source
distance of zero.
