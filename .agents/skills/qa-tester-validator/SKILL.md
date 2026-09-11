---
name: qa-tester-validator
description: >-
  Automatically use this skill whenever testing code, running test suites, verifying manifest.json integrity, checking YAML workflow syntax, compiling C/Yacc parsers, or validating assets across the repository.
---

# QA, Test Runner & Validation Skill

## Purpose
Ensure no broken code, invalid manifests, regression bugs, or syntax errors enter the codebase or artifact pipelines.

## Key Test Locations
- `2026-09-09/collision/test_ball_collision.py`
- `2026-09-08/gcd_python/test_gcd_grid.py`
- `2026-09-12/matrix_multiplication_manim/test_matrix_math.py`
- `2026-09-12/rsa_key_generation_manim/test_rsa_math.py`
- `2026-09-05/yacc_test/` & `2026-09-05/statement_parser/`

## Procedures

### 1. Run All Tests
```bash
python3 -m unittest discover -s 2026-09-09/collision -p "test_*.py" -v
python3 -m unittest discover -s 2026-09-08/gcd_python -p "test_*.py" -v
python3 -m unittest discover -s 2026-09-12/matrix_multiplication_manim -p "test_*.py" -v
python3 -m unittest discover -s 2026-09-12/rsa_key_generation_manim -p "test_*.py" -v
```

### 2. Lint Shell & YAML
```bash
python3 -c "import yaml, glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]; print('YAML valid')"
bash -n .github/scripts/push_artifacts.sh
bash -n .github/scripts/create_release.sh
```
