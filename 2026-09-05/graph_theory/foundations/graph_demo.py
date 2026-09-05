"""Small, modifiable graph representations for the foundations tutorial.

Run with:
    python3 graph_demo.py
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Hashable, Iterable, List, Optional, Tuple

Vertex = Hashable


@dataclass(frozen=True)
class Edge:
    """One edge record; ``key`` lets parallel edges remain distinct."""

    source: Vertex
    target: Vertex
    weight: float = 1
    key: Optional[str] = None


class Graph:
    """A graph supporting directed/undirected, weighted, and parallel edges."""

    def __init__(
        self,
        vertices: Iterable[Vertex] = (),
        *,
        directed: bool = False,
        allow_parallel: bool = False,
    ) -> None:
        self.directed = directed
        self.allow_parallel = allow_parallel
        self.vertices = set(vertices)
        self.edges: List[Edge] = []

    def add_edge(
        self, source: Vertex, target: Vertex, weight: float = 1, key: Optional[str] = None
    ) -> None:
        """Add an edge, inserting the reverse record for an undirected graph."""
        self.vertices.update((source, target))
        if not self.allow_parallel:
            for edge in self.edges:
                same_direction = edge.source == source and edge.target == target
                reverse_direction = (
                    not self.directed
                    and edge.source == target
                    and edge.target == source
                )
                if same_direction or reverse_direction:
                    raise ValueError("parallel edge is not allowed")
        self.edges.append(Edge(source, target, weight, key))

    def edge_list(self) -> List[Edge]:
        return list(self.edges)

    def adjacency_list(self) -> DefaultDict[Vertex, List[Tuple[Vertex, float]]]:
        result: DefaultDict[Vertex, List[Tuple[Vertex, float]]] = defaultdict(list)
        for vertex in self.vertices:
            result[vertex]  # Ensure isolated vertices appear.
        for edge in self.edges:
            result[edge.source].append((edge.target, edge.weight))
            if not self.directed:
                result[edge.target].append((edge.source, edge.weight))
        return result

    def adjacency_matrix(self) -> Tuple[List[Vertex], List[List[Optional[float]]]]:
        """Return vertex order and a None-filled matrix (minimum parallel weight)."""
        order = sorted(self.vertices, key=str)
        position = {vertex: i for i, vertex in enumerate(order)}
        matrix: List[List[Optional[float]]] = [
            [None for _ in order] for _ in order
        ]
        for edge in self.edges:
            i, j = position[edge.source], position[edge.target]
            old = matrix[i][j]
            matrix[i][j] = edge.weight if old is None else min(old, edge.weight)
            if not self.directed:
                old = matrix[j][i]
                matrix[j][i] = edge.weight if old is None else min(old, edge.weight)
        return order, matrix

    def neighbors(self, vertex: Vertex) -> List[Vertex]:
        """Return outgoing (or undirected) neighbors, preserving edge records."""
        result = []
        for edge in self.edges:
            if edge.source == vertex:
                result.append(edge.target)
            elif not self.directed and edge.target == vertex:
                result.append(edge.source)
        return result

    def degree(self, vertex: Vertex) -> int:
        """Return degree, or out-degree for a directed graph."""
        return len(self.neighbors(vertex))

    def in_degree(self, vertex: Vertex) -> int:
        if not self.directed:
            return self.degree(vertex)
        return sum(edge.target == vertex for edge in self.edges)


def print_matrix(graph: Graph) -> None:
    order, matrix = graph.adjacency_matrix()
    print("matrix order:", order)
    for row in matrix:
        print(" ", row)


def demo() -> None:
    # Change these labels, weights, or edges to explore the representation.
    roads = Graph(["A", "B", "C", "D"])
    roads.add_edge("A", "B", 4)
    roads.add_edge("A", "C", 2)
    roads.add_edge("B", "D", 5)
    roads.add_edge("C", "D", 1)

    print("Weighted undirected graph")
    print("edge list:", roads.edge_list())
    print("adjacency list:", dict(roads.adjacency_list()))
    print_matrix(roads)
    print("neighbors of A:", roads.neighbors("A"))
    print("degree of D:", roads.degree("D"))

    web = Graph(["home", "docs", "search"], directed=True)
    web.add_edge("home", "docs")
    web.add_edge("home", "search")
    web.add_edge("docs", "search")
    print("\nDirected graph")
    print("out-neighbors of home:", web.neighbors("home"))
    print("in-degree of search:", web.in_degree("search"))

    flights = Graph(["X", "Y"], directed=False, allow_parallel=True)
    flights.add_edge("X", "Y", 100, key="morning")
    flights.add_edge("X", "Y", 120, key="evening")
    print("\nMultigraph")
    print("parallel edge list:", flights.edge_list())
    print("matrix keeps the minimum weight:", flights.adjacency_matrix()[1])


if __name__ == "__main__":
    demo()
