"""Small, runnable demonstrations of spanning-tree algorithms.

Run with:
    python3 spanning_trees.py

The implementation uses only the Python standard library and represents an
undirected weighted graph as ``(u, v, weight)`` edge tuples.
"""

from __future__ import annotations

from dataclasses import dataclass
import heapq
from typing import Hashable, Iterable, Sequence

Vertex = Hashable
Edge = tuple[Vertex, Vertex, float]


class DisjointSet:
    """Union-find (DSU) with path compression and union by rank."""

    def __init__(self, items: Iterable[Vertex] = ()) -> None:
        self.parent = {item: item for item in items}
        self.rank = {item: 0 for item in self.parent}

    def find(self, item: Vertex) -> Vertex:
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, left: Vertex, right: Vertex) -> bool:
        root_left, root_right = self.find(left), self.find(right)
        if root_left == root_right:
            return False
        if self.rank[root_left] < self.rank[root_right]:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left
        if self.rank[root_left] == self.rank[root_right]:
            self.rank[root_left] += 1
        return True


def vertices_and_edges(edges: Iterable[Edge], vertices: Iterable[Vertex] = ()) -> tuple[set[Vertex], list[Edge]]:
    edge_list = list(edges)
    vertex_set = set(vertices)
    for left, right, _ in edge_list:
        vertex_set.update((left, right))
    return vertex_set, edge_list


def connected_components(vertices: Iterable[Vertex], edges: Iterable[Edge]) -> list[set[Vertex]]:
    dsu = DisjointSet(vertices)
    for left, right, _ in edges:
        dsu.union(left, right)
    groups: dict[Vertex, set[Vertex]] = {}
    for vertex in dsu.parent:
        groups.setdefault(dsu.find(vertex), set()).add(vertex)
    return list(groups.values())


def kruskal(
    edges: Iterable[Edge], vertices: Iterable[Vertex] = ()
) -> tuple[list[Edge], float]:
    """Return an MST, or a minimum spanning forest if the graph is disconnected."""
    vertex_set, edge_list = vertices_and_edges(edges, vertices)
    dsu = DisjointSet(vertex_set)
    chosen: list[Edge] = []
    total = 0.0
    for left, right, weight in sorted(edge_list, key=lambda edge: edge[2]):
        if dsu.union(left, right):
            chosen.append((left, right, weight))
            total += weight
    return chosen, total


def prim(
    edges: Iterable[Edge], vertices: Iterable[Vertex] = ()
) -> tuple[list[Edge], float]:
    """Return a minimum spanning forest using Prim, restarting per component."""
    vertex_set, edge_list = vertices_and_edges(edges, vertices)
    adjacency: dict[Vertex, list[tuple[float, Vertex, Vertex]]] = {
        vertex: [] for vertex in vertex_set
    }
    for left, right, weight in edge_list:
        adjacency[left].append((weight, left, right))
        adjacency[right].append((weight, right, left))

    visited: set[Vertex] = set()
    chosen: list[Edge] = []
    total = 0.0
    for start in sorted(vertex_set, key=repr):
        if start in visited:
            continue
        visited.add(start)
        heap: list[tuple[float, Vertex, Vertex]] = list(adjacency[start])
        heapq.heapify(heap)
        while heap:
            weight, parent, child = heapq.heappop(heap)
            if child in visited:
                continue
            visited.add(child)
            chosen.append((parent, child, weight))
            total += weight
            for next_weight, _, neighbor in adjacency[child]:
                if neighbor not in visited:
                    heapq.heappush(heap, (next_weight, child, neighbor))
    return chosen, total


def is_forest(vertices: Iterable[Vertex], edges: Iterable[Edge]) -> bool:
    """Check acyclicity, including parallel edges as a 2-cycle."""
    dsu = DisjointSet(vertices)
    for left, right, _ in edges:
        if left == right or not dsu.union(left, right):
            return False
    return True


def is_spanning_forest(
    vertices: Iterable[Vertex], graph_edges: Iterable[Edge], candidate: Iterable[Edge]
) -> bool:
    vertex_set = set(vertices)
    graph_pairs = {frozenset((left, right)) for left, right, _ in graph_edges}
    candidate_list = list(candidate)
    if any(left not in vertex_set or right not in vertex_set for left, right, _ in candidate_list):
        return False
    if any(frozenset((left, right)) not in graph_pairs for left, right, _ in candidate_list):
        return False
    return is_forest(vertex_set, candidate_list) and len(candidate_list) == (
        len(vertex_set) - len(connected_components(vertex_set, graph_edges))
    )


def unique_mst(vertices: Iterable[Vertex], edges: Iterable[Edge]) -> bool:
    """A practical uniqueness test: every equal-weight Kruskal choice is forced.

    Equivalently, for each weight group, contract components formed by lighter
    edges; the graph of equal-weight candidate edges must be acyclic.
    """
    vertex_set, edge_list = vertices_and_edges(edges, vertices)
    dsu = DisjointSet(vertex_set)
    for weight in sorted({edge[2] for edge in edge_list}):
        group = [(u, v) for u, v, w in edge_list if w == weight]
        temporary = DisjointSet(vertex_set)
        for u, v in group:
            ru, rv = dsu.find(u), dsu.find(v)
            if ru != rv and not temporary.union(ru, rv):
                return False
        for u, v in group:
            dsu.union(u, v)
    return True


def demo() -> None:
    vertices = {"A", "B", "C", "D", "E", "F"}
    edges: list[Edge] = [
        ("A", "B", 4), ("A", "C", 2), ("B", "C", 1),
        ("B", "D", 5), ("C", "D", 8), ("C", "E", 10),
        ("D", "E", 2), ("D", "F", 6), ("E", "F", 3),
    ]
    k_edges, k_weight = kruskal(edges, vertices)
    p_edges, p_weight = prim(edges, vertices)
    print("Kruskal:", k_edges, "weight =", k_weight)
    print("Prim:   ", p_edges, "weight =", p_weight)
    assert k_weight == p_weight == 13
    assert is_spanning_forest(vertices, edges, k_edges)
    assert is_spanning_forest(vertices, edges, p_edges)
    assert unique_mst(vertices, edges)

    disconnected = [("A", "B", 1), ("B", "C", 2), ("X", "Y", 4)]
    forest, weight = kruskal(disconnected, {"A", "B", "C", "X", "Y", "Z"})
    assert weight == 7 and len(forest) == 3
    assert is_spanning_forest({"A", "B", "C", "X", "Y", "Z"}, disconnected, forest)
    print("Disconnected minimum spanning forest:", forest, "weight =", weight)

    tied = [("A", "B", 1), ("B", "C", 1), ("A", "C", 1)]
    assert not unique_mst({"A", "B", "C"}, tied)
    print("Sanity tests: all passed")


if __name__ == "__main__":
    demo()
