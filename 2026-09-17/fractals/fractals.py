#!/usr/bin/env python3
"""
Fractal SVG Generator
=====================
Generates mathematically rigorous, high-resolution, responsive SVGs of
fractals across three difficulty tiers (Easy, Medium, Hard):

Level 1 (Easy - Elementary Recursive Geometry & Removals):
  1. Cantor Set / Dust
  2. Koch Snowflake & Anti-Snowflake
  3. Sierpiński Triangle (Gasket)
  4. Sierpiński Carpet
  5. Vicsek Fractal (Box Fractal)

Level 2 (Medium - Branching Trees, L-Systems & Space-Filling Curves):
  6. Pythagoras Tree (Symmetric & Asymmetric)
  7. Heighway Dragon Curve
  8. Hilbert Space-Filling Curve
  9. Fractal Binary Canopy (Botanical Tree)
  10. Lévy C Curve

Level 3 (Hard - Iterated Function Systems & Complex Dynamics):
  11. Barnsley Fern (IFS Chaos Game)
  12. Gosper Curve (Flowsnake Hexagonal Space-Filling L-System)
  13. Mandelbrot Set (Escape-Time Boundary Contours)
  14. Julia Set (Quadratic Polynomial Dynamics)
  15. Newton-Raphson Basins of Attraction Fractal

Zero external dependencies: only uses Python 3 standard library.
"""

from __future__ import annotations

import argparse
import colorsys
import cmath
import json
import math
import os
from pathlib import Path
import random
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple


# ==============================================================================
# Palette & Color Utilities
# ==============================================================================

PALETTES: Dict[str, List[str]] = {
    "neon": [
        "#00f0ff", "#00ff66", "#ffe600", "#ff007f", "#9d00ff", "#00d4ff", "#ff00c8"
    ],
    "cyberpunk": [
        "#fcee0a", "#00f0ff", "#ff0055", "#7122fa", "#05d9e8", "#ff2a6d", "#01012b"
    ],
    "sunset": [
        "#f72585", "#b5179e", "#7209b7", "#560bad", "#480ca8", "#3a0ca3", "#3f37c9", "#4cc9f0"
    ],
    "emerald": [
        "#059669", "#10b981", "#34d399", "#6ee7b7", "#a7f3d0", "#047857", "#065f46"
    ],
    "ocean": [
        "#03045e", "#023e8a", "#0077b6", "#0096c7", "#00b4d8", "#48cae4", "#90e0ef", "#ade8f4"
    ],
    "fire": [
        "#ff4800", "#ff5400", "#ff6000", "#ff6d00", "#ff7900", "#ff8500", "#ff9100", "#ff9e00", "#ffaa00"
    ],
    "gold": [
        "#bf953f", "#fcf6ba", "#b38728", "#fbf5b7", "#aa771c", "#d4af37", "#f3e5ab"
    ],
}


def get_gradient_color(palette: List[str], t: float) -> str:
    """Interpolate smoothly across a list of hex colors given t in [0.0, 1.0]."""
    t = max(0.0, min(1.0, t))
    if len(palette) == 1:
        return palette[0]
    scaled = t * (len(palette) - 1)
    idx = int(scaled)
    frac = scaled - idx
    if idx >= len(palette) - 1:
        return palette[-1]

    def hex_to_rgb(h: str) -> Tuple[float, float, float]:
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore

    r1, g1, b1 = hex_to_rgb(palette[idx])
    r2, g2, b2 = hex_to_rgb(palette[idx + 1])

    r = r1 + (r2 - r1) * frac
    g = g1 + (g2 - g1) * frac
    b = b1 + (b2 - b1) * frac
    return f"#{int(round(r * 255)):02x}{int(round(g * 255)):02x}{int(round(b * 255)):02x}"


# ==============================================================================
# SVG Canvas Helper
# ==============================================================================

class SvgCanvas:
    """Constructs a responsive SVG document with dark theme and header badge."""

    def __init__(
        self,
        width: int = 1200,
        height: int = 1200,
        title: str = "",
        subtitle: str = "",
        difficulty: str = "easy",
        dimension: str = "",
        bg_color: str = "#0b0f19",
    ):
        self.width = width
        self.height = height
        self.title = title
        self.subtitle = subtitle
        self.difficulty = difficulty.lower()
        self.dimension = dimension
        self.bg_color = bg_color
        self.defs: List[str] = []
        self.elements: List[str] = []

    def add_def(self, def_content: str) -> None:
        self.defs.append(def_content)

    def add_element(self, elem: str) -> None:
        self.elements.append(elem)

    def render(self) -> str:
        diff_colors = {
            "easy": ("#10b981", "Level 1: Easy"),
            "medium": ("#f59e0b", "Level 2: Medium"),
            "hard": ("#ef4444", "Level 3: Hard"),
        }
        badge_color, badge_label = diff_colors.get(self.difficulty, ("#6366f1", self.difficulty.capitalize()))

        # Header card overlay
        header_xml = f"""
  <!-- Title & Info Overlay -->
  <g class="overlay" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
    <!-- Header background pill -->
    <rect x="30" y="30" width="380" height="96" rx="14" fill="#111827" fill-opacity="0.82" stroke="#1f2937" stroke-width="1.5" />
    
    <!-- Difficulty badge -->
    <rect x="46" y="44" width="112" height="22" rx="11" fill="{badge_color}" fill-opacity="0.2" stroke="{badge_color}" stroke-width="1" />
    <text x="102" y="59" fill="{badge_color}" font-size="11" font-weight="700" text-anchor="middle" letter-spacing="0.5">{badge_label.upper()}</text>
    
    <!-- Dimension tag -->
    <text x="170" y="59" fill="#9ca3af" font-size="12" font-family="'JetBrains Mono', 'Fira Code', monospace">D ≈ {self.dimension}</text>
    
    <!-- Title -->
    <text x="46" y="92" fill="#f9fafb" font-size="20" font-weight="700" letter-spacing="-0.3">{self.title}</text>
    <text x="46" y="112" fill="#9ca3af" font-size="12">{self.subtitle}</text>
  </g>
"""

        defs_joined = "\n".join(self.defs)
        elements_joined = "\n".join(self.elements)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="100%" height="100%" style="max-width: 100%; height: auto; display: block; background: {self.bg_color};">
  <defs>
    <radialGradient id="ambient-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#1f293d" stop-opacity="0.4" />
      <stop offset="100%" stop-color="{self.bg_color}" stop-opacity="1" />
    </radialGradient>
{defs_joined}
  </defs>

  <!-- Background Canvas -->
  <rect width="{self.width}" height="{self.height}" fill="{self.bg_color}" />
  <circle cx="{self.width // 2}" cy="{self.height // 2}" r="{min(self.width, self.height) // 2}" fill="url(#ambient-glow)" />

  <!-- Fractal Geometry -->
  <g class="fractal-geometry">
{elements_joined}
  </g>

