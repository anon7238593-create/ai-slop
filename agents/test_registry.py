#!/usr/bin/env python3
"""
Unit tests for Agent Registry validation.
"""

import tempfile
import unittest
from pathlib import Path

from registry import AgentRegistry


class TestAgentRegistry(unittest.TestCase):
    """Test suite for AgentRegistry."""

    def test_registry_not_empty(self):
        """Registry should contain agents."""
        self.assertGreater(len(AgentRegistry.AGENTS), 0)

    def test_all_agents_have_doc_path(self):
        """Each agent must have a 'doc' field."""
        for agent_id, config in AgentRegistry.AGENTS.items():
            self.assertIn("doc", config, f"Agent '{agent_id}' missing 'doc' field")
            self.assertIsInstance(
                config["doc"], str, f"Agent '{agent_id}' doc is not a string"
            )

    def test_all_agents_have_description(self):
        """Each agent must have a description."""
        for agent_id, config in AgentRegistry.AGENTS.items():
            self.assertIn(
                "description", config, f"Agent '{agent_id}' missing 'description'"
            )
            self.assertGreater(
                len(config["description"]),
                0,
                f"Agent '{agent_id}' has empty description",
            )

    def test_all_agents_have_keywords(self):
        """Each agent must have keywords list."""
        for agent_id, config in AgentRegistry.AGENTS.items():
            self.assertIn(
                "keywords", config, f"Agent '{agent_id}' missing 'keywords'"
            )
            self.assertIsInstance(
                config["keywords"],
                list,
                f"Agent '{agent_id}' keywords is not a list",
            )
            self.assertGreater(
                len(config["keywords"]),
                0,
                f"Agent '{agent_id}' has no keywords",
            )

    def test_no_duplicate_doc_paths(self):
        """No two agents should have the same documentation path."""
        doc_paths = [config["doc"] for config in AgentRegistry.AGENTS.values()]
        self.assertEqual(
            len(doc_paths),
            len(set(doc_paths)),
            "Duplicate documentation paths detected",
        )

    def test_get_agent_by_id(self):
        """get_agent_by_id should return correct agent."""
        first_agent_id = list(AgentRegistry.AGENTS.keys())[0]
        agent = AgentRegistry.get_agent_by_id(first_agent_id)
        self.assertIsNotNone(agent)
        self.assertIn("doc", agent)

    def test_get_nonexistent_agent(self):
        """get_agent_by_id should return None for nonexistent agent."""
        agent = AgentRegistry.get_agent_by_id("nonexistent-agent")
        self.assertIsNone(agent)

    def test_list_agents(self):
        """list_agents should return all agent IDs."""
        agents = AgentRegistry.list_agents()
        self.assertEqual(len(agents), len(AgentRegistry.AGENTS))
        self.assertEqual(set(agents), set(AgentRegistry.AGENTS.keys()))

    def test_get_docs_path(self):
        """get_docs_path should return correct path."""
        first_agent_id = list(AgentRegistry.AGENTS.keys())[0]
        expected_path = AgentRegistry.AGENTS[first_agent_id]["doc"]
        actual_path = AgentRegistry.get_docs_path(first_agent_id)
        self.assertEqual(actual_path, expected_path)

    def test_validate_with_missing_doc(self):
        """validate_all should detect missing documentation files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create agents directory but no files
            (tmppath / "agents").mkdir()
            is_valid, errors = AgentRegistry.validate_all(tmppath)
            self.assertFalse(is_valid)
            self.assertGreater(len(errors), 0)

    def test_validate_with_valid_docs(self):
        """validate_all should pass when all docs exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "agents").mkdir()
            # Create all agent documentation files
            for agent_id, config in AgentRegistry.AGENTS.items():
                doc_path = tmppath / config["doc"]
                doc_path.parent.mkdir(parents=True, exist_ok=True)
                doc_path.write_text(f"# {agent_id}\n\nAgent documentation." * 50)
            # Create AGENTS.md with all agent mentions
            agents_md = tmppath / "AGENTS.md"
            content = "# Agents\n" + "\n".join(
                f"- {agent_id}" for agent_id in AgentRegistry.AGENTS.keys()
            )
            agents_md.write_text(content)
            is_valid, errors = AgentRegistry.validate_all(tmppath)
            self.assertTrue(is_valid, f"Validation failed: {errors}")


if __name__ == "__main__":
    unittest.main()
