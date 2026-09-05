"""Small, runnable graph-theory explorations using only the Python standard library."""

from __future__ import annotations

import argparse
import math
import random
from collections import deque
from typing import Dict, Hashable, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

Vertex = Hashable
Edge = Tuple[Vertex, Vertex]


def connected_vertices(graph: Mapping[Vertex, Set[Vertex]]) -> Set[Vertex]:
    nonempty = {v for v, ns in graph.items() if ns}
    if not nonempty:
        return set()
    seen = {next(iter(nonempty))}
    queue = deque(seen)
    while queue:
        v = queue.popleft()
        for w in graph[v]:
            if w not in seen:
                seen.add(w)
                queue.append(w)
    return seen


def eulerian_trail(edges: Iterable[Edge]) -> Optional[List[Vertex]]:
    """Return an Euler trail for an undirected multigraph, or None.

    Parallel edges are supported because adjacency entries carry edge IDs.
    """
    adjacency: Dict[Vertex, List[Tuple[int, Vertex]]] = {}
    edge_list = list(edges)
    for edge_id, (a, b) in enumerate(edge_list):
        adjacency.setdefault(a, []).append((edge_id, b))
        adjacency.setdefault(b, []).append((edge_id, a))
    if not edge_list:
        return []
    active = {v for v, ns in adjacency.items() if ns}
    start_seen = {next(iter(active))}
    queue = deque(start_seen)
    while queue:
        v = queue.popleft()
        for _, w in adjacency[v]:
            if w not in start_seen:
                start_seen.add(w)
                queue.append(w)
    if start_seen != active:
        return None
    odd = [v for v, ns in adjacency.items() if len(ns) % 2]
    if len(odd) not in (0, 2):
        return None
    start = odd[0] if odd else next(iter(active))
    used: Set[int] = set()
    stack = [start]
    trail: List[Vertex] = []
    while stack:
        v = stack[-1]
        while adjacency[v] and adjacency[v][-1][0] in used:
            adjacency[v].pop()
        if adjacency[v]:
            edge_id, w = adjacency[v].pop()
            if edge_id not in used:
                used.add(edge_id)
                stack.append(w)
        else:
            trail.append(stack.pop())
    trail.reverse()
    return trail if len(used) == len(edge_list) else None


def hamiltonian_path(graph: Mapping[Vertex, Set[Vertex]], start: Optional[Vertex] = None) -> Optional[List[Vertex]]:
    vertices = list(graph)
    if not vertices:
        return []
    starts = [start] if start is not None else vertices
    for first in starts:
        if first not in graph:
            continue
        path = [first]
        used = {first}

        def search(v: Vertex) -> bool:
            if len(path) == len(vertices):
                return True
            candidates = sorted((w for w in graph[v] if w not in used),
                                key=lambda w: sum(x not in used for x in graph[w]))
            for w in candidates:
                used.add(w)
                path.append(w)
                if search(w):
                    return True
                path.pop()
                used.remove(w)
            return False

        if search(first):
            return path
    return None


def greedy_coloring(graph: Mapping[Vertex, Set[Vertex]]) -> Dict[Vertex, int]:
    order = sorted(graph, key=lambda v: len(graph[v]), reverse=True)
    colors: Dict[Vertex, int] = {}
    for v in order:
        forbidden = {colors[w] for w in graph[v] if w in colors}
        color = 0
        while color in forbidden:
            color += 1
        colors[v] = color
    return colors


def random_graph(n: int, p: float, rng: random.Random) -> Dict[int, Set[int]]:
    graph = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                graph[i].add(j)
                graph[j].add(i)
    return graph


def degree_centrality(graph: Mapping[Vertex, Set[Vertex]]) -> Dict[Vertex, float]:
    denominator = max(1, len(graph) - 1)
    return {v: len(graph[v]) / denominator for v in graph}


def closeness_centrality(graph: Mapping[Vertex, Set[Vertex]]) -> Dict[Vertex, float]:
    result: Dict[Vertex, float] = {}
    for source in graph:
        distances = {source: 0}
        queue = deque([source])
        while queue:
            v = queue.popleft()
            for w in graph[v]:
                if w not in distances:
                    distances[w] = distances[v] + 1
                    queue.append(w)
        total = sum(distances.values())
        result[source] = (len(distances) - 1) / total if total else 0.0
    return result


def pagerank(graph: Mapping[Vertex, Set[Vertex]], damping: float = 0.85,
             tolerance: float = 1e-10, max_iter: int = 200) -> Dict[Vertex, float]:
    vertices = list(graph)
    n = len(vertices)
    if not n:
        return {}
    rank = {v: 1.0 / n for v in vertices}
    for _ in range(max_iter):
        next_rank = {v: (1 - damping) / n for v in vertices}
        dangling = sum(rank[v] for v in vertices if not graph[v])
        for v in vertices:
            share = rank[v] / len(graph[v]) if graph[v] else 0.0
            for w in graph[v]:
                next_rank[w] += damping * share
        for v in vertices:
            next_rank[v] += damping * dangling / n
        delta = sum(abs(next_rank[v] - rank[v]) for v in vertices)
        rank = next_rank
        if delta < tolerance:
            break
    return rank


def power_iteration(matrix: Sequence[Sequence[float]], iterations: int = 100) -> Tuple[float, List[float]]:
    n = len(matrix)
    vector = [1.0 / math.sqrt(n)] * n
    eigenvalue = 0.0
    for _ in range(iterations):
        product = [sum(matrix[i][j] * vector[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(x * x for x in product))
        if norm == 0:
            return 0.0, vector
        vector = [x / norm for x in product]
        eigenvalue = sum(vector[i] * sum(matrix[i][j] * vector[j] for j in range(n)) for i in range(n))
    return eigenvalue, vector


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=3)
    parser.add_argument("--random-trials", type=int, default=50)
    args = parser.parse_args()
    trail = eulerian_trail([("a", "b"), ("b", "c"), ("c", "a"), ("a", "d"), ("d", "b")])
    assert trail and len(trail) == 6
    graph = {"a": {"b", "c"}, "b": {"a", "c", "d"}, "c": {"a", "b", "d"}, "d": {"b", "c"}}
    path = hamiltonian_path(graph)
    assert path and len(path) == len(graph)
    coloring = greedy_coloring(graph)
    assert all(coloring[v] != coloring[w] for v in graph for w in graph[v])
    rng = random.Random(args.seed)
    samples = [sum(len(ns) for ns in random_graph(20, 0.12, rng).values()) // 2
               for _ in range(args.random_trials)]
    print("Euler trail:", trail)
    print("Hamiltonian path:", path)
    print("Greedy colors:", coloring, f"({max(coloring.values()) + 1} colors)")
    print("Random G(20, .12) mean edges:", round(sum(samples) / len(samples), 2))
    print("Degree centrality:", degree_centrality(graph))
    print("Closeness:", closeness_centrality(graph))
    print("PageRank:", {v: round(x, 4) for v, x in pagerank(graph).items()})
    matrix = [[0, 1, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 1, 0]]
    print("Dominant adjacency eigenvalue estimate:", round(power_iteration(matrix)[0], 5))


if __name__ == "__main__":
    main()
