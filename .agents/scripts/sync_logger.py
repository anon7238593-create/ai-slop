#!/usr/bin/env python3
"""
Sync Logger & State Synchronizer Engine for ai-slop.

Provides a unified, thread-safe, and process-safe event ledger and living state
snapshot to keep multiple agents, subagents, and concurrent Antigravity instances
in continuous synchronization.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def find_repo_root(start_path: Optional[Path] = None) -> Path:
    """Find repository root by looking for .git or .agents directory."""
    cur = (start_path or Path.cwd()).resolve()
    while cur != cur.parent:
        if (cur / ".git").exists() or (cur / ".agents").exists():
            return cur
        cur = cur.parent
    return (start_path or Path.cwd()).resolve()


class SyncLogger:
    """Manages activity logging, file locking, git state inspection, and state synchronization."""

    def __init__(self, repo_root: Optional[Path] = None, sync_dir: Optional[Path] = None):
        self.repo_root = repo_root or find_repo_root()
        self.sync_dir = sync_dir or (self.repo_root / ".agents" / "sync")
        self.sync_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.sync_dir / "activity_log.jsonl"
        self.state_file = self.sync_dir / "CURRENT_STATE.md"
        self.locks_file = self.sync_dir / "locks.json"
        self.meta_file = self.sync_dir / "last_scan.json"

    def _now_iso(self) -> str:
        """Return current UTC timestamp in ISO 8601 format."""
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def log_event(
        self,
        agent: str,
        action: str,
        status: str = "in_progress",
        details: str = "",
        files: Optional[List[str]] = None,
        level: str = "INFO",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Append an event record to activity_log.jsonl in an atomic, flock-protected manner."""
        event = {
            "id": f"evt-{int(time.time() * 1000)}",
            "timestamp": self._now_iso(),
            "agent": agent,
            "action": action,
            "status": status.lower(),
            "level": level.upper(),
            "details": details,
            "files": files or [],
            "metadata": metadata or {},
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(event) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return event

    def get_recent_events(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Read the most recent events from activity_log.jsonl."""
        if not self.log_file.exists():
            return []

        lines = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    line = line.strip()
                    if line:
                        lines.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        events = []
        for line in reversed(lines[-limit:]):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return events

    def get_active_locks(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve active resource locks, pruning expired locks."""
        if not self.locks_file.exists():
            return {}

        locks = {}
        with open(self.locks_file, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                content = f.read().strip()
                if content:
                    locks = json.loads(content)
            except Exception:
                locks = {}
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        # Filter expired locks
        now = time.time()
        active = {}
        dirty = False
        for resource, lock in locks.items():
            expires_at = lock.get("expires_at_epoch", 0)
            if expires_at > now:
                active[resource] = lock
            else:
                dirty = True

        if dirty:
            self._save_locks(active)

        return active

    def _save_locks(self, locks: Dict[str, Dict[str, Any]]) -> None:
        """Write locks map atomically."""
        tmp_file = self.locks_file.with_suffix(".tmp")
        with open(tmp_file, "w", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(locks, f, indent=2)
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        os.replace(tmp_file, self.locks_file)

    def acquire_lock(
        self,
        resource: str,
        agent: str,
        reason: str = "",
        timeout_minutes: int = 60,
        force: bool = False,
    ) -> Tuple[bool, str]:
        """Acquire a lock on a file or shared resource to prevent concurrent editing conflicts."""
        with open(self.sync_dir / ".lock.mutex", "a", encoding="utf-8") as mutex:
            fcntl.flock(mutex.fileno(), fcntl.LOCK_EX)
            try:
                active = self.get_active_locks()
                if resource in active and not force:
                    existing = active[resource]
                    if existing["agent"] != agent:
                        msg = f"Lock conflict: resource '{resource}' already locked by '{existing['agent']}' until {existing.get('expires_at_iso')} for '{existing.get('reason')}'"
                        return False, msg

                expires_epoch = time.time() + (timeout_minutes * 60)
                expires_iso = datetime.fromtimestamp(expires_epoch, timezone.utc).isoformat(timespec="seconds")
                active[resource] = {
                    "resource": resource,
                    "agent": agent,
                    "reason": reason,
                    "acquired_at_iso": self._now_iso(),
                    "expires_at_iso": expires_iso,
                    "expires_at_epoch": expires_epoch,
                }
                self._save_locks(active)
                self.log_event(
                    agent=agent,
                    action="acquire_lock",
                    status="completed",
                    details=f"Locked resource '{resource}': {reason}",
                    files=[resource],
                )
                return True, f"Successfully locked '{resource}'"
            finally:
                fcntl.flock(mutex.fileno(), fcntl.LOCK_UN)

    def release_lock(self, resource: str, agent: str, force: bool = False) -> Tuple[bool, str]:
        """Release a previously acquired resource lock."""
        with open(self.sync_dir / ".lock.mutex", "a", encoding="utf-8") as mutex:
            fcntl.flock(mutex.fileno(), fcntl.LOCK_EX)
            try:
                active = self.get_active_locks()
                if resource not in active:
                    return True, f"Resource '{resource}' was not locked."

                existing = active[resource]
                if existing["agent"] != agent and not force:
                    return False, f"Cannot unlock '{resource}': held by '{existing['agent']}' (use force=True if needed)."

                del active[resource]
                self._save_locks(active)
                self.log_event(
                    agent=agent,
                    action="release_lock",
                    status="completed",
                    details=f"Unlocked resource '{resource}'",
                    files=[resource],
                )
                return True, f"Successfully unlocked '{resource}'"
            finally:
                fcntl.flock(mutex.fileno(), fcntl.LOCK_UN)

    def get_git_state(self) -> Dict[str, Any]:
        """Inspect git branch, recent commit, and modified/untracked files."""
        state: Dict[str, Any] = {
            "branch": "unknown",
            "last_commit": "unknown",
            "modified": [],
            "staged": [],
            "untracked": [],
        }

        try:
            b = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            if b.returncode == 0:
                state["branch"] = b.stdout.strip()
        except Exception:
            pass

        try:
            c = subprocess.run(
                ["git", "log", "-1", "--format=%h %s (%an, %ar)"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            if c.returncode == 0:
                state["last_commit"] = c.stdout.strip()
        except Exception:
            pass

        try:
            s = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            if s.returncode == 0:
                for line in s.stdout.splitlines():
                    line = line.rstrip()
                    if not line:
                        continue
                    code = line[:2]
                    path = line[3:].strip()
                    if code == "??":
                        state["untracked"].append(path)
                    elif code[0] in ("M", "A", "D", "R"):
                        state["staged"].append(path)
                    elif code[1] in ("M", "D"):
                        state["modified"].append(path)
        except Exception:
            pass

        return state

    def scan_and_record_diff(self, agent: str = "state-sync-logger") -> Dict[str, Any]:
        """Scan workspace changes, record an event if git state changed, and update cache."""
        current = self.get_git_state()

        last_state = {}
        if self.meta_file.exists():
            try:
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    last_state = json.load(f)
            except Exception:
                last_state = {}

        # Detect changes in modified / untracked / staged
        curr_files = sorted(set(current["modified"] + current["staged"] + current["untracked"]))
        last_files = sorted(set(last_state.get("modified", []) + last_state.get("staged", []) + last_state.get("untracked", [])))

        changed = (curr_files != last_files) or (current.get("branch") != last_state.get("branch")) or (current.get("last_commit") != last_state.get("last_commit"))

        if changed and curr_files:
            summary_desc = f"Git state change on branch '{current['branch']}': {len(current['modified'])} modified, {len(current['staged'])} staged, {len(current['untracked'])} untracked."
            self.log_event(
                agent=agent,
                action="workspace_scan",
                status="completed",
                details=summary_desc,
                files=curr_files[:10],
                metadata={"total_changed": len(curr_files)},
            )

        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)

        return current

    def update_summary(self) -> str:
        """Render and atomically write .agents/sync/CURRENT_STATE.md."""
        git_state = self.get_git_state()
        locks = self.get_active_locks()
        events = self.get_recent_events(limit=25)

        # Unique active agents in recent window
        active_agents = set()
        for evt in events:
            if evt.get("agent"):
                active_agents.add(evt["agent"])

        md_lines = [
            "# Antigravity Fleet Synchronization & Live Activity State",
            "",
            f"> **Last Synchronized**: `{self._now_iso()}`  ",
            f"> **Active Git Branch**: `{git_state.get('branch', 'unknown')}`  ",
            f"> **Latest Git Commit**: `{git_state.get('last_commit', 'unknown')}`",
            "",
            "---",
            "",
            "## 🔄 Active Agents & Instances",
            "",
        ]

        if active_agents:
            md_lines.append("| Agent / Instance | Status | Last Observed Action |")
            md_lines.append("|---|---|---|")
            for ag in sorted(active_agents):
                # find latest event for this agent
                latest = next((e for e in events if e.get("agent") == ag), None)
                if latest:
                    status_badge = f"`{latest.get('status', 'active')}`"
                    action_text = latest.get("action", "unknown")
                    time_ago = latest.get("timestamp", "")
                    md_lines.append(f"| **{ag}** | {status_badge} | {action_text} ({time_ago}) |")
        else:
            md_lines.append("_No recent agent activity recorded._")

        md_lines.extend([
            "",
            "---",
            "",
            "## 🔒 Active Resource Locks (Concurrency Guard)",
            "",
        ])

        if locks:
            md_lines.append("| Resource | Locked By | Reason | Expires (UTC) |")
            md_lines.append("|---|---|---|---|")
            for res, lock in locks.items():
                md_lines.append(
                    f"| `{res}` | **{lock.get('agent')}** | {lock.get('reason')} | `{lock.get('expires_at_iso')}` |"
                )
        else:
            md_lines.append("🟢 **No resources locked.** All files and workstreams are available for concurrent execution.")

        md_lines.extend([
            "",
            "---",
            "",
            "## 📁 Workspace Working Tree & Uncommitted Diffs",
            "",
        ])

        total_dirty = len(git_state["modified"]) + len(git_state["staged"]) + len(git_state["untracked"])
        if total_dirty == 0:
            md_lines.append("🟢 **Working tree clean.** No uncommitted modifications or untracked files.")
        else:
            if git_state["staged"]:
                md_lines.append(f"- **Staged ({len(git_state['staged'])})**:")
                for f in git_state["staged"][:10]:
                    md_lines.append(f"  - `{f}`")
                if len(git_state["staged"]) > 10:
                    md_lines.append(f"  - _...and {len(git_state['staged']) - 10} more_")
            if git_state["modified"]:
                md_lines.append(f"- **Modified ({len(git_state['modified'])})**:")
                for f in git_state["modified"][:10]:
                    md_lines.append(f"  - `{f}`")
                if len(git_state["modified"]) > 10:
                    md_lines.append(f"  - _...and {len(git_state['modified']) - 10} more_")
            if git_state["untracked"]:
                md_lines.append(f"- **Untracked ({len(git_state['untracked'])})**:")
                for f in git_state["untracked"][:10]:
                    md_lines.append(f"  - `{f}`")
                if len(git_state["untracked"]) > 10:
                    md_lines.append(f"  - _...and {len(git_state['untracked']) - 10} more_")

        md_lines.extend([
            "",
            "---",
            "",
            "## 📜 Chronological Activity Timeline (Recent Events)",
            "",
            "| Timestamp (UTC) | Agent | Action | Status | Details | Files |",
            "|---|---|---|---|---|---|",
        ])

        if events:
            for evt in events:
                ts = evt.get("timestamp", "").replace("T", " ").replace("+00:00", "")
                agent_name = evt.get("agent", "unknown")
                action = evt.get("action", "")
                status = evt.get("status", "")
                details = evt.get("details", "").replace("|", "\\|")
                files_str = ", ".join(f"`{f}`" for f in evt.get("files", [])[:3])
                if len(evt.get("files", [])) > 3:
                    files_str += f" (+{len(evt['files']) - 3})"
                if not files_str:
                    files_str = "-"
                md_lines.append(f"| `{ts}` | {agent_name} | `{action}` | `{status}` | {details} | {files_str} |")
        else:
            md_lines.append("| - | - | - | - | _No activity logged yet_ | - |")

        md_lines.extend([
            "",
            "---",
            "",
            "## 💡 Quick Coordination Protocols for Agents",
            "",
            "1. **Read Before Writing**: Check this document (`.agents/sync/CURRENT_STATE.md`) to verify which files are locked or modified by other agents/instances.",
            "2. **Claim Lock**: Use `python3 .agents/scripts/sync_logger.py lock --resource <file> --agent <agent_name> --reason <why>` to prevent conflicts.",
            "3. **Log Progress**: Emit status updates with `python3 .agents/scripts/sync_logger.py log --agent <agent_name> --action <action> --status in_progress --details <details>`.",
            "4. **Release & Snapshot**: Unlock and refresh summary when work completes with `python3 .agents/scripts/sync_logger.py unlock ...` and `snapshot`.",
            "",
        ])

        content = "\n".join(md_lines)

        tmp_state = self.state_file.with_suffix(".tmp")
        with open(tmp_state, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_state, self.state_file)

        return content

    def snapshot(self, agent: str = "state-sync-logger") -> Dict[str, Any]:
        """Perform scan, record diffs, and regenerate CURRENT_STATE.md."""
        git_state = self.scan_and_record_diff(agent=agent)
        summary_md = self.update_summary()
        return {
            "timestamp": self._now_iso(),
            "git_state": git_state,
            "summary_length": len(summary_md),
        }

    def run_daemon(self, interval: int = 30, agent: str = "sync-daemon") -> None:
        """Run continuous monitoring loop."""
        print(f"[*] Starting SyncLogger daemon (interval={interval}s, repo={self.repo_root}). Press Ctrl+C to stop.")
        self.log_event(agent=agent, action="daemon_start", status="completed", details=f"Daemon started with {interval}s interval")
        self.snapshot(agent=agent)
        try:
            while True:
                time.sleep(interval)
                self.snapshot(agent=agent)
        except KeyboardInterrupt:
            print("\n[*] Daemon stopped by user.")
            self.log_event(agent=agent, action="daemon_stop", status="completed", details="Daemon stopped cleanly")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Antigravity Fleet Sync Logger: Keeps all agents and instances synchronized."
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # log
    p_log = subparsers.add_parser("log", help="Log an activity event")
    p_log.add_argument("--agent", required=True, help="Agent or instance name")
    p_log.add_argument("--action", required=True, help="Action identifier (e.g. refactor, generate, test)")
    p_log.add_argument("--status", default="in_progress", choices=["started", "in_progress", "completed", "failed", "blocked"])
    p_log.add_argument("--details", default="", help="Human-readable event summary")
    p_log.add_argument("--files", nargs="*", default=[], help="Files affected by this event")
    p_log.add_argument("--level", default="INFO", choices=["INFO", "SUCCESS", "WARN", "ERROR"])

    # lock
    p_lock = subparsers.add_parser("lock", help="Acquire a resource lock")
    p_lock.add_argument("--resource", required=True, help="Path or identifier to lock")
    p_lock.add_argument("--agent", required=True, help="Agent claiming the lock")
    p_lock.add_argument("--reason", default="", help="Reason for the lock")
    p_lock.add_argument("--timeout", type=int, default=60, help="Lock timeout in minutes")
    p_lock.add_argument("--force", action="store_true", help="Force lock even if already held")

    # unlock
    p_unlock = subparsers.add_parser("unlock", help="Release a resource lock")
    p_unlock.add_argument("--resource", required=True, help="Resource to unlock")
    p_unlock.add_argument("--agent", required=True, help="Agent releasing the lock")
    p_unlock.add_argument("--force", action="store_true", help="Force unlock regardless of owner")

    # scan
    subparsers.add_parser("scan", help="Scan git working tree and record diffs")

    # update-summary
    subparsers.add_parser("update-summary", help="Regenerate CURRENT_STATE.md")

    # snapshot
    p_snap = subparsers.add_parser("snapshot", help="Scan diffs and regenerate CURRENT_STATE.md in one step")
    p_snap.add_argument("--agent", default="state-sync-logger", help="Agent identifier")

    # status
    subparsers.add_parser("status", help="Print brief synchronization status to stdout")

    # daemon
    p_daemon = subparsers.add_parser("daemon", help="Run continuous periodic synchronization loop")
    p_daemon.add_argument("--interval", type=int, default=30, help="Interval in seconds between scans")
    p_daemon.add_argument("--agent", default="sync-daemon", help="Daemon agent identifier")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    logger = SyncLogger()

    if args.command == "log":
        evt = logger.log_event(
            agent=args.agent,
            action=args.action,
            status=args.status,
            details=args.details,
            files=args.files,
            level=args.level,
        )
        logger.update_summary()
        print(f"[OK] Logged event {evt['id']} for {args.agent}: {args.action} [{args.status}]")

    elif args.command == "lock":
        ok, msg = logger.acquire_lock(
            resource=args.resource,
            agent=args.agent,
            reason=args.reason,
            timeout_minutes=args.timeout,
            force=args.force,
        )
        logger.update_summary()
        if ok:
            print(f"[OK] {msg}")
        else:
            print(f"[ERROR] {msg}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "unlock":
        ok, msg = logger.release_lock(resource=args.resource, agent=args.agent, force=args.force)
        logger.update_summary()
        if ok:
            print(f"[OK] {msg}")
        else:
            print(f"[ERROR] {msg}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "scan":
        st = logger.scan_and_record_diff()
        print(f"[OK] Scan completed. Branch: {st.get('branch')}, Modified: {len(st.get('modified', []))}, Staged: {len(st.get('staged', []))}, Untracked: {len(st.get('untracked', []))}")

    elif args.command == "update-summary":
        logger.update_summary()
        print(f"[OK] Updated state summary in {logger.state_file}")

    elif args.command == "snapshot":
        res = logger.snapshot(agent=args.agent)
        print(f"[OK] Snapshot completed at {res['timestamp']}. Updated {logger.state_file}")

    elif args.command == "status":
        locks = logger.get_active_locks()
        events = logger.get_recent_events(limit=5)
        git_st = logger.get_git_state()
        print("=== Antigravity Sync Status ===")
        print(f"Branch: {git_st.get('branch')} | Last Commit: {git_st.get('last_commit')}")
        print(f"Active Locks: {len(locks)}")
        for res, lk in locks.items():
            print(f"  - {res}: held by {lk.get('agent')} ({lk.get('reason')})")
        print(f"Recent Events: {len(events)}")
        for e in events[:5]:
            print(f"  - [{e.get('timestamp')}] {e.get('agent')} -> {e.get('action')} ({e.get('status')}): {e.get('details')}")
        print(f"State File: {logger.state_file}")

    elif args.command == "daemon":
        logger.run_daemon(interval=args.interval, agent=args.agent)


if __name__ == "__main__":
    main()
