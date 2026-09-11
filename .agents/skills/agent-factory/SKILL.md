---
name: agent-factory
description: >-
  Automatically use this skill whenever creating, designing, updating, or registering new specialized agents, meta-agents, subagent personas, or agent skills in the repository.
---

# Agent Factory & Meta-Agent Skill

## Purpose
Scaffold, standardize, and register new specialized agents and skills for the `ai-slop` repository.

## Standard Creation Flow

### 1. Specification File: `agents/<name>.md`
Ensure it includes:
- Persona & Mission statement.
- Key file paths and references.
- Invariants (e.g. speed conservation, seeds, file limits).
- Standard runbooks.

### 2. Progressive Disclosure Skill: `.agents/skills/<name>/SKILL.md`
Must include YAML frontmatter:
```markdown
---
name: <name>
description: >-
  Automatically use this skill whenever <trigger conditions and keywords>.
---
```

### 3. Registry Update: `AGENTS.md`
Add a row to the **Automatic Intent Routing Table**:
```markdown
| <Keywords / Trigger Intents> | **<Agent Display Name>** | [**`agents/<name>.md`**](file:///home/aman/dev/ai-slop/agents/<name>.md)<br>`skills/<name>` |
```

### 4. Verification
Ensure links are valid, YAML parses cleanly, and trigger intents are distinct from existing agents.
