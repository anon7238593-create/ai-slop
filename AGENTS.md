# Specialized Agents Directory & Architecture Guide

Welcome to the **`ai-slop`** agent system. This document outlines the specialized agents designed for this repository, what tasks they handle, and how Antigravity automatically routes and invokes them.

---

## ⚡ Automatic Agent Invocation Protocol (Zero Manual Invocation Required)

**Rule for Antigravity**: The user does **not** need to manually invoke, name, or remember any agent. Antigravity MUST automatically inspect every user prompt, detect the task domain, and immediately adopt the appropriate agent persona, apply its specialized knowledge, and enforce its safety invariants.

### Automatic Intent Routing Table

| If User Asks About / Works On | Automatically Activate Agent | Reference File & Skill |
|---|---|---|
| Workflows, CI/CD pipelines, `.github/workflows/`, `push_artifacts.sh`, `create_release.sh`, GitHub Releases, failed action runs, or branch sync errors | **GitHub Actions & CI/CD Specialist** | [**`agents/github-actions-checker.md`**](file:///home/aman/dev/ai-slop/agents/github-actions-checker.md)<br>`skills/github-actions-checker` |
| Bouncing balls, 2D physics simulation, elastic collision, `ball_collision.py`, speed conservation, spatial audio synthesis, FFmpeg piping, batch videos | **Simulation & Physics Video Generator** | [**`agents/simulation-physics-generator.md`**](file:///home/aman/dev/ai-slop/agents/simulation-physics-generator.md)<br>`skills/simulation-physics-generator` |
| Euclidean GCD tiling (`gcd_grid.py`), 4K Voronoi half-plane clipping, Graph Theory (BFS/DFS, shortest paths), Manim animations (Matrix / RSA), SVGs | **Mathematical & Algorithmic Visualizer** | [**`agents/math-algorithm-visualizer.md`**](file:///home/aman/dev/ai-slop/agents/math-algorithm-visualizer.md)<br>`skills/math-algorithm-visualizer` |
| GitHub Pages site, web showcase, `template.html`, `build_pages.py`, `#collision` / `#gcd` / `#voronoi` tabs, video spotlight player, CSS dark mode | **Frontend & GitHub Pages Specialist** | [**`agents/frontend-pages-explorer.md`**](file:///home/aman/dev/ai-slop/agents/frontend-pages-explorer.md)<br>`skills/frontend-pages-explorer` |
| Running unit tests (`test_*.py`), manifest validation, schema checks, C/Yacc compilation, workflow YAML linting, pre-commit regressions | **QA, Test Runner & Validation Specialist** | [**`agents/qa-tester-validator.md`**](file:///home/aman/dev/ai-slop/agents/qa-tester-validator.md)<br>`skills/qa-tester-validator` |
| Creating a new experiment, new date folder (`YYYY-MM-DD/<feature>/`), generator CLI, end-to-end integration across pipelines and site | **Experiment Scaffolding & Integration Specialist** | [**`agents/experiment-scaffolder.md`**](file:///home/aman/dev/ai-slop/agents/experiment-scaffolder.md)<br>`skills/experiment-scaffolder` |

---

## 🤖 Automatic Multi-Agent Delegation

When a user request spans multiple domains (e.g. *"Create a new sorting algorithm visualizer with an automated GitHub workflow and showcase it on the web"*), Antigravity will **not** ask the user to pick an agent. Instead, Antigravity will automatically orchestrate the required roles in sequence:

```
User Prompt (e.g. "Add a new cellular automata generator")
   │
   ├─► 1. Experiment Scaffolder: Creates YYYY-MM-DD/automata/, CLI, test suite, README
   │
   ├─► 2. Math & Algorithm Visualizer: Validates algorithmic correctness & SVG output
   │
   ├─► 3. QA & Test Runner: Runs python3 -m unittest discover to guarantee tests pass
   │
   ├─► 4. GitHub Actions Specialist: Sets up .github/workflows/generate_automata.yml with push_artifacts.sh
   │
   └─► 5. Frontend Pages Specialist: Wires manifest.json into build_pages.py and template.html
```

---

## Global Repository Guidelines & Safety Protocols

1. **GitHub 100MB File Limit Protection**:
   - Files $\ge 95\text{MB}$ must **never** be committed into Git history.
   - Use `.github/scripts/create_release.sh` to publish large assets directly to GitHub Releases.
2. **Atomic Artifact Publishing**:
   - Never commit directly to the `artifacts` branch via standard `git push`. Always use `.github/scripts/push_artifacts.sh` to prevent overwriting parallel job outputs.
3. **Reproducibility & Verification**:
   - All procedural generators must support explicit seeds (`--seed`).
   - Every algorithmic feature must include a corresponding unit test file (`test_*.py`).
4. **Speed Conservation Invariant**:
   - For all collision simulations, $\|\vec{v}_{child}\| = \|\vec{v}_{parent}\|$ must be preserved unless the user explicitly asks for energy dissipation.
