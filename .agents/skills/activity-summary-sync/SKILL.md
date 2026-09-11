---
name: activity-summary-sync
description: >-
  Automatically use this skill whenever summarizing ongoing work, generating activity logs, synchronizing state across multiple agents or Antigravity instances, tracking in-progress tasks, managing lockfiles, or setting up recurring sync heartbeats.
---

# Activity Summary & State Synchronization Skill

## Purpose
Maintain continuous cross-agent and cross-instance alignment by managing the structured event log, tracking active locks, and publishing the living state snapshot (`CURRENT_STATE.md`).

---

## Core Workflows

### 1. Check Current System State
Before starting work in a shared or multi-agent environment, inspect:
```bash
python3 .agents/scripts/sync_logger.py status
```
Or view [`file:///home/aman/dev/ai-slop/.agents/sync/CURRENT_STATE.md`](file:///home/aman/dev/ai-slop/.agents/sync/CURRENT_STATE.md).

### 2. Log Progress Milestones
Whenever starting, progressing, or completing a notable task:
```bash
python3 .agents/scripts/sync_logger.py log \
  --agent "<agent-or-instance-name>" \
  --action "<action-key>" \
  --status "in_progress" \
  --details "<description of what is happening>" \
  --files "<file1>" "<file2>"
```

Status choices:
- `started`: Work has begun.
- `in_progress`: Sub-step in progress.
- `completed`: Successfully finished.
- `failed`: Encountered an error.
- `blocked`: Waiting on another agent or external dependency.

### 3. Resource Locking (Concurrency Guard)
To prevent clobbering when modifying shared files:
```bash
# Acquire lock
python3 .agents/scripts/sync_logger.py lock --resource "<path>" --agent "<agent-name>" --reason "<reason>"

# Release lock
python3 .agents/scripts/sync_logger.py unlock --resource "<path>" --agent "<agent-name>"
```

### 4. Refresh Living Snapshot
Generate an immediate fresh snapshot of the workspace and update `CURRENT_STATE.md`:
```bash
python3 .agents/scripts/sync_logger.py snapshot --agent "<agent-name>"
```

### 5. Run Continuous Daemon
To monitor and update state continuously in the background:
```bash
python3 .agents/scripts/sync_logger.py daemon --interval 30
```

### 6. Scheduled Heartbeat via Antigravity `schedule`
To set up a periodic background sync without blocking execution:
- Call `schedule` with:
  - `CronExpression`: `"*/2 * * * *"` (every 2 minutes)
  - `Prompt`: `"Execute sync snapshot: python3 .agents/scripts/sync_logger.py snapshot --agent 'antigravity-sync-cron'"`

---

## Verification & Testing

Verify that the sync engine passes all tests:
```bash
python3 -m unittest discover -s .agents/scripts
```
