---
name: experiment-scaffolder
description: >-
  Automatically use this skill whenever creating, prototyping, or scaffolding a new experiment, project directory (YYYY-MM-DD/<feature>/), generator script, or setting up new algorithmic visualizations with CI/CD wiring.
---

# Experiment Scaffolding & Integration Skill

## Purpose
Rapidly scaffold, implement, document, and wire up new AI-generated experiments following repository standards.

## Standard Layout
```text
YYYY-MM-DD/<experiment_name>/
├── <experiment_name>.py      # Standalone CLI generator (--seed, --output)
├── test_<experiment_name>.py # Unit tests
└── README.md                 # Mathematical background & CLI usage
```

## Checklist
1. Create directory: `mkdir -p $(date +%Y-%m-%d)/<name>`
2. Implement CLI with `--seed` support and unit tests.
3. Verify test suite passes.
4. Add GitHub Actions workflow (`.github/workflows/generate_<name>.yml`) using `push_artifacts.sh`.
5. Connect manifest to `build_pages.py` and update `SUMMARY.md`.
