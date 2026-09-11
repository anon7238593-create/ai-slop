#!/usr/bin/env python3
"""High-definition graph traversal animation video generator for BFS and DFS.

Renders 1080p 60/30fps MP4 videos demonstrating:
- Force-directed graph topology with animated edge traversal signals
- Live state-colored nodes (Unvisited, Frontier, Active, Visited)
- Live Memory Inspector showing Queue (FIFO) for BFS and Stack (LIFO) for DFS
- Real-time Visited Sequence order ribbon and step-by-step commentary
- Comparative side-by-side mode contrasting BFS wavefront vs DFS branch diving

Usage:
    python3 traversal_animator.py --algorithm all --output output/
    python3 traversal_animator.py --algorithm bfs --random-graph --nodes 10 --seed 42
"""

from __future__ import annotations

import argparse
from collections import deque
import glob
import json
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

import cairo

# Default graph matching bfs_dfs_visualizer.py
DEFAULT_GRAPH: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B", "G"],
    "E": ["B", "G", "H"],
    "F": ["C", "H"],
    "G": ["D", "E"],
    "H": ["E", "F"],
}
DEFAULT_START_NODE = "A"


# Color Palette (Dark Theme / Editorial Aesthetic)
COLOR_BG = (0.04, 0.06, 0.09)          # #0A0F17 Deep Slate Background
COLOR_PANEL = (0.07, 0.10, 0.16)       # #121A29 Card Surface
COLOR_PANEL_BORDER = (0.15, 0.20, 0.29)# #26334A Border
COLOR_GRID_DOT = (0.12, 0.16, 0.24)    # #1E293D Graph Dot Grid

# Node State Colors: (Fill RGB, Border RGB, Text RGB)
NODE_COLORS = {
    "unvisited": ((0.11, 0.15, 0.22), (0.35, 0.42, 0.52), (0.65, 0.72, 0.82)), # Slate
    "frontier":  ((0.03, 0.20, 0.28), (0.02, 0.71, 0.83), (0.88, 0.96, 1.00)), # Cyan (In Queue/Stack)
    "active":    ((0.30, 0.11, 0.02), (0.96, 0.62, 0.04), (1.00, 0.95, 0.80)), # Amber / Orange Glow
    "visited":   ((0.02, 0.28, 0.18), (0.06, 0.73, 0.51), (0.92, 0.99, 0.96)), # Emerald Green
}

# Edge Colors
COLOR_EDGE_DORMANT = (0.20, 0.26, 0.36, 0.8) # Slate Dormant Edge
COLOR_EDGE_VISITED = (0.30, 0.38, 0.50, 0.6) # Non-tree traversed edge
COLOR_EDGE_TREE    = (0.55, 0.36, 0.96, 1.0) # Violet Spanning Tree Edge
COLOR_EDGE_GLOW    = (0.65, 0.45, 1.00, 0.3) # Violet Glow
COLOR_SIGNAL_CORE  = (0.22, 0.74, 0.97)      # Electric Cyan Particle
COLOR_SIGNAL_GLOW  = (0.02, 0.71, 0.83, 0.4) # Cyan Particle Glow


def find_ffmpeg(custom_path: Optional[str] = None) -> Optional[str]:
    """Locate the ffmpeg binary across system paths and Nix stores."""
    if custom_path and os.path.exists(custom_path) and os.access(custom_path, os.X_OK):
        return custom_path

    bin_path = shutil.which("ffmpeg")
    if bin_path:
        return bin_path

    known_paths = [
        "/nix/store/hymfywbp7rfkr3iymsiqx7i6x1ajpxvz-ffmpeg-8.1.2-bin/bin/ffmpeg",
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
    ]
    for p in known_paths:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p

    # Check Nix store glob matches if on NixOS
    nix_matches = glob.glob("/nix/store/*ffmpeg*/bin/ffmpeg")
    for m in nix_matches:
        if os.path.exists(m) and os.access(m, os.X_OK):
            return m

    return None


def random_connected_graph(nodes: int, edge_probability: float, seed: Optional[int]) -> dict[str, list[str]]:
    """Generate a connected undirected graph with a reproducible seed."""
    if not 3 <= nodes <= 26:
        raise ValueError("nodes must be between 3 and 26")
    if not 0.0 <= edge_probability <= 1.0:
        raise ValueError("edge_probability must be between 0.0 and 1.0")

    rng = random.Random(seed)
    labels = [chr(ord("A") + i) for i in range(nodes)]
    graph: dict[str, set[str]] = {label: set() for label in labels}

    # Spanning tree guarantees connectivity
    for idx in range(1, nodes):
        parent = labels[rng.randrange(idx)]
        child = labels[idx]
        graph[parent].add(child)
        graph[child].add(parent)

    # Add extra random edges according to probability
    for i in range(nodes):
        for j in range(i + 1, nodes):
            u, v = labels[i], labels[j]
            if v not in graph[u] and rng.random() < edge_probability:
                graph[u].add(v)
                graph[v].add(u)

    return {k: sorted(list(v)) for k, v in sorted(graph.items())}


def layout_graph(
    graph: dict[str, list[str]],
    box_x: float,
    box_y: float,
    box_w: float,
    box_h: float,
    margin: float = 65.0,
    seed: int = 42,
) -> dict[str, tuple[float, float]]:
    """Compute deterministic force-directed 2D positions for all nodes."""
    rng = random.Random(seed)
    nodes = sorted(list(graph.keys()))
    n = len(nodes)
    if n == 0:
        return {}

    center_x = box_x + box_w / 2.0
    center_y = box_y + box_h / 2.0
    init_r = min(box_w, box_h) * 0.35

    # Circular initialization
    pos: dict[str, list[float]] = {}
    for i, u in enumerate(nodes):
        angle = 2.0 * math.pi * i / n
        pos[u] = [center_x + init_r * math.cos(angle), center_y + init_r * math.sin(angle)]

    # Collect unique undirected edges
    unique_edges: set[tuple[str, str]] = set()
    for u in graph:
        for v in graph[u]:
            if u != v:
                unique_edges.add(tuple(sorted((u, v))))

    # Fruchterman-Reingold relaxation
    area = (box_w - 2 * margin) * (box_h - 2 * margin)
    k = math.sqrt(area / max(1, n)) * 0.72
    temp = min(box_w, box_h) * 0.12
    cooling = 0.95

    for _ in range(85):
        disp: dict[str, list[float]] = {u: [0.0, 0.0] for u in nodes}

        # Repulsion
        for i in range(n):
            u = nodes[i]
            for j in range(i + 1, n):
                v = nodes[j]
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                dist = math.hypot(dx, dy)
                if dist < 1e-4:
                    dx, dy, dist = rng.uniform(-1, 1), rng.uniform(-1, 1), 1.0
                rep = (k * k) / dist
                disp[u][0] += (dx / dist) * rep
                disp[u][1] += (dy / dist) * rep
                disp[v][0] -= (dx / dist) * rep
                disp[v][1] -= (dy / dist) * rep

        # Attraction
        for u, v in unique_edges:
            dx = pos[u][0] - pos[v][0]
            dy = pos[u][1] - pos[v][1]
            dist = math.hypot(dx, dy)
            if dist < 1e-4:
                continue
            attr = (dist * dist) / k
            disp[u][0] -= (dx / dist) * attr
            disp[u][1] -= (dy / dist) * attr
            disp[v][0] += (dx / dist) * attr
            disp[v][1] += (dy / dist) * attr

        # Displacement
        for u in nodes:
            d_len = math.hypot(disp[u][0], disp[u][1])
            if d_len > 1e-4:
                step = min(d_len, temp)
                pos[u][0] += (disp[u][0] / d_len) * step
                pos[u][1] += (disp[u][1] / d_len) * step

        temp *= cooling

    # Normalize within bounds
    xs = [pos[u][0] for u in nodes]
    ys = [pos[u][1] for u in nodes]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(1.0, max_x - min_x)
    span_y = max(1.0, max_y - min_y)

    avail_w = box_w - 2 * margin
    avail_h = box_h - 2 * margin
    scale = min(avail_w / span_x, avail_h / span_y)

    result: dict[str, tuple[float, float]] = {}
    for u in nodes:
        nx = (pos[u][0] - min_x - span_x / 2.0) * scale
        ny = (pos[u][1] - min_y - span_y / 2.0) * scale
        result[u] = (center_x + nx, center_y + ny)

    return result


