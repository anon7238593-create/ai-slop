"""Standard-library max-flow and bipartite matching examples.

Run this file directly for a small demonstration, or import the functions in
``test_flow_matching.py``.
"""
from collections import deque
from math import inf


def _residual(capacity):
    """Return a fresh residual matrix with all missing arcs represented as 0."""
    vertices = set(capacity)
    for edges in capacity.values():
        vertices.update(edges)
    residual = {u: {v: 0 for v in vertices} for u in vertices}
    for u, edges in capacity.items():
        for v, value in edges.items():
            if value < 0:
                raise ValueError("capacities must be non-negative")
            residual[u][v] += value
    return residual


def _find_path(residual, source, sink, strategy="bfs"):
    """Find a positive-residual source-to-sink path and its bottleneck."""
    parent = {source: None}
    frontier = [source] if strategy == "dfs" else deque([source])
    while frontier:
        u = frontier.pop() if strategy == "dfs" else frontier.popleft()
        for v, remaining in residual[u].items():
            if remaining > 0 and v not in parent:
                parent[v] = u
                if v == sink:
                    path = []
                    x = sink
                    bottleneck = inf
                    while parent[x] is not None:
                        p = parent[x]
                        path.append((p, x))
                        bottleneck = min(bottleneck, residual[p][x])
                        x = p
                    return list(reversed(path)), bottleneck
                frontier.append(v)
    return [], 0


def max_flow(capacity, source, sink, strategy="bfs"):
    """Compute max flow and return ``(value, flow, residual)``.

    ``strategy='dfs'`` is Ford--Fulkerson's generic path selection;
    ``strategy='bfs'`` is Edmonds--Karp. The input is never mutated.
    """
    if source == sink:
        raise ValueError("source and sink must differ")
    if strategy not in {"bfs", "dfs"}:
        raise ValueError("strategy must be 'bfs' or 'dfs'")
    residual = _residual(capacity)
    if source not in residual or sink not in residual:
        raise KeyError("source and sink must occur in the network")
    flow = {u: {v: 0 for v in residual} for u in residual}
    value = 0
    while True:
        path, amount = _find_path(residual, source, sink, strategy)
        if not path:
            break
        value += amount
        for u, v in path:
            residual[u][v] -= amount
            residual[v][u] += amount
            # A reverse residual edge cancels earlier flow; otherwise this is
            # an original forward edge (or a harmless zero-flow extra edge).
            if capacity.get(u, {}).get(v, 0):
                flow[u][v] += amount
            elif flow[v][u]:
                flow[v][u] -= amount
    return value, flow, residual


def min_cut(capacity, source, sink, strategy="bfs"):
    """Return ``(max_flow_value, source_side, sink_side, flow)``."""
    value, flow, residual = max_flow(capacity, source, sink, strategy)
    reachable = {source}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v, remaining in residual[u].items():
            if remaining > 0 and v not in reachable:
                reachable.add(v)
                queue.append(v)
    return value, reachable, set(residual) - reachable, flow


def bipartite_matching(left, right, edges):
    """Return a maximum matching as ``{left_vertex: right_vertex}``.

    This is a max-flow reduction: source -> left (1), allowed pairs (1),
    right -> sink (1). Vertex names may be any hashable values.
    """
    source, sink = object(), object()
    capacity = {source: {}, sink: {}}
    for u in left:
        capacity[source][u] = 1
        capacity.setdefault(u, {})
    for v in right:
        capacity.setdefault(v, {})[sink] = 1
    right_set = set(right)
    for u, v in edges:
        if u not in set(left) or v not in right_set:
            raise ValueError("matching edge must connect left to right")
        capacity[u][v] = 1
        capacity.setdefault(v, {})
    _, flow, _ = max_flow(capacity, source, sink, strategy="bfs")
    return {u: v for u in left for v in right if flow.get(u, {}).get(v, 0) == 1}


if __name__ == "__main__":
    network = {
        "s": {"a": 3, "b": 2}, "a": {"b": 1, "c": 2},
        "b": {"c": 2, "d": 3}, "c": {"t": 2}, "d": {"t": 3}, "t": {},
    }
    value, source_side, sink_side, _ = min_cut(network, "s", "t")
    print(f"max flow = {value}; min-cut sides = {source_side} | {sink_side}")
    print("matching =", bipartite_matching("ABC", {1, 2, 3}, [("A", 1), ("A", 2), ("B", 2), ("C", 2), ("C", 3)]))
