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
- **GitHub Releases (High-Capacity Media Hosting)**: Before generated assets are committed to Git, an automated GitHub Release is created via [`.github/scripts/create_release.sh`](.github/scripts/create_release.sh). This enables hosting large media assets (videos up to 2GB per asset) without bloating the Git object store or encountering GitHub's 100MB repository file limit. Each release includes individual media assets and a consolidated `.zip` bundle.
- **`artifacts` Branch**: An automated, orphan-based storage branch where scheduled and event-triggered GitHub Actions jobs commit generated SVG visualizers, walkthrough PDFs, manifests, and documentation tables.
- **GitHub Pages Static Deployment**: Hosted directly from GitHub Actions at [`https://anon7238593-create.github.io/ai-slop/`](https://anon7238593-create.github.io/ai-slop/). Rebuilds and deploys automatically on every single commit pushed to the `artifacts` branch.
- **Atomic Artifacts Publisher (Conflict-Free Concurrency)**: Workflows generate their media artifacts in parallel and publish atomically to the `artifacts` branch using [`.github/scripts/push_artifacts.sh`](.github/scripts/push_artifacts.sh). This synchronizes with the latest remote HEAD on each retry attempt, eliminates `git rebase` merge conflicts across generated directories, and resolves ref-locking push contention through randomized exponential backoff and jitter. Any oversized media files ($\ge 95\text{MB}$) are excluded from Git commits while remaining fully accessible via the GitHub Release URLs in `manifest.json`.

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
  - Parallel batch generator that creates 20 randomized 1920x1080 Full HD ball collision simulations with different ball counts ($12 \le N \le 1000$), starting launch angles ($10^\circ \dots 350^\circ$), video lengths, slow analytical speeds ($160 - 260$ px/s), and organic random spawn directions.
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

# Run batch generator for 20 randomized Full HD (1920x1080) videos
python3 generate_batch.py --count 20 --width 1920 --height 1080 --output-dir ./collision-videos

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
- Generates **100 distinct diagrams** for site counts $N = 1$ through $N = 100$ at **very high 4K resolution ($3840 \times 2400$)**.
- Fully styled with a rich 20-color pastel palette, adaptive site dispersion, scalable typography, site coordinate markers, and SVG metadata.

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

Workflows reside in [`.github/workflows/`](.github/workflows/) with a structured execution order: generation pipelines run first (hourly at minute 0 and 5, or on push to `master`), and GitHub Pages deploys last (triggered upon completion of the generation pipelines via `workflow_run`, hourly at minute 10, or on `workflow_dispatch`).

| Workflow | File | Output Path on `artifacts` | Description |
|---|---|---|---|
| **GCD Grid Visualizations** | [`generate_gcd_grids.yml`](.github/workflows/generate_gcd_grids.yml) | `gcd-grids/` | Generates **100 unique GCD grid SVGs** with large dimensions (up to ~15,000) on each run. Avoids duplicates from prior runs via manifest inspection. Runs at `0 * * * *` and on push. |
| **Voronoi Diagrams** | [`generate_voronoi_diagrams.yml`](.github/workflows/generate_voronoi_diagrams.yml) | `voronoi/` | Generates **100 high-resolution (3840x2400 4K UHD)** Voronoi diagrams (1–100 sites) with timestamp-derived seeds. Runs at `0 * * * *` and on push. |
| **Traversal Walkthrough PDFs** | [`generate_pdf_for_traversel.yml`](.github/workflows/generate_pdf_for_traversel.yml) | `generated/` | Generates random graphs, runs BFS/DFS step walkthroughs, and combines them into single unified PDFs using `pdfunite`. Runs at `0 * * * *` and on push. |
| **Ball Collision Videos** | [`generate_collision_videos.yml`](.github/workflows/generate_collision_videos.yml) | `collision-videos/` | Generates **20 randomized 1920x1080 Full HD ball collision MP4 videos** varying in ball count, starting angle, video duration, and speeds with spatial audio. Runs at `5 * * * *`. |
| **500-Ball Collision Videos Release** | [`generate_500_ball_collision_videos.yml`](.github/workflows/generate_500_ball_collision_videos.yml) | GitHub Releases (`collision-500-balls-*`) | Generates **20 videos with exactly 500 balls** at 1920x1080 resolution. Publishes directly as unique GitHub Releases without pushing to the `artifacts` branch. Runs hourly (`0 * * * *`). |
| **Deploy GitHub Pages** | [`deploy_pages.yml`](.github/workflows/deploy_pages.yml) | GitHub Pages (`_site/`) | **Runs last**: Builds and deploys the browsable media explorer website to GitHub Pages after generator pipelines complete (`workflow_run`), hourly at minute 10, or on `artifacts` updates. |

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
   - **Voronoi Diagrams (`#voronoi`)**: Interactive site count slider ($N = 1 \dots 100$), quick jump presets, and scrollable site buttons with live 4K SVG display, download links, and direct viewing.
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
│   ├── bfs_traversal.mp4              # Queue-driven BFS animation video
│   ├── dfs_traversal.mp4              # Stack-driven DFS animation video
│   ├── bfs_dfs_comparison.mp4         # Side-by-side synchronized comparison video
│   └── graph.json                     # Seed and graph metadata
├── matrix-animations/
│   ├── animation_manifest.json        # Manifest with matrix configs, eigenvalues, eigenvectors, seeds
│   ├── space_transformations.mp4      # Scaling, shearing, and general stretching animations
│   ├── eigenvectors_invariant_directions.mp4 # Invariant eigen-lines (Av = λv)
│   ├── matrix_multiplication_composition.mp4 # Spatial composition: A then B vs C = B · A
│   ├── master_matrix_multiplication_story.mp4 # Master cinematic pedagogical film
│   └── code/                          # Bundled generator scripts
└── voronoi/
    ├── README.md
    ├── manifest.json
    └── voronoi_001_sites.svg ... voronoi_100_sites.svg
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

6. **Zero-Cancellation Atomic Artifacts Publisher**:
   - Resolved GitHub Actions cancellation issue (`Canceling since a higher priority waiting request for visualization-artifacts exists`) and `git rebase` / push ref lock errors by implementing an atomic, retry-capable publisher (`.github/scripts/push_artifacts.sh`).
   - Workflows now run and generate artifacts concurrently without blocking or artificial queue delays, atomically synchronizing with `origin/artifacts` on every push retry to guarantee conflict-free, 100% reliable publishing.

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

10. **Expanded Ball Capacity (Upper Limit: 1000 Balls)**:
   - Raised the maximum ball capacity from 36/60 to **1000 balls** across both the single-video generator and batch pipeline (`ball_collision.py` and `generate_batch.py`).
   - Added strict CLI and config bounds validation ($1 \le N \le 1000$).
   - Enhanced HUD metrics layout and logging to cleanly accommodate up to 4-digit ball counts.

11. **Release-First Publishing Pipeline for Large Media Hosting**:
   - Integrated automated GitHub Release creation (`.github/scripts/create_release.sh`) into all artifact pipelines before files are committed to the `artifacts` branch.
   - Enables hosting large media assets (videos up to 2GB per file) without being blocked by GitHub's 100MB repository limit or causing Git object store bloat.
   - Automatically packages a full `.zip` bundle alongside individual assets, and dynamically enriches `manifest.json` with `release_tag`, `release_url`, `release_download_url`, and `has_git_blob` flags.
   - Implemented a safety threshold in `push_artifacts.sh`: files $\ge 95\text{MB}$ are safely excluded from Git commits while remaining hosted on GitHub Releases, with seamless video player fallback on the GitHub Pages website.

12. **High-Density 500-Ball Collision Videos Release Pipeline**:
   - Added a dedicated hourly GitHub Actions workflow ([`.github/workflows/generate_500_ball_collision_videos.yml`](.github/workflows/generate_500_ball_collision_videos.yml)) running at `0 * * * *`.
   - Generates 20 full-scale simulations at 1920x1080 resolution featuring exactly 500 balls per video.
   - Completely bypasses the `artifacts` branch to eliminate Git repository bloat from heavy high-density media, publishing assets directly as unique timestamped GitHub Releases (`collision-500-balls-<timestamp>-run<id>`).
   - Generates unique release names / titles on every run (with optional manual tag and release name overrides via `workflow_dispatch`).

13. **High-Resolution 100-Diagram 4K Voronoi Pipeline**:
   - Scaled diagram generation from 20 to **100 diagrams** ($N = 1 \dots 100$ sites).
   - Upgraded canvas resolution from $1200 \times 760$ to **4K UHD+ ($3840 \times 2400$)**, a $10.1\times$ increase in total pixel resolution.
   - Built resolution-aware proportional scaling across typography, drop shadows, card margins, cell stroke borders, and adaptive site markers.
   - Implemented dynamic Poisson-area site spacing calculation ensuring fast placement without clustering even at 100 sites.
   - Expanded color palette to 20 vibrant cohesive pastel shades.
   - Upgraded web explorer with interactive site slider, quick presets ($2, 10, 25, 50, 75, 100$), and dynamic button generation.

14. **Graph Traversal Animations (BFS & DFS Walkthroughs)**:
   - Built an end-to-end graph traversal animation engine ([`2026-09-05/bfs_dfs_tutorial/traversal_animator.py`](2026-09-05/bfs_dfs_tutorial/traversal_animator.py)) rendering high-definition 1080p 60fps videos via PyCairo and FFmpeg.
   - Implemented force-directed spring graph layouts, animated signal packet pulses traveling across edges, active traversal path edge glows, and live real-time data structure HUDs (FIFO Queue for BFS, LIFO Stack for DFS).
   - Produced single-algorithm exploration videos (`bfs_traversal.mp4`, `dfs_traversal.mp4`) as well as a synchronized side-by-side comparative video (`bfs_dfs_comparison.mp4`) contrasting breadth-oriented wavefront expansion against depth-oriented branch exploration on the identical topology.
   - Integrated with automated unit tests ([`test_traversal_animator.py`](2026-09-05/bfs_dfs_tutorial/test_traversal_animator.py)), GitHub Actions workflow ([`generate_pdf_for_traversel.yml`](.github/workflows/generate_pdf_for_traversel.yml)), and the GitHub Pages media showcase website.

15. **Manim Matrix Multiplication & Linear Transformation Animations (`2026-09-12`)**:
   - Built a comprehensive mathematical animation suite using Manim Community (`v0.21.0`) located in [`2026-09-12/matrix_multiplication_manim/`](2026-09-12/matrix_multiplication_manim/).
   - **Space Transformations**: Visualizes 2D space deformation under non-uniform scaling ($S = \begin{bmatrix} s_x & 0 \\ 0 & s_y \end{bmatrix}$), horizontal/vertical shearing ($H_x = \begin{bmatrix} 1 & k \\ 0 & 1 \end{bmatrix}$), and general stretching. Highlights that grid lines remain parallel and evenly spaced, basis vectors $\hat{i}, \hat{j}$ transform into matrix columns, and determinant $\det(M)$ dictates signed area scaling.
   - **Eigenvectors & Invariant Directions**: Constructs randomized symmetric transformations via spectral decomposition $A = P D P^T$ with guaranteed real, distinct eigenvalues $\lambda_1, \lambda_2 \in [0.5, 2.0]$ and orthogonal eigenvectors $\vec{v}_1, \vec{v}_2$. Illustrates invariant eigen-lines along which vectors scale without rotating ($A\vec{v} = \lambda\vec{v}$), contrasted against arbitrary test vectors that tilt and rotate off their span.
   - **Matrix Multiplication as Spatial Composition**: Visually demonstrates that multiplying two matrices $C = B \cdot A$ represents sequential linear transformations. Compares applying transformation $A$ followed by $B$ step-by-step against applying composite matrix $C$ directly, proving that both yield the identical space deformation.
   - **Procedural Randomization**: Generates fresh random transformation parameters, shear coefficients, rotation angles, eigenvalues, and matrices on every run unless explicitly seeded.
   - **Automated Hourly Workflow & Site Integration**: Added dedicated hourly GitHub Actions workflow ([`generate_matrix_multiplication_animation.yml`](.github/workflows/generate_matrix_multiplication_animation.yml)), mathematical unit tests ([`test_matrix_math.py`](2026-09-12/matrix_multiplication_manim/test_matrix_math.py)), standalone CLI driver ([`generate_matrix_animation.py`](2026-09-12/matrix_multiplication_manim/generate_matrix_animation.py)), technical guide ([`README.md`](2026-09-12/matrix_multiplication_manim/README.md)), and web explorer integration.

16. **Interactive Probability Lab & GitHub Actions Pipeline Enhancements**:
   - Built a comprehensive, zero-dependency interactive **Probability Lab** web application ([`probability/index.html`](probability/index.html) and [`.github/scripts/probability.html`](.github/scripts/probability.html)) featuring 10 intuitive visual modules:
     1. **Law of Large Numbers (LLN)**: Real-time 3D animated coin flip simulation, running frequency convergence graph ($\hat{p} \to p$), 95% Wilson confidence intervals, streak tracking, and customizable coin bias.
     2. **Galton Board (Quincunx & CLT)**: 60fps HTML5 Canvas 2D physics simulation with triangular pin grids ($6 \dots 16$ rows), adjustable left/right bounce probability $p$, gravity, restitution, bin accumulation, and real-time Gaussian & Binomial probability density overlays.
     3. **Dice Rolling & Central Limit Theorem**: Roll $k = 1 \dots 8$ dice simultaneously across various distributions (fair, loaded, bimodal, exponential). Features 3D dice rendering with physics animations, empirical sum histograms, theoretical PMF step curves, and limiting Gaussian bell curves.
     4. **Monty Hall Paradox**: Playable 3-door game show interface (door selection, host goat reveal, switch/stay prompt) plus a high-speed Monte Carlo simulator (up to 10,000 automated rounds) demonstrating the counterintuitive $2/3$ vs $1/3$ winning ratio.
     5. **Bayes' Theorem & Diagnostic Screener**: Visualizes clinical diagnostic testing via an interactive 1,000-person waffle matrix color-coded by True Positive, False Positive, False Negative, and True Negative counts. Sliders for base rate (prevalence), test sensitivity ($P(T+|D+)$), and specificity ($P(T-|D-)$) dynamically demonstrate the Base Rate Fallacy and posterior probability $P(D+|T+)$.
     6. **Birthday Paradox (Collision Probability)**: Interactive classroom generator with live calendar matrix and collision detection, calculating exact combinatorial probabilities $P(N) = 1 - \prod (1 - k/365)$ and explaining why 23 people suffice for a $>50\%$ collision chance via $\binom{N}{2}$ pairwise comparisons.
     7. **Buffon's Needle**: Geometric probability simulation estimating $\pi \approx \frac{2LN}{DC}$ by dropping needles across parallel floorboards with real-time crossing collision detection and convergence plotting.
     8. **Gambler's Ruin & Random Walk**: Stochastic wealth walk simulation with absorbing barriers at $\$0$ (ruin) and target $\$N$ (bank break). Features animated multi-path trajectories and analytical ruin formulas showing the devastating impact of negative expected return and the house edge.
     9. **Distributions Sandbox**: Interactive PMF/PDF and CDF visualizer for Normal, Binomial, Poisson, Exponential, and Uniform distributions. Features live parameter sliders, statistics breakdown ($\mu, \sigma^2, \text{skewness}$), and dynamic interval area integration $P(x_1 \le X \le x_2)$.
     10. **Marble Urn Sampling**: Visual urn draw experiment comparing independent sampling with replacement (Binomial) against dependent sampling without replacement (Hypergeometric) with card probability breakdowns.
   - **CI Subprocess Bug Fix (`traversal_animator.py`)**: Fixed `ValueError: flush of closed file` occurring in Python 3.12+ when `proc.stdin.close()` was followed by `proc.communicate()`. Replaced with non-redundant stdin stream closing, direct `proc.stderr.read()`, and `proc.wait()` across both single and comparative video renderers. Added dedicated unit test verification (`test_render_standalone_encoding`).
   - **GitHub Pages & CI/CD Pipeline Integration**:
     - Updated `.github/workflows/deploy_pages.yml` to trigger automatically on pushes to `master` and after completion of `Generate Matrix Multiplication Animations`.
     - Updated `.github/scripts/build_pages.py` to copy the probability lab and automatically discover matrix multiplication animations across `artifacts-src`, `master-src`, and repository root fallbacks.
     - Updated `.github/scripts/template.html` with a dedicated **Probability Lab** tab, top navigation link, and seamless iframe embedding.
     - Optimized `.github/workflows/generate_matrix_multiplication_animation.yml` with `--no-install-recommends` for streamlined package installations.

17. **RSA Cryptosystem & Foundational Number Theory Manim Suite (`2026-09-12`)**:
   - Created folder [`2026-09-12/rsa_key_generation_manim/`](2026-09-12/rsa_key_generation_manim/) featuring 5 detailed Manim animations:
     1. **Fermat's Little Theorem (`FermatsLittleTheoremScene`)**: Proves $a^{p-1} \equiv 1 \pmod p$ for prime $p$ and $\gcd(a, p) = 1$. Visualizes the residue set $S = \{1, \dots, p-1\}$ and demonstrates that multiplying each element by $a$ modulo $p$ creates an exact permutation of $S$, leading to the cancellation of $(p-1)!$ and yielding $a^{p-1} \equiv 1 \pmod p$.
     2. **Bézout's Identity & Extended Euclidean Algorithm (`BezoutsIdentityScene`)**: Visualizes how any two integers $a, b$ satisfy $a x + b y = \gcd(a, b)$. Illustrates step-by-step forward Euclidean division and backward substitution for RSA numbers ($e=17, \phi(n)=40$), isolating $1 = 3 \cdot 40 - 7 \cdot 17 \implies 17 \cdot 33 \equiv 1 \pmod{40}$ to find the private decryption exponent.
     3. **Euler's Totient Theorem & Sieve Grid (`EulersTheoremScene`)**: Generalizes modular exponentiation to composite moduli ($a^{\phi(n)} \equiv 1 \pmod n$). Visualizes the $p \times q$ integer grid ($n=15$), eliminating multiples of $p=3$ and $q=5$ to prove $\phi(pq) = pq - p - q + 1 = (p-1)(q-1)$. Proves that multiplying the reduced residue system by $a$ permutes the set, establishing $a^{\phi(n)} \equiv 1 \pmod n$.
     4. **Modular Multiplicative Inverse (`ModularInverseScene`)**: Demonstrates why standard division does not exist in modular arithmetic and why an inverse $x \equiv a^{-1} \pmod m$ exists if and only if $\gcd(a, m) = 1$. Features a circular modular clock with step traces, contrasting coprime success ($3 \cdot 4 \equiv 1 \pmod{11}$) against non-coprime trapping ($4x \pmod{12}$ trapped in $\{0, 4, 8\}$).
     5. **Full RSA Key Generation & Synthesis (`RSAKeyGenerationScene`)**: Integrates all 4 theorems into the complete cryptographic protocol. Walks through prime selection ($p=11, q=13$), modulus calculation ($n=143$), totient calculation ($\phi(n)=120$), public key selection ($e=7$), private key computation via Bézout ($d=103$), live encryption of plaintext $M=9 \to C=48$, live decryption $C=48 \to M'=9$, and the complete algebraic proof of correctness synthesized from Euler's Totient Theorem ($M^{ed} = M^{1+k\phi(n)} \equiv M \pmod n$).
   - **Tested and Verified Locally**: All 5 scenes tested and compiled into high-definition MP4 video files in `rendered_animations/` with complete JSON metadata in `rsa_manifest.json`.
   - **Mathematical Unit Tests (`test_rsa_math.py`)**: 6 comprehensive unit tests verifying primality, Extended Euclidean algorithm, Bézout coefficients, modular inverses, totient calculations, and RSA keypair generation.
   - **CI/CD Automation & GitHub Pages Explorer Integration**:
     - Added hourly GitHub Actions workflow ([`.github/workflows/generate_rsa_key_generation_animation.yml`](.github/workflows/generate_rsa_key_generation_animation.yml)) to run tests, render videos, publish to GitHub Releases, and commit to the `artifacts` branch.
     - Updated [`.github/workflows/deploy_pages.yml`](.github/workflows/deploy_pages.yml) to trigger on completion of RSA animation runs.
     - Updated [`.github/scripts/build_pages.py`](.github/scripts/build_pages.py) and [`.github/scripts/template.html`](.github/scripts/template.html) with a dedicated **RSA Cryptosystem** tab, spotlight player, and interactive cards for all 5 animation scenes.

18. **Graph Traversal Animations: 2K QHD Resolution, Anti-Aliasing & Pedagogical Pacing Upgrade (`2026-09-12`)**:
    - **Slower Pedagogical Pacing**: Replaced rapid 0.5s transitions with deliberate, easily readable pacing (default 1.8s per step, ~54 frames at 30fps). Added `--speed` presets (`slow` = 2.5s/step, `normal` = 1.8s/step, `fast` = 1.0s/step) and `--step-duration` CLI flag. Viewers can now comfortably read the step action cards, follow the active node glowing pulse, and observe Queue/Stack state changes.
    - **Fluid Signal Motion Easing**: Replaced linear signal motion with smoothstep ease-in-out interpolation ($S(t) = 3t^2 - 2t^3$) so the electric cyan signal packet accelerates out of the parent node and decelerates into the neighbor node.
    - **Upgraded Default Resolution to 2K QHD (2560×1440)**: Raised default canvas dimensions from 1080p to 2K QHD (`2560x1440`), with full support for 4K UHD (`3840x2160`), 1080p, and 720p via `--preset`.
    - **Resolution-Independent Dynamic Scaling**: Built a responsive scaling engine ($s = \min(W/1920, H/1080)$) across both standalone (`TraversalVideoRenderer`) and comparative dual-panel (`ComparativeTraversalRenderer`) engines, dynamically computing margins, panel bounds, force-directed graph stages, node radii, stroke widths, typography, cards, and bottom mini-HUDs.
    - **Cairo Vector Anti-Aliasing**: Applied `cairo.ANTIALIAS_BEST`, `cairo.LINE_CAP_ROUND`, and `cairo.LINE_JOIN_ROUND` across all contexts. Configured Cairo `FontOptions` with `ANTIALIAS_BEST`, `HINT_STYLE_FULL`, `HINT_METRICS_ON`, and `SUBPIXEL_ORDER_RGB` for razor-sharp typography and vector contours.
    - **Crisp Animation Video Compression**: Configured FFmpeg with `-tune animation -crf 17 -preset medium -pix_fmt yuv420p` and `-loglevel error`, producing clean vector lines and dark-mode contrast with compact file sizes (~2-5 MB, well below the 95MB limit).
    - **Unit Test Coverage**: Added tests in `test_traversal_animator.py` verifying anti-aliasing configuration, multi-resolution scaling (1080p, 2K, 4K), and custom step pacing (all 9 unit tests passing).
    - **Frontend & Documentation Updates**: Updated `template.html` spotlight metadata, `README.md` CLI guide, and repository tables to feature 2K anti-aliased traversal animations.
