"""Reusable graph-traversal algorithms using only the Python standard library.

Run ``python traversals.py`` for a small demonstration and assertion-based test
suite.  Graphs are adjacency mappings: ``{vertex: iterable_of_neighbors}``.
Vertices only need to be hashable.
"""

from collections import deque
from dataclasses import dataclass
from typing import Hashable, Iterable, Mapping, TypeVar

Vertex = TypeVar("Vertex", bound=Hashable)
Graph = Mapping[Vertex, Iterable[Vertex]]


@dataclass(frozen=True)
class BFSStep:
    """A snapshot of BFS immediately before processing one queue item."""

    step: int
    current: Vertex
    queue: tuple[Vertex, ...]
    discovered: frozenset[Vertex]
    parent: dict[Vertex, Vertex | None]


def _vertices(graph: Graph[Vertex]) -> set[Vertex]:
    vertices = set(graph)
    for neighbors in graph.values():
        vertices.update(neighbors)
    return vertices


def bfs(graph: Graph[Vertex], start: Vertex) -> tuple[list[Vertex], dict[Vertex, Vertex | None], dict[Vertex, int]]:
    """Return BFS order, parent tree, and shortest unweighted distances."""
    if start not in _vertices(graph):
        raise KeyError(f"unknown start vertex: {start!r}")
    order: list[Vertex] = []
    parent: dict[Vertex, Vertex | None] = {start: None}
    distance: dict[Vertex, int] = {start: 0}
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        for neighbor in graph.get(vertex, ()):
            if neighbor not in parent:
                parent[neighbor] = vertex
                distance[neighbor] = distance[vertex] + 1
                queue.append(neighbor)
    return order, parent, distance


def bfs_trace(
    graph: Graph[Vertex], start: Vertex
) -> tuple[list[BFSStep], list[Vertex], dict[Vertex, Vertex | None], dict[Vertex, int]]:
    """Return BFS snapshots as well as the ordinary BFS results.

    Each snapshot is captured immediately before its ``current`` vertex is
    expanded. The snapshot copies are safe for visualization or later
    inspection and do not expose BFS's mutable internal state.
    """
    if start not in _vertices(graph):
        raise KeyError(f"unknown start vertex: {start!r}")
    steps: list[BFSStep] = []
    order: list[Vertex] = []
    parent: dict[Vertex, Vertex | None] = {start: None}
    distance: dict[Vertex, int] = {start: 0}
    queue = deque([start])
    step_number = 0
    while queue:
        vertex = queue.popleft()
        steps.append(
            BFSStep(
                step=step_number,
                current=vertex,
                queue=tuple(queue),
                discovered=frozenset(parent),
                parent=dict(parent),
            )
        )
        step_number += 1
        order.append(vertex)
        for neighbor in graph.get(vertex, ()):
            if neighbor not in parent:
                parent[neighbor] = vertex
                distance[neighbor] = distance[vertex] + 1
                queue.append(neighbor)
    return steps, order, parent, distance


def dfs_iterative(graph: Graph[Vertex], start: Vertex) -> tuple[list[Vertex], dict[Vertex, Vertex | None]]:
    """Depth-first preorder and parent tree, implemented with an explicit stack."""
    if start not in _vertices(graph):
        raise KeyError(f"unknown start vertex: {start!r}")
    order: list[Vertex] = []
    parent: dict[Vertex, Vertex | None] = {start: None}
    stack = [start]
    while stack:
        vertex = stack.pop()
        order.append(vertex)
        neighbors = list(graph.get(vertex, ()))
        for neighbor in reversed(neighbors):
            if neighbor not in parent:
                parent[neighbor] = vertex
                stack.append(neighbor)
    return order, parent


def dfs_recursive(graph: Graph[Vertex], start: Vertex) -> tuple[list[Vertex], dict[Vertex, Vertex | None], dict[Vertex, int], dict[Vertex, int]]:
    """Depth-first preorder, parents, discovery timestamps, and finish timestamps."""
    if start not in _vertices(graph):
        raise KeyError(f"unknown start vertex: {start!r}")
    order: list[Vertex] = []
    parent: dict[Vertex, Vertex | None] = {start: None}
    discovered: dict[Vertex, int] = {}
    finished: dict[Vertex, int] = {}
    clock = 0

    def visit(vertex: Vertex) -> None:
        nonlocal clock
        clock += 1
        discovered[vertex] = clock
        order.append(vertex)
        for neighbor in graph.get(vertex, ()):
            if neighbor not in discovered:
                parent[neighbor] = vertex
                visit(neighbor)
        clock += 1
        finished[vertex] = clock

    visit(start)
    return order, parent, discovered, finished


