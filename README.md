# AI Slop 🎨

A modular repository for AI-generated educational content and visualization generators. Experiments with **graph algorithms**, **physics simulations**, **probability theory**, **cryptography animations**, and more—all with sophisticated GitHub Actions automation and live GitHub Pages showcase.

> **What it is:** A collection of experiments, prototypes, odd ideas, useful snippets, and things that may or may not be worth keeping. The contents are intentionally eclectic.

---

## 🚀 Quick Links

- **📊 Live Showcase:** [GitHub Pages](https://anon7238593-create.github.io/ai-slop/) – Interactive media explorer with all generated visualizations
- **📚 Detailed Guides:** See [`AGENTS.md`](./AGENTS.md) for architecture; [`CONTRIBUTING.md`](./CONTRIBUTING.md) for development
- **🔬 Experiments:** Browse individual project folders (e.g., `2026-09-05/`, `2026-09-08/`, etc.)

---

## 📋 Table of Contents

- [What's Inside](#whats-inside)
- [Quick Start](#quick-start)
- [Running Experiments Locally](#running-experiments-locally)
- [Architecture & Agents](#architecture--agents)
- [Repository Guidelines](#repository-guidelines)
- [Contributing](#contributing)

---

## 🏛️ What's Inside

Each dated folder (`YYYY-MM-DD/`) contains a collection of thematic experiments:

### Featured Experiments

#### **2026-09-05: Graph Theory & Visualization**
- **BFS/DFS Graphviz Walkthrough** – Interactive step-by-step PDF visualizations of breadth-first and depth-first search
- **Graph Theory Playground** – Educational curriculum with clear Python implementations (stdlib only)
- [→ Full README](./2026-09-05/README.md)

#### **2026-09-08: GCD Grids & Euclidean Algorithm**
- Random tiling visualizations using the Euclidean algorithm
- 4K SVG outputs, hundreds of unique seeds
- Deployed to GitHub Pages via automated workflows

#### **2026-09-09: Physics Simulations**
- 2D bouncing ball collision simulations with speed conservation
- Video generation via FFmpeg with configurable ball counts
- High-performance batch processing (100–1000 balls per video)

#### **2026-09-12: Manim Animations**
- Matrix multiplication transformations and linear algebra visualizations
- RSA key generation & number theory animations
- Educational mathematical storytelling

#### **probability/: Interactive Probability Lab**
- 10 interactive learning modules (Monty Hall, Birthday Paradox, Bayes' Theorem, etc.)
- Pure HTML5/Canvas, zero external dependencies
- Deployed standalone and embedded in GitHub Pages showcase
- [→ Full README](./probability/README.md)

---

## 🏃 Quick Start

### For Visual Learners (BFS/DFS Interactive)

```bash
cd 2026-09-05/bfs_dfs_tutorial
python3 bfs_dfs_visualizer.py --algorithm both
# Output: PDF visualizations in output/bfs/ and output/dfs/
```

**Requirements:**
- Python 3.7+
- Graphviz (`brew install graphviz` on macOS)

### For Theory Learners (Graph Theory)

```bash
cd 2026-09-05/graph_theory
python3 -m unittest -v  # Run all tests

cd foundations
cat README.md         # Read the theory
python3 graph_demo.py # Run interactive examples
```

### For Experimenters

```bash
cd 2026-09-05/graph_theory/traversals
python3 traversals.py
# Edit traversals.py, modify the graph, re-run to see effects
```

### Probability Lab (No Installation Required)

```bash
# View locally
open probability/index.html

# Or visit deployed version
# https://anon7238593-create.github.io/ai-slop/probability.html
```

---

## 🔧 Running Experiments Locally

### Prerequisites

- **Python 3.9+** (3.12 recommended for latest features)
- **pip** for dependency management
- **Graphviz** (for graph visualizations)
- **FFmpeg** (for video generation)
- **Git** for version control

### Installation

```bash
# Clone the repository
git clone https://github.com/anon7238593-create/ai-slop.git
cd ai-slop

# (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all unit tests
python3 -m pytest 2026-09-*/**/test_*.py -v

# Or use unittest
python3 -m unittest discover 2026-09- -p test_*.py -v

# Validate agent registry
python3 agents/registry.py
```

### Running Workflows Locally (Simulation)

```bash
# Example: Generate GCD grids (this generates 100 random SVGs)
cd 2026-09-08/gcd_python
python3 -c "
from gcd_grid import fresh_seed, random_dimensions, svg_visualization
from pathlib import Path

out = Path('/tmp/gcd-demo')
out.mkdir(exist_ok=True)

for i in range(5):
    seed = fresh_seed()
    width, height = random_dimensions(seed)
    svg, _, _, _ = svg_visualization(width, height, seed)
    (out / f'gcd-{width}-{height}.svg').write_text(svg)
    print(f'Generated: gcd-{width}-{height}.svg')

print(f'Output: {out}')
"
```

---

## 🤖 Architecture & Agents

This repository uses a **specialized agent system** for automated CI/CD and code generation:

### Key Agents

1. **Master Orchestrator** – Coordinates multi-component features and parallel workflows
2. **GitHub Actions & CI/CD Specialist** – Manages `.github/workflows/`, release publishing, artifact management
3. **Mathematical & Algorithmic Visualizer** – Graph theory, Manim animations, Voronoi diagrams
4. **Simulation & Physics Generator** – 2D physics, collision detection, video generation
5. **Frontend & GitHub Pages Specialist** – Static site generation, web showcase
6. **QA & Test Runner** – Unit tests, validation, linting
7. **Experiment Scaffolder** – Sets up new `YYYY-MM-DD/<feature>/` folders with boilerplate
8. **Activity & State Sync** – Logs milestones, maintains state across parallel jobs

See [`AGENTS.md`](./AGENTS.md) for complete agent routing and multi-agent delegation workflows.

### Validation

All agents are registered in `agents/registry.py`. To validate:

```bash
python3 agents/registry.py
```

---

## 📦 Repository Structure

```
ai-slop/
├── README.md                                    (this file)
├── CONTRIBUTING.md                              (contribution guidelines)
├── AGENTS.md                                    (agent architecture)
├── .github/
│   ├── workflows/
│   │   ├── deploy_pages.yml                    (GitHub Pages deployment)
│   │   ├── generate_*.yml                      (various generators)
│   │   └── ...
│   └── scripts/
│       ├── build_pages.py                      (static site builder)
│       ├── create_release.sh                   (GitHub Releases publisher)
│       ├── push_artifacts.sh                   (atomic artifact pusher)
│       └── ...
├── agents/
│   ├── registry.py                             (agent registry & validation)
│   ├── test_registry.py                        (registry tests)
│   ├── master-orchestrator.md
│   ├── github-actions-checker.md
│   └── [8 more agent docs]
├── 2026-09-05/                                 (Graph Theory & Visualization)
│   ├── bfs_dfs_tutorial/
│   │   ├── bfs_dfs_visualizer.py
│   │   ├── README.md
│   │   └── output/                            (generated PDFs)
│   └── graph_theory/
│       ├── foundations/
│       ├── traversals/
│       ├── shortest_paths/
│       └── ...
├── 2026-09-08/                                 (GCD Grids)
├── 2026-09-09/                                 (Physics Simulations)
├── 2026-09-12/                                 (Manim Animations)
├── probability/                                (Interactive Probability Lab)
└── requirements-dev.txt                        (development dependencies)
```

---

## 🛡️ Repository Guidelines

### File Size Limits

- **GitHub 100MB limit:** Files ≥ 95MB must be published via GitHub Releases only, never committed to Git history
- Use `.github/scripts/create_release.sh` to publish large assets
- Use `.github/scripts/push_artifacts.sh` for atomic publishing to the `artifacts` branch

### Testing & Validation

- **All experiments must include unit tests** (`test_*.py`)
- Tests run automatically in CI; see `.github/workflows/test.yml`
- Run locally: `python3 -m pytest` or `python3 -m unittest discover`

### Reproducibility

- All procedural generators must support `--seed` for reproducibility
- Document expected inputs/outputs in README files
- Include minimal example usage in docstrings

---

## 🤝 Contributing

We welcome contributions! See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for:

- **Development Setup** – How to set up your local environment
- **Creating New Experiments** – Folder structure, scaffolding, boilerplate
- **Adding Tests** – Testing conventions and CI integration
- **Submitting PRs** – Workflow and review expectations
- **Agent Integration** – How to register and document new agents

### Quick Contribution Checklist

- [ ] Create a new branch: `git checkout -b feat/your-feature-name`
- [ ] Add your code and tests
- [ ] Run tests locally: `python3 -m pytest` (or `unittest`)
- [ ] Run agent validation: `python3 agents/registry.py`
- [ ] Commit with a descriptive message
- [ ] Push and open a pull request

---

## 📊 Media Showcase

All generated media is automatically published to:

- **GitHub Pages:** [Live Demo](https://anon7238593-create.github.io/ai-slop/)
- **GitHub Releases:** Large assets (videos, PDFs) → release downloads
- **Artifacts Branch:** Manifests and metadata tracking

The static site is built and deployed automatically by `.github/workflows/deploy_pages.yml`.

---

## 📚 See Also

- [Graph Theory & Visualization](./2026-09-05/README.md) – Detailed guide for BFS/DFS and graph algorithms
- [Interactive Probability Lab](./probability/README.md) – 10 interactive learning modules
- [AGENTS.md](./AGENTS.md) – Complete agent architecture and routing
- [CONTRIBUTING.md](./CONTRIBUTING.md) – Development guide and contribution workflow

---

## 📝 License

This repository is intentionally eclectic and experimental. Use, modify, and remix as you see fit.

---

**Questions?** Open an issue or check the individual project READMEs for detailed documentation.
