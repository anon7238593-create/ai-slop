#!/usr/bin/env python3
"""Generate BFS and DFS walkthrough PDFs from one chosen start node.

Example:
    python3 specific_node_traversal.py --node G
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import bfs_dfs_visualizer as visualizer


def main() -> None:
    parser = argparse.ArgumentParser(description="Create BFS/DFS PDF walkthroughs starting at one specific node.")
    parser.add_argument("--node", default="G", help="node at which to begin (default: G)")
    parser.add_argument("--algorithm", choices=("bfs", "dfs", "both"), default="both")
    parser.add_argument("--output", type=Path, default=Path("specific_node_output"))
    parser.add_argument("--random-graph", action="store_true", help="use a generated connected graph")
    parser.add_argument("--nodes", type=int, default=10, help="number of nodes for --random-graph (3-26)")
    parser.add_argument("--edge-probability", type=float, default=0.30)
    parser.add_argument("--seed", type=int, help="seed for reproducible random graph generation")
    args = parser.parse_args()

    if not shutil.which("dot"):
        raise SystemExit("Graphviz is required. Install it, then ensure the 'dot' command is on PATH.")
    if args.random_graph:
        visualizer.GRAPH = visualizer.random_connected_graph(args.nodes, args.edge_probability, args.seed)
    if args.node not in visualizer.GRAPH:
        raise SystemExit(f"Unknown node {args.node!r}. Choose one of: {', '.join(visualizer.GRAPH)}")

    visualizer.START_NODE = args.node
    args.output.mkdir(parents=True, exist_ok=True)
    metadata = {
        "graph": visualizer.GRAPH,
        "start_node": args.node,
        "random_seed": args.seed,
        "edge_probability": args.edge_probability if args.random_graph else None,
    }
    (args.output / "specific_node_graph.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    for algorithm in (("bfs", "dfs") if args.algorithm == "both" else (args.algorithm,)):
        visualizer.render(algorithm, args.output)


if __name__ == "__main__":
    main()