class TraversalStep:
    """Represents an atomic animation state during graph traversal."""

    def __init__(
        self,
        step_number: int,
        action_type: str,
        title: str,
        description: str,
        active_node: Optional[str],
        target_neighbor: Optional[str],
        frontier: list[str],
        visited_nodes: set[str],
        visited_order: list[str],
        tree_edges: set[frozenset[str]],
        active_edges: set[frozenset[str]],
        pulse_progress: float = 0.0,
        frame_duration: int = 15,
    ):
        self.step_number = step_number
        self.action_type = action_type  # INIT, ACTIVATE, EXAMINE, DISCOVER, SKIP, COMPLETE_NODE, FINISHED
        self.title = title
        self.description = description
        self.active_node = active_node
        self.target_neighbor = target_neighbor
        self.frontier = frontier.copy()
        self.visited_nodes = visited_nodes.copy()
        self.visited_order = visited_order.copy()
        self.tree_edges = tree_edges.copy()
        self.active_edges = active_edges.copy()
        self.pulse_progress = pulse_progress
        self.frame_duration = frame_duration


def build_traversal_steps(
    graph: dict[str, list[str]],
    start_node: str,
    algorithm: str,
    frames_per_step: int = 16,
) -> list[TraversalStep]:
    """Generate fine-grained traversal events with animated transitions."""
    steps: list[TraversalStep] = []
    step_counter = 1

    frontier: list[str] = [start_node]
    discovered: set[str] = {start_node}
    visited_nodes: set[str] = set()
    visited_order: list[str] = []
    tree_edges: set[frozenset[str]] = set()

    is_bfs = algorithm == "bfs"
    ds_name = "FIFO Queue" if is_bfs else "LIFO Stack"

    # Step 0: Initialization
    steps.append(
        TraversalStep(
            step_number=step_counter,
            action_type="INIT",
            title=f"INITIALIZE {ds_name.upper()}",
            description=f"Push start node {start_node} to {ds_name}. Node marked Frontier.",
            active_node=None,
            target_neighbor=None,
            frontier=frontier,
            visited_nodes=visited_nodes,
            visited_order=visited_order,
            tree_edges=tree_edges,
            active_edges=set(),
            frame_duration=25,
        )
    )

    while frontier:
        step_counter += 1
        # Extract node
        if is_bfs:
            current = frontier.pop(0)  # Dequeue from front
            pop_desc = f"Dequeue node {current} from front of Queue."
            action_title = "DEQUEUE NODE"
        else:
            current = frontier.pop()  # Pop from top of stack
            pop_desc = f"Pop node {current} from top of Stack."
            action_title = "POP NODE"

        steps.append(
            TraversalStep(
                step_number=step_counter,
                action_type="ACTIVATE",
                title=action_title,
                description=pop_desc,
                active_node=current,
                target_neighbor=None,
                frontier=frontier,
                visited_nodes=visited_nodes,
                visited_order=visited_order,
                tree_edges=tree_edges,
                active_edges=set(),
                frame_duration=frames_per_step,
            )
        )

        neighbors = graph[current] if is_bfs else list(reversed(graph[current]))

        for neighbor in neighbors:
            step_counter += 1
            edge = frozenset((current, neighbor))
            is_unvisited = neighbor not in discovered

            # Signal traversal animation along edge
            if is_unvisited:
                discovered.add(neighbor)
                frontier.append(neighbor)
                tree_edges.add(edge)

                steps.append(
                    TraversalStep(
                        step_number=step_counter,
                        action_type="DISCOVER",
                        title="DISCOVER NEIGHBOR",
                        description=f"Explore edge ({current} -> {neighbor}). New node discovered! Added to {ds_name}.",
                        active_node=current,
                        target_neighbor=neighbor,
                        frontier=frontier,
                        visited_nodes=visited_nodes,
                        visited_order=visited_order,
                        tree_edges=tree_edges,
                        active_edges={edge},
                        frame_duration=frames_per_step,
                    )
                )
            else:
                steps.append(
                    TraversalStep(
                        step_number=step_counter,
                        action_type="SKIP",
                        title="EXAMINE NEIGHBOR",
                        description=f"Inspect edge ({current} -> {neighbor}). Neighbor already seen; skip.",
                        active_node=current,
                        target_neighbor=neighbor,
                        frontier=frontier,
                        visited_nodes=visited_nodes,
                        visited_order=visited_order,
                        tree_edges=tree_edges,
                        active_edges={edge},
                        frame_duration=max(8, frames_per_step // 2),
                    )
                )

        # Node finishes
        step_counter += 1
        visited_nodes.add(current)
        visited_order.append(current)

        steps.append(
            TraversalStep(
                step_number=step_counter,
                action_type="COMPLETE_NODE",
                title="NODE EXPLORATION DONE",
                description=f"All edges for {current} examined. Marked Visited and added to order.",
                active_node=current,
                target_neighbor=None,
                frontier=frontier,
                visited_nodes=visited_nodes,
                visited_order=visited_order,
                tree_edges=tree_edges,
                active_edges=set(),
                frame_duration=frames_per_step,
            )
        )

    # Traversal Complete
    step_counter += 1
    steps.append(
        TraversalStep(
            step_number=step_counter,
            action_type="FINISHED",
            title="TRAVERSAL COMPLETE",
            description=f"All {len(visited_order)} reachable nodes explored. Spanning tree complete.",
            active_node=None,
            target_neighbor=None,
            frontier=[],
            visited_nodes=visited_nodes,
            visited_order=visited_order,
            tree_edges=tree_edges,
            active_edges=set(),
            frame_duration=45,
        )
    )

    return steps


# Cairo Drawing Utilities
def draw_rounded_rect(
    ctx: cairo.Context,
    x: float,
    y: float,
    w: float,
    h: float,
    r: float,
) -> None:
    """Draw a smooth rounded rectangle path."""
    r = max(0.0, min(r, w / 2.0, h / 2.0))
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2.0, 0.0)
    ctx.arc(x + w - r, y + h - r, r, 0.0, math.pi / 2.0)
    ctx.arc(x + r, y + h - r, r, math.pi / 2.0, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3.0 * math.pi / 2.0)
    ctx.close_path()


