# AI Slop — Project & Repository Summary

This document provides a comprehensive summary of all code, algorithms, visualizers, assets, and automated GitHub Actions workflows built in this repository.

---

## Table of Contents

1. [Repository Architecture & Workflow Model](#repository-architecture--workflow-model)
2. [Euclidean Algorithm GCD Grid Visualizer (`2026-09-08/gcd_python`)](#euclidean-algorithm-gcd-grid-visualizer-2026-09-08gcd_python)
3. [Graph Theory Suite & Tutorial Walkthroughs (`2026-09-05`)](#graph-theory-suite--tutorial-walkthroughs-2026-09-05)
4. [Voronoi Diagram Generator (`2026-09-05/voronoi_diagram`)](#voronoi-diagram-generator-2026-09-05voronoi_diagram)
5. [C / Yacc Parsers (`2026-09-05`)](#c--yacc-parsers-2026-09-05)
6. [Automated GitHub Actions Pipelines (`.github/workflows`)](#automated-github-actions-pipelines-githubworkflows)
7. [Artifact Branch Layout](#artifact-branch-layout)
8. [Recent Enhancements & Milestones](#recent-enhancements--milestones)

---

## Repository Architecture & Workflow Model

- **`master` Branch**: Contains all source code, CLI tools, unit tests, and GitHub Actions workflow definitions.
- **`artifacts` Branch**: An automated, orphan-based storage branch where scheduled and event-triggered GitHub Actions jobs commit generated SVG visualizers, walkthrough PDFs, manifests, and documentation tables.
- **Shared Concurrency**: All publishing workflows synchronize under the `visualization-artifacts` concurrency lock (`cancel-in-progress: false`), ensuring race-free, serial commits to the `artifacts` branch.

---

## Euclidean Algorithm GCD Grid Visualizer (`2026-09-08/gcd_python`)

Location: [`2026-09-08/gcd_python/`](2026-09-08/gcd_python/)

### Overview
A dependency-free Python tool that geometrically visualizes the Euclidean algorithm by tiling an $a \times b$ rectangle with progressively smaller squares. At each step, as many squares as possible of size $\min(w, h)$ are placed into the remaining area. The final square size is mathematically equal to $\gcd(a, b)$.

### Key Components
- **[`gcd_grid.py`](2026-09-08/gcd_python/gcd_grid.py)**:
  - `euclidean_square_tiling(a, b)`: Core algorithm that computes exact tile placements $(x, y, \text{side}, \text{step})$.
  - `fresh_seed()`: Generates 32-bit OS entropy seeds via Python's `secrets` module.
  - `random_dimensions(seed)`: Constructs random, non-square $(a, b)$ dimensions with guaranteed coprime multipliers and GCD $> 1$.
  - `svg_visualization(a, b, seed)`: Generates high-resolution, responsive SVGs.
    - **Guaranteed Label Visibility**: Enforces `min_tile_px = 110` so that 100% of squares (including the smallest GCD squares) clearly display their `{side}×{side}` text labels.
    - **Demonstration Typography**: Responsive bold labels scaled up to 48px, 30px titles, 24px axis labels, and 22px legend swatches.
    - **Unconstrained Canvas**: Generates generous canvases (1400px+ up to 6000px+ for large dimensions) with `style="max-width: 100%; height: auto;"`.
- **[`test_gcd_grid.py`](2026-09-08/gcd_python/test_gcd_grid.py)**:
  - Comprehensive unit test suite covering tiling correctness, GCD equivalence, SVG legend and seed formatting, seed reproducibility, CLI options, and entropy.
- **[`gcd_48_36.svg`](2026-09-08/gcd_python/gcd_48_36.svg)**:
  - Bundled reference visualization showing $\gcd(48, 36) = 12$ tiled by one $36 \times 36$ square and three $12 \times 12$ squares.

### CLI Usage
```bash
cd 2026-09-08/gcd_python

# Generate and open a new random pair in browser
python3 gcd_grid.py --open

# Generate with explicit dimensions or reproducible seed
python3 gcd_grid.py 84 60 --open
python3 gcd_grid.py --seed 20260908 --save custom.svg

# Run tests
python3 -m unittest test_gcd_grid.py
```

---

## Graph Theory Suite & Tutorial Walkthroughs (`2026-09-05`)

Location: [`2026-09-05/`](2026-09-05/)

### 1. BFS & DFS Tutorial Visualizer ([`bfs_dfs_tutorial/`](2026-09-05/bfs_dfs_tutorial/))
- **`bfs_dfs_visualizer.py`**: Generates step-by-step Graphviz `.dot` files and rendered PDFs for Breadth-First and Depth-First searches.
  - Color-coded state tracking: Active node (orange), Frontier (blue), Completed (green), Discovery tree edges (purple).
  - Displays data structure states (Queue / Stack) and visited node history side-by-side with the graph.
  - Supports teaching graphs and seeded random connected graphs.
- **`specific_node_traversal.py`**: Walkthrough generator starting from a chosen target node (default: node `G`).

### 2. Shortest Path Visualizer ([`graph_theory/shortest_paths/`](2026-09-05/graph_theory/shortest_paths/))
- **`shortest_path_visualizer.py`**: Step-by-step Graphviz visualizer for single-source shortest path algorithms:
  - **Dijkstra's Algorithm** (with priority queue state visualization).
  - **Bellman-Ford Algorithm** (round-by-round edge relaxations and negative cycle detection).
  - **DAG Shortest Paths** (topological sort order processing).
- **`VISUALIZER_README.md`**: Detailed pedagogical walkthrough and documentation.

### 3. Comprehensive Graph Theory Algorithms ([`graph_theory/`](2026-09-05/graph_theory/))
- **Foundations**: Graph representations (Adjacency Matrix / List), degree sequences, handshaking lemma.
- **Connectivity**: Articulation points, bridge detection, connected components, Kosaraju / Tarjan strongly connected components.
- **Spanning Trees**: Kruskal's algorithm (Disjoint Set Union / Union-Find) and Prim's algorithm.
- **Network Flow & Matching**: Ford-Fulkerson with Edmonds-Karp augmenting paths, maximum bipartite matching.
- **Advanced**: Graph vertex coloring (Welsh-Powell, greedy), Eulerian paths/circuits (Hierholzer), Hamiltonian paths.

---

## Voronoi Diagram Generator (`2026-09-05/voronoi_diagram`)

Location: [`2026-09-05/voronoi_diagram/`](2026-09-05/voronoi_diagram/)

- **`voronoi_svg_generator.py`**: Dependency-free geometric Voronoi diagram generator.
- Implements polygon half-plane clipping against perpendicular bisectors of site pairs.
- Generates 19 distinct diagrams for site counts $N = 2$ through $N = 20$.
- Fully styled with distinct translucent cell fills, site coordinate markers, and SVG metadata.

---

## C / Yacc Parsers (`2026-09-05`)

Location: [`2026-09-05/yacc_test/`](2026-09-05/yacc_test/) & [`2026-09-05/statement_parser/`](2026-09-05/statement_parser/)

1. **`yacc_test/` (Arithmetic Expression Parser)**:
   - Implements Lex and Yacc grammars for evaluating arithmetic expressions.
   - Handles standard operator precedence (`+`, `-`, `*`, `/`, unary minus, nested parentheses).
   - Includes standalone Makefile for binary compilation.
2. **`statement_parser/` (Stateful Statement Parser)**:
   - Extends the parser to handle variable declarations, assignments, and multi-statement evaluations with a persistent symbol table.

---

## Automated GitHub Actions Pipelines (`.github/workflows`)

All workflows reside in [`.github/workflows/`](.github/workflows/) and run **hourly** (`cron: "0 * * * *"`), on `workflow_dispatch`, and on pushes to `master`.

| Workflow | File | Output Path on `artifacts` | Description |
|---|---|---|---|
| **GCD Grid Visualizations** | [`generate_gcd_grids.yml`](.github/workflows/generate_gcd_grids.yml) | `gcd-grids/` | Generates **100 unique GCD grid SVGs** with large dimensions (up to ~15,000) on each run. Avoids duplicates from prior runs via manifest inspection. |
| **Voronoi Diagrams** | [`generate_voronoi_diagrams.yml`](.github/workflows/generate_voronoi_diagrams.yml) | `voronoi/` | Generates 19 Voronoi diagrams (2–20 sites) with timestamp-derived seeds. |
| **Traversal Walkthrough PDFs** | [`generate_pdf_for_traversel.yml`](.github/workflows/generate_pdf_for_traversel.yml) | `generated/` | Generates random graphs, runs BFS/DFS step walkthroughs, and combines them into single unified PDFs using `pdfunite`. |

---

## Artifact Branch Layout

When the workflows execute, the `artifacts` branch maintains the following directory structure:

```text
artifacts
├── gcd-grids/
│   ├── README.md                      # Markdown table cataloging all 100 generated pairs
│   ├── manifest.json                  # JSON metadata (a, b, gcd, seed, steps, squares)
│   ├── gcd-<a1>-<b1>.svg              # 100 individual high-resolution SVGs
│   └── ...
├── generated/
│   ├── bfs_dfs_complete_walkthrough.pdf
│   ├── specific-node/
│   │   ├── specific_node_bfs_dfs_walkthrough.pdf
│   │   └── code/                      # Bundled generator scripts
│   ├── bfs/ and dfs/                  # Step-by-step PDF slides
│   └── graph.json                     # Seed and graph metadata
└── voronoi/
    ├── README.md
    ├── manifest.json
    └── voronoi_02_sites.svg ... voronoi_20_sites.svg
```

---

## Recent Enhancements & Milestones

1. **Automated Seeded GCD Generation**:
   - Replaced static test pairs with randomized, reproducible $(a, b)$ dimensions on every GitHub Actions run.
   - Implemented cross-run state tracking: the workflow inspects the previous `manifest.json` on `origin/artifacts` to guarantee that consecutive runs never repeat identical pairs.

2. **Demonstration-Scale SVGs**:
   - Eliminated artificial 620×430 box clamping.
   - Enforced a minimum tile size of $110 \times 110$ px for the smallest GCD square, ensuring **100% of squares have clearly visible, bold text labels** without clipping or omissions.

3. **High-Volume Production & Large Numbers**:
   - Scaled up divisor range to $10 \dots 250$ and multiplier range to $3 \dots 60$, generating numbers into the thousands ($a, b$ up to ~15,000).
   - Increased batch generation size to **100 SVGs per run**.

4. **Hourly Automation**:
   - Transitioned all three repository workflows from daily schedules to **hourly schedules** (`cron: "0 * * * *"`).
