# Flow networks, cuts, and matching

A **flow network** is a directed graph with a source `s`, sink `t`, and a non-negative capacity `c(u,v)` on each directed edge. A feasible flow `f` obeys:

1. **Capacity:** `0 <= f(u,v) <= c(u,v)`.
2. **Conservation:** every vertex other than `s` and `t` has equal inflow and outflow.
3. **Value:** `|f|` is the net flow leaving `s` (equivalently entering `t`).

The practical goal is to route as much material, bandwidth, traffic, or work as possible from `s` to `t` without exceeding any bottleneck.

The accompanying `flow_matching.py` uses only the Python standard library. Its graph representation is a nested dictionary: `{"u": {"v": capacity}}`. Vertices that have no outgoing edges should still appear with an empty dictionary.

## Residual graphs: the key idea

After sending flow, an edge has two kinds of remaining freedom:

- forward residual capacity `c(u,v) - f(u,v)`, which allows more flow;
- reverse residual capacity `f(u,v)`, which allows us to **undo** flow and reroute it elsewhere.

The residual graph records both. A residual edge is not necessarily an original edge: a reverse edge exists precisely because an earlier choice sent flow forward. This ability to cancel earlier choices is why augmenting algorithms can recover from a locally poor route.

A flow is maximum exactly when the residual graph has no `s`-to-`t` path. An `s`-to-`t` residual path is an **augmenting path**. Its bottleneck is the smallest residual capacity on the path; adding that bottleneck preserves feasibility and increases the flow value.

### Tiny example

Suppose `s -> a` has capacity 4 and `a -> t` has capacity 2. The first augmentation sends 2 and saturates `a -> t`. The residual graph contains `a -> s` with capacity 2 and `t -> a` with capacity 2. If another route later makes it desirable to stop using `s -> a`, the reverse residual edge `a -> s` can cancel that choice. Always include reverse residual edges; omitting them is a common incorrect implementation.

## Ford–Fulkerson and Edmonds–Karp

**Ford–Fulkerson** repeatedly finds any augmenting path and augments by its bottleneck. With integer capacities it terminates and returns an integral maximum flow. With arbitrary real capacities, careless path choices can lead to very slow convergence (and pathological irrational examples can fail to terminate).

**Edmonds–Karp** is Ford–Fulkerson with breadth-first search, so it always selects a path with the fewest edges. Its running time is `O(V E^2)`, independent of the sizes of integer capacities. The implementation exposes both choices:

```python
from flow_matching import max_flow

value, flow, residual = max_flow(network, "s", "t", strategy="bfs")  # Edmonds–Karp
value2, _, _ = max_flow(network, "s", "t", strategy="dfs")            # Ford–Fulkerson style
```

For production-scale or floating-point work, consider a tested library and explicit numeric tolerances. The example implementation assumes exact, non-negative numeric capacities.

## Max-flow/min-cut theorem

For any partition `(S, T)` of the vertices with `s in S` and `t in T`, the cut capacity is

`cap(S,T) = sum(c(u,v) for u in S, v in T)`.

Every feasible flow has value at most every cut capacity: flow crossing from `S` to `T` must be balanced by flow crossing back, so it cannot exceed the forward capacity. The **max-flow/min-cut theorem** says equality is achievable: maximum flow value equals the minimum cut capacity.

After max flow, mark all vertices reachable from `s` in the residual graph. Those vertices form `S`; the rest form `T`. Every crossing edge is saturated, and its capacity is a certificate of optimality. In code:

```python
from flow_matching import min_cut
value, S, T, flow = min_cut(network, "s", "t")
print(value, S, T)
```

A cut is often more informative than a flow: it identifies the bottleneck resource (a server link, staffing limit, or quota) that prevents improvement.

## Reduction: bipartite matching to flow

Given left vertices `L`, right vertices `R`, and allowed pairs `E`, a matching chooses edges so that no vertex is used twice. Build a network:

1. Add `s -> u` with capacity 1 for every `u in L`.
2. Add `u -> v` with capacity 1 for each allowed pair `(u,v)`.
3. Add `v -> t` with capacity 1 for every `v in R`.

An integral flow of value `k` corresponds to `k` matched pairs. Integrality follows because all capacities are integers and augmentations use integer bottlenecks. The source and sink edges enforce “at most one” use on each endpoint.

```python
from flow_matching import bipartite_matching

pairs = [("Alice", "database"), ("Alice", "web"),
         ("Bea", "web"), ("Chen", "mobile")]
matching = bipartite_matching(["Alice", "Bea", "Chen"],
                              ["database", "web", "mobile"], pairs)
# one possible result: {'Alice': 'database', 'Bea': 'web', 'Chen': 'mobile'}
```

The reduction also handles unequal side sizes and disconnected vertices. A maximum matching need not be unique; tests should verify cardinality and validity, not a particular pairing.

## Modeling pitfalls and defensive checks

### Direction and capacity

An edge is directed. Capacity `u -> v` does not imply capacity `v -> u`; if both directions are allowed, add both explicitly. Do not use a single undirected edge unless the problem truly means a shared two-way resource (which needs a different model).

### Conservation exceptions

Only `s` and `t` may create or consume net flow. If a story has supplies, demands, multiple sources, or multiple sinks, add a super-source/super-sink and capacity edges. For lower bounds or exact demands, transform the problem carefully rather than silently violating conservation.

### “At most” versus “exactly”

A capacity is an upper bound. Max flow may leave capacity unused. To require an exact amount, first check feasibility (or add lower-bound constraints); do not assume max flow will fill every edge. Similarly, a matching maximizes cardinality but does not automatically satisfy preferences or fairness objectives.

### Parallel edges and aggregation

The nested-dictionary representation has one capacity per ordered pair. If the input contains parallel edges, aggregate their capacities or assign distinct intermediate vertices. Accidentally overwriting one edge loses capacity.

### Zero and negative capacities

Zero-capacity edges are harmless but unnecessary. Negative capacities have no physical interpretation and are rejected by the implementation. Keep numeric types consistent; mixing floating point and exact integer reasoning can make “zero residual” comparisons fragile.

### Vertex identity

Use unique, hashable labels. In reductions, avoid naming a real vertex `s` or `t`; the implementation uses private object sentinels for this reason. If serializing graphs, choose a collision-proof naming scheme for super-nodes.

### Inspect certificates

Do not trust only the returned number. For a flow, check capacity and conservation. For optimality, inspect the residual graph or verify that the reported cut has the same capacity. For matching, check that every pair is an allowed edge and that no endpoint repeats.

## Running the examples

From this directory:

```bash
python flow_matching.py
python -m unittest -v
```

The tests cover both path-selection strategies, input immutability, a min-cut certificate, matching cardinality/uniqueness constraints, and invalid capacities/edges. The code is intentionally compact for learning; its asymptotic behavior is Edmonds–Karp-style when `strategy="bfs"` and it does not implement min-cost flow, lower bounds, or capacity scaling.
