#!/usr/bin/env python3
"""
Agent Registry & Validation System
===================================
Centralized registry of all specialized agents and their documentation.
Validates that agent documentation exists and is properly configured.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple


class AgentRegistry:
    """
    Maintains and validates the registry of all specialized agents.
    Each agent has:
    - A unique identifier (agent_id)
    - Documentation file path
    - Description of responsibilities
    - Keywords that trigger this agent
    """

    AGENTS: Dict[str, Dict[str, str | List[str]]] = {
        "master-orchestrator": {
            "doc": "agents/master-orchestrator.md",
            "description": "Multi-component architectures, large features, fleet execution, parallel subagents, batch migrations",
            "keywords": ["orchestrate", "multi-agent", "delegation", "fleet"],
        },
        "github-actions-checker": {
            "doc": "agents/github-actions-checker.md",
            "description": "Workflows, CI/CD pipelines, .github/workflows/, push_artifacts.sh, create_release.sh, GitHub Releases, failed action runs, branch sync errors",
            "keywords": ["workflow", "github actions", "ci/cd", "pipeline", "release"],
        },
        "simulation-physics-generator": {
            "doc": "agents/simulation-physics-generator.md",
            "description": "Bouncing balls, 2D physics simulation, elastic collision, ball_collision.py, speed conservation, spatial audio synthesis, FFmpeg piping, batch videos",
            "keywords": ["collision", "physics", "simulation", "video", "ffmpeg"],
        },
        "math-algorithm-visualizer": {
            "doc": "agents/math-algorithm-visualizer.md",
            "description": "Euclidean GCD tiling (gcd_grid.py), 4K Voronoi half-plane clipping, Graph Theory (BFS/DFS, shortest paths), Manim animations (Matrix / RSA), SVGs",
            "keywords": ["graph", "algorithm", "visualization", "manim", "svg", "bfs", "dfs", "voronoi"],
        },
        "frontend-pages-explorer": {
            "doc": "agents/frontend-pages-explorer.md",
            "description": "GitHub Pages site, web showcase, template.html, build_pages.py, #collision / #gcd / #voronoi tabs, video spotlight player, CSS dark mode",
            "keywords": ["github pages", "web", "frontend", "html", "css", "showcase"],
        },
        "qa-tester-validator": {
            "doc": "agents/qa-tester-validator.md",
            "description": "Running unit tests (test_*.py), manifest validation, schema checks, C/Yacc compilation, workflow YAML linting, pre-commit regressions",
            "keywords": ["test", "qa", "validation", "pytest", "unittest"],
        },
        "experiment-scaffolder": {
            "doc": "agents/experiment-scaffolder.md",
            "description": "Creating a new experiment, new date folder (YYYY-MM-DD/<feature>/), generator CLI, end-to-end integration across pipelines and site",
            "keywords": ["scaffold", "experiment", "new feature", "setup"],
        },
        "agent-factory": {
            "doc": "agents/agent-factory.md",
            "description": "Creating, designing, updating, or registering new specialized agents, skills, or subagent personas",
            "keywords": ["agent", "factory", "meta", "architect"],
        },
        "activity-summary-sync": {
            "doc": "agents/activity-summary-sync.md",
            "description": "Activity logging, state synchronization, heartbeat logs, agent coordination, inter-agent synchronization, keeping Antigravity instances in sync",
            "keywords": ["log", "sync", "state", "activity"],
        },
    }

    @classmethod
    def validate_all(cls, repo_root: Path = None) -> Tuple[bool, List[str]]:
        """
        Validate that all agents have valid documentation.

        Args:
            repo_root: Path to repository root. Defaults to current directory.

        Returns:
            Tuple of (is_valid, errors)
            - is_valid: True if all validations pass
            - errors: List of error messages (empty if valid)
        """
        if repo_root is None:
            repo_root = Path.cwd()
        else:
            repo_root = Path(repo_root)

        errors = []

        # 1. Validate each agent has a documentation file
        for agent_id, config in cls.AGENTS.items():
            doc_path = repo_root / config["doc"]
            if not doc_path.exists():
                errors.append(
                    f"❌ Agent '{agent_id}': Documentation file not found at {config['doc']}"
                )
            elif not doc_path.is_file():
                errors.append(
                    f"❌ Agent '{agent_id}': Path {config['doc']} exists but is not a file"
                )
            else:
                # Validate file has content
                content = doc_path.read_text(encoding="utf-8")
                if len(content.strip()) < 100:
                    errors.append(
                        f"⚠️  Agent '{agent_id}': Documentation is suspiciously short (<100 chars)"
                    )

        # 2. Validate AGENTS.md cross-references
        agents_md_path = repo_root / "AGENTS.md"
        if agents_md_path.exists():
            agents_md = agents_md_path.read_text(encoding="utf-8")
            for agent_id in cls.AGENTS.keys():
                if agent_id not in agents_md:
                    errors.append(
                        f"⚠️  Agent '{agent_id}': Not mentioned in AGENTS.md routing table"
                    )
        else:
            errors.append("⚠️  AGENTS.md not found; cannot cross-validate agent references")

        # 3. Validate no duplicate agent IDs or doc paths
        doc_paths = [config["doc"] for config in cls.AGENTS.values()]
        if len(doc_paths) != len(set(doc_paths)):
            errors.append("❌ Duplicate documentation paths detected in registry")

        is_valid = len(errors) == 0
        return is_valid, errors

    @classmethod
    def get_agent_by_id(cls, agent_id: str) -> Dict | None:
        """Retrieve agent configuration by ID."""
        return cls.AGENTS.get(agent_id)

    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent IDs."""
        return list(cls.AGENTS.keys())

    @classmethod
    def get_docs_path(cls, agent_id: str) -> str | None:
        """Get documentation path for an agent."""
        agent = cls.get_agent_by_id(agent_id)
        return agent["doc"] if agent else None


def validate_registry(repo_root: str = None) -> int:
    """
    Validate agent registry and print results.

    Returns:
        0 if valid, 1 if invalid
    """
    is_valid, errors = AgentRegistry.validate_all(repo_root)

    print("=" * 70)
    print("AGENT REGISTRY VALIDATION")
    print("=" * 70)
    print(f"Total Agents Registered: {len(AgentRegistry.AGENTS)}")
    print()

    if is_valid:
        print("✅ All agents valid!")
        print()
        print("Registered agents:")
        for agent_id in sorted(AgentRegistry.list_agents()):
            agent = AgentRegistry.get_agent_by_id(agent_id)
            print(f"  - {agent_id:30} {agent['doc']}")
        print()
        return 0
    else:
        print(f"❌ Validation failed with {len(errors)} error(s):\n")
        for error in errors:
            print(f"  {error}")
        print()
        return 1


if __name__ == "__main__":
    repo_root = sys.argv[1] if len(sys.argv) > 1 else None
    exit_code = validate_registry(repo_root)
    sys.exit(exit_code)