def draw_text_centered(
    ctx: cairo.Context,
    text: str,
    cx: float,
    cy: float,
    font_size: float,
    font_bold: bool = True,
    color: tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> None:
    """Draw text centered at (cx, cy)."""
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if font_bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(font_size)
    ext = ctx.text_extents(text)
    x = cx - (ext.width / 2.0 + ext.x_bearing)
    y = cy - (ext.height / 2.0 + ext.y_bearing)
    ctx.set_source_rgb(*color)
    ctx.move_to(x, y)
    ctx.show_text(text)


def draw_card_panel(
    ctx: cairo.Context,
    x: float,
    y: float,
    w: float,
    h: float,
    title: Optional[str] = None,
    badge: Optional[str] = None,
    badge_color: tuple[float, float, float] = (0.02, 0.71, 0.83),
) -> None:
    """Draw a modern glass/slate card panel with title header."""
    # Outer Card
    draw_rounded_rect(ctx, x, y, w, h, 14.0)
    ctx.set_source_rgb(*COLOR_PANEL)
    ctx.fill_preserve()
    ctx.set_source_rgb(*COLOR_PANEL_BORDER)
    ctx.set_line_width(1.5)
    ctx.stroke()

    # Optional Header
    if title:
        header_h = 44.0
        # Header background
        ctx.save()
        draw_rounded_rect(ctx, x, y, w, header_h, 14.0)
        # Rectify bottom corners
        ctx.rectangle(x, y + 20.0, w, header_h - 20.0)
        ctx.set_source_rgb(0.09, 0.13, 0.20)
        ctx.fill()
        ctx.restore()

        # Header border divider
        ctx.set_source_rgb(*COLOR_PANEL_BORDER)
        ctx.set_line_width(1.0)
        ctx.move_to(x, y + header_h)
        ctx.line_to(x + w, y + header_h)
        ctx.stroke()

        # Title text
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgb(0.85, 0.90, 0.98)
        ctx.move_to(x + 18.0, y + 28.0)
        ctx.show_text(title)

        # Optional Right Badge
        if badge:
            ctx.set_font_size(12.0)
            b_ext = ctx.text_extents(badge)
            bw = b_ext.width + 16.0
            bh = 22.0
            bx = x + w - bw - 16.0
            by = y + 11.0
            draw_rounded_rect(ctx, bx, by, bw, bh, 6.0)
            ctx.set_source_rgba(badge_color[0], badge_color[1], badge_color[2], 0.2)
            ctx.fill_preserve()
            ctx.set_source_rgb(*badge_color)
            ctx.set_line_width(1.2)
            ctx.stroke()
            draw_text_centered(ctx, badge, bx + bw / 2.0, by + bh / 2.0, 11.0, font_bold=True, color=badge_color)


class TraversalVideoRenderer:
    """High-performance frame renderer for BFS and DFS traversal animations."""

    def __init__(
        self,
        graph: dict[str, list[str]],
        layout: dict[str, tuple[float, float]],
        algorithm: str,
        width: int = 1920,
        height: int = 1080,
    ):
        self.graph = graph
        self.layout = layout
        self.algorithm = algorithm
        self.width = width
        self.height = height

        # Precompute unique edges
        self.unique_edges: list[tuple[str, str]] = []
        for u in sorted(graph.keys()):
            for v in sorted(graph[u]):
                if u < v:
                    self.unique_edges.append((u, v))

        # Node radius based on node count
        n_nodes = len(graph)
        self.node_radius = max(24.0, min(36.0, 360.0 / math.sqrt(n_nodes * 2.5)))

    def render_frame(
        self,
        ctx: cairo.Context,
        step: TraversalStep,
        frame_idx: int,
        total_steps: int,
        global_frame: int,
    ) -> None:
        """Render a complete 1080p frame representing the current animation state."""
        # 1. Background
        ctx.set_source_rgb(*COLOR_BG)
        ctx.paint()

        # Stage Layout: Graph Canvas (Left) & Inspector HUD (Right)
        graph_x, graph_y = 40.0, 40.0
        graph_w, graph_h = 1240.0, 1000.0

        hud_x, hud_y = 1310.0, 40.0
        hud_w, hud_h = 570.0, 1000.0

        # Draw Graph Container
        draw_card_panel(
            ctx,
            graph_x,
            graph_y,
            graph_w,
            graph_h,
            title="GRAPH TOPOLOGY & EXPLORATION",
            badge=f"{len(self.graph)} Nodes · {len(self.unique_edges)} Edges",
            badge_color=(0.55, 0.36, 0.96),
        )

        # Subtle Dot Grid inside graph area
        self._draw_dot_grid(ctx, graph_x + 20.0, graph_y + 55.0, graph_w - 40.0, graph_h - 75.0)

        # Draw Edges & Active Signal Particles
        self._draw_edges(ctx, step, frame_idx)

        # Draw Nodes with Status & Glow
        self._draw_nodes(ctx, step, global_frame)

        # Draw HUD Memory Inspector
        self._draw_hud(ctx, hud_x, hud_y, hud_w, hud_h, step, total_steps, global_frame)

    def _draw_dot_grid(self, ctx: cairo.Context, x: float, y: float, w: float, h: float) -> None:
        """Draw a sleek subtle background dot grid."""
        spacing = 40.0
        ctx.set_source_rgb(*COLOR_GRID_DOT)
        curr_y = y + spacing / 2.0
        while curr_y < y + h:
            curr_x = x + spacing / 2.0
            while curr_x < x + w:
                ctx.arc(curr_x, curr_y, 1.2, 0.0, 2.0 * math.pi)
                ctx.fill()
                curr_x += spacing
            curr_y += spacing

    def _draw_edges(self, ctx: cairo.Context, step: TraversalStep, frame_idx: int) -> None:
        """Draw dormant, tree, and active traveling edges."""
        # 1. Dormant and Non-Tree Edges
        for u, v in self.unique_edges:
            pair = frozenset((u, v))
            if pair in step.tree_edges:
                continue  # Tree edges drawn in pass 2
            p1 = self.layout[u]
            p2 = self.layout[v]
            ctx.set_source_rgba(*COLOR_EDGE_DORMANT)
            ctx.set_line_width(2.5)
            ctx.move_to(p1[0], p1[1])
            ctx.line_to(p2[0], p2[1])
            ctx.stroke()

        # 2. Spanning Tree Edges (Thick with violet glow)
        for u, v in self.unique_edges:
            pair = frozenset((u, v))
            if pair in step.tree_edges:
                p1 = self.layout[u]
                p2 = self.layout[v]

                # Glow halo
                ctx.set_source_rgba(*COLOR_EDGE_GLOW)
                ctx.set_line_width(8.0)
                ctx.move_to(p1[0], p1[1])
                ctx.line_to(p2[0], p2[1])
                ctx.stroke()

                # Core tree line
                ctx.set_source_rgba(*COLOR_EDGE_TREE)
                ctx.set_line_width(4.0)
                ctx.move_to(p1[0], p1[1])
                ctx.line_to(p2[0], p2[1])
                ctx.stroke()

        # 3. Active Exploration Signal Particle
        if step.action_type in ("DISCOVER", "SKIP") and step.active_node and step.target_neighbor:
            u = step.active_node
            v = step.target_neighbor
            p1 = self.layout[u]
            p2 = self.layout[v]

            # Progress t from 0.0 to 1.0 along the edge
            t = min(1.0, max(0.0, frame_idx / max(1, step.frame_duration - 1)))
            part_x = (1.0 - t) * p1[0] + t * p2[0]
            part_y = (1.0 - t) * p1[1] + t * p2[1]

            # Glowing trail line from u to particle
            ctx.set_source_rgba(0.02, 0.71, 0.83, 0.6)
            ctx.set_line_width(3.0)
            ctx.move_to(p1[0], p1[1])
            ctx.line_to(part_x, part_y)
            ctx.stroke()

            # Glowing particle aura
            ctx.arc(part_x, part_y, 14.0, 0.0, 2.0 * math.pi)
            ctx.set_source_rgba(*COLOR_SIGNAL_GLOW)
            ctx.fill()

            # Solid particle core
            ctx.arc(part_x, part_y, 5.5, 0.0, 2.0 * math.pi)
            ctx.set_source_rgb(*COLOR_SIGNAL_CORE)
            ctx.fill()

    def _draw_nodes(self, ctx: cairo.Context, step: TraversalStep, global_frame: int) -> None:
        """Draw all graph nodes with high-contrast state styling and badges."""
        r = self.node_radius
        frontier_set = set(step.frontier)

        for node, (nx, ny) in sorted(self.layout.items()):
            # Determine Node State
            if node == step.active_node:
                state = "active"
            elif node in step.visited_nodes:
                state = "visited"
            elif node in frontier_set:
                state = "frontier"
            else:
                state = "unvisited"

            fill_c, border_c, text_c = NODE_COLORS[state]

            # Drop Shadow
            ctx.arc(nx + 2.0, ny + 3.0, r, 0.0, 2.0 * math.pi)
            ctx.set_source_rgba(0.0, 0.0, 0.0, 0.35)
            ctx.fill()

            # Active Pulsing Aura
            if state == "active":
                pulse_phase = (global_frame % 30) / 30.0
                pulse_r = r + 6.0 + 8.0 * math.sin(pulse_phase * math.pi)
                pulse_alpha = 0.5 * (1.0 - pulse_phase)
                ctx.arc(nx, ny, pulse_r, 0.0, 2.0 * math.pi)
                ctx.set_source_rgba(border_c[0], border_c[1], border_c[2], pulse_alpha)
                ctx.set_line_width(3.0)
                ctx.stroke()

            # Base Node Circle
            ctx.arc(nx, ny, r, 0.0, 2.0 * math.pi)
            ctx.set_source_rgb(*fill_c)
            ctx.fill_preserve()

            # Border Ring
            border_w = 4.0 if state in ("active", "frontier") else 2.5
            ctx.set_source_rgb(*border_c)
            ctx.set_line_width(border_w)
            ctx.stroke()

            # Node Label
            draw_text_centered(ctx, node, nx, ny, font_size=r * 0.72, font_bold=True, color=text_c)

            # Visited Order Badge (Small emerald circle with visit sequence index)
            if node in step.visited_order:
                order_idx = step.visited_order.index(node) + 1
                badge_r = 11.0
                bx = nx + r * 0.72
                by = ny - r * 0.72

                ctx.arc(bx, by, badge_r, 0.0, 2.0 * math.pi)
                ctx.set_source_rgb(0.06, 0.73, 0.51)
                ctx.fill_preserve()
                ctx.set_source_rgb(0.02, 0.28, 0.18)
                ctx.set_line_width(1.5)
                ctx.stroke()

                draw_text_centered(
                    ctx,
                    str(order_idx),
                    bx,
                    by,
                    font_size=11.0,
                    font_bold=True,
                    color=(1.0, 1.0, 1.0),
                )

    def _draw_hud(
        self,
        ctx: cairo.Context,
        x: float,
        y: float,
        w: float,
        h: float,
        step: TraversalStep,
        total_steps: int,
        global_frame: int,
    ) -> None:
        """Draw the right-side Memory Inspector HUD with live Queue/Stack and statistics."""
        is_bfs = self.algorithm == "bfs"
        alg_name = "Breadth-First Search (BFS)" if is_bfs else "Depth-First Search (DFS)"
        ds_badge = "FIFO QUEUE" if is_bfs else "LIFO STACK"
        ds_badge_color = (0.02, 0.71, 0.83) if is_bfs else (0.85, 0.20, 0.50)

        # 1. Main Inspector Card Frame
        draw_card_panel(
            ctx,
            x,
            y,
            w,
            h,
            title="ALGORITHM & MEMORY INSPECTOR",
            badge=ds_badge,
            badge_color=ds_badge_color,
        )

        inner_x = x + 20.0
        inner_w = w - 40.0
        curr_y = y + 60.0

        # Section A: Header & Complexities
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(20.0)
        ctx.set_source_rgb(0.95, 0.98, 1.0)
        ctx.move_to(inner_x, curr_y + 18.0)
        ctx.show_text(alg_name)

        # Complexity Pills
        curr_y += 32.0
        comp_text = "Time: O(V + E)  │  Space: O(V)"
        draw_rounded_rect(ctx, inner_x, curr_y, inner_w, 28.0, 6.0)
        ctx.set_source_rgba(0.12, 0.18, 0.28, 0.8)
        ctx.fill()
        draw_text_centered(
            ctx,
            comp_text,
            inner_x + inner_w / 2.0,
            curr_y + 14.0,
            font_size=12.0,
            font_bold=True,
            color=(0.65, 0.75, 0.90),
        )

        # Section B: Current Step & Action Commentary Card
        curr_y += 42.0
        card_h = 135.0
        draw_rounded_rect(ctx, inner_x, curr_y, inner_w, card_h, 10.0)
        ctx.set_source_rgb(0.09, 0.13, 0.22)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.22, 0.30, 0.44)
        ctx.set_line_width(1.2)
        ctx.stroke()

        # Step Counter Pill
        step_pill_w = 110.0
        step_pill_h = 24.0
        draw_rounded_rect(ctx, inner_x + 14.0, curr_y + 12.0, step_pill_w, step_pill_h, 5.0)
        ctx.set_source_rgba(0.55, 0.36, 0.96, 0.25)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.55, 0.36, 0.96)
        ctx.set_line_width(1.0)
        ctx.stroke()
        draw_text_centered(
            ctx,
            f"STEP {step.step_number:02d} / {total_steps:02d}",
            inner_x + 14.0 + step_pill_w / 2.0,
            curr_y + 12.0 + step_pill_h / 2.0,
            11.0,
            font_bold=True,
            color=(0.85, 0.75, 1.0),
        )

        # Action Title Badge
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        ctx.set_source_rgb(0.96, 0.62, 0.04)
        ctx.move_to(inner_x + 135.0, curr_y + 29.0)
        ctx.show_text(step.title)

        # Action Description (wrapped if long)
        self._draw_wrapped_text(
            ctx,
            text=step.description,
            x=inner_x + 14.0,
            y=curr_y + 56.0,
            max_width=inner_w - 28.0,
            line_height=20.0,
            font_size=13.5,
            color=(0.85, 0.90, 0.98),
        )

        # Section C: Live Memory Data Structure Visualizer (Queue or Stack)
        curr_y += card_h + 18.0
        if is_bfs:
            curr_y = self._draw_queue_visualizer(ctx, inner_x, curr_y, inner_w, step)
        else:
            curr_y = self._draw_stack_visualizer(ctx, inner_x, curr_y, inner_w, step)

        # Section D: Visited Sequence Ribbon
        curr_y += 18.0
        curr_y = self._draw_visited_sequence(ctx, inner_x, curr_y, inner_w, step, global_frame)

        # Section E: State Legend & Stats
        curr_y += 18.0
        self._draw_legend_and_progress(ctx, inner_x, curr_y, inner_w, step, total_steps)

    def _draw_queue_visualizer(
        self,
        ctx: cairo.Context,
        x: float,
        y: float,
        w: float,
        step: TraversalStep,
    ) -> float:
        """Draw the animated horizontal FIFO Queue memory visualizer."""
        container_h = 160.0
        draw_rounded_rect(ctx, x, y, w, container_h, 10.0)
        ctx.set_source_rgb(0.08, 0.12, 0.19)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.18, 0.25, 0.36)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Title and element count
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.0)
        ctx.set_source_rgb(0.02, 0.71, 0.83)
        ctx.move_to(x + 14.0, y + 24.0)
        ctx.show_text("ACTIVE MEMORY: QUEUE (FIFO)")

        ctx.set_font_size(11.0)
        ctx.set_source_rgb(0.60, 0.70, 0.85)
        ctx.move_to(x + w - 120.0, y + 24.0)
        ctx.show_text(f"Length: {len(step.frontier)}")

        # Track Rail Background
        rail_y = y + 42.0
        rail_h = 76.0
        draw_rounded_rect(ctx, x + 10.0, rail_y, w - 20.0, rail_h, 6.0)
        ctx.set_source_rgba(0.04, 0.07, 0.12, 0.9)
        ctx.fill()

        # Labels: [FRONT] Dequeue <--- | --- Enqueue [REAR]
        ctx.set_font_size(11.0)
        ctx.set_source_rgb(0.96, 0.62, 0.04)
        ctx.move_to(x + 16.0, rail_y + 18.0)
        ctx.show_text("◀ FRONT (Dequeue)")

        ctx.set_source_rgb(0.02, 0.71, 0.83)
        ctx.move_to(x + w - 150.0, rail_y + 18.0)
        ctx.show_text("REAR (Enqueue) ◀")

        # Draw Queue Cards
        card_w, card_h = 44.0, 44.0
        gap = 8.0
        items = step.frontier

        if not items:
            draw_text_centered(
                ctx,
                "(Queue Empty)",
                x + w / 2.0,
                rail_y + 44.0,
                font_size=13.0,
                font_bold=False,
                color=(0.40, 0.48, 0.60),
            )
        else:
            start_x = x + 20.0
            max_visible = min(len(items), int((w - 40.0) / (card_w + gap)))
            for i in range(max_visible):
                cx = start_x + i * (card_w + gap)
                cy = rail_y + 26.0

                # Front card highlight
                is_front = i == 0
                draw_rounded_rect(ctx, cx, cy, card_w, card_h, 6.0)
                if is_front:
                    ctx.set_source_rgb(0.18, 0.10, 0.02)
                    ctx.fill_preserve()
                    ctx.set_source_rgb(0.96, 0.62, 0.04)
                else:
                    ctx.set_source_rgb(0.04, 0.20, 0.28)
                    ctx.fill_preserve()
                    ctx.set_source_rgb(0.02, 0.71, 0.83)
                ctx.set_line_width(1.8)
                ctx.stroke()

                draw_text_centered(
                    ctx,
                    items[i],
                    cx + card_w / 2.0,
                    cy + card_h / 2.0,
                    font_size=18.0,
                    font_bold=True,
                    color=(1.0, 1.0, 1.0),
                )

            if len(items) > max_visible:
                overflow_text = f"+{len(items) - max_visible} more"
                ctx.set_font_size(11.0)
                ctx.set_source_rgb(0.60, 0.70, 0.85)
                ctx.move_to(start_x + max_visible * (card_w + gap), rail_y + 52.0)
                ctx.show_text(overflow_text)

        # Bottom descriptor
        ctx.set_font_size(11.0)
        ctx.set_source_rgb(0.50, 0.60, 0.75)
        ctx.move_to(x + 14.0, y + 145.0)
        ctx.show_text("FIFO Policy: Oldest discovered node is dequeued first.")

        return y + container_h

    def _draw_stack_visualizer(
        self,
        ctx: cairo.Context,
        x: float,
        y: float,
        w: float,
        step: TraversalStep,
    ) -> float:
        """Draw the animated vertical LIFO Stack memory visualizer."""
        container_h = 160.0
        draw_rounded_rect(ctx, x, y, w, container_h, 10.0)
        ctx.set_source_rgb(0.08, 0.12, 0.19)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.18, 0.25, 0.36)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Header
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.0)
        ctx.set_source_rgb(0.85, 0.20, 0.50)
        ctx.move_to(x + 14.0, y + 24.0)
        ctx.show_text("ACTIVE MEMORY: STACK (LIFO)")

        ctx.set_font_size(11.0)
        ctx.set_source_rgb(0.60, 0.70, 0.85)
        ctx.move_to(x + w - 120.0, y + 24.0)
        ctx.show_text(f"Depth: {len(step.frontier)}")

        # Stack Rack
        rack_y = y + 42.0
        rack_h = 76.0
        draw_rounded_rect(ctx, x + 10.0, rack_y, w - 20.0, rack_h, 6.0)
        ctx.set_source_rgba(0.04, 0.07, 0.12, 0.9)
        ctx.fill()

        # Labels: TOP OF STACK (Push/Pop)
        ctx.set_font_size(11.0)
        ctx.set_source_rgb(0.96, 0.62, 0.04)
        ctx.move_to(x + 16.0, rack_y + 18.0)
        ctx.show_text("▲ TOP OF STACK (Next to Pop)")

        ctx.set_source_rgb(0.50, 0.58, 0.70)
        ctx.move_to(x + w - 120.0, rack_y + 18.0)
        ctx.show_text("BOTTOM (Base)")

        items = list(reversed(step.frontier))  # Top of stack first!
        card_w, card_h = 44.0, 44.0
        gap = 8.0

        if not items:
            draw_text_centered(
                ctx,
                "(Stack Empty)",
                x + w / 2.0,
                rack_y + 44.0,
                font_size=13.0,
                font_bold=False,
                color=(0.40, 0.48, 0.60),
            )
        else:
            start_x = x + 20.0
            max_visible = min(len(items), int((w - 40.0) / (card_w + gap)))
            for i in range(max_visible):
                cx = start_x + i * (card_w + gap)
                cy = rack_y + 26.0
                is_top = i == 0

                draw_rounded_rect(ctx, cx, cy, card_w, card_h, 6.0)
                if is_top:
                    ctx.set_source_rgb(0.24, 0.08, 0.14)
                    ctx.fill_preserve()
                    ctx.set_source_rgb(0.96, 0.62, 0.04)
                else:
                    ctx.set_source_rgb(0.12, 0.06, 0.16)
                    ctx.fill_preserve()
                    ctx.set_source_rgb(0.85, 0.20, 0.50)
                ctx.set_line_width(1.8)
                ctx.stroke()

                draw_text_centered(
                    ctx,
                    items[i],
                    cx + card_w / 2.0,
                    cy + card_h / 2.0,
                    font_size=18.0,
                    font_bold=True,
                    color=(1.0, 1.0, 1.0),
                )

            if len(items) > max_visible:
                overflow_text = f"+{len(items) - max_visible} more"
                ctx.set_font_size(11.0)
                ctx.set_source_rgb(0.60, 0.70, 0.85)
                ctx.move_to(start_x + max_visible * (card_w + gap), rack_y + 52.0)
                ctx.show_text(overflow_text)

        # Bottom descriptor
        ctx.set_font_size(11.0)
        ctx.set_source_rgb(0.50, 0.60, 0.75)
        ctx.move_to(x + 14.0, y + 145.0)
        ctx.show_text("LIFO Policy: Most recently discovered node is popped first (depth plunge).")

        return y + container_h

    def _draw_visited_sequence(
        self,
        ctx: cairo.Context,
        x: float,
        y: float,
        w: float,
        step: TraversalStep,
        global_frame: int,
    ) -> float:
        """Draw the sequential order ribbon of visited nodes."""
        container_h = 135.0
        draw_rounded_rect(ctx, x, y, w, container_h, 10.0)
        ctx.set_source_rgb(0.08, 0.12, 0.19)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.18, 0.25, 0.36)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Header
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.0)
        ctx.set_source_rgb(0.06, 0.73, 0.51)
        ctx.move_to(x + 14.0, y + 24.0)
        ctx.show_text("VISITED ORDER SEQUENCE")

        ctx.set_font_size(11.0)
        ctx.set_source_rgb(0.60, 0.70, 0.85)
        ctx.move_to(x + w - 160.0, y + 24.0)
        ctx.show_text(f"Completed: {len(step.visited_order)} / {len(self.graph)}")

        # Ribbon rack
        rack_y = y + 36.0
        pill_w = 40.0
        pill_h = 36.0
        gap_x = 22.0
        gap_y = 12.0

        if not step.visited_order:
            draw_text_centered(
                ctx,
                "(No nodes fully completed yet)",
                x + w / 2.0,
                rack_y + 40.0,
                font_size=13.0,
                font_bold=False,
                color=(0.40, 0.48, 0.60),
            )
        else:
            max_per_row = max(1, int((w - 30.0) / (pill_w + gap_x)))
            for idx, node in enumerate(step.visited_order):
                row = idx // max_per_row
                col = idx % max_per_row
                px = x + 16.0 + col * (pill_w + gap_x)
                py = rack_y + 8.0 + row * (pill_h + gap_y)

                is_latest = idx == len(step.visited_order) - 1

                draw_rounded_rect(ctx, px, py, pill_w, pill_h, 6.0)
                if is_latest:
                    ctx.set_source_rgb(0.04, 0.38, 0.24)
                    ctx.fill_preserve()
                    ctx.set_source_rgb(0.06, 0.90, 0.60)
                    ctx.set_line_width(2.0)
                else:
                    ctx.set_source_rgb(0.02, 0.24, 0.15)
                    ctx.fill_preserve()
                    ctx.set_source_rgb(0.06, 0.73, 0.51)
                    ctx.set_line_width(1.2)
                ctx.stroke()

                draw_text_centered(
                    ctx,
                    node,
                    px + pill_w / 2.0,
                    py + pill_h / 2.0,
                    font_size=16.0,
                    font_bold=True,
                    color=(1.0, 1.0, 1.0),
                )

                # Small connector arrow if not end of row and has next
                if col < max_per_row - 1 and idx < len(step.visited_order) - 1:
                    arrow_x = px + pill_w + 5.0
                    arrow_y = py + pill_h / 2.0
                    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    ctx.set_font_size(12.0)
                    ctx.set_source_rgb(0.35, 0.45, 0.58)
                    ctx.move_to(arrow_x, arrow_y + 4.0)
                    ctx.show_text("→")

        return y + container_h

    def _draw_legend_and_progress(
        self,
        ctx: cairo.Context,
        x: float,
        y: float,
        w: float,
        step: TraversalStep,
        total_steps: int,
    ) -> None:
        """Draw state color legend, metrics, and traversal progress bar."""
        # Legend items
        legend = [
            ("Unvisited", NODE_COLORS["unvisited"][1]),
            ("Frontier", NODE_COLORS["frontier"][1]),
            ("Active", NODE_COLORS["active"][1]),
            ("Visited", NODE_COLORS["visited"][1]),
            ("Tree Edge", COLOR_EDGE_TREE[:3]),
        ]

        # Draw legend pills
        item_w = w / len(legend)
        for i, (label, col) in enumerate(legend):
            lx = x + i * item_w
            ctx.arc(lx + 8.0, y + 10.0, 5.0, 0.0, 2.0 * math.pi)
            ctx.set_source_rgb(*col)
            ctx.fill()

            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(11.5)
            ctx.set_source_rgb(0.70, 0.78, 0.88)
            ctx.move_to(lx + 18.0, y + 14.0)
            ctx.show_text(label)

        # Traversal Progress Bar
        bar_y = y + 36.0
        bar_h = 10.0
        pct = min(1.0, max(0.0, step.step_number / max(1, total_steps)))

        draw_rounded_rect(ctx, x, bar_y, w, bar_h, 5.0)
        ctx.set_source_rgba(0.12, 0.16, 0.24, 0.8)
        ctx.fill()

        if pct > 0.01:
            draw_rounded_rect(ctx, x, bar_y, w * pct, bar_h, 5.0)
            ctx.set_source_rgb(0.02, 0.71, 0.83)
            ctx.fill()

        # Progress text
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.set_source_rgb(0.50, 0.60, 0.75)
        ctx.move_to(x, bar_y + 24.0)
        ctx.show_text(f"Overall Walkthrough Progress: {int(pct * 100)}%")

    def _draw_wrapped_text(
        self,
        ctx: cairo.Context,
        text: str,
        x: float,
        y: float,
        max_width: float,
        line_height: float,
        font_size: float,
        color: tuple[float, float, float],
    ) -> None:
        """Helper to render multi-line text with word wrapping."""
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)
        ctx.set_source_rgb(*color)

        words = text.split()
        lines: list[str] = []
        current_line: list[str] = []

        for w in words:
            test_line = " ".join(current_line + [w])
            ext = ctx.text_extents(test_line)
            if ext.width <= max_width:
                current_line.append(w)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [w]
                else:
                    lines.append(w)
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        for idx, line in enumerate(lines[:3]):
            ctx.move_to(x, y + idx * line_height)
            ctx.show_text(line)


