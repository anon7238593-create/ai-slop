"""Connectivity algorithms implemented with the Python standard library only.

Vertices may be any hashable object.  Graph arguments are adjacency mappings
whose values are iterables of neighboring vertices.  The undirected routines
assume a simple, symmetric graph; directed routines do not require symmetry.
"""

from collections import defaultdict


def _vertices(graph):
    result = set(graph)
    for neighbors in graph.values():
        result.update(neighbors)
    return result


def connected_components(graph):
    """Return the connected components of an undirected graph."""
    unseen = _vertices(graph)
    components = []
    while unseen:
        start = unseen.pop()
        component = {start}
        stack = [start]
        while stack:
            vertex = stack.pop()
            for neighbor in graph.get(vertex, ()):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)
        components.append(component)
    return components


def kosaraju_scc(graph):
    """Return strongly connected components using Kosaraju's two DFS passes."""
    vertices = _vertices(graph)
    reverse = defaultdict(list)
    for vertex in vertices:
        for neighbor in graph.get(vertex, ()):
            reverse[neighbor].append(vertex)

    visited = set()
    finish_order = []

    def first_pass(vertex):
        visited.add(vertex)
        for neighbor in graph.get(vertex, ()):
            if neighbor not in visited:
                first_pass(neighbor)
        finish_order.append(vertex)

    for vertex in vertices:
        if vertex not in visited:
            first_pass(vertex)

    visited.clear()
    components = []

    def second_pass(vertex, component):
        visited.add(vertex)
        component.add(vertex)
        for neighbor in reverse[vertex]:
            if neighbor not in visited:
                second_pass(neighbor, component)

    for vertex in reversed(finish_order):
        if vertex not in visited:
            component = set()
            second_pass(vertex, component)
            components.append(component)
    return components


def tarjan_scc(graph):
    """Return strongly connected components using Tarjan's low-link DFS."""
    vertices = _vertices(graph)
    index = 0
    indices, lowlink, stack = {}, {}, []
    on_stack = set()
    components = []

    def visit(vertex):
        nonlocal index
        indices[vertex] = lowlink[vertex] = index
        index += 1
        stack.append(vertex)
        on_stack.add(vertex)

        for neighbor in graph.get(vertex, ()):
            if neighbor not in indices:
                visit(neighbor)
                lowlink[vertex] = min(lowlink[vertex], lowlink[neighbor])
            elif neighbor in on_stack:
                lowlink[vertex] = min(lowlink[vertex], indices[neighbor])

        if lowlink[vertex] == indices[vertex]:
            component = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == vertex:
                    break
            components.append(component)

    for vertex in vertices:
        if vertex not in indices:
            visit(vertex)
    return components


def articulation_points_and_bridges(graph):
    """Return (cut vertices, bridges) for an undirected simple graph.

    A bridge is represented as a frozenset of its two endpoints.  The DFS
    maintains discovery times and ``low`` values: low[v] is the earliest
    discovery time reachable from v's subtree using at most one tree edge.
    """
    vertices = _vertices(graph)
    time = 0
    discovery, low = {}, {}
    articulation = set()
    bridges = set()

    def visit(vertex, parent):
        nonlocal time
        discovery[vertex] = low[vertex] = time
        time += 1
        child_count = 0
        for neighbor in graph.get(vertex, ()):
            if neighbor == parent:
                continue
            if neighbor not in discovery:
                child_count += 1
                visit(neighbor, vertex)
                low[vertex] = min(low[vertex], low[neighbor])
                if parent is not None and low[neighbor] >= discovery[vertex]:
                    articulation.add(vertex)
                if low[neighbor] > discovery[vertex]:
                    bridges.add(frozenset((vertex, neighbor)))
            else:
                low[vertex] = min(low[vertex], discovery[neighbor])
        if parent is None and child_count > 1:
            articulation.add(vertex)

    for vertex in vertices:
        if vertex not in discovery:
            visit(vertex, None)
    return articulation, bridges


def biconnected_components(graph):
    """Return vertex-biconnected blocks as sets of vertices.

    Blocks are maximal subgraphs with no articulation vertex internally.  The
    edge stack emits one block whenever a DFS child closes at a low-link
    boundary.  Isolated vertices are singleton blocks.
    """
    vertices = _vertices(graph)
    time = 0
    discovery, low = {}, {}
    edge_stack = []
    blocks = []

    def emit_until(stop_edge):
        block = set()
        while edge_stack:
            edge = edge_stack.pop()
            block.update(edge)
            if edge == stop_edge:
                break
        if block:
            blocks.append(block)

    def visit(vertex, parent):
        nonlocal time
        discovery[vertex] = low[vertex] = time
        time += 1
        child_count = 0
        for neighbor in graph.get(vertex, ()):
            if neighbor == parent:
                continue
            edge = frozenset((vertex, neighbor))
            if neighbor not in discovery:
                child_count += 1
                edge_stack.append(edge)
                visit(neighbor, vertex)
                low[vertex] = min(low[vertex], low[neighbor])
                if low[neighbor] >= discovery[vertex]:
                    emit_until(edge)
            elif discovery[neighbor] < discovery[vertex]:
                edge_stack.append(edge)
                low[vertex] = min(low[vertex], discovery[neighbor])
        if parent is None and child_count == 0:
            blocks.append({vertex})

    for vertex in vertices:
        if vertex not in discovery:
            visit(vertex, None)
            edge_stack.clear()
    return blocks


class DisjointSetUnion:
    """Union-find with path compression and union by size."""

    def __init__(self, items=()):
        self.parent = {}
        self.size = {}
        for item in items:
            self.add(item)

    def add(self, item):
        if item not in self.parent:
            self.parent[item] = item
            self.size[item] = 1

    def find(self, item):
        if item not in self.parent:
            self.add(item)
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, first, second):
        root_first, root_second = self.find(first), self.find(second)
        if root_first == root_second:
            return False
        if self.size[root_first] < self.size[root_second]:
            root_first, root_second = root_second, root_first
        self.parent[root_second] = root_first
        self.size[root_first] += self.size[root_second]
        return True

    def connected(self, first, second):
        return self.find(first) == self.find(second)

    def component_count(self):
        return len({self.find(item) for item in self.parent})


if __name__ == "__main__":
    sample = {0: [1], 1: [0, 2], 2: [1], 3: []}
    print("components:", connected_components(sample))
    print("cut vertices, bridges:", articulation_points_and_bridges(sample))
