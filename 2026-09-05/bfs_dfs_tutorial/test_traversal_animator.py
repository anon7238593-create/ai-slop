#!/usr/bin/env python3
"""Unit tests for graph traversal animator."""

import os
from pathlib import Path
import tempfile
import unittest

import cairo

from traversal_animator import (
    DEFAULT_GRAPH,
    ComparativeTraversalRenderer,
    TraversalVideoRenderer,
    build_traversal_steps,
    configure_cairo_context,
    find_ffmpeg,
    layout_graph,
    random_connected_graph,
    render_standalone_video,
)


class TestTraversalAnimator(unittest.TestCase):
    def test_random_connected_graph(self):
        graph = random_connected_graph(nodes=8, edge_probability=0.3, seed=123)
        self.assertEqual(len(graph), 8)
        self.assertIn("A", graph)
        # Check connectivity: BFS from A must visit all nodes
        visited = set()
        queue = ["A"]
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                queue.extend(graph[node])
        self.assertEqual(len(visited), 8)

    def test_layout_graph(self):
        layout = layout_graph(DEFAULT_GRAPH, box_x=0.0, box_y=0.0, box_w=800.0, box_h=600.0, margin=50.0, seed=42)
        self.assertEqual(len(layout), len(DEFAULT_GRAPH))
        for node, (x, y) in layout.items():
            self.assertTrue(0.0 <= x <= 800.0)
            self.assertTrue(0.0 <= y <= 600.0)

    def test_traversal_steps_bfs(self):
        steps = build_traversal_steps(DEFAULT_GRAPH, "A", "bfs")
        self.assertGreater(len(steps), 5)
        # First step should be INIT
        self.assertEqual(steps[0].action_type, "INIT")
        # Final step should be FINISHED
        self.assertEqual(steps[-1].action_type, "FINISHED")
        self.assertEqual(len(steps[-1].visited_order), len(DEFAULT_GRAPH))

    def test_traversal_steps_dfs(self):
        steps = build_traversal_steps(DEFAULT_GRAPH, "A", "dfs")
        self.assertGreater(len(steps), 5)
        self.assertEqual(steps[0].action_type, "INIT")
        self.assertEqual(steps[-1].action_type, "FINISHED")
        self.assertEqual(len(steps[-1].visited_order), len(DEFAULT_GRAPH))

    def test_find_ffmpeg(self):
        ffmpeg_path = find_ffmpeg()
        self.assertIsNotNone(ffmpeg_path)
        self.assertTrue(os.path.exists(ffmpeg_path))

    def test_configure_cairo_context_anti_aliasing(self):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
        ctx = cairo.Context(surf)
        configure_cairo_context(ctx)
        self.assertEqual(ctx.get_antialias(), cairo.ANTIALIAS_BEST)
        self.assertEqual(ctx.get_line_cap(), cairo.LINE_CAP_ROUND)
        self.assertEqual(ctx.get_line_join(), cairo.LINE_JOIN_ROUND)

    def test_resolution_scaling(self):
        layout = {"A": (100.0, 100.0), "B": (300.0, 300.0)}
        graph = {"A": ["B"], "B": ["A"]}

        # 1080p (scale 1.0)
        r_1080 = TraversalVideoRenderer(graph, layout, "bfs", width=1920, height=1080)
        self.assertAlmostEqual(r_1080.scale, 1.0, places=2)

        # 2K QHD (scale 1.33)
        r_2k = TraversalVideoRenderer(graph, layout, "bfs", width=2560, height=1440)
        self.assertAlmostEqual(r_2k.scale, 1440.0 / 1080.0, places=2)
        self.assertGreater(r_2k.node_radius, r_1080.node_radius)

        # 4K UHD (scale 2.0)
        r_4k = TraversalVideoRenderer(graph, layout, "bfs", width=3840, height=2160)
        self.assertAlmostEqual(r_4k.scale, 2.0, places=2)
        self.assertGreater(r_4k.node_radius, r_2k.node_radius)

    def test_step_duration_customization(self):
        # Slower pedagogical pacing: frames_per_step = 60
        steps_slow = build_traversal_steps(DEFAULT_GRAPH, "A", "bfs", frames_per_step=60)
        # Faster pacing: frames_per_step = 20
        steps_fast = build_traversal_steps(DEFAULT_GRAPH, "A", "bfs", frames_per_step=20)
        self.assertEqual(len(steps_slow), len(steps_fast))
        self.assertGreater(steps_slow[1].frame_duration, steps_fast[1].frame_duration)

    def test_render_standalone_encoding(self):
        ffmpeg_path = find_ffmpeg()
        if not ffmpeg_path:
            self.skipTest("ffmpeg not found")
        tiny_graph = {"A": ["B"], "B": []}
        layout = {"A": (50.0, 50.0), "B": (150.0, 50.0)}
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "test_mini.mp4"
            render_standalone_video(
                tiny_graph, layout, "bfs", out_file,
                start_node="A", fps=10, width=320, height=240,
                step_duration=0.5,
            )
            self.assertTrue(out_file.exists())
            self.assertGreater(out_file.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
