---
name: master-orchestrator
description: >-
  Automatically use this skill whenever breaking down complex, large-scale multi-file features into parallel workstreams, spawning a fleet of concurrent subagents, coordinating branch merges, or orchestrating multi-agent systems across the repository.
---

# Master Orchestrator & Fleet Coordination Skill

## Purpose
Decompose large repository initiatives into modular workstreams, provision and dispatch fleets of parallel worker subagents, coordinate isolated workspaces, and synthesize results into production-grade commits.

## Parallel Fleet Dispatch Pattern

### 1. Partition Subtasks
Separate tasks so that workers touch disjoint files or operate on clear interface contracts:
- Worker A: Core algorithmic / math logic
- Worker B: Visual generation / rendering pipeline
- Worker C: Test suite & validation assertions
- Worker D: CI/CD workflow & release scripts

### 2. Configure Subagents
- **Branch Workspaces**: Set `Workspace: "branch"` on writing agents to prevent git conflicts.
- **Model Efficiency**: Use `Model: "pro"` for architectural logic, `Model: "flash"` for tests, scripts, and documentation.
- **Atomic Prompts**: Provide explicit target file paths, contracts, and expected output formats in each worker's prompt.

### 3. Synthesis Checklist
1. Inspect subagent outcomes and logs.
2. Integrate / merge changes from branches.
3. Execute repository-wide test suite: `python3 -m unittest discover`.
4. Verify repository guidelines:
   - Assets < 95MB.
   - Deterministic seeds (`--seed`) supported.
   - Speed conservation intact for simulations.
5. Provide the user with a unified summary of all parallel worker outputs.