def reconstruct_path(parent: Mapping[Vertex, Vertex | None], target: Vertex) -> list[Vertex]:
    """Reconstruct root-to-target path from a parent mapping."""
    if target not in parent:
        return []
    path = []
    current: Vertex | None = target
    while current is not None:
        path.append(current)
        current = parent[current]
    return list(reversed(path))


def has_cycle_undirected(graph: Graph[Vertex]) -> bool:
    """Detect a cycle in an undirected graph (each edge normally appears twice)."""
    seen: set[Vertex] = set()

    def visit(vertex: Vertex, parent: Vertex | None) -> bool:
        seen.add(vertex)
        for neighbor in graph.get(vertex, ()):
            if neighbor not in seen:
                if visit(neighbor, vertex):
                    return True
            elif neighbor != parent:
                return True
        return False

    return any(vertex not in seen and visit(vertex, None) for vertex in _vertices(graph))


def has_cycle_directed(graph: Graph[Vertex]) -> bool:
    """Detect a directed cycle with three-color DFS (white, gray, black)."""
    state: dict[Vertex, int] = {}

    def visit(vertex: Vertex) -> bool:
        state[vertex] = 1
        for neighbor in graph.get(vertex, ()):
            if state.get(neighbor, 0) == 1 or (state.get(neighbor, 0) == 0 and visit(neighbor)):
                return True
        state[vertex] = 2
        return False

    return any(state.get(vertex, 0) == 0 and visit(vertex) for vertex in _vertices(graph))


def bipartite_coloring(graph: Graph[Vertex]) -> dict[Vertex, int] | None:
    """Return a 0/1 coloring, or None when an odd cycle makes it impossible."""
    color: dict[Vertex, int] = {}
    for root in _vertices(graph):
        if root in color:
            continue
        color[root] = 0
        queue = deque([root])
        while queue:
            vertex = queue.popleft()
            for neighbor in graph.get(vertex, ()):
                if neighbor not in color:
                    color[neighbor] = 1 - color[vertex]
                    queue.append(neighbor)
                elif color[neighbor] == color[vertex]:
                    return None
    return color


def connected_components(graph: Graph[Vertex]) -> list[set[Vertex]]:
    """Return weak components (or ordinary components for undirected input)."""
    vertices = _vertices(graph)
    undirected: dict[Vertex, set[Vertex]] = {vertex: set() for vertex in vertices}
    for vertex, neighbors in graph.items():
        for neighbor in neighbors:
            undirected[vertex].add(neighbor)
            undirected[neighbor].add(vertex)
    remaining = set(vertices)
    components: list[set[Vertex]] = []
    while remaining:
        root = next(iter(remaining))
        component = set(bfs(undirected, root)[0])
        components.append(component)
        remaining -= component
    return components


def topological_sort(graph: Graph[Vertex]) -> list[Vertex]:
    """Return a topological ordering using Kahn's algorithm; raise on a cycle."""
    vertices = _vertices(graph)
    indegree = {vertex: 0 for vertex in vertices}
    for neighbors in graph.values():
        for neighbor in neighbors:
            indegree[neighbor] += 1
    queue = deque(vertex for vertex in vertices if indegree[vertex] == 0)
    order = []
    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        for neighbor in graph.get(vertex, ()):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    if len(order) != len(vertices):
        raise ValueError("graph contains a directed cycle")
    return order


def _demo() -> None:
    undirected = {
        "A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"],
        "D": ["B", "C", "E"], "E": ["D"], "F": [],
    }
    order, parent, distance = bfs(undirected, "A")
    assert order == ["A", "B", "C", "D", "E"]
    assert distance["E"] == 3
    assert reconstruct_path(parent, "E") in (["A", "B", "D", "E"], ["A", "C", "D", "E"])
    preorder, iterative_parent = dfs_iterative(undirected, "A")
    assert set(preorder) == set(order) and iterative_parent["A"] is None
    preorder, _, discovered, finished = dfs_recursive(undirected, "A")
    assert len(preorder) == len(discovered) == len(finished) == 5
    assert all(discovered[v] < finished[v] for v in preorder)
    assert has_cycle_undirected(undirected)
    assert bipartite_coloring({"a": ["b"], "b": ["a", "c"], "c": ["b"]}) is not None
    assert bipartite_coloring({"a": ["b", "c"], "b": ["a", "c"], "c": ["a", "b"]}) is None
    assert len(connected_components(undirected)) == 2
    dag = {"shop": ["cook"], "cook": ["eat"], "eat": [], "read": []}
    topo = topological_sort(dag)
    assert topo.index("shop") < topo.index("cook") < topo.index("eat")
    assert has_cycle_directed({"a": ["b"], "b": ["a"]})
    print("BFS:", order)
    print("BFS path A -> E:", reconstruct_path(parent, "E"))
    print("DFS:", preorder)
    print("Topological order:", topo)
    print("All traversal demos/tests passed.")


if __name__ == "__main__":
    _demo()
