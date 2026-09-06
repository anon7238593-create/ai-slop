#!/usr/bin/env python3
"""Generate polished, step-by-step Graphviz PDFs for shortest path algorithms.

Supports Dijkstra, Bellman-Ford, DAG shortest paths, and BFS (for unweighted graphs).

Run:
    python shortest_path_visualizer.py --algorithm dijkstra
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from collections import deque
from heapq import heappop, heappush
from itertools import count
from math import inf
from pathlib import Path
from typing import Iterable, Mapping

Vertex = str
WeightedGraph = dict[Vertex, list[tuple[Vertex, float]]]


# Example weighted graph
GRAPH: WeightedGraph = {
    "A": [("B", 4), ("C", 2)],
    "B": [("D", 5), ("E", 10)],
    "C": [("B", 1), ("D", 8), ("E", 2)],
    "D": [("E", 2), ("F", 6)],
    "E": [("F", 3)],
    "F": [],
}
START_NODE = "A"

# Color palette for visualization states
COLORS = {
    "unseen": ("#F8FAFC", "#94A3B8", "#334155"),           # gray
    "frontier": ("#DBEAFE", "#2563EB", "#1E3A8A"),         # blue (discovered)
    "processing": ("#FFEDD5", "#EA580C", "#9A3412"),       # orange (current)
    "finalized": ("#DCFCE7", "#16A34A", "#14532D"),        # green (finalized)
}


def undirected_edges(graph: WeightedGraph) -> list[tuple[Vertex, Vertex]]:
    """Return each directed edge exactly once, in stable order."""
    seen = set()
    edges = []
    for node in sorted(graph.keys()):
        for neighbor, _ in graph[node]:
            edge = (node, neighbor)
            if edge not in seen:
                edges.append(edge)
                seen.add(edge)
    return edges


def random_weighted_graph(nodes: int, seed: int | None = None) -> WeightedGraph:
    """Generate a small random weighted DAG for demonstration."""
    import random
    
    if not 3 <= nodes <= 10:
        raise ValueError("--nodes must be between 3 and 10")
    
    generator = random.Random(seed)
    labels = [chr(ord("A") + i) for i in range(nodes)]
    graph: WeightedGraph = {label: [] for label in labels}
    
    # Create edges in topological order (left to right) to avoid cycles
    for i, source in enumerate(labels):
        num_edges = generator.randint(1, min(3, nodes - i - 1))
        targets = generator.sample(labels[i + 1 :], num_edges)
        for target in targets:
            weight = generator.randint(1, 10)
            graph[source].append((target, weight))
    
    return graph


def dot_quote(value: str) -> str:
    return '"' + value.replace('"', r'\"') + '"'


def make_dot(
    algorithm: str,
    step: int,
    action: str,
    graph: WeightedGraph,
    current: Vertex | None,
    distances: dict[Vertex, float],
    finalized: set[Vertex],
    frontier: list[Vertex],
    predecessors: dict[Vertex, Vertex | None],
) -> str:
    """Build a DOT document for one moment in the algorithm."""
    title = algorithm.replace("_", " ").title() + " Shortest Paths"
    lines = [
        "digraph shortest_paths {",
        '  graph [layout=dot, rankdir=LR, bgcolor="#FFFFFF", pad="0.35", nodesep="0.5", ranksep="1.0", fontname="Arial"];',
        '  node [shape=circle, style="filled", fontname="Arial Bold", fontsize=14, width=0.6, fixedsize=true, penwidth=2.0];',
        '  edge [fontsize=10, fontname="Arial"];',
        f'  label=<<B>{title}</B><BR/><FONT POINT-SIZE="14">Step {step}: {action}</FONT>>; labelloc="t"; fontsize=20; fontname="Arial"; fontcolor="#0F172A";',
        '  subgraph cluster_legend { label="Legend"; color="#CBD5E1"; penwidth=1.2; style="rounded"; fontsize=12; fontname="Arial Bold";',
        '    key_unseen [label="Unseen", fillcolor="#F8FAFC", color="#94A3B8", fontsize=10, width=0.6];',
        '    key_frontier [label="Frontier", fillcolor="#DBEAFE", color="#2563EB", fontsize=10, width=0.6];',
        '    key_processing [label="Processing", fillcolor="#FFEDD5", color="#EA580C", fontsize=10, width=0.7];',
        '    key_finalized [label="Finalized", fillcolor="#DCFCE7", color="#16A34A", fontsize=10, width=0.7];',
        '    { rank=same; key_unseen; key_frontier; key_processing; key_finalized; }',
        '  }',
    ]
    
    # Add nodes with state-based coloring
    for node in sorted(graph.keys()):
        if node == current:
            state = "processing"
        elif node in finalized:
            state = "finalized"
        elif node in frontier:
            state = "frontier"
        else:
            state = "unseen"
        
        fill, border, text = COLORS[state]
        dist = distances.get(node, inf)
        dist_label = str(int(dist)) if dist != inf else "∞"
        label = f"{node}\\n{dist_label}"
        
        lines.append(
            f"  {node} [fillcolor={dot_quote(fill)}, color={dot_quote(border)}, "
            f"fontcolor={dot_quote(text)}, label={dot_quote(label)}];"
        )
    
    # Add edges with weights
    for source, neighbors in graph.items():
        for target, weight in neighbors:
            edge_color = "#7C3AED" if (source in predecessors and predecessors[target] == source) else "#94A3B8"
            edge_width = "2.5" if (source in predecessors and predecessors[target] == source) else "1.5"
            lines.append(
                f'  {source} -> {target} [label={dot_quote(str(int(weight)))}, '
                f'color="{edge_color}", penwidth={edge_width}];'
            )
    
    # Add status box
    frontier_str = ", ".join(frontier) if frontier else "(empty)"
    finalized_str = ", ".join(sorted(finalized)) if finalized else "(none)"
    lines.extend([
        '  status [shape=plain, fixedsize=false, width=0, height=0, margin=0, label=<',
        '    <TABLE BORDER="0" CELLBORDER="0" CELLPADDING="7" BGCOLOR="#F1F5F9">',
        f'      <TR><TD ALIGN="LEFT"><B>Frontier:</B> {frontier_str}</TD></TR>',
        f'      <TR><TD ALIGN="LEFT"><B>Finalized:</B> {finalized_str}</TD></TR>',
        '    </TABLE>',
        '  >];',
        "}",
    ])
    
    return "\n".join(lines) + "\n"


def dijkstra_steps(graph: WeightedGraph, source: Vertex) -> list[tuple[str, Vertex | None, dict, set, list, dict]]:
    """Capture states during Dijkstra's algorithm execution."""
    distances = {vertex: inf for vertex in graph}
    distances[source] = 0
    predecessors = {source: None}
    finalized: set[Vertex] = set()
    sequence = count()
    heap = [(0, next(sequence), source)]
    
    steps = [
        (f"Initialize source {source} with distance 0", None, dict(distances), set(finalized), [], dict(predecessors))
    ]
    
    while heap:
        distance, _, vertex = heappop(heap)
        
        if distance != distances[vertex]:
            continue
        
        frontier = [v for v, d in distances.items() if d != inf and v not in finalized and v != vertex]
        steps.append(
            (f"Process vertex {vertex} (distance: {int(distance)})", vertex, dict(distances), set(finalized), frontier, dict(predecessors))
        )
        
        for neighbor, weight in graph.get(vertex, []):
            candidate = distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                predecessors[neighbor] = vertex
                heappush(heap, (candidate, next(sequence), neighbor))
        
        finalized.add(vertex)
        frontier = [v for v, d in distances.items() if d != inf and v not in finalized]
        steps.append(
            (f"Finalize {vertex}; frontier: {frontier}", None, dict(distances), set(finalized), frontier, dict(predecessors))
        )
    
    return steps