class ComparativeTraversalRenderer:
    """Side-by-side comparative renderer presenting BFS vs DFS on identical graphs."""

    def __init__(
        self,
        graph: dict[str, list[str]],
        layout: dict[str, tuple[float, float]],
        bfs_steps: list[TraversalStep],
        dfs_steps: list[TraversalStep],
        width: int = 1920,
        height: int = 1080,
    ):
        self.graph = graph
        self.layout = layout
        self.bfs_steps = bfs_steps
        self.dfs_steps = dfs_steps
        self.width = width
        self.height = height

        # Compute dual layouts: one for left half, one for right half
        self.bfs_layout = layout_graph(graph, box_x=30.0, box_y=110.0, box_w=890.0, box_h=720.0, margin=55.0)
        self.dfs_layout = layout_graph(graph, box_x=990.0, box_y=110.0, box_w=890.0, box_h=720.0, margin=55.0)

        self.bfs_renderer = TraversalVideoRenderer(graph, self.bfs_layout, "bfs", width=920, height=height)
        self.dfs_renderer = TraversalVideoRenderer(graph, self.dfs_layout, "dfs", width=920, height=height)

    def render_frame(
        self,
        ctx: cairo.Context,
        bfs_step: TraversalStep,
        dfs_step: TraversalStep,
        bfs_frame: int,
        dfs_frame: int,
        global_frame: int,
    ) -> None:
        """Render a comparative side-by-side frame with synchronized execution."""
        # 1. Background
        ctx.set_source_rgb(*COLOR_BG)
        ctx.paint()

        # 2. Main Title Banner
        draw_rounded_rect(ctx, 30.0, 20.0, self.width - 60.0, 68.0, 10.0)
        ctx.set_source_rgb(0.08, 0.12, 0.19)
        ctx.fill_preserve()
        ctx.set_source_rgb(*COLOR_PANEL_BORDER)
        ctx.set_line_width(1.5)
        ctx.stroke()

        draw_text_centered(
            ctx,
            "GRAPH TRAVERSAL COMPARISON: BREADTH-FIRST SEARCH vs DEPTH-FIRST SEARCH",
            self.width / 2.0,
            42.0,
            font_size=20.0,
            font_bold=True,
            color=(0.95, 0.98, 1.0),
        )
        draw_text_centered(
            ctx,
            "Wavefront Level-by-Level Expansion (Queue)  vs  Deep Branch Diving with Backtracking (Stack)",
            self.width / 2.0,
            68.0,
            font_size=13.0,
            font_bold=False,
            color=(0.60, 0.72, 0.88),
        )

        # 3. Left Panel: BFS
        panel_w = 910.0
        draw_card_panel(
            ctx,
            30.0,
            105.0,
            panel_w,
            945.0,
            title="BREADTH-FIRST SEARCH (BFS)",
            badge="FIFO QUEUE",
            badge_color=(0.02, 0.71, 0.83),
        )
        self.bfs_renderer._draw_dot_grid(ctx, 45.0, 155.0, panel_w - 30.0, 660.0)
        self.bfs_renderer._draw_edges(ctx, bfs_step, bfs_frame)
        self.bfs_renderer._draw_nodes(ctx, bfs_step, global_frame)

        # BFS Mini Bottom HUD
        self._draw_mini_hud(ctx, 45.0, 830.0, panel_w - 30.0, bfs_step, "bfs", (0.02, 0.71, 0.83))

        # 4. Right Panel: DFS
        draw_card_panel(
            ctx,
            970.0,
            105.0,
            panel_w,
            945.0,
            title="DEPTH-FIRST SEARCH (DFS)",
            badge="LIFO STACK",
            badge_color=(0.85, 0.20, 0.50),
        )
        self.dfs_renderer._draw_dot_grid(ctx, 985.0, 155.0, panel_w - 30.0, 660.0)
        self.dfs_renderer._draw_edges(ctx, dfs_step, dfs_frame)
        self.dfs_renderer._draw_nodes(ctx, dfs_step, global_frame)

        # DFS Mini Bottom HUD
        self._draw_mini_hud(ctx, 985.0, 830.0, panel_w - 30.0, dfs_step, "dfs", (0.85, 0.20, 0.50))

        # 5. Center Divider "VS" Badge
        cx = self.width / 2.0
        cy = 500.0
        ctx.arc(cx, cy, 26.0, 0.0, 2.0 * math.pi)
        ctx.set_source_rgb(0.08, 0.12, 0.20)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.55, 0.36, 0.96)
        ctx.set_line_width(2.5)
        ctx.stroke()
        draw_text_centered(ctx, "VS", cx, cy, 15.0, font_bold=True, color=(0.95, 0.90, 1.0))

    def _draw_mini_hud(
        self,
        ctx: cairo.Context,
        x: float,
        y: float,
        w: float,
        step: TraversalStep,
        algorithm: str,
        theme_color: tuple[float, float, float],
    ) -> None:
        """Draw compact bottom summary card for side-by-side mode."""
        draw_rounded_rect(ctx, x, y, w, 200.0, 8.0)
        ctx.set_source_rgb(0.08, 0.12, 0.19)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.18, 0.25, 0.36)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Step and Title
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.0)
        ctx.set_source_rgb(*theme_color)
        ctx.move_to(x + 14.0, y + 24.0)
        ctx.show_text(f"Step {step.step_number}: {step.title}")

        # Description
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12.5)
        ctx.set_source_rgb(0.85, 0.90, 0.98)
        ctx.move_to(x + 14.0, y + 46.0)
        ctx.show_text(step.description[:95] + ("..." if len(step.description) > 95 else ""))

        # Frontier sequence
        ds_type = "Queue (Front → Rear)" if algorithm == "bfs" else "Stack (Top → Bottom)"
        frontier_items = step.frontier if algorithm == "bfs" else list(reversed(step.frontier))
        frontier_str = " → ".join(frontier_items) if frontier_items else "(empty)"

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12.0)
        ctx.set_source_rgb(0.65, 0.75, 0.88)
        ctx.move_to(x + 14.0, y + 74.0)
        ctx.show_text(f"{ds_type}:  ")

        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.show_text(frontier_str)

        # Visited sequence
        vis_str = " → ".join(step.visited_order) if step.visited_order else "(none)"
        ctx.set_source_rgb(0.06, 0.73, 0.51)
        ctx.move_to(x + 14.0, y + 102.0)
        ctx.show_text("Visited Order:  ")

        ctx.set_source_rgb(0.90, 0.98, 0.94)
        ctx.show_text(vis_str)

        # Spanning Tree Edges count
        ctx.set_font_size(11.5)
        ctx.set_source_rgb(0.55, 0.65, 0.80)
        ctx.move_to(x + 14.0, y + 132.0)
        ctx.show_text(f"Spanning Tree Edges: {len(step.tree_edges)}  │  Total Visited: {len(step.visited_order)}")


