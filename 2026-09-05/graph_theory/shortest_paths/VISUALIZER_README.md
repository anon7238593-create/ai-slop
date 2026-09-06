# Shortest Paths Visualizer

A step-by-step Graphviz visualizer for shortest path algorithms. Generate beautiful, annotated PDFs showing how algorithms like Dijkstra, Bellman-Ford, and DAG shortest paths work.

## Overview

This tool generates numbered Graphviz PDFs for each step of a shortest path algorithm's execution. Each PDF shows:
- **Node colors:** unseen (gray) → frontier (blue) → processing (orange) → finalized (green)
- **Edge weights:** labeled on each directed edge
- **Distance labels:** current distance estimate for each node
- **Predecessor links:** highlighted in purple showing the shortest path tree
- **Status box:** frontier and finalized nodes at each step

## Quick Start

**Run Dijkstra algorithm with the example graph:**
```bash
python3 shortest_path_visualizer.py --algorithm dijkstra
```

**Generate all algorithms:**
```bash
python3 shortest_path_visualizer.py --algorithm all
```

**Output:** PDFs appear in `output/dijkstra/`, `output/bellman_ford/`, `output/dag/`, and `output/bfs/`

## Supported Algorithms

| Algorithm | Use case | Complexity | Supports |
|-----------|----------|-----------|----------|
| **Dijkstra** | Weighted, nonnegative edges | O((V+E) log V) | Positive weights only |
| **Bellman-Ford** | Weighted, can have negative edges | O(VE) | Negative weights, detects cycles |
| **DAG** | Directed acyclic graphs | O(V+E) | Negative weights (if acyclic) |
| **BFS** | Unweighted / unit weights | O(V+E) | Treats all edges as weight 1 |

## Command-line Options

```bash
python3 shortest_path_visualizer.py [OPTIONS]

Options:
  --algorithm {dijkstra,bellman_ford,bfs,dag,all}
                        Which algorithm to visualize (default: dijkstra)
  --output PATH         Directory for generated files (default: output)
  --random-graph        Generate a random weighted DAG instead of the example
  --nodes N             Number of nodes for random graph (3-10, default: 6)
  --seed SEED           Reproducible seed for random graph generation
  --start-node NODE     Starting node for shortest paths (default: A)
```

## Examples

**Visualize Bellman-Ford:**
```bash
python3 shortest_path_visualizer.py --algorithm bellman_ford
```

**Generate a random graph with 8 nodes, reproducible seed:**
```bash
python3 shortest_path_visualizer.py --algorithm all --random-graph --nodes 8 --seed 20260906
```

**Run BFS (treats edges as unit weight):**
```bash
python3 shortest_path_visualizer.py --algorithm bfs
```

**Start from node D instead of A:**
```bash
python3 shortest_path_visualizer.py --algorithm dijkstra --start-node D
```

**Custom output directory:**
```bash
python3 shortest_path_visualizer.py --output my_output --algorithm all
```

## Example Graph

The default example graph has 6 nodes (A–F) with weighted edges:

```
A ──4──> B ──5──> D
│        │        │
└──2──> C └─1──> E
    │    │       │
    └───8┴──2───┘
        │
        └──3──> F
```

Shortest paths from A:
- A: 0
- B: 3 (A → C → B)
- C: 2
- D: 8 (A → C → D)
- E: 4 (A → C → E)
- F: 7 (A → C → E → F)

## Output Structure

Each run generates a directory per algorithm:

```
output/
├── dijkstra/
│   ├── step_01.dot
│   ├── step_01.pdf
│   ├── step_02.dot
│   ├── step_02.pdf
│   └── ...
├── bellman_ford/
├── dag/
└── bfs/
```

Each PDF is a standalone visual snapshot of the algorithm at one moment. Open them in sequence to watch the algorithm unfold.

## Requirements

