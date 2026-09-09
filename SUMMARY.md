# AI Slop — Project & Repository Summary

This document provides a comprehensive summary of all code, algorithms, visualizers, assets, and automated GitHub Actions workflows built in this repository.

---

## Table of Contents

1. [Repository Architecture & Workflow Model](#repository-architecture--workflow-model)
2. [90-Degree Ball Collision Spawner Simulation (`2026-09-09/collision`)](#90-degree-ball-collision-spawner-simulation-2026-09-09collision)
3. [Euclidean Algorithm GCD Grid Visualizer (`2026-09-08/gcd_python`)](#euclidean-algorithm-gcd-grid-visualizer-2026-09-08gcd_python)
4. [Graph Theory Suite & Tutorial Walkthroughs (`2026-09-05`)](#graph-theory-suite--tutorial-walkthroughs-2026-09-05)
5. [Voronoi Diagram Generator (`2026-09-05/voronoi_diagram`)](#voronoi-diagram-generator-2026-09-05voronoi_diagram)
6. [C / Yacc Parsers (`2026-09-05`)](#c--yacc-parsers-2026-09-05)
7. [Automated GitHub Actions Pipelines (`.github/workflows`)](#automated-github-actions-pipelines-githubworkflows)
8. [GitHub Pages Interactive Media Explorer](#github-pages-interactive-media-explorer)
9. [Artifact Branch Layout](#artifact-branch-layout)
10. [Recent Enhancements & Milestones](#recent-enhancements--milestones)

---

## Repository Architecture & Workflow Model

- **`master` Branch**: Contains all source code, CLI tools, unit tests, and GitHub Actions workflow definitions.
- **`artifacts` Branch**: An automated, orphan-based storage branch where scheduled and event-triggered GitHub Actions jobs commit generated SVG visualizers, walkthrough PDFs, manifests, and documentation tables.
- **GitHub Pages Static Deployment**: Hosted directly from GitHub Actions at [`https://anon7238593-create.github.io/ai-slop/`](https://anon7238593-create.github.io/ai-slop/). Rebuilds and deploys automatically on every single commit pushed to the `artifacts` branch.
- **FIFO Queue Serializer (Zero-Cancellation Concurrency)**: Workflows execute sequentially one by one using `.github/scripts/wait_for_turn.py`. This inspects active runs via `gh run list` and pauses until older runs complete, completely eliminating GitHub Actions concurrency cancellations (`Canceling since a higher priority waiting request... exists`) while ensuring race-free, serial commits to the `artifacts` branch.

---

## Random Angle Ball Collision Spawner Simulation (`2026-09-09/collision`)

Location: [`2026-09-09/collision/`](2026-09-09/collision/)

### Overview
A high-performance 2D physics simulation and video generator in Python. A ball begins bouncing within a spacious arena (default 1080p Full HD: $1920 \times 1080$) at a calm, slow pace ($240$ px/s, batch range $160 - 260$ px/s) allowing viewers to clearly track, observe, and analyze each trajectory. Upon every boundary collision, the ball reflects elastically and immediately spawns a new ball with the **exact same scalar speed** and a **random inward angle** (across a $150^\circ$ inward fan) directed into the arena interior. Balls duplicate continuously on each border collision until a target count of $N$ balls is reached, creating organic, dynamic geometric webs and vivid neon color-burst patterns.

### Key Components
- **[`ball_collision.py`](2026-09-09/collision/ball_collision.py)**:
  - `calculate_spawn_velocity(vx_base, vy_base, wall_normal, speed, angle_mode='random', ...)`: Random inward deflection preserving exact scalar speed $\|\vec{v}_{spawn}\| = s$, with backward compatibility for fixed deflection angles.
  - `BallSimulation`: Sub-step continuous collision physics engine preventing tunneling at high velocities.
  - `SimulationRenderer`: Full HD 60 FPS renderer with 3D sphere highlights, neon golden-angle palette, fading motion trails, expanding shockwave rings, and impact wall flashes.
  - `synthesize_audio_track()`: Spatial stereo audio synthesizer generating multi-octave pentatonic collision chimes with horizontal position panning ($x / W$).
  - Dual encoder: Direct H.264 pipe via FFmpeg (`libx264` / `aac`) with seamless fallback to OpenCV `VideoWriter`.
- **[`generate_batch.py`](2026-09-09/collision/generate_batch.py)**:
  - Parallel batch generator that creates 100 randomized ball collision simulations with different ball counts ($12 \le N \le 36$), starting launch angles ($10^\circ \dots 350^\circ$), video lengths, slow analytical speeds ($160 - 260$ px/s), and organic random spawn directions.
  - Automatically compiles a comprehensive `manifest.json` and formatted `README.md` cataloging each video's metadata.
- **[`test_ball_collision.py`](2026-09-09/collision/test_ball_collision.py)**:
  - Comprehensive unit test suite validating strict speed conservation, random inward projection ($\vec{u} \cdot \hat{n} > 0$), angle diversity, 90-degree backward compatibility, termination on $N$ balls, palette generation, audio synthesis, frame rendering, and batch spec randomization.
- **[`README.md`](2026-09-09/collision/README.md)**:
  - Complete documentation, mathematical derivations, resolution presets, and CLI usage.

### CLI Usage
```bash
cd 2026-09-09/collision

# Generate default 1080p 60 FPS video (50 balls)
python3 ball_collision.py -n 50

# Custom resolution presets and starting angles
python3 ball_collision.py -n 30 --preset vertical -o tiktok_shorts.mp4
python3 ball_collision.py -n 40 --initial-angle 42.5 --preset square -o instagram.mp4

# Run batch generator for 100 randomized videos
python3 generate_batch.py --count 100 --output-dir ./collision-videos

# Run unit tests
python3 -m unittest test_ball_collision.py
```

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
| **Ball Collision Videos** | [`generate_collision_videos.yml`](.github/workflows/generate_collision_videos.yml) | `collision-videos/` | Generates **100 randomized ball collision MP4 videos** varying in ball count, starting angle, video duration, and speeds with spatial audio. |
| **GCD Grid Visualizations** | [`generate_gcd_grids.yml`](.github/workflows/generate_gcd_grids.yml) | `gcd-grids/` | Generates **100 unique GCD grid SVGs** with large dimensions (up to ~15,000) on each run. Avoids duplicates from prior runs via manifest inspection. |
| **Voronoi Diagrams** | [`generate_voronoi_diagrams.yml`](.github/workflows/generate_voronoi_diagrams.yml) | `voronoi/` | Generates 19 Voronoi diagrams (2–20 sites) with timestamp-derived seeds. |
| **Traversal Walkthrough PDFs** | [`generate_pdf_for_traversel.yml`](.github/workflows/generate_pdf_for_traversel.yml) | `generated/` | Generates random graphs, runs BFS/DFS step walkthroughs, and combines them into single unified PDFs using `pdfunite`. |
| **Deploy GitHub Pages** | [`deploy_pages.yml`](.github/workflows/deploy_pages.yml) | GitHub Pages (`_site/`) | Builds and deploys the browsable media explorer website to GitHub Pages on every commit to `artifacts`. |

---

## GitHub Pages Interactive Media Explorer

- **Live URL**: [`https://anon7238593-create.github.io/ai-slop/`](https://anon7238593-create.github.io/ai-slop/)
- **Generator Script**: [`.github/scripts/build_pages.py`](.github/scripts/build_pages.py)
- **HTML Template**: [`.github/scripts/template.html`](.github/scripts/template.html)
- **Automated Workflow**: [`.github/workflows/deploy_pages.yml`](.github/workflows/deploy_pages.yml)

### Architecture & Features
1. **Continuous Deployment on `artifacts` Updates**:
   - The workflow listens on `push: branches: [ artifacts, master ]` and `workflow_dispatch`.
   - Whenever any media generation workflow pushes updated videos or SVGs to the `artifacts` branch, GitHub Pages automatically checks out the latest commit, processes the metadata manifests, bundles static assets into `_site/`, and deploys via official `actions/deploy-pages@v4`.
2. **Simple, Intuitive Tab Navigation**:
   - Clean, dark-mode single page interface with instant URL hash routing (`#collision`, `#gcd`, `#voronoi`, `#traversal`).
   - Sticky header with live repo links and media count badges.
3. **Dedicated Showcase Views**:
   - **Collision Videos (`#collision`)**: Spotlight HTML5 video player with real-time metadata badges (ball count $N$, speed in px/s, launch angle, canvas dimensions, file size), instant keyword filter, aspect ratio dropdown, sorting, and 12-item pagination.
   - **GCD Grids (`#gcd`)**: Interactive SVG inspector displaying Euclidean step counts and square totals, GCD size filters (Small, Medium, Large), and responsive tile cards.
   - **Voronoi Diagrams (`#voronoi`)**: Interactive site count slider ($N = 2 \dots 20$) with live SVG display, download links, and a thumbnail gallery.
   - **Graph Traversals (`#traversal`)**: Cards for complete BFS/DFS walkthrough PDFs with direct browser viewing and downloading.
4. **Zero Heavy Dependencies**:
   - Completely vanilla HTML5, CSS3, and JavaScript with embedded JSON manifest payload.
   - Sub-second load times and lightweight GitHub Actions builds (< 20 seconds).

---

## Artifact Branch Layout

When the workflows execute, the `artifacts` branch maintains the following directory structure:

```text
artifacts
├── collision-videos/
│   ├── README.md                      # Markdown table cataloging all 100 generated collision videos
│   ├── manifest.json                  # JSON metadata (filename, n_balls, initial_angle, speed, dims, size)
│   ├── collision_001.mp4              # 100 individual randomized MP4 simulations with spatial audio
│   └── ...
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
   - Transitioned all repository workflows to **hourly schedules** (`cron: "0 * * * *"`).

5. **Randomized 90-Degree Collision Video Suite**:
   - Added automated batch generation of 100 randomized ball collision MP4 videos on GitHub Actions (`.github/workflows/generate_collision_videos.yml`).
   - Every video features varied target ball counts ($12 \dots 60$), unique starting angles ($10^\circ \dots 350^\circ$), differing speeds and lengths, and synthesized spatial stereo pentatonic audio.

6. **Zero-Cancellation FIFO Workflow Serializer**:
   - Resolved GitHub Actions cancellation issue (`Canceling since a higher priority waiting request for visualization-artifacts exists`) by replacing GitHub's built-in single-slot pending concurrency groups with an intelligent FIFO queue serializer (`.github/scripts/wait_for_turn.py`).
   - Workflows now run sequentially one by one in true order of dispatch, eliminating race conditions on the `artifacts` branch while preventing any premature run terminations.

7. **Slow-Speed Analytical Tracking & Organic Random Inward Spawning**:
   - Reduced simulation speeds from $650$ px/s to a calm, trackable $240$ px/s (batch: $160 - 260$ px/s), enabling human viewers to effortlessly analyze ball trajectories, elastic wall bounces, and spawn dynamics.
   - Replaced fixed 90-degree orthogonal deflection with organic random inward angles sampled across a $150^\circ$ interior fan ($-\pm 75^\circ$ from wall normal), producing diverse, kaleidoscopic geometric webs and visual aesthetics.

8. **30-Second Post-Max Floating Ensemble Showcase**:
   - Configured `duration_after: 30.0s` across simulation and batch generator so that when the maximum ball count $N$ is reached, the video continues running for 30 more seconds.
   - The HUD dynamically switches to display a floating countdown (`BALLS: N/N (FLOATING: XX.Xs / 30.0s)`) with a dedicated floating progress bar, allowing viewers to marvel at the complex floating ensemble of balls gliding and reflecting smoothly together.

9. **Automated GitHub Pages Media Showcase Website**:
   - Deployed an interactive, high-performance static website to GitHub Pages (`https://anon7238593-create.github.io/ai-slop/`).
   - Integrated with GitHub Actions (`.github/workflows/deploy_pages.yml`) to automatically rebuild and publish whenever new media assets are committed to the `artifacts` branch.
   - Features single-page tab navigation, spotlight video player with live physics metadata, GCD grid tiling explorer, Voronoi site slider, and direct PDF traversal walkthrough viewers.

