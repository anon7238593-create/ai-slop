"""Reusable shortest-path algorithms with small runnable demonstrations.

The module uses adjacency lists of ``(neighbor, weight)`` pairs.  Vertices may
be any hashable values, although the examples use strings and integers.
"""

from __future__ import annotations

from collections import deque
from heapq import heappop, heappush
from itertools import count
from math import inf
from typing import Hashable, Iterable, Mapping, Sequence

Vertex = Hashable
WeightedGraph = Mapping[Vertex, Iterable[tuple[Vertex, float]]]
UnweightedGraph = Mapping[Vertex, Iterable[Vertex]]


def _vertices(graph: Mapping[Vertex, Iterable], source: Vertex | None = None) -> set[Vertex]:
    result = set(graph)
    for edges in graph.values():
        for edge in edges:
            result.add(edge[0] if isinstance(edge, tuple) else edge)
    if source is not None:
        result.add(source)
    return result


def reconstruct_path(
    predecessors: Mapping[Vertex, Vertex | None], source: Vertex, target: Vertex
) -> list[Vertex]:
    """Return source-to-target vertices, or [] when target is unreachable."""
    if target != source and target not in predecessors:
        return []
    path: list[Vertex] = []
    current: Vertex | None = target
    seen: set[Vertex] = set()
    while current is not None:
        if current in seen:
            raise ValueError("predecessor mapping contains a cycle")
        seen.add(current)
        path.append(current)
        if current == source:
            return path[::-1]
        current = predecessors.get(current)
    return []


def bfs_shortest_paths(
    graph: UnweightedGraph, source: Vertex
) -> tuple[dict[Vertex, int], dict[Vertex, Vertex | None]]:
    """Shortest hop counts in an unweighted graph."""
    distances = {source: 0}
    predecessors: dict[Vertex, Vertex | None] = {source: None}
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for neighbor in graph.get(vertex, ()):
            if neighbor not in distances:
                distances[neighbor] = distances[vertex] + 1
                predecessors[neighbor] = vertex
                queue.append(neighbor)
    return distances, predecessors


def dijkstra(
    graph: WeightedGraph, source: Vertex
) -> tuple[dict[Vertex, float], dict[Vertex, Vertex | None]]:
    """Single-source shortest paths for graphs with nonnegative weights."""
    distances = {vertex: inf for vertex in _vertices(graph, source)}
    predecessors: dict[Vertex, Vertex | None] = {source: None}
    distances[source] = 0
    sequence = count()
    heap: list[tuple[float, int, Vertex]] = [(0, next(sequence), source)]
    while heap:
        distance, _, vertex = heappop(heap)
        if distance != distances[vertex]:
            continue
        for neighbor, weight in graph.get(vertex, ()):
            if weight < 0:
                raise ValueError("Dijkstra requires nonnegative edge weights")
            candidate = distance + weight
            if candidate < distances.get(neighbor, inf):
                distances[neighbor] = candidate
                predecessors[neighbor] = vertex
                heappush(heap, (candidate, next(sequence), neighbor))
    return distances, predecessors


def bellman_ford(
    graph: WeightedGraph, source: Vertex
) -> tuple[dict[Vertex, float], dict[Vertex, Vertex | None]]:
    """Single-source paths with negative edges; raise on a reachable negative cycle."""
    vertices = _vertices(graph, source)
    edges = [(vertex, neighbor, weight) for vertex in graph for neighbor, weight in graph[vertex]]
    distances = {vertex: inf for vertex in vertices}
    predecessors: dict[Vertex, Vertex | None] = {source: None}
    distances[source] = 0
    for _ in range(max(0, len(vertices) - 1)):
        changed = False
        for vertex, neighbor, weight in edges:
            if distances[vertex] != inf and distances[vertex] + weight < distances[neighbor]:
                distances[neighbor] = distances[vertex] + weight
                predecessors[neighbor] = vertex
                changed = True
        if not changed:
            break
    for vertex, neighbor, weight in edges:
        if distances[vertex] != inf and distances[vertex] + weight < distances[neighbor]:
            raise ValueError("reachable negative-weight cycle")
    return distances, predecessors