def bellman_ford_steps(graph: WeightedGraph, source: Vertex) -> list[tuple[str, Vertex | None, dict, set, list, dict]]:
    """Capture states during Bellman-Ford algorithm execution."""
    vertices = set(graph.keys())
    for neighbors in graph.values():
        vertices.update(n for n, _ in neighbors)
    
    distances = {vertex: inf for vertex in vertices}
    distances[source] = 0
    predecessors = {source: None}
    edges = [(u, v, w) for u in graph for v, w in graph[u]]
    
    steps = [
        (f"Initialize source {source}", None, dict(distances), set(), [], dict(predecessors))
    ]
    
    # Relax edges V-1 times
    for iteration in range(len(vertices) - 1):
        changed = False
        for u, v, weight in edges:
            if distances[u] != inf and distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                predecessors[v] = u
                changed = True
        
        finalized = set(v for v in vertices if distances[v] != inf)
        frontier = []
        steps.append(
            (f"Iteration {iteration + 1}: relax all edges", None, dict(distances), finalized, frontier, dict(predecessors))
        )
        
        if not changed:
            break
    
    return steps


def bfs_unweighted_steps(graph: WeightedGraph, source: Vertex) -> list[tuple[str, Vertex | None, dict, set, list, dict]]:
    """Capture states during BFS (treating all edges as weight 1)."""
    distances = {source: 0}
    predecessors = {source: None}
    frontier = deque([source])
    finalized: set[Vertex] = set()
    
    steps = [(f"Start at {source}", None, dict(distances), set(finalized), list(frontier), dict(predecessors))]
    
    while frontier:
        vertex = frontier.popleft()
        steps.append(
            (f"Process {vertex}", vertex, dict(distances), set(finalized), list(frontier), dict(predecessors))
        )
        
        for neighbor, _ in graph.get(vertex, []):
            if neighbor not in distances:
                distances[neighbor] = distances[vertex] + 1
                predecessors[neighbor] = vertex
                frontier.append(neighbor)
        
        finalized.add(vertex)
        steps.append(
            (f"Finalize {vertex}", None, dict(distances), set(finalized), list(frontier), dict(predecessors))
        )
    
    return steps


