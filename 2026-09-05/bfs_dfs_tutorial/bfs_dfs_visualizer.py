#!/usr/bin/env python3
"""Generate polished, step-by-step Graphviz PDFs for BFS and DFS.

Run:
    python bfs_dfs_visualizer.py --algorithm both
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from collections import deque
from pathlib import Path
from typing import Iterable


# An undirected graph. List order intentionally makes the traversal repeatable.
GRAPH: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B", "G"],
    "E": ["B", "G", "H"],
    "F": ["C", "H"],
    "G": ["D", "E"],
    "H": ["E", "F"],
}
START_NODE = "A"

COLORS = {
    "unseen": ("#F8FAFC", "#94A3B8", "#334155"),
    "frontier": ("#DBEAFE", "#2563EB", "#1E3A8A"),
    "current": ("#FFEDD5", "#EA580C", "#9A3412"),
    "done": ("#DCFCE7", "#16A34A", "#14532D"),
}


def undirected_edges(graph: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Return each undirected edge exactly once, in a stable order."""
    return [(node, neighbor) for node in graph for neighbor in graph[node] if node < neighbor]


def dot_quote(value: str) -> str:
    return '"' + value.replace('"', r'\"') + '"'


def make_dot(
    algorithm: str,
    step: int,
    action: str,
    current: str | None,
    frontier: Iterable[str],
    done: Iterable[str],
    discovery_edges: set[frozenset[str]],
) -> str:
    """Build a DOT document for one moment in the traversal."""
    frontier_list = list(frontier)
    done_set = set(done)
    frontier_set = set(frontier_list)
    queue_name = "Queue" if algorithm == "bfs" else "Stack (top at right)"
    frontier_label = "  →  ".join(frontier_list) if algorithm == "bfs" else "  |  ".join(frontier_list)
    frontier_label = frontier_label or "(empty)"
    title = algorithm.upper() + " Traversal"
    lines = [
        "graph traversal {",
        '  graph [layout=dot, rankdir=TB, bgcolor="#FFFFFF", pad="0.35", nodesep="0.65", ranksep="0.8", fontname="Arial"];',
        '  node [shape=circle, style="filled", fontname="Arial Bold", fontsize=18, width=0.72, fixedsize=true, penwidth=2.4];',
        '  edge [color="#94A3B8", penwidth=2.0];',
        f'  label=<<B>{title}</B><BR/><FONT POINT-SIZE="16">Step {step}: {action}</FONT>>; labelloc="t"; fontsize=26; fontname="Arial"; fontcolor="#0F172A";',
        '  subgraph cluster_legend { label="Legend"; color="#CBD5E1"; penwidth=1.2; style="rounded"; fontsize=14; fontname="Arial Bold";',
        '    key_unseen [label="Unseen", fillcolor="#F8FAFC", color="#94A3B8", fontcolor="#334155", fontsize=12, width=0.82];',
        '    key_frontier [label="Discovered", fillcolor="#DBEAFE", color="#2563EB", fontcolor="#1E3A8A", fontsize=12, width=0.95];',
        '    key_current [label="Processing", fillcolor="#FFEDD5", color="#EA580C", fontcolor="#9A3412", fontsize=12, width=1.05];',
        '    key_done [label="Complete", fillcolor="#DCFCE7", color="#16A34A", fontcolor="#14532D", fontsize=12, width=0.92];',
        '    { rank=same; key_unseen; key_frontier; key_current; key_done; }',
        '  }',
    ]
    for node in GRAPH:
        state = "current" if node == current else "done" if node in done_set else "frontier" if node in frontier_set else "unseen"
        fill, border, text = COLORS[state]
        lines.append(f"  {node} [fillcolor={dot_quote(fill)}, color={dot_quote(border)}, fontcolor={dot_quote(text)}];")
    for left, right in undirected_edges(GRAPH):
        if frozenset((left, right)) in discovery_edges:
            lines.append(f'  {left} -- {right} [color="#7C3AED", penwidth=3.8];')
        else:
            lines.append(f"  {left} -- {right};")
    lines.extend([
        '  status [shape=plain, fixedsize=false, width=0, height=0, margin=0, label=<',
        '    <TABLE BORDER="0" CELLBORDER="0" CELLPADDING="7" BGCOLOR="#F1F5F9">',
        f'      <TR><TD ALIGN="LEFT"><B>{queue_name}:</B> {frontier_label}</TD></TR>',
        f'      <TR><TD ALIGN="LEFT"><B>Visited:</B> {", ".join(sorted(done_set)) or "(none)"}</TD></TR>',
        '    </TABLE>',
        '  >];',
        "}",
    ])
    return "\n".join(lines) + "\n"


def traversal_steps(algorithm: str) -> list[tuple[str, str | None, list[str], set[str], set[frozenset[str]]]]:
    """Capture visual states immediately before and after each processing action."""
    frontier: deque[str] | list[str] = deque([START_NODE]) if algorithm == "bfs" else [START_NODE]
    discovered = {START_NODE}
    done: set[str] = set()
    discovery_edges: set[frozenset[str]] = set()
    steps = [(f"Start at {START_NODE}", None, list(frontier), set(done), set(discovery_edges))]

    while frontier:
        current = frontier.popleft() if algorithm == "bfs" else frontier.pop()
        steps.append((f"Process node {current}", current, list(frontier), set(done), set(discovery_edges)))
        neighbors = GRAPH[current] if algorithm == "bfs" else list(reversed(GRAPH[current]))
        new_nodes: list[str] = []
        for neighbor in neighbors:
            if neighbor not in discovered:
                discovered.add(neighbor)
                frontier.append(neighbor)
                new_nodes.append(neighbor)
                discovery_edges.add(frozenset((current, neighbor)))
        done.add(current)
        detail = f"Discover {', '.join(new_nodes)} from {current}" if new_nodes else f"No new neighbors from {current}"
        steps.append((detail, None, list(frontier), set(done), set(discovery_edges)))
    return steps


def render(algorithm: str, output_root: Path) -> None:
    """Write numbered .dot files and matching PDFs for an algorithm."""
    target = output_root / algorithm
    target.mkdir(parents=True, exist_ok=True)
    for index, (action, current, frontier, done, edges) in enumerate(traversal_steps(algorithm), start=1):
        dot_path = target / f"step_{index:02d}.dot"
        pdf_path = dot_path.with_suffix(".pdf")
        dot_path.write_text(make_dot(algorithm, index, action, current, frontier, done, edges), encoding="utf-8")
        subprocess.run(["dot", "-Tpdf", str(dot_path), "-o", str(pdf_path)], check=True)
    print(f"Created {len(traversal_steps(algorithm))} DOT files and PDFs in {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create BFS/DFS Graphviz walkthrough PDFs.")
    parser.add_argument("--algorithm", choices=("bfs", "dfs", "both"), default="both")
    parser.add_argument("--output", type=Path, default=Path("output"), help="directory for generated files")
    args = parser.parse_args()
    if not shutil.which("dot"):
        raise SystemExit("Graphviz is required. Install it, then ensure the 'dot' command is on PATH.")
    for algorithm in (("bfs", "dfs") if args.algorithm == "both" else (args.algorithm,)):
        render(algorithm, args.output)


if __name__ == "__main__":
    main()