def render_standalone_video(
    graph: dict[str, list[str]],
    layout: dict[str, tuple[float, float]],
    algorithm: str,
    output_path: Path,
    start_node: str = "A",
    fps: int = 30,
    width: int = 1920,
    height: int = 1080,
    ffmpeg_bin: Optional[str] = None,
    save_preview_frame: Optional[Path] = None,
) -> None:
    """Encode a standalone high-definition traversal video (BFS or DFS)."""
    ffmpeg_cmd = find_ffmpeg(ffmpeg_bin)
    if not ffmpeg_cmd:
        raise RuntimeError("FFmpeg executable not found. Please install ffmpeg or specify --ffmpeg-bin.")

    steps = build_traversal_steps(graph, start_node, algorithm)
    renderer = TraversalVideoRenderer(graph, layout, algorithm, width=width, height=height)

    # Calculate total frames
    total_frames = 20 + sum(s.frame_duration for s in steps) + 45
    print(f"[{algorithm.upper()}] Encoding {total_frames} frames ({total_frames / fps:.1f}s) to {output_path}...")

    # Spawn ffmpeg
    cmd = [
        ffmpeg_cmd,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "bgra",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "19",
        str(output_path),
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    global_frame = 0

    # 1. Initial Hold
    init_step = steps[0]
    for f in range(20):
        renderer.render_frame(ctx, init_step, f, len(steps), global_frame)
        surface.flush()
        proc.stdin.write(surface.get_data())
        global_frame += 1

    # 2. Main Traversal Steps
    mid_frame_saved = False
    for step_idx, step in enumerate(steps):
        for f in range(step.frame_duration):
            renderer.render_frame(ctx, step, f, len(steps), global_frame)
            surface.flush()
            proc.stdin.write(surface.get_data())

            # Save preview frame if requested
            if save_preview_frame and not mid_frame_saved and step_idx == len(steps) // 2:
                surface.write_to_png(str(save_preview_frame))
                mid_frame_saved = True

            global_frame += 1

    # 3. Final Hold
    final_step = steps[-1]
    for f in range(45):
        renderer.render_frame(ctx, final_step, f, len(steps), global_frame)
        surface.flush()
        proc.stdin.write(surface.get_data())
        global_frame += 1

    proc.stdin.close()
    err = proc.stderr.read() if proc.stderr else b""
    if proc.stderr:
        proc.stderr.close()
    proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg encoding failed with code {proc.returncode}:\n{err.decode('utf-8', errors='replace')[-600:]}")

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[{algorithm.upper()}] Successfully created {output_path} ({size_mb:.2f} MB)")


def render_comparative_video(
    graph: dict[str, list[str]],
    layout: dict[str, tuple[float, float]],
    output_path: Path,
    start_node: str = "A",
    fps: int = 30,
    width: int = 1920,
    height: int = 1080,
    ffmpeg_bin: Optional[str] = None,
    save_preview_frame: Optional[Path] = None,
) -> None:
    """Encode a comparative side-by-side video contrasting BFS and DFS."""
    ffmpeg_cmd = find_ffmpeg(ffmpeg_bin)
    if not ffmpeg_cmd:
        raise RuntimeError("FFmpeg executable not found. Please install ffmpeg or specify --ffmpeg-bin.")

    bfs_steps = build_traversal_steps(graph, start_node, "bfs")
    dfs_steps = build_traversal_steps(graph, start_node, "dfs")

    renderer = ComparativeTraversalRenderer(graph, layout, bfs_steps, dfs_steps, width=width, height=height)

    # Align step sequences by step progress
    max_steps = max(len(bfs_steps), len(dfs_steps))
    total_frames = 20 + max_steps * 18 + 50
    print(f"[COMPARISON] Encoding {total_frames} frames ({total_frames / fps:.1f}s) to {output_path}...")

    cmd = [
        ffmpeg_cmd,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "bgra",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "19",
        str(output_path),
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    global_frame = 0

    # 1. Initial Hold
    for f in range(20):
        renderer.render_frame(ctx, bfs_steps[0], dfs_steps[0], f, f, global_frame)
        surface.flush()
        proc.stdin.write(surface.get_data())
        global_frame += 1

    # 2. Stepping Loop
    step_duration = 18
    mid_saved = False
    for s_idx in range(max_steps):
        b_step = bfs_steps[min(s_idx, len(bfs_steps) - 1)]
        d_step = dfs_steps[min(s_idx, len(dfs_steps) - 1)]

        for f in range(step_duration):
            renderer.render_frame(ctx, b_step, d_step, f, f, global_frame)
            surface.flush()
            proc.stdin.write(surface.get_data())

            if save_preview_frame and not mid_saved and s_idx == max_steps // 2:
                surface.write_to_png(str(save_preview_frame))
                mid_saved = True

            global_frame += 1

    # 3. Final Hold
    for f in range(50):
        renderer.render_frame(ctx, bfs_steps[-1], dfs_steps[-1], f, f, global_frame)
        surface.flush()
        proc.stdin.write(surface.get_data())
        global_frame += 1

    proc.stdin.close()
    err = proc.stderr.read() if proc.stderr else b""
    if proc.stderr:
        proc.stderr.close()
    proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg encoding failed with code {proc.returncode}:\n{err.decode('utf-8', errors='replace')[-600:]}")

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[COMPARISON] Successfully created {output_path} ({size_mb:.2f} MB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create demonstrative graph traversal animation videos (BFS & DFS).")
    parser.add_argument(
        "--algorithm",
        choices=("bfs", "dfs", "both", "comparison", "all"),
        default="all",
        help="algorithm to visualize: bfs, dfs, both, comparison, or all",
    )
    parser.add_argument("--output", type=Path, default=Path("output"), help="directory for generated MP4 files")
    parser.add_argument("--graph-json", type=Path, help="path to graph.json metadata file to reuse existing graph")
    parser.add_argument("--random-graph", action="store_true", help="generate a random connected graph")
    parser.add_argument("--nodes", type=int, default=10, help="number of nodes (3-26) for random graph")
    parser.add_argument("--edge-probability", type=float, default=0.30, help="edge probability for random graph")
    parser.add_argument("--seed", type=int, default=42, help="random seed for reproducible graph generation")
    parser.add_argument("--start-node", help="node from which to start the traversal")
    parser.add_argument("--fps", type=int, default=30, help="video framerate (default 30)")
    parser.add_argument("--width", type=int, default=1920, help="video width in pixels (default 1920)")
    parser.add_argument("--height", type=int, default=1080, help="video height in pixels (default 1080)")
    parser.add_argument("--ffmpeg-bin", help="path to ffmpeg binary executable")
    parser.add_argument("--save-frames", action="store_true", help="export sample preview PNG frames")

    args = parser.parse_args()

    # Determine Graph
    if args.graph_json and args.graph_json.exists():
        with open(args.graph_json, "r", encoding="utf-8") as f:
            meta = json.load(f)
            graph = meta.get("graph", DEFAULT_GRAPH)
            start_node = args.start_node or meta.get("start_node", DEFAULT_START_NODE)
            seed = meta.get("random_seed", args.seed)
    elif args.random_graph:
        graph = random_connected_graph(args.nodes, args.edge_probability, args.seed)
        start_node = args.start_node or next(iter(graph))
        seed = args.seed
    else:
        graph = DEFAULT_GRAPH
        start_node = args.start_node or DEFAULT_START_NODE
        seed = args.seed

    if start_node not in graph:
        start_node = next(iter(graph))

    args.output.mkdir(parents=True, exist_ok=True)

    # Compute graph layout for 1200x950 stage
    layout = layout_graph(graph, box_x=60.0, box_y=80.0, box_w=1200.0, box_h=920.0, margin=75.0, seed=seed)

    # Write manifest / metadata
    manifest = {
        "graph": graph,
        "start_node": start_node,
        "seed": seed,
        "nodes": len(graph),
        "edges": sum(len(neighbors) for neighbors in graph.values()) // 2,
        "generated_videos": [],
    }

    # Render Selected Animations
    alg_choice = args.algorithm

    if alg_choice in ("bfs", "both", "all"):
        out_bfs = args.output / "bfs_traversal.mp4"
        prev_bfs = (args.output / "bfs_traversal_preview.png") if args.save_frames else None
        render_standalone_video(
            graph,
            layout,
            "bfs",
            out_bfs,
            start_node=start_node,
            fps=args.fps,
            width=args.width,
            height=args.height,
            ffmpeg_bin=args.ffmpeg_bin,
            save_preview_frame=prev_bfs,
        )
        manifest["generated_videos"].append({
            "algorithm": "bfs",
            "filename": out_bfs.name,
            "title": "Breadth-First Search (BFS) Animation",
            "data_structure": "FIFO Queue",
        })

    if alg_choice in ("dfs", "both", "all"):
        out_dfs = args.output / "dfs_traversal.mp4"
        prev_dfs = (args.output / "dfs_traversal_preview.png") if args.save_frames else None
        render_standalone_video(
            graph,
            layout,
            "dfs",
            out_dfs,
            start_node=start_node,
            fps=args.fps,
            width=args.width,
            height=args.height,
            ffmpeg_bin=args.ffmpeg_bin,
            save_preview_frame=prev_dfs,
        )
        manifest["generated_videos"].append({
            "algorithm": "dfs",
            "filename": out_dfs.name,
            "title": "Depth-First Search (DFS) Animation",
            "data_structure": "LIFO Stack",
        })

    if alg_choice in ("comparison", "all"):
        out_comp = args.output / "bfs_dfs_comparison.mp4"
        prev_comp = (args.output / "bfs_dfs_comparison_preview.png") if args.save_frames else None
        render_comparative_video(
            graph,
            layout,
            out_comp,
            start_node=start_node,
            fps=args.fps,
            width=args.width,
            height=args.height,
            ffmpeg_bin=args.ffmpeg_bin,
            save_preview_frame=prev_comp,
        )
        manifest["generated_videos"].append({
            "algorithm": "comparison",
            "filename": out_comp.name,
            "title": "Comparative Traversal: BFS vs DFS",
            "data_structure": "Queue vs Stack",
        })

    (args.output / "video_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("All requested traversal animations generated successfully!")


if __name__ == "__main__":
    main()
