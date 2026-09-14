# Contributing to AI Slop 🤝

Thank you for your interest in contributing! This guide walks you through the development workflow, testing conventions, and expectations for pull requests.

---

## Table of Contents

- [Development Setup](#development-setup)
- [Creating New Experiments](#creating-new-experiments)
- [Testing & Validation](#testing--validation)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Agent Integration](#agent-integration)
- [GitHub Actions & Workflows](#github-actions--workflows)
- [Style Guide](#style-guide)

---

## 🛠️ Development Setup

### Prerequisites

- **Python 3.9+** (3.12 recommended)
- **pip** or **conda** for dependency management
- **Git** for version control
- **Graphviz** (for graph visualizations)
  - macOS: `brew install graphviz`
  - Ubuntu/Debian: `sudo apt-get install graphviz`
  - Windows: Download from [graphviz.org](https://graphviz.org/download/)
- **FFmpeg** (optional, for video generation)
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/anon7238593-create/ai-slop.git
cd ai-slop

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install development dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt

# 4. Verify setup
python3 agents/registry.py  # Should show all agents as valid
python3 -m pytest --version  # Should work
```

### Visual Studio Code Setup (Optional)

Add to `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["2026-09-*/**/test_*.py"],
  "editor.formatOnSave": true
}
```

---

## 🎯 Creating New Experiments

### Folder Structure Convention

New experiments follow the `YYYY-MM-DD/<feature-name>/` convention:

```
2026-09-15/my-new-feature/
├── README.md                    (experiment overview & usage)
├── main.py                      (entry point)
├── utils.py                     (helper functions)
├── test_main.py                 (unit tests)
├── requirements.txt             (dependencies)
└── output/                      (generated files, .gitignored)
```

### Quick Start Template

#### `README.md`

```markdown
# My New Feature

Brief description of what this experiment does.

## Quick Start

```bash
python3 main.py --help
```

## Requirements

- Python 3.9+
- numpy, matplotlib (optional)

## Usage Examples

```bash
# Generate default visualization
python3 main.py

# Custom parameters
python3 main.py --param1 value --seed 12345
```

## Testing

```bash
python3 -m pytest test_main.py -v
```
```

#### `main.py`

```python
#!/usr/bin/env python3
"""
My New Feature - Description.
"""

import argparse
from pathlib import Path


def main(args):
    """Main entry point."""
    print(f"Running with args: {args}")
    # TODO: Implement feature


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="My new feature")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    args = parser.parse_args()
    
    Path(args.output).mkdir(exist_ok=True)
    main(args)
```

#### `test_main.py`

```python
#!/usr/bin/env python3

import unittest
from main import main  # Import your functions


class TestMain(unittest.TestCase):
    """Test suite for main module."""

    def test_main_runs(self):
        """Basic sanity test."""
        # Simple test that your code doesn't crash
        from argparse import Namespace
        args = Namespace(seed=42, output="/tmp/test")
        # Should not raise an exception
        main(args)


if __name__ == "__main__":
    unittest.main()
```

### Using the Experiment Scaffolder (Future)

Once fully implemented, you'll be able to:

```bash
python3 agents/experiment-scaffolder.py --name my-feature --date 2026-09-15
```

This will auto-generate the folder structure and boilerplate.

---

## ✅ Testing & Validation

### Writing Tests

- **Naming:** Test files should be `test_<module>.py` in the same directory
- **Framework:** Use Python's built-in `unittest` or `pytest`
- **Coverage:** Aim for at least 70% line coverage

### Running Tests Locally

```bash
# Run all tests in the repository
python3 -m pytest 2026-09-*/**/test_*.py -v

# Or using unittest
python3 -m unittest discover 2026-09- -p test_*.py -v

# Run specific test file
python3 -m pytest 2026-09-05/graph_theory/test_connectivity.py -v

# Run with coverage
pip install coverage
coverage run -m pytest 2026-09-*/**/test_*.py
coverage report
```

### Validation Checklist

Before submitting a PR, verify:

- [ ] **Tests pass:** `python3 -m pytest` succeeds
- [ ] **Agent registry is valid:** `python3 agents/registry.py` shows no errors
- [ ] **Code is clean:**
  ```bash
  pip install black pylint mypy
  black 2026-09-*
  pylint 2026-09-* --exit-zero
  mypy 2026-09-* --ignore-missing-imports
  ```
- [ ] **No large files:** Check that files are <100MB
- [ ] **Documentation is complete:** README.md exists with usage examples
- [ ] **Reproducibility:** All generators support `--seed` parameter

---

## 🔀 Submitting Pull Requests

### Branch Naming Convention

- **Features:** `feat/<feature-name>`
- **Bug fixes:** `fix/<issue-description>`
- **Documentation:** `docs/<change-description>`
- **Tests:** `test/<test-description>`

Examples:
- `feat/add-cellular-automata`
- `fix/graph-traversal-edge-case`
- `docs/improve-readme`

### Workflow

```bash
# 1. Create a new branch
git checkout -b feat/your-feature-name

# 2. Make your changes
# ... edit files, add tests, etc.

# 3. Run tests and validation
python3 -m pytest 2026-09-*/**/test_*.py -v
python3 agents/registry.py

# 4. Commit your changes
git add .
git commit -m "feat: add new feature

- Describe what the feature does
- Keep commit messages concise
- Reference issues: 'Closes #123'"

# 5. Push your branch
git push origin feat/your-feature-name

# 6. Open a pull request on GitHub
# - Give it a clear title
# - Reference related issues
# - Describe what changed and why
```

### Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] New experiment/feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Test addition
- [ ] Workflow/CI improvement

## Testing
- [ ] All existing tests pass
- [ ] New tests added for this change
- [ ] Tested locally with at least one example

## Checklist
- [ ] Code follows the project's style guide
- [ ] Documentation is updated
- [ ] No new warnings are introduced
- [ ] Files are <100MB
- [ ] Agent registry validates successfully

## Screenshots (if applicable)
If visualization or UI changes, include screenshots.

## Related Issues
Closes #123
```

### Review Expectations

- **Response time:** Reviews typically within 2-3 days
- **Feedback:** May request changes or improvements
- **Merging:** Maintainers will merge after approval
- **CI must pass:** All GitHub Actions checks must be green

---

## 🤖 Agent Integration

### Registering a New Agent

If you create or modify an agent:

1. **Update `agents/registry.py`:**
   ```python
   "my-new-agent": {
       "doc": "agents/my-new-agent.md",
       "description": "What this agent does",
       "keywords": ["keyword1", "keyword2"],
   },
   ```

2. **Create agent documentation** at `agents/my-new-agent.md`

3. **Update `AGENTS.md`** routing table with the new agent

4. **Validate:**
   ```bash
   python3 agents/registry.py  # Should show your agent as valid
   python3 -m pytest agents/test_registry.py -v
   ```

### Agent Conventions

- **Naming:** Use kebab-case (e.g., `my-new-agent`)
- **Documentation:** Markdown file in `agents/` directory, ≥500 chars
- **Keywords:** List 3-5 keywords that trigger this agent
- **No duplication:** Each agent must have a unique documentation path

---

## 🔄 GitHub Actions & Workflows

### Adding a New Workflow

If you create a new generator or experiment that should run automatically:

1. **Create `.github/workflows/generate_my_feature.yml`:**
   ```yaml
   name: Generate My Feature
   
   on:
     workflow_dispatch:  # Manual trigger
     schedule:
       - cron: "0 */6 * * *"  # Every 6 hours
   
   permissions:
     contents: write
     actions: read
   
   jobs:
     generate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: "3.12"
         - run: python3 2026-09-XX/my_feature/generate.py --output /tmp/output
         - run: bash .github/scripts/push_artifacts.sh
           env:
             TARGET_DIR: my-feature
             ARTIFACT_DIRECTORY: /tmp/output
   ```

2. **Update `.github/workflows/deploy_pages.yml`** to trigger on your workflow:
   ```yaml
   workflow_run:
     workflows:
       - "Generate My Feature"  # Add this
   ```

3. **Test locally** (simulate):
   ```bash
   python3 2026-09-XX/my_feature/generate.py --output /tmp/test
   ```

---

## 📝 Style Guide

### Python

- **Format:** Follow PEP 8; use `black` for consistency
- **Type hints:** Add type annotations to functions (Python 3.9+)
- **Docstrings:** Use triple-quoted docstrings for modules, classes, and functions
- **Line length:** Max 100 characters

```python
def my_function(x: int, y: str) -> str:
    """
    Brief description.
    
    Args:
        x: Description of x
        y: Description of y
    
    Returns:
        Description of return value
    """
    return f"{x}: {y}"
```

### Markdown

- **Headers:** Use `#` for top-level, `##` for sections, etc.
- **Code blocks:** Specify language (e.g., ```python```)
- **Links:** Use [text](url) format
- **Lists:** Use `-` for unordered, `1.` for ordered

### Commit Messages

- **Format:** `<type>: <subject>`
- **Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `ci`
- **Subject:** Use imperative mood ("add" not "added")
- **Body:** Explain *why*, not *what*

```
feat: add Monty Hall simulation to probability lab

Implements interactive Monty Hall paradox with Monte Carlo solver.
Demonstrates why switching doors increases win probability from 33% to 67%.

Closes #42
```

---

## 🐛 Reporting Issues

Found a bug or have a feature request?

1. **Check existing issues** to avoid duplicates
2. **Provide context:**
   - What did you expect to happen?
   - What actually happened?
   - How can we reproduce it?
3. **Include environment info:**
   ```bash
   python3 --version
   pip show numpy matplotlib  # List relevant packages
   ```

---

## ❓ Questions?

- **Documentation:** See [`README.md`](./README.md) and individual project READMEs
- **Architecture:** Check [`AGENTS.md`](./AGENTS.md)
- **Issues:** Open a GitHub Issue
- **Discussions:** Start a GitHub Discussion

---

**Thank you for contributing! 🎉**
