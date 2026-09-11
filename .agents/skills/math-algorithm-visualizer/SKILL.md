---
name: math-algorithm-visualizer
description: >-
  Automatically use this skill whenever working on mathematical visualizers, Euclidean algorithm GCD grid tiling (gcd_grid.py), Voronoi diagram SVG generation (voronoi_svg_generator.py), Graph Theory BFS/DFS/Dijkstra walkthroughs, or Manim linear algebra and RSA animations.
---

# Mathematical & Algorithmic Visualizer Skill

## Purpose
Develop, test, and render mathematically rigorous, responsive visualizations for discrete math, computational geometry, graph theory, and linear algebra animations.

## Key Files
- `2026-09-08/gcd_python/gcd_grid.py`: Euclidean algorithm square tiling SVG generator.
- `2026-09-05/voronoi_diagram/voronoi_svg_generator.py`: 4K UHD Voronoi diagram generator.
- `2026-09-05/bfs_dfs_tutorial/`: Graphviz DOT to PDF step-by-step traversals.
- `2026-09-05/graph_theory/shortest_paths/`: Dijkstra, Bellman-Ford, DAG paths.
- `2026-09-12/matrix_multiplication_manim/`: Manim 2D transformations & eigenvalue scenes.
- `2026-09-12/rsa_key_generation_manim/`: Manim RSA prime selection & key pair animation.

## Procedures

### 1. Geometric & SVG Invariants
- Use responsive SVG containers (`viewBox`, `style="max-width: 100%; height: auto;"`).
- Enforce label visibility: `min_tile_px = 110` so `{side}×{side}` text labels never get obscured.

### 2. Algorithmic Verifications
```bash
# Test & generate GCD grid
python3 -m unittest discover -s 2026-09-08/gcd_python -p "test_*.py"

# Test matrix and RSA math
python3 -m unittest discover -s 2026-09-12/matrix_multiplication_manim -p "test_*.py"
python3 -m unittest discover -s 2026-09-12/rsa_key_generation_manim -p "test_*.py"
```