def dag_shortest_paths(
    graph: WeightedGraph, source: Vertex, topological_order: Sequence[Vertex] | None = None
) -> tuple[dict[Vertex, float], dict[Vertex, Vertex | None]]:
    """Linear-time shortest paths in a DAG, optionally given a topological order."""
    vertices = _vertices(graph, source)
    if topological_order is None:
        indegree = {vertex: 0 for vertex in vertices}
        for vertex in graph:
            for neighbor, _ in graph[vertex]:
                indegree[neighbor] += 1
        queue = deque(vertex for vertex, degree in indegree.items() if degree == 0)
        order: list[Vertex] = []
        while queue:
            vertex = queue.popleft()
            order.append(vertex)
            for neighbor, _ in graph.get(vertex, ()):
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
        if len(order) != len(vertices):
            raise ValueError("graph is not acyclic")
        topological_order = order
    distances = {vertex: inf for vertex in vertices}
    predecessors: dict[Vertex, Vertex | None] = {source: None}
    distances[source] = 0
    for vertex in topological_order:
        if distances.get(vertex, inf) == inf:
            continue
        for neighbor, weight in graph.get(vertex, ()):
            candidate = distances[vertex] + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                predecessors[neighbor] = vertex
    return distances, predecessors


def floyd_warshall(
    graph: WeightedGraph,
) -> tuple[dict[Vertex, dict[Vertex, float]], dict[Vertex, dict[Vertex, Vertex | None]]]:
    """All-pairs shortest paths; raise when any negative cycle exists."""
    vertices = _vertices(graph)
    distances = {u: {v: inf for v in vertices} for u in vertices}
    next_hop: dict[Vertex, dict[Vertex, Vertex | None]] = {
        u: {v: None for v in vertices} for u in vertices
    }
    for vertex in vertices:
        distances[vertex][vertex] = 0
        next_hop[vertex][vertex] = vertex
    for vertex in graph:
        for neighbor, weight in graph[vertex]:
            if weight < distances[vertex][neighbor]:
                distances[vertex][neighbor] = weight
                next_hop[vertex][neighbor] = neighbor
    for middle in vertices:
        for start in vertices:
            if distances[start][middle] == inf:
                continue
            for end in vertices:
                candidate = distances[start][middle] + distances[middle][end]
                if candidate < distances[start][end]:
                    distances[start][end] = candidate
                    next_hop[start][end] = next_hop[start][middle]
    if any(distances[vertex][vertex] < 0 for vertex in vertices):
        raise ValueError("negative-weight cycle")
    return distances, next_hop


def reconstruct_floyd_path(
    next_hop: Mapping[Vertex, Mapping[Vertex, Vertex | None]], start: Vertex, target: Vertex
) -> list[Vertex]:
    if next_hop.get(start, {}).get(target) is None:
        return []
    path = [start]
    while start != target:
        start = next_hop[start][target]  # type: ignore[assignment]
        path.append(start)
        if len(path) > len(next_hop) + 1:
            raise ValueError("next-hop mapping contains a cycle")
    return path


def demo() -> None:
    unweighted = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    distances, predecessors = bfs_shortest_paths(unweighted, "A")
    assert distances["D"] == 2
    assert reconstruct_path(predecessors, "A", "D") in (["A", "B", "D"], ["A", "C", "D"])
    weighted = {"A": [("B", 4), ("C", 1)], "C": [("B", 2), ("D", 5)], "B": [("D", 1)], "D": []}
    distances, predecessors = dijkstra(weighted, "A")
    assert distances["D"] == 4 and reconstruct_path(predecessors, "A", "D") == ["A", "C", "B", "D"]
    negative = {"A": [("B", 4), ("C", 5)], "B": [("C", -3)], "C": []}
    assert bellman_ford(negative, "A")[0]["C"] == 1
    dag = {"A": [("B", 2), ("C", 6)], "B": [("C", -1)], "C": []}
    assert dag_shortest_paths(dag, "A")[0]["C"] == 1
    all_pairs, next_hop = floyd_warshall(weighted)
    assert all_pairs["A"]["D"] == 4
    assert reconstruct_floyd_path(next_hop, "A", "D") == ["A", "C", "B", "D"]
    assert bfs_shortest_paths({"A": []}, "A")[0] == {"A": 0}
    try:
        dijkstra({"A": [("B", -1)]}, "A")
    except ValueError:
        pass
    else:
        raise AssertionError("negative Dijkstra edge was not rejected")
    try:
        bellman_ford({"A": [("B", 1)], "B": [("A", -2)]}, "A")
    except ValueError:
        pass
    else:
        raise AssertionError("negative cycle was not detected")
    print("All shortest-path demonstrations passed.")


if __name__ == "__main__":
    demo()
