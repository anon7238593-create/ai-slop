# 2026-09-05: Graph Theory & Visualization

A comprehensive collection of educational graph theory materials and interactive visualizations.

## Overview

This folder contains two major projects focused on teaching and exploring graph algorithms:

1. **BFS/DFS Tutorial** – Interactive step-by-step Graphviz visualizations for breadth-first and depth-first search
2. **Graph Theory Playground** – A broad, self-contained curriculum covering graph fundamentals through advanced topics

Both projects prioritize clarity and interactivity, making complex graph algorithms approachable for learners.

---

## Projects

### 1. BFS/DFS Graphviz Walkthrough

**Purpose:** Generate polished, step-by-step PDF visualizations of breadth-first search (BFS) and depth-first search (DFS) on graphs.

**Key Features:**
- Visual state tracking: unseen (gray), discovered (blue), processing (orange), complete (green)
- Numbered steps showing exactly what happens at each stage
- Customizable graphs (default 8-node example or random generation)
- Automated PDF generation via Graphviz
- Color-coded discovery edges (purple) vs. regular edges
- Queue/stack visualization showing frontier nodes at each step

**Quick Start:**
```bash
cd 2026-09-05/bfs_dfs_tutorial
python3 bfs_dfs_visualizer.py --algorithm both
```
Outputs appear in `output/bfs/` and `output/dfs/` (one PDF per traversal step).

**Main Scripts:**
- `bfs_dfs_visualizer.py` – Generate BFS and DFS step PDFs from a graph
- `specific_node_traversal.py` – Run BFS/DFS from a single chosen starting node

**Key Commands:**
```bash
# Generate both BFS and DFS
python3 bfs_dfs_visualizer.py --algorithm both

# Generate a random graph (10 nodes, 30% edge probability, reproducible seed)
python3 bfs_dfs_visualizer.py --random-graph --nodes 10 --edge-probability 0.30 --seed 20260905

# Run from a specific node
python3 bfs_dfs_visualizer.py --algorithm bfs --start-node E

# Custom output directory
python3 bfs_dfs_visualizer.py --output my_output

# Traverse from node G (produces step PDFs and a combined walkthrough)
python3 specific_node_traversal.py --node G --algorithm both
```

