#!/usr/bin/env python3
"""
Unit tests for SyncLogger & State Synchronizer Engine (.agents/scripts/sync_logger.py).
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from sync_logger import SyncLogger


class TestSyncLogger(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_sync_logger_")
        self.repo_root = Path(self.temp_dir)
        self.sync_dir = self.repo_root / ".agents" / "sync"
        self.logger = SyncLogger(repo_root=self.repo_root, sync_dir=self.sync_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_event_and_retrieve(self):
        evt = self.logger.log_event(
            agent="Worker-1",
            action="refactor",
            status="in_progress",
            details="Refactoring math module",
            files=["math.py"],
            level="INFO",
        )
        self.assertTrue(evt["id"].startswith("evt-"))
        self.assertEqual(evt["agent"], "Worker-1")
        self.assertEqual(evt["action"], "refactor")
        self.assertEqual(evt["files"], ["math.py"])

        # Retrieve recent events
        recent = self.logger.get_recent_events(limit=10)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["id"], evt["id"])
        self.assertEqual(recent[0]["agent"], "Worker-1")

    def test_multi_event_order(self):
        self.logger.log_event(agent="AgentA", action="step1", status="completed")
        self.logger.log_event(agent="AgentB", action="step2", status="completed")
        self.logger.log_event(agent="AgentC", action="step3", status="completed")

        recent = self.logger.get_recent_events(limit=2)
        self.assertEqual(len(recent), 2)
        # Should be in reverse chronological order (newest first)
        self.assertEqual(recent[0]["agent"], "AgentC")
        self.assertEqual(recent[1]["agent"], "AgentB")

    def test_lock_acquire_and_conflict(self):
        ok1, msg1 = self.logger.acquire_lock(
            resource="file_a.py",
            agent="AgentA",
            reason="Refactoring",
            timeout_minutes=10,
        )
        self.assertTrue(ok1)

        # Another agent attempts to acquire same resource without force
        ok2, msg2 = self.logger.acquire_lock(
            resource="file_a.py",
            agent="AgentB",
            reason="Formatting",
            timeout_minutes=10,
        )
        self.assertFalse(ok2)
        self.assertIn("Lock conflict", msg2)

        # Same agent can re-acquire / update lock
        ok3, msg3 = self.logger.acquire_lock(
            resource="file_a.py",
            agent="AgentA",
            reason="Updating lock",
            timeout_minutes=15,
        )
        self.assertTrue(ok3)

        # Release lock
        ok4, msg4 = self.logger.release_lock(resource="file_a.py", agent="AgentA")
        self.assertTrue(ok4)

        # Now AgentB can acquire it
        ok5, msg5 = self.logger.acquire_lock(
            resource="file_a.py",
            agent="AgentB",
            reason="Formatting",
            timeout_minutes=10,
        )
        self.assertTrue(ok5)

    def test_lock_expiration(self):
        # Acquire lock with 0 timeout minutes (already expired or expires immediately)
        self.logger.acquire_lock(
            resource="expired_file.py",
            agent="AgentOld",
            reason="Old job",
            timeout_minutes=-1,
        )
        # Active locks should prune expired ones
        active = self.logger.get_active_locks()
        self.assertNotIn("expired_file.py", active)

    def test_update_summary_generates_markdown(self):
        self.logger.log_event(
            agent="Orchestrator",
            action="init",
            status="completed",
            details="Initialized fleet",
        )
        self.logger.acquire_lock(
            resource="shared_doc.md",
            agent="Orchestrator",
            reason="Updating guide",
        )
        md = self.logger.update_summary()

        self.assertTrue(self.logger.state_file.exists())
        self.assertIn("# Antigravity Fleet Synchronization & Live Activity State", md)
        self.assertIn("Orchestrator", md)
        self.assertIn("shared_doc.md", md)
        self.assertIn("Active Resource Locks", md)
        self.assertIn("Chronological Activity Timeline", md)

    def test_snapshot(self):
        snap = self.logger.snapshot(agent="test-agent")
        self.assertIn("timestamp", snap)
        self.assertIn("git_state", snap)
        self.assertTrue(self.logger.state_file.exists())


if __name__ == "__main__":
    unittest.main()