{header_xml}
</svg>
"""
        return svg


# ==============================================================================
# Fractal Generator Registry
# ==============================================================================

class FractalSpec:
    def __init__(
        self,
        fid: str,
        title: str,
        difficulty: str,
        dimension_formula: str,
        dimension_val: str,
        default_depth: int,
        description: str,
        func: Callable[..., str],
    ):
        self.fid = fid
        self.title = title
        self.difficulty = difficulty
        self.dimension_formula = dimension_formula
        self.dimension_val = dimension_val
        self.default_depth = default_depth
        self.description = description
        self.func = func


REGISTRY: Dict[str, FractalSpec] = {}


def register(
    fid: str,
    title: str,
    difficulty: str,
    dimension_formula: str,
    dimension_val: str,
    default_depth: int,
    description: str,
):
    def decorator(fn: Callable[..., str]):
        REGISTRY[fid] = FractalSpec(
            fid=fid,
            title=title,
            difficulty=difficulty,
            dimension_formula=dimension_formula,
            dimension_val=dimension_val,
            default_depth=default_depth,
            description=description,
            func=fn,
        )
        return fn

    return decorator


# ==============================================================================
# LEVEL 1: EASY (Elementary Recursive Geometry & Removals)
# ==============================================================================

@register(
    fid="cantor_set",
    title="Cantor Set Ladder",
    difficulty="easy",
    dimension_formula="log(2)/log(3)",
    dimension_val="0.6309",
    default_depth=8,
    description="Triadic Cantor set formed by iteratively removing the open middle third from line segments.",
)
def generate_cantor_set(
    width: int = 1200,
    height: int = 1200,
    depth: int = 8,
    seed: int = 42,
    palette_name: str = "sunset",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["sunset"])
    canvas = SvgCanvas(width, height, "Cantor Set Ladder", "Triadic Middle-Third Removal", "easy", "0.6309")

    margin_x = 100
    margin_top = 180
    margin_bottom = 80
    usable_h = height - margin_top - margin_bottom
    row_height = usable_h / max(1, depth + 1)
    bar_thickness = max(4.0, row_height * 0.45)

    def draw_cantor(level: int, x1: float, x2: float) -> None:
        y = margin_top + level * row_height
        color = get_gradient_color(palette, level / max(1, depth))
        canvas.add_element(
            f'    <rect x="{x1:.2f}" y="{y:.2f}" width="{(x2 - x1):.2f}" height="{bar_thickness:.2f}" rx="{min(bar_thickness / 3, (x2 - x1) / 2):.2f}" fill="{color}" opacity="0.95" />'
        )
        if level < depth:
            third = (x2 - x1) / 3.0
            draw_cantor(level + 1, x1, x1 + third)
            draw_cantor(level + 1, x2 - third, x2)

    draw_cantor(0, margin_x, width - margin_x)
    return canvas.render()


@register(
    fid="koch_snowflake",
    title="Koch Snowflake",
    difficulty="easy",
    dimension_formula="log(4)/log(3)",
    dimension_val="1.2619",
    default_depth=6,
    description="Continuous fractal boundary with infinite perimeter enclosing a finite planar area.",
)
def generate_koch_snowflake(
    width: int = 1200,
    height: int = 1200,
    depth: int = 6,
    seed: int = 42,
    palette_name: str = "neon",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["neon"])
    canvas = SvgCanvas(width, height, "Koch Snowflake", "Infinite Perimeter, Finite Area", "easy", "1.2619")

    cx, cy = width / 2.0, height / 2.0 + 40
    r = min(width, height) * 0.42

    # Equilateral triangle vertices
    angles = [math.pi / 2, math.pi / 2 + 2 * math.pi / 3, math.pi / 2 + 4 * math.pi / 3]
    p1 = (cx + r * math.cos(angles[0]), cy - r * math.sin(angles[0]))
    p2 = (cx + r * math.cos(angles[1]), cy - r * math.sin(angles[1]))
    p3 = (cx + r * math.cos(angles[2]), cy - r * math.sin(angles[2]))

    def koch_curve(a: Tuple[float, float], b: Tuple[float, float], current_depth: int) -> List[Tuple[float, float]]:
        if current_depth == 0:
            return [a]
        dx, dy = b[0] - a[0], b[1] - a[1]
        p_a = (a[0] + dx / 3.0, a[1] + dy / 3.0)
        p_b = (a[0] + 2 * dx / 3.0, a[1] + 2 * dy / 3.0)

        # Apex rotated 60 degrees outward
        sin60 = math.sqrt(3) / 2.0
        cos60 = 0.5
        vx, vy = p_b[0] - p_a[0], p_b[1] - p_a[1]
        p_tip = (p_a[0] + vx * cos60 + vy * sin60, p_a[1] - vx * sin60 + vy * cos60)

        pts = []
        pts.extend(koch_curve(a, p_a, current_depth - 1))
        pts.extend(koch_curve(p_a, p_tip, current_depth - 1))
        pts.extend(koch_curve(p_tip, p_b, current_depth - 1))
        pts.extend(koch_curve(p_b, b, current_depth - 1))
        return pts

    # Collect points around all 3 edges
    pts = []
    pts.extend(koch_curve(p1, p2, depth))
    pts.extend(koch_curve(p2, p3, depth))
    pts.extend(koch_curve(p3, p1, depth))

    d_str = f"M {pts[0][0]:.2f} {pts[0][1]:.2f} " + " ".join(f"L {p[0]:.2f} {p[1]:.2f}" for p in pts[1:]) + " Z"

    grad_c1 = palette[0]
    grad_c2 = palette[min(3, len(palette) - 1)]
    canvas.add_def(f"""    <linearGradient id="koch-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{grad_c1}" stop-opacity="0.35" />
      <stop offset="100%" stop-color="{grad_c2}" stop-opacity="0.1" />
    </linearGradient>""")

    stroke_color = palette[1] if len(palette) > 1 else "#00f0ff"
    canvas.add_element(
        f'    <path d="{d_str}" fill="url(#koch-grad)" stroke="{stroke_color}" stroke-width="1.0" stroke-linejoin="round" />'
    )
    return canvas.render()


@register(
    fid="sierpinski_triangle",
    title="Sierpiński Triangle",
    difficulty="easy",
    dimension_formula="log(3)/log(2)",
    dimension_val="1.5850",
    default_depth=8,
    description="Subdivision of equilateral triangle with central inverted cutout yielding a zero-measure area.",
)
def generate_sierpinski_triangle(
    width: int = 1200,
    height: int = 1200,
    depth: int = 8,
    seed: int = 42,
    palette_name: str = "cyberpunk",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["cyberpunk"])
    canvas = SvgCanvas(width, height, "Sierpiński Triangle", "Recursive Triadic Gasket", "easy", "1.5850")

    cx, cy = width / 2.0, height / 2.0 + 40
    size = min(width, height) * 0.82
    h = size * math.sqrt(3) / 2.0

    p_top = (cx, cy - h / 2.0)
    p_left = (cx - size / 2.0, cy + h / 2.0)
    p_right = (cx + size / 2.0, cy + h / 2.0)

    def draw_triangle(
        a: Tuple[float, float],
        b: Tuple[float, float],
        c: Tuple[float, float],
        level: int,
    ) -> None:
        if level == depth:
            color = get_gradient_color(palette, (a[1] - (cy - h / 2.0)) / max(1.0, h))
            canvas.add_element(
                f'    <polygon points="{a[0]:.2f},{a[1]:.2f} {b[0]:.2f},{b[1]:.2f} {c[0]:.2f},{c[1]:.2f}" fill="{color}" fill-opacity="0.9" stroke="{color}" stroke-width="0.25" />'
            )
            return

        ab = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        bc = ((b[0] + c[0]) / 2.0, (b[1] + c[1]) / 2.0)
        ca = ((c[0] + a[0]) / 2.0, (c[1] + a[1]) / 2.0)

        draw_triangle(a, ab, ca, level + 1)
        draw_triangle(ab, b, bc, level + 1)
        draw_triangle(ca, bc, c, level + 1)

    draw_triangle(p_top, p_left, p_right, 0)
    return canvas.render()


@register(
    fid="sierpinski_carpet",
    title="Sierpiński Carpet",
    difficulty="easy",
    dimension_formula="log(8)/log(3)",
    dimension_val="1.8928",
    default_depth=5,
    description="Planar fractal obtained by cutting out the center sub-square from a 3x3 grid repeatedly.",
)
def generate_sierpinski_carpet(
    width: int = 1200,
    height: int = 1200,
    depth: int = 5,
    seed: int = 42,
    palette_name: str = "ocean",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["ocean"])
    canvas = SvgCanvas(width, height, "Sierpiński Carpet", "Nine-Square Central Cutout", "easy", "1.8928")

    size = min(width, height) * 0.78
    x0 = (width - size) / 2.0
    y0 = (height - size) / 2.0 + 35

    # Base square
    base_color = palette[-2]
    canvas.add_element(f'    <rect x="{x0:.2f}" y="{y0:.2f}" width="{size:.2f}" height="{size:.2f}" fill="{base_color}" fill-opacity="0.85" />')

    def carve_carpet(x: float, y: float, s: float, level: int) -> None:
        if level > depth:
            return
        sub = s / 3.0
        # Cutout center
        cut_x = x + sub
        cut_y = y + sub
        color = canvas.bg_color
        canvas.add_element(
            f'    <rect x="{cut_x:.2f}" y="{cut_y:.2f}" width="{sub:.2f}" height="{sub:.2f}" fill="{color}" />'
        )

        # Recurse on remaining 8 sub-squares
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:
                    continue
                carve_carpet(x + i * sub, y + j * sub, sub, level + 1)

    carve_carpet(x0, y0, size, 1)
    return canvas.render()


@register(
    fid="vicsek_fractal",
    title="Vicsek Box Fractal",
    difficulty="easy",
    dimension_formula="log(5)/log(3)",
    dimension_val="1.4650",
    default_depth=5,
    description="Cross-type decomposition fractal keeping 5 of 9 equal sub-squares per iteration.",
)
def generate_vicsek_fractal(
    width: int = 1200,
    height: int = 1200,
    depth: int = 5,
    seed: int = 42,
    palette_name: str = "emerald",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["emerald"])
    canvas = SvgCanvas(width, height, "Vicsek Box Fractal", "Cross-Decomposition 5-of-9 Sub-Squares", "easy", "1.4650")

    size = min(width, height) * 0.76
    x0 = (width - size) / 2.0
    y0 = (height - size) / 2.0 + 35

    def draw_vicsek(x: float, y: float, s: float, level: int) -> None:
        if level == depth:
            color = get_gradient_color(palette, (x - x0) / max(1.0, size))
            canvas.add_element(
                f'    <rect x="{x:.2f}" y="{y:.2f}" width="{s:.2f}" height="{s:.2f}" fill="{color}" rx="{min(1.0, s * 0.1):.2f}" />'
            )
            return

        sub = s / 3.0
        # 5 squares: center, top, bottom, left, right
        positions = [
            (x + sub, y + sub),  # Center
            (x + sub, y),        # Top
            (x + sub, y + 2 * sub),  # Bottom
            (x, y + sub),        # Left
            (x + 2 * sub, y + sub),  # Right
        ]
        for px, py in positions:
            draw_vicsek(px, py, sub, level + 1)

    draw_vicsek(x0, y0, size, 0)
    return canvas.render()


# ==============================================================================
# LEVEL 2: MEDIUM (Branching Trees, L-Systems & Space-Filling Curves)
# ==============================================================================

@register(
    fid="pythagoras_tree",
    title="Pythagoras Tree",
    difficulty="medium",
    dimension_formula="log(2)/log(sqrt(2))",
    dimension_val="2.0000",
    default_depth=13,
    description="Harmonic branching fractal formed by erecting right triangles on top of recursive squares.",
)
def generate_pythagoras_tree(
    width: int = 1200,
    height: int = 1200,
    depth: int = 13,
    seed: int = 42,
    palette_name: str = "emerald",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["emerald"])
    canvas = SvgCanvas(width, height, "Pythagoras Tree", "Pythagorean Theorem Recursive Squares", "medium", "2.0000")

    rng = random.Random(seed)
    base_size = min(width, height) * 0.14
    x0 = width / 2.0 - base_size / 2.0
    y0 = height - 120.0

    # Symmetric or slightly randomized angle
    alpha = math.radians(45.0 + (rng.random() - 0.5) * 8.0)
    cos_a = math.cos(alpha)
    sin_a = math.sin(alpha)

    def draw_square(
        x: float, y: float, size: float, angle: float, level: int
    ) -> None:
        if level > depth or size < 0.6:
            return

        color = get_gradient_color(palette, level / max(1, depth))
        # 4 corners of the square
        cos_ang = math.cos(angle)
        sin_ang = math.sin(angle)

        p1 = (x, y)
        p2 = (x + size * cos_ang, y - size * sin_ang)
        p3 = (p2[0] - size * sin_ang, p2[1] - size * cos_ang)
        p4 = (p1[0] - size * sin_ang, p1[1] - size * cos_ang)

        canvas.add_element(
            f'    <polygon points="{p1[0]:.2f},{p1[1]:.2f} {p2[0]:.2f},{p2[1]:.2f} {p3[0]:.2f},{p3[1]:.2f} {p4[0]:.2f},{p4[1]:.2f}" fill="{color}" fill-opacity="0.8" stroke="#111827" stroke-width="0.2" />'
        )

        s_left = size * cos_a
        s_right = size * sin_a

        apex = (
            p4[0] + s_left * math.cos(angle + alpha),
            p4[1] - s_left * math.sin(angle + alpha),
        )

        # Left child square originates at p4
        draw_square(p4[0], p4[1], s_left, angle + alpha, level + 1)
        # Right child square originates at apex
        draw_square(apex[0], apex[1], s_right, angle + alpha - math.pi / 2, level + 1)

    draw_square(x0, y0, base_size, 0.0, 0)
    return canvas.render()


@register(
    fid="dragon_curve",
    title="Heighway Dragon Curve",
    difficulty="medium",
    dimension_formula="dim_boundary",
    dimension_val="1.5236",
    default_depth=16,
    description="Paper-folding sequence turning 90° alternating left and right, tiling the plane without overlapping.",
)
def generate_dragon_curve(
    width: int = 1200,
    height: int = 1200,
    depth: int = 16,
    seed: int = 42,
    palette_name: str = "neon",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["neon"])
    canvas = SvgCanvas(width, height, "Heighway Dragon Curve", "Boundary Dim: 1.5236, Plane Tiling", "medium", "1.5236")

    turns: List[int] = []
    for _ in range(depth):
        turns = turns + [1] + [-t for t in reversed(turns)]

    cx, cy = 0.0, 0.0
    dx, dy = 1.0, 0.0
    pts = [(cx, cy)]
    for t in turns:
        cx += dx
        cy += dy
        pts.append((cx, cy))
        if t == 1:
            dx, dy = dy, -dx
        else:
            dx, dy = -dy, dx
    cx += dx
    cy += dy
    pts.append((cx, cy))

    min_x = min(p[0] for p in pts)
    max_x = max(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)

    margin = 120
    scale = min((width - 2 * margin) / max(1e-5, max_x - min_x), (height - 2 * margin - 50) / max(1e-5, max_y - min_y))
    ox = width / 2.0 - ((min_x + max_x) / 2.0) * scale
    oy = height / 2.0 + 30.0 - ((min_y + max_y) / 2.0) * scale

    n_pts = len(pts)
    chunk_size = max(1, n_pts // 60)
    for i in range(0, n_pts - 1, chunk_size):
        sub_pts = pts[i:min(n_pts, i + chunk_size + 1)]
        color = get_gradient_color(palette, i / n_pts)
        d_str = " ".join(
            (f"M" if j == 0 else "L") + f" {(ox + p[0] * scale):.2f} {(oy + p[1] * scale):.2f}"
            for j, p in enumerate(sub_pts)
        )
        canvas.add_element(
            f'    <path d="{d_str}" fill="none" stroke="{color}" stroke-width="1.0" stroke-linecap="round" />'
        )

    return canvas.render()


@register(
    fid="hilbert_curve",
    title="Hilbert Space-Filling Curve",
    difficulty="medium",
    dimension_formula="log(4)/log(2)",
    dimension_val="2.0000",
    default_depth=7,
    description="Locality-preserving continuous fractal mapping a 1D line segment into the 2D unit square.",
)
def generate_hilbert_curve(
    width: int = 1200,
    height: int = 1200,
    depth: int = 7,
    seed: int = 42,
    palette_name: str = "sunset",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["sunset"])
    canvas = SvgCanvas(width, height, "Hilbert Space-Filling Curve", "Continuous 1D-to-2D Surjection", "medium", "2.0000")

    def d2xy(n: int, d: int) -> Tuple[int, int]:
        rx, ry = 0, 0
        t = d
        x, y = 0, 0
        s = 1
        while s < n:
            rx = 1 & (t // 2)
            ry = 1 & (t ^ rx)
            if ry == 0:
                if rx == 1:
                    x = s - 1 - x
                    y = s - 1 - y
                x, y = y, x
            x += s * rx
            y += s * ry
            t //= 4
            s *= 2
        return x, y

    n_order = 1 << depth
    total_points = n_order * n_order
    margin = 120
    usable = min(width - 2 * margin, height - 2 * margin - 60)
    step = usable / max(1, n_order - 1)
    x_off = (width - usable) / 2.0
    y_off = (height - usable) / 2.0 + 35.0

    chunk_size = max(1, total_points // 80)
    for i in range(0, total_points - 1, chunk_size):
        end = min(total_points, i + chunk_size + 1)
        sub_pts = [d2xy(n_order, pt) for pt in range(i, end)]
        color = get_gradient_color(palette, i / total_points)
        d_str = " ".join(
            (f"M" if j == 0 else "L") + f" {(x_off + p[0] * step):.2f} {(y_off + p[1] * step):.2f}"
            for j, p in enumerate(sub_pts)
        )
        canvas.add_element(
            f'    <path d="{d_str}" fill="none" stroke="{color}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" />'
        )

    return canvas.render()


@register(
    fid="fractal_canopy",
    title="Fractal Binary Canopy",
    difficulty="medium",
    dimension_formula="da Vinci Taper",
    dimension_val="1.8400",
    default_depth=13,
    description="Harmonic botanical tree branching with Leonardo da Vinci thickness conservation: d² = d₁² + d₂².",
)
def generate_fractal_canopy(
    width: int = 1200,
    height: int = 1200,
    depth: int = 13,
    seed: int = 42,
    palette_name: str = "emerald",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["emerald"])
    canvas = SvgCanvas(width, height, "Fractal Binary Canopy", "Vascular Branching with Da Vinci Taper", "medium", "1.8400")

    rng = random.Random(seed)
    base_x = width / 2.0
    base_y = height - 90.0
    trunk_len = min(width, height) * 0.22
    trunk_thick = 16.0

    def branch(
        x: float, y: float, length: float, angle: float, thickness: float, level: int
    ) -> None:
        if level > depth or length < 0.8:
            return

        nx = x + length * math.sin(angle)
        ny = y - length * math.cos(angle)

        color = get_gradient_color(palette, level / max(1, depth))
        canvas.add_element(
            f'    <line x1="{x:.2f}" y1="{y:.2f}" x2="{nx:.2f}" y2="{ny:.2f}" stroke="{color}" stroke-width="{thickness:.2f}" stroke-linecap="round" />'
        )

        new_thick = max(0.4, thickness * 0.72)
        spread1 = math.radians(24.0 + (rng.random() - 0.5) * 6.0)
        spread2 = math.radians(24.0 + (rng.random() - 0.5) * 6.0)
        ratio1 = 0.74 + (rng.random() - 0.5) * 0.06
        ratio2 = 0.74 + (rng.random() - 0.5) * 0.06

        branch(nx, ny, length * ratio1, angle - spread1, new_thick, level + 1)
        branch(nx, ny, length * ratio2, angle + spread2, new_thick, level + 1)

    branch(base_x, base_y, trunk_len, 0.0, trunk_thick, 0)
    return canvas.render()


@register(
    fid="levy_c_curve",
    title="Lévy C Curve",
    difficulty="medium",
    dimension_formula="log(2)/log(sqrt(2))",
    dimension_val="1.9340",
    default_depth=15,
    description="Isosceles right-triangle folding yielding an intricate self-similar coastal perimeter.",
)
def generate_levy_c_curve(
    width: int = 1200,
    height: int = 1200,
    depth: int = 15,
    seed: int = 42,
    palette_name: str = "fire",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["fire"])
    canvas = SvgCanvas(width, height, "Lévy C Curve", "Self-Similar Shoreline Fractal", "medium", "1.9340")

    def levy(a: Tuple[float, float], b: Tuple[float, float], current_depth: int) -> List[Tuple[float, float]]:
        if current_depth == 0:
            return [a]
        mx = (a[0] + b[0]) / 2.0 - (b[1] - a[1]) / 2.0
        my = (a[1] + b[1]) / 2.0 + (b[0] - a[0]) / 2.0
        apex = (mx, my)

        pts = []
        pts.extend(levy(a, apex, current_depth - 1))
        pts.extend(levy(apex, b, current_depth - 1))
        return pts

    start_x = width * 0.3
    end_x = width * 0.7
    start_y = height * 0.65
    end_y = height * 0.65

    pts = levy((start_x, start_y), (end_x, end_y), depth)
    pts.append((end_x, end_y))

    n_pts = len(pts)
    chunk_size = max(1, n_pts // 80)
    for i in range(0, n_pts - 1, chunk_size):
        sub_pts = pts[i:min(n_pts, i + chunk_size + 1)]
        color = get_gradient_color(palette, i / n_pts)
        d_str = " ".join(
            (f"M" if j == 0 else "L") + f" {p[0]:.2f} {p[1]:.2f}" for j, p in enumerate(sub_pts)
        )
        canvas.add_element(
            f'    <path d="{d_str}" fill="none" stroke="{color}" stroke-width="0.9" stroke-linecap="round" />'
        )

    return canvas.render()


# ==============================================================================
# LEVEL 3: HARD (Iterated Function Systems & Complex Dynamics)
# ==============================================================================

@register(
    fid="barnsley_fern",
    title="Barnsley Fern",
    difficulty="hard",
    dimension_formula="IFS Invariant Measure",
    dimension_val="1.8600",
    default_depth=120000,
    description="Iterated Function System (IFS) affine transformations simulating natural biological self-similarity.",
)
def generate_barnsley_fern(
    width: int = 1200,
    height: int = 1200,
    depth: int = 120000,
    seed: int = 42,
    palette_name: str = "emerald",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["emerald"])
    canvas = SvgCanvas(width, height, "Barnsley Fern", "Iterated Function System (Chaos Game)", "hard", "1.8600")

    rng = random.Random(seed)
    x, y = 0.0, 0.0
    pts: List[Tuple[float, float, int]] = []

    for i in range(depth):
        r = rng.random()
        if r < 0.01:
            x, y = 0.0, 0.16 * y
            rule = 0
        elif r < 0.86:
            x, y = 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
            rule = 1
        elif r < 0.93:
            x, y = 0.20 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
            rule = 2
        else:
            x, y = -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
            rule = 3

        if i > 50:
            pts.append((x, y, rule))

    scale_y = (height - 180) / 10.2
    scale_x = scale_y
    cx = width / 2.0
    base_y = height - 70.0

    buckets: Dict[int, List[Tuple[float, float]]] = {}
    num_buckets = 12
    for px, py, rule in pts:
        sx = cx + px * scale_x
        sy = base_y - py * scale_y
        b_idx = int(min(num_buckets - 1, max(0, (py / 10.0) * num_buckets)))
        buckets.setdefault(b_idx, []).append((sx, sy))

    for b_idx, pt_list in buckets.items():
        color = get_gradient_color(palette, b_idx / num_buckets)
        d_chunks = " ".join(f"M {p[0]:.1f} {p[1]:.1f} l 0.01 0" for p in pt_list)
        canvas.add_element(
            f'    <path d="{d_chunks}" fill="none" stroke="{color}" stroke-width="1.0" stroke-linecap="round" opacity="0.80" />'
        )

    return canvas.render()


@register(
    fid="gosper_curve",
    title="Gosper Curve (Flowsnake)",
    difficulty="hard",
    dimension_formula="log(7)/log(sqrt(7))",
    dimension_val="2.0000",
    default_depth=5,
    description="Hexagonal space-filling curve with non-trivial L-system rules, yielding a fractal boundary.",
)
def generate_gosper_curve(
    width: int = 1200,
    height: int = 1200,
    depth: int = 5,
    seed: int = 42,
    palette_name: str = "neon",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["neon"])
    canvas = SvgCanvas(width, height, "Gosper Curve (Flowsnake)", "Hexagonal Space-Filling L-System", "hard", "2.0000")

    axiom = "A"
    curr = axiom
    for _ in range(depth):
        nxt = []
        for ch in curr:
            if ch == "A":
                nxt.append("A-B--B+A++AA+B-")
            elif ch == "B":
                nxt.append("+A-BB--B-A++A+B")
            else:
                nxt.append(ch)
        curr = "".join(nxt)

    angle = 0.0
    x, y = 0.0, 0.0
    pts = [(x, y)]
    rad60 = math.pi / 3.0

    for ch in curr:
        if ch in ("A", "B"):
            x += math.cos(angle)
            y += math.sin(angle)
            pts.append((x, y))
        elif ch == "+":
            angle += rad60
        elif ch == "-":
            angle -= rad60

    min_x = min(p[0] for p in pts)
    max_x = max(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)

    margin = 130
    scale = min((width - 2 * margin) / max(1e-5, max_x - min_x), (height - 2 * margin - 50) / max(1e-5, max_y - min_y))
    ox = width / 2.0 - ((min_x + max_x) / 2.0) * scale
    oy = height / 2.0 + 35.0 - ((min_y + max_y) / 2.0) * scale

    n_pts = len(pts)
    chunk_size = max(1, n_pts // 70)
    for i in range(0, n_pts - 1, chunk_size):
        sub_pts = pts[i:min(n_pts, i + chunk_size + 1)]
        color = get_gradient_color(palette, i / n_pts)
        d_str = " ".join(
            (f"M" if j == 0 else "L") + f" {(ox + p[0] * scale):.2f} {(oy + p[1] * scale):.2f}"
            for j, p in enumerate(sub_pts)
        )
        canvas.add_element(
            f'    <path d="{d_str}" fill="none" stroke="{color}" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" />'
        )

    return canvas.render()


@register(
    fid="mandelbrot_set",
    title="Mandelbrot Boundary Contours",
    difficulty="hard",
    dimension_formula="dim(boundary)",
    dimension_val="2.0000",
    default_depth=128,
    description="Boundary isolines and escape contours of the quadratic complex iteration z_{n+1} = z_n² + c.",
)
def generate_mandelbrot_set(
    width: int = 1200,
    height: int = 1200,
    depth: int = 128,
    seed: int = 42,
    palette_name: str = "sunset",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["sunset"])
    canvas = SvgCanvas(width, height, "Mandelbrot Boundary Contours", "Complex Polynomial Escape Dynamics", "hard", "2.0000")

    grid_cols = 260
    grid_rows = 260
    c_real_min, c_real_max = -2.1, 0.7
    c_imag_min, c_imag_max = -1.4, 1.4

    cell_w = width / grid_cols
    cell_h = height / grid_rows

    bands: Dict[int, List[str]] = {}
    num_bands = len(palette)

    for r in range(grid_rows):
        ci = c_imag_min + (r / grid_rows) * (c_imag_max - c_imag_min)
        for c in range(grid_cols):
            cr = c_real_min + (c / grid_cols) * (c_real_max - c_real_min)

            q = (cr - 0.25) ** 2 + ci ** 2
            if q * (q + (cr - 0.25)) < 0.25 * (ci ** 2) or (cr + 1) ** 2 + ci ** 2 < 0.0625:
                continue

            zr, zi = 0.0, 0.0
            escaped = False
            it = 0
            while it < depth:
                zr2 = zr * zr
                zi2 = zi * zi
                if zr2 + zi2 > 4.0:
                    escaped = True
                    break
                zi = 2.0 * zr * zi + ci
                zr = zr2 - zi2 + cr
                it += 1

            if escaped and it > 2:
                smooth_val = it + 1 - math.log(math.log(max(1.01, math.sqrt(zr2 + zi2)))) / math.log(2.0)
                band_idx = int((smooth_val / depth) * (num_bands - 1)) % num_bands
                bands.setdefault(band_idx, []).append(
                    f"M {c * cell_w:.1f} {r * cell_h:.1f} h {cell_w:.1f} v {cell_h:.1f} h -{cell_w:.1f} Z"
                )

    for b_idx, path_chunks in bands.items():
        color = palette[b_idx % len(palette)]
        d_combined = " ".join(path_chunks)
        canvas.add_element(
            f'    <path d="{d_combined}" fill="{color}" fill-opacity="0.85" stroke="{color}" stroke-width="0.3" />'
        )

    return canvas.render()


@register(
    fid="julia_set",
    title="Julia Set (Douady's Rabbit)",
    difficulty="hard",
    dimension_formula="dim(boundary)",
    dimension_val="1.4100",
    default_depth=128,
    description="Filled Julia set for c = -0.123 + 0.745i, exhibiting 3-fold rotational dendritic symmetry.",
)
def generate_julia_set(
    width: int = 1200,
    height: int = 1200,
    depth: int = 128,
    seed: int = 42,
    palette_name: str = "cyberpunk",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["cyberpunk"])
    canvas = SvgCanvas(width, height, "Julia Set (Douady's Rabbit)", "Quadratic Julia Dynamics: c = -0.123 + 0.745i", "hard", "1.4100")

    grid_cols = 260
    grid_rows = 260
    c_const = complex(-0.123, 0.745)
    r_min, r_max = -1.4, 1.4
    i_min, i_max = -1.4, 1.4

    cell_w = width / grid_cols
    cell_h = height / grid_rows

    bands: Dict[int, List[str]] = {}
    num_bands = len(palette)

    for row in range(grid_rows):
        zi0 = i_min + (row / grid_rows) * (i_max - i_min)
        for col in range(grid_cols):
            zr0 = r_min + (col / grid_cols) * (r_max - r_min)
            z = complex(zr0, zi0)

            escaped = False
            it = 0
            while it < depth:
                if abs(z) > 2.0:
                    escaped = True
                    break
                z = z * z + c_const
                it += 1

            if escaped and it > 2:
                band_idx = int((it / depth) * (num_bands - 1)) % num_bands
                bands.setdefault(band_idx, []).append(
                    f"M {col * cell_w:.1f} {row * cell_h:.1f} h {cell_w:.1f} v {cell_h:.1f} h -{cell_w:.1f} Z"
                )

    for b_idx, path_chunks in bands.items():
        color = palette[b_idx % len(palette)]
        d_combined = " ".join(path_chunks)
        canvas.add_element(
            f'    <path d="{d_combined}" fill="{color}" fill-opacity="0.88" stroke="{color}" stroke-width="0.3" />'
        )

    return canvas.render()


@register(
    fid="newton_fractal",
    title="Newton-Raphson Basins",
    difficulty="hard",
    dimension_formula="dim(boundary)",
    dimension_val="2.0000",
    default_depth=60,
    description="Julia boundary separating the basins of attraction for the cube roots of unity (z³ - 1 = 0).",
)
def generate_newton_fractal(
    width: int = 1200,
    height: int = 1200,
    depth: int = 60,
    seed: int = 42,
    palette_name: str = "neon",
) -> str:
    palette = PALETTES.get(palette_name, PALETTES["neon"])
    canvas = SvgCanvas(width, height, "Newton-Raphson Basins", "Root-Finding Basins for z³ - 1 = 0", "hard", "2.0000")

    roots = [
        complex(1.0, 0.0),
        complex(-0.5, math.sqrt(3) / 2.0),
        complex(-0.5, -math.sqrt(3) / 2.0),
    ]
    root_colors = [palette[0], palette[2 % len(palette)], palette[4 % len(palette)]]

    grid_cols = 260
    grid_rows = 260
    span = 1.8
    cell_w = width / grid_cols
    cell_h = height / grid_rows

    paths_by_root: Dict[int, List[str]] = {0: [], 1: [], 2: []}

    for row in range(grid_rows):
        y_val = -span + (row / grid_rows) * (2 * span)
        for col in range(grid_cols):
            x_val = -span + (col / grid_cols) * (2 * span)
            z = complex(x_val, y_val)

            converged_root = -1
            for _ in range(depth):
                if abs(z) < 1e-6:
                    break
                z3 = z * z * z
                z = (2.0 * z3 + 1.0) / (3.0 * z * z)

                for r_idx, r in enumerate(roots):
                    if abs(z - r) < 1e-3:
                        converged_root = r_idx
                        break
                if converged_root != -1:
                    break

            if converged_root != -1:
                paths_by_root[converged_root].append(
                    f"M {col * cell_w:.1f} {row * cell_h:.1f} h {cell_w:.1f} v {cell_h:.1f} h -{cell_w:.1f} Z"
                )

    for r_idx, chunks in paths_by_root.items():
        color = root_colors[r_idx]
        d_combined = " ".join(chunks)
        canvas.add_element(
            f'    <path d="{d_combined}" fill="{color}" fill-opacity="0.82" stroke="{color}" stroke-width="0.3" />'
        )
    return canvas.render()


# ==============================================================================
# CLI and Batch Dispatcher
# ==============================================================================

def print_fractal_table() -> None:
    """Print clean terminal table of all registered fractals."""
    print("=" * 82)
    print(f"{'ID':<22} | {'DIFFICULTY':<8} | {'DIMENSION':<10} | {'NAME'}")
    print("-" * 82)
    for fid, spec in REGISTRY.items():
        print(f"{fid:<22} | {spec.difficulty.upper():<8} | {spec.dimension_val:<10} | {spec.title}")
    print("=" * 82)


def generate_single_fractal(
    fid: str,
    output_path: Path,
    width: int,
    height: int,
    depth: Optional[int],
    seed: int,
    palette: str,
) -> Dict[str, Any]:
    if fid not in REGISTRY:
        raise ValueError(f"Unknown fractal ID: '{fid}'. Run with --list to view valid IDs.")

    spec = REGISTRY[fid]
    actual_depth = depth if depth is not None else spec.default_depth
    svg_content = spec.func(
        width=width,
        height=height,
        depth=actual_depth,
        seed=seed,
        palette_name=palette,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content, encoding="utf-8")

    return {
        "id": spec.fid,
        "title": spec.title,
        "difficulty": spec.difficulty,
        "dimension_formula": spec.dimension_formula,
        "dimension_val": spec.dimension_val,
        "depth": actual_depth,
        "seed": seed,
        "palette": palette,
        "file": output_path.name,
        "description": spec.description,
        "size_bytes": len(svg_content.encode("utf-8")),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate mathematical SVG fractals from easy to hard.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available fractals with difficulty tiers and exit.",
    )
    parser.add_argument(
        "--fractal",
        type=str,
        default=None,
        help="Specific fractal ID to generate (e.g., 'koch_snowflake', 'mandelbrot_set').",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all registered fractals.",
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=["easy", "medium", "hard", "all"],
        default="all",
        help="Filter fractals by difficulty level.",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=None,
        help="Override iteration/recursion depth.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for procedural variations and organic branches.",
    )
    parser.add_argument(
        "--palette",
        type=str,
        default="neon",
        choices=list(PALETTES.keys()),
        help="Color palette theme for the SVG rendering.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1200,
        help="SVG canvas width.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1200,
        help="SVG canvas height.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Destination directory for generated SVGs.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Explicit output filepath for a single fractal.",
    )
    parser.add_argument(
        "--manifest",
        action="store_true",
        help="Write manifest.json summarizing all generated fractals.",
    )

    args = parser.parse_args()

    if args.list:
        print_fractal_table()
        return

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    targets: List[str] = []
    if args.fractal:
        targets = [args.fractal]
    elif args.all or args.difficulty:
        for fid, spec in REGISTRY.items():
            if args.difficulty == "all" or spec.difficulty == args.difficulty:
                targets.append(fid)

    if not targets:
        print("Error: No fractal specified. Use --all, --difficulty, or --fractal <ID>. Run --list to see available fractals.")
        sys.exit(1)

    records = []
    for fid in targets:
        if args.output and len(targets) == 1:
            dest_file = Path(args.output)
        else:
            dest_file = out_dir / f"{fid}.svg"

        print(f"==> Generating {fid} ({REGISTRY[fid].difficulty.upper()} tier)...")
        meta = generate_single_fractal(
            fid=fid,
            output_path=dest_file,
            width=args.width,
            height=args.height,
            depth=args.depth,
            seed=args.seed,
            palette=args.palette,
        )
        records.append(meta)
        print(f"    Saved: {dest_file} ({meta['size_bytes']:,} bytes)")

    if args.manifest or args.all:
        manifest_path = out_dir / "manifest.json"
        manifest_data = {
            "title": "Mathematical Fractals SVG Showcase",
            "total": len(records),
            "generated_at": os.environ.get("GENERATED_AT", "2026-09-17T00:00:00Z"),
            "seed": args.seed,
            "palette": args.palette,
            "fractals": records,
        }
        manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")
        print(f"==> Manifest written: {manifest_path}")


if __name__ == "__main__":
    main()