**Requirements:**
- Python 3.7+
- Graphviz (must have `dot` command on PATH)
  - macOS: `brew install graphviz`
  - Ubuntu/Debian: `sudo apt-get install graphviz`
  - Windows: [graphviz.org/download](https://graphviz.org/download/)

**Architecture:**
- Builds a state machine capturing the traversal at each step
- Colors nodes based on state (unseen → frontier → current → done)
- Highlights discovery edges (tree edges) in purple
- Generates a Graphviz DOT file for each step
- Invokes the `dot` command to render each DOT file as a PDF

---

### 2. Graph Theory Playground

**Purpose:** A practical, self-contained educational tour of graph theory with mathematical exposition and clear Python implementations.

**Philosophy:**
- Each topic has both a **Markdown explanation** (theory, invariants, complexity) and a **Python implementation** (clear, stdlib-only code)
- Code favors readability over optimization; uses basic dictionaries, lists, sets, heaps
- Small enough to read and modify interactively; large enough to be genuinely useful

**Curriculum Structure:**

| Topic | Main Ideas | Run with |
|-------|-----------|----------|
| **Foundations** | Graph models, adjacency representations, degrees, neighborhoods | `python3 graph_demo.py` |
| **Traversals** | BFS, DFS, parent trees, cycles, bipartiteness, topological sort | `python3 traversals.py` |
| **Shortest Paths** | BFS paths, Dijkstra, Bellman-Ford, DAG paths, Floyd-Warshall | `python3 shortest_paths.py` |
| **Connectivity** | Components, SCCs, DSU, articulation points, bridges | `python3 connectivity.py` |
| **Spanning Trees** | MSTs, cuts, Kruskal, Prim, Disjoint Set Union | `python3 spanning_trees.py` |
| **Flow & Matching** | Residual networks, Edmonds-Karp, max-flow, bipartite matching | `python3 flow_matching.py` |
| **Advanced** | Eulerian/Hamiltonian paths, graph coloring, planarity, PageRank | `python3 explore.py` |

**Suggested Learning Path:**
1. **Foundations** – Understand graph representations (adjacency list, matrix, edge list)
2. **Traversals** – Learn BFS/DFS, the building blocks for everything else
3. **Shortest Paths** + **Spanning Trees** – Apply traversals to optimization
4. **Connectivity** – Understand graph robustness (articulation points, bridges)
5. **Flow & Matching** – Tackle complex optimization models
6. **Advanced** – Explore hard problems and heuristics

**Quick Start:**
```bash
cd 2026-09-05/graph_theory
python3 -m unittest -v  # Run all tests
```

**Study Approach:**
For each topic, the README guides you through:
1. Graph model and input assumptions
2. Algorithm invariants (what stays true during execution)
3. Correctness sketch (why it works)
4. Time and space complexity
5. Edge cases that break naive implementations

Then run the Python file and experiment:
- Add/remove edges
- Change weights
- Construct counterexamples (disconnected graphs, cycles, negative weights, etc.)

**Key Conventions:**
- Vertices: hashable values (strings, integers)
- Adjacency lists: `vertex → [neighbors]` or `[(neighbor, weight), ...]`
- Unreachable vertices: represented as omitted or `None`
- Results: `True`/`False` in Python, `1`/`0` when printed
- Scope: Educational, not production-grade; omits concurrency, persistence, huge data

**Example Output:**
```
$ cd 2026-09-05/graph_theory/foundations
$ python3 graph_demo.py
Graph adjacency list:
{'A': ['B', 'C'], 'B': ['A', 'D'], 'C': ['A'], 'D': ['B']}

Degrees: {'A': 2, 'B': 2, 'C': 1, 'D': 1}

Generated graph.dot (render with: dot -Tpdf graph.dot -o graph.pdf)
```

---

## Repository Integration

A GitHub Actions workflow automatically regenerates BFS/DFS visualizations:
- **File:** `.github/workflows/generate_pdf_for_traversal.yml`
- **Behavior:** Generates a random graph, renders step PDFs, publishes to `artifacts` branch
- **Use:** Reference slides for presentations or external documentation

---

## Dependencies

### BFS/DFS Tutorial
- **Python 3.7+** (standard library: `argparse`, `json`, `random`, `subprocess`, `pathlib`)
- **Graphviz** (external tool; `dot` command must be available)

### Graph Theory Playground
- **Python 3.7+** (standard library only; no external packages)
- **Optional:** Graphviz (for Foundations graph visualization)

---

## File Structure

```
2026-09-05/
├── README.md                           (this file)
├── bfs_dfs_tutorial/
│   ├── README.md                       (BFS/DFS specifics)
│   ├── bfs_dfs_visualizer.py          (main entry point)
│   ├── specific_node_traversal.py     (single-node variant)
│   └── output/                         (generated PDFs, .dot files)
│
└── graph_theory/
    ├── README.md                       (curriculum guide)
    ├── foundations/
    │   ├── README.md
    │   └── graph_demo.py
    ├── traversals/
    │   ├── README.md
    │   ├── traversals.py
    │   └── bfs_visualize.py
    ├── shortest_paths/
    │   ├── README.md
    │   └── shortest_paths.py
    ├── connectivity/
    │   ├── README.md
    │   ├── connectivity.py
    │   └── test_connectivity.py
    ├── spanning_trees/
    │   ├── README.md
    │   └── spanning_trees.py
    ├── flow_and_matching/
    │   ├── README.md
    │   ├── flow_matching.py
    │   └── test_flow_matching.py
    └── advanced/
        ├── README.md
        └── explore.py
```

---

## Getting Started

### For Visual Learners (BFS/DFS)
```bash
cd 2026-09-05/bfs_dfs_tutorial
python3 bfs_dfs_visualizer.py --algorithm both
# Open output/bfs/step_01.pdf and output/dfs/step_01.pdf
```

### For Theory Learners (Graph Theory)
```bash
cd 2026-09-05/graph_theory
# Start with Foundations
cd foundations
cat README.md         # Read the theory
python3 graph_demo.py # Run the code
```

### For Experimenters
```bash
cd 2026-09-05/graph_theory/traversals
python3 traversals.py
# Edit traversals.py, modify the graph, re-run to see effects
```

---

## Use Cases

- **Teaching graph algorithms** – Use visualizations and code for classroom/tutorial content
- **Interview prep** – Understand BFS/DFS deeply with visual walkthroughs
- **Algorithm study** – Modify code to test hypotheses (e.g., "What if I change edge order?")
- **Presentation slides** – Export PDFs from BFS/DFS visualizer for talks
- **Interactive learning** – Run Python scripts, tweak inputs, observe outcomes

---

## Notes & Limitations

- **Clarity over production:** Graph Theory code uses simple data structures, not optimized libraries
- **Educational scope:** Does not cover dynamic graphs, distributed algorithms, or hardware-specific optimizations
- **Graphviz requirement:** BFS/DFS visuals depend on external `dot` command; Graph Theory Playground runs with stdlib only
- **Graph size:** BFS/DFS visualizer tested with up to ~15 nodes; very large graphs produce large PDF files

---

## See Also

- Root repository: [ai-slop](../README.md)
- GitHub Graphviz documentation: [graphviz.org](https://graphviz.org)
- Related Wikipedia topics: [Graph theory](https://en.wikipedia.org/wiki/Graph_theory), [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search), [Depth-first search](https://en.wikipedia.org/wiki/Depth-first_search)