def dag_shortest_paths_steps(graph: WeightedGraph, source: Vertex) -> list[tuple[str, Vertex | None, dict, set, list, dict]]:
    """Capture states during DAG shortest paths."""
    vertices = set(graph.keys())
    for neighbors in graph.values():
        vertices.update(n for n, _ in neighbors)
    
    # Topological sort
    indegree = {v: 0 for v in vertices}
    for u in graph:
        for v, _ in graph[u]:
            indegree[v] += 1
    
    topo_queue = deque(v for v in vertices if indegree[v] == 0)
    topological_order = []
    while topo_queue:
        u = topo_queue.popleft()
        topological_order.append(u)
        for v, _ in graph.get(u, []):
            indegree[v] -= 1
            if indegree[v] == 0:
                topo_queue.append(v)
    
    if len(topological_order) != len(vertices):
        raise ValueError("Graph is not a DAG")
    
    distances = {v: inf for v in vertices}
    distances[source] = 0
    predecessors = {source: None}
    finalized: set[Vertex] = set()
    
    steps = [(f"Topological sort: {topological_order}", None, dict(distances), set(finalized), [], dict(predecessors))]
    
    for vertex in topological_order:
        if distances[vertex] == inf:
            continue
        
        steps.append(
            (f"Relax edges from {vertex}", vertex, dict(distances), set(finalized), [], dict(predecessors))
        )
        
        for neighbor, weight in graph.get(vertex, []):
            if distances[vertex] + weight < distances[neighbor]:
                distances[neighbor] = distances[vertex] + weight
                predecessors[neighbor] = vertex
        
        finalized.add(vertex)
    
    return steps


def render(algorithm: str, output_root: Path, graph: WeightedGraph, source: Vertex) -> None:
    """Write numbered .dot files and matching PDFs."""
    target = output_root / algorithm
    target.mkdir(parents=True, exist_ok=True)
    
    if algorithm == "dijkstra":
        steps = dijkstra_steps(graph, source)
    elif algorithm == "bellman_ford":
        steps = bellman_ford_steps(graph, source)
    elif algorithm == "bfs":
        steps = bfs_unweighted_steps(graph, source)
    elif algorithm == "dag":
        steps = dag_shortest_paths_steps(graph, source)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    for index, (action, current, distances, finalized, frontier, predecessors) in enumerate(steps, start=1):
        dot_path = target / f"step_{index:02d}.dot"
        pdf_path = dot_path.with_suffix(".pdf")
        dot_content = make_dot(algorithm, index, action, graph, current, distances, finalized, frontier, predecessors)
        dot_path.write_text(dot_content, encoding="utf-8")
        subprocess.run(["dot", "-Tpdf", str(dot_path), "-o", str(pdf_path)], check=True)
    
    print(f"Created {len(steps)} DOT files and PDFs in {target}")


def main() -> None:
    global GRAPH, START_NODE
    
    parser = argparse.ArgumentParser(description="Create shortest-path algorithm Graphviz walkthrough PDFs.")
    parser.add_argument(
        "--algorithm",
        choices=("dijkstra", "bellman_ford", "bfs", "dag", "all"),
        default="dijkstra",
        help="Which algorithm(s) to visualize"
    )
    parser.add_argument("--output", type=Path, default=Path("output"), help="directory for generated files")
    parser.add_argument("--random-graph", action="store_true", help="generate a random weighted DAG")
    parser.add_argument("--nodes", type=int, default=6, help="number of nodes for --random-graph (3-10)")
    parser.add_argument("--seed", type=int, help="seed for reproducible random graph")
    parser.add_argument("--start-node", help="starting node for shortest paths")
    
    args = parser.parse_args()
    
    if not shutil.which("dot"):
        raise SystemExit("Graphviz is required. Install it, then ensure the 'dot' command is on PATH.")
    
    if args.random_graph:
        GRAPH = random_weighted_graph(args.nodes, args.seed)
        START_NODE = list(GRAPH.keys())[0]
        args.output.mkdir(parents=True, exist_ok=True)
        metadata = {
            "graph": {k: [(v, float(w)) for v, w in GRAPH[k]] for k in GRAPH},
            "start_node": START_NODE,
            "seed": args.seed,
        }
        (args.output / "graph.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    
    if args.start_node:
        if args.start_node not in GRAPH:
            raise SystemExit(f"Unknown start node {args.start_node!r}. Choose one of: {', '.join(GRAPH)}")
        START_NODE = args.start_node
    
    algorithms = ("dijkstra", "bellman_ford", "bfs", "dag") if args.algorithm == "all" else (args.algorithm,)
    for algo in algorithms:
        try:
            render(algo, args.output, GRAPH, START_NODE)
        except Exception as e:
            print(f"Warning: {algo} failed: {e}")


if __name__ == "__main__":
    main()