- Python 3.7+
- Graphviz (with `dot` command on PATH)
  - **macOS:** `brew install graphviz`
  - **Ubuntu/Debian:** `sudo apt-get install graphviz`
  - **Windows:** [graphviz.org/download](https://graphviz.org/download/)

## How Algorithms are Visualized

### Dijkstra
1. **Initialize** source with distance 0, all others with ∞
2. **Process vertex:** Select unsettled node with smallest distance, relax its edges
3. **Finalize:** Mark as settled; cannot improve again
4. **Repeat** until all reachable nodes are finalized

**Key invariant:** All finalized nodes have their true shortest distance.

### Bellman-Ford
1. **Initialize** source with distance 0, others with ∞
2. **Relax edges** in V–1 passes, updating distances when a shorter path is found
3. **Each pass** scans all edges; captures progress after each pass
4. **Detects cycles** by noting if a final pass still improves any edge

**Key invariant:** After k passes, all paths of ≤k edges are optimal.

### DAG Shortest Paths
1. **Topological sort** to establish a processing order
2. **Process in order:** Each node's predecessors are already done
3. **Relax edges** once per node (no need for multiple passes)
4. **Supports negative weights** because acyclicity guarantees correctness

**Key invariant:** Processing in topological order means predecessors are finalized.

### BFS (Unweighted)
1. **Initialize** source with distance 0
2. **Process in queue order:** FIFO ensures we process by layer (distance)
3. **Discover neighbors:** First-time discovery = shortest path found
4. **Finalize** each node when popped from queue

**Key invariant:** Queue layers correspond to distance bands.

## Customizing the Graph

Edit the `GRAPH` and `START_NODE` variables near the top of `shortest_path_visualizer.py`:

```python
GRAPH: WeightedGraph = {
    "A": [("B", 4), ("C", 2)],
    "B": [("D", 5), ("E", 10)],
    "C": [("B", 1), ("D", 8), ("E", 2)],
    "D": [("E", 2), ("F", 6)],
    "E": [("F", 3)],
    "F": [],
}
START_NODE = "A"
```

Format: `vertex -> [(neighbor, weight), ...]`

Re-run the script to visualize your custom graph.

## Edge Cases Covered

- **Isolated nodes:** Unreachable from source stay at distance ∞
- **Negative weights:** Bellman-Ford and DAG handle them; Dijkstra rejects them
- **Tied distances:** Algorithm picks first in iteration order
- **Zero-weight edges:** Treated normally (Bellman-Ford) or as distance-neutral (Dijkstra)
- **Single-node graph:** Source has distance 0, no outgoing edges
- **Disconnected components:** Unreachable nodes never finalize

## Generating Random Graphs

```bash
python3 shortest_path_visualizer.py --random-graph --nodes 8 --seed 12345
```

- Generates a random weighted DAG (no cycles)
- Edges are topologically ordered (left to right)
- Each edge weight is 1–10
- Seed makes it reproducible; same seed = same graph

The graph structure is saved to `output/graph.json`:
```json
{
  "graph": {
    "A": [["B", 4], ["C", 2]],
    ...
  },
  "start_node": "A",
  "seed": 12345
}
```

## Color Meanings

- **Gray (unseen):** Not yet discovered by the algorithm
- **Blue (frontier):** Discovered but not yet finalized
- **Orange (processing):** Currently being processed
- **Green (finalized):** Shortest distance is certain; will not change

## Using for Teaching

1. **Generate PDFs** for a graph
2. **Show step by step** in a presentation or live demo
3. **Ask predictions:** "What happens next? Which node will be finalized?"
4. **Modify and re-run:** "What if we change this edge weight?"
5. **Compare algorithms:** Generate all 4 algorithms on the same graph

## Troubleshooting

**Error: "Graphviz is required"**
- Install Graphviz and ensure `dot` is on your PATH
- Test: `which dot` (should show a path)

**PDFs not generated**
- Check for error messages; most relate to Graphviz not being installed
- Try a smaller graph (fewer nodes) to rule out memory issues

**Algorithm fails on my graph**
- DAG check: ensure graph is actually acyclic
- Dijkstra: all weights must be ≥ 0
- Bellman-Ford: detects negative cycles and will raise an error

## See Also

- **Shortest Paths Theory:** [2026-09-05/graph_theory/shortest_paths/README.md](README.md)
- **BFS/DFS Visualizer:** [2026-09-05/bfs_dfs_tutorial/](../../bfs_dfs_tutorial/)
- **Graph Theory Playground:** [2026-09-05/graph_theory/](../)
