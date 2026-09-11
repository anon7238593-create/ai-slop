---
name: github-actions-checker
description: >-
  Automatically use this skill whenever working with GitHub Actions workflows in .github/workflows/, CI/CD pipelines, push_artifacts.sh, create_release.sh, git tree-plumbing, GitHub Releases, artifacts branch updates, or debugging failed workflow runs.
---

# GitHub Actions Checker & CI/CD Pipeline Skill

## Purpose
Ensure automated workflows, artifact publishing scripts, GitHub Releases, and GitHub Pages deployments operate reliably, securely, and efficiently without race conditions or storage bloat.

## Key Files
- Workflows: `.github/workflows/*.yml`
  - `generate_gcd_grids.yml` (Hourly GCD SVGs)
  - `generate_voronoi_diagrams.yml` (Hourly 4K Voronoi SVGs)
  - `generate_pdf_for_traversel.yml` (Hourly BFS/DFS walkthrough PDFs)
  - `generate_collision_videos.yml` (Nightly 1080p ball collision MP4s)
  - `generate_500_ball_collision_videos.yml` (Hourly GitHub Releases for 500-ball videos)
  - `generate_matrix_multiplication_animation.yml` (Manim animations)
  - `deploy_pages.yml` (GitHub Pages build & deploy)
- Scripts: `.github/scripts/`
  - `push_artifacts.sh`: Atomic Git tree-plumbing publisher to orphan `artifacts` branch with retry backoff.
  - `create_release.sh`: Handles high-capacity GitHub Releases and uploads `.zip` bundles.
  - `build_pages.py`: Aggregates manifests and compiles static site.

## Procedures

### 1. Validate Workflows
Run YAML validation before pushing changes:
```bash
python3 -c "import yaml, glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]; print('All workflows valid YAML')"
```

### 2. Verify Concurrency & Tree-Plumbing Integrity
When publishing to `artifacts`, ensure:
- The script uses `push_artifacts.sh`.
- Isolated git index (`GIT_INDEX_FILE="$TMP_INDEX" git --work-tree="$ARTIFACT_DIRECTORY" add -A`).
- Files $\ge 95\text{MB}$ are stripped from git commit and published via GitHub Releases.
- `push_artifacts.sh` has backoff retry logic.

### 3. Debug Pipeline Runs
```bash
gh run list --limit 10
gh run view <RUN_ID> --log-failed
```

## Invariants & Rules
- Never push files $\ge 95\text{MB}$ to the Git branch.
- Prevent infinite recursion loops: ignore `artifacts` and `master` where appropriate (`branches-ignore: [master, artifacts]`).
- Never use direct `git push` without conflict retry handling on `artifacts`.
