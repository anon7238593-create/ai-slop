#!/usr/bin/env python3
"""Create presentation-ready Voronoi diagram SVGs for 2 through 20 sites.

Example:
    python3 voronoi_svg_generator.py --seed 20260905
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path


WIDTH, HEIGHT = 1200, 760
PADDING = 38
PLOT_TOP = 160
PLOT_BOTTOM = HEIGHT - PADDING - 72
PALETTE = ("#38BDF8", "#A78BFA", "#F472B6", "#FB923C", "#FACC15", "#4ADE80", "#2DD4BF", "#60A5FA")

Point = tuple[float, float]


def clip_polygon(polygon: list[Point], normal: Point, constant: float) -> list[Point]:
    """Clip a polygon to points satisfying normal · point <= constant."""
    if not polygon:
        return []
    clipped: list[Point] = []
    previous = polygon[-1]
    previous_value = normal[0] * previous[0] + normal[1] * previous[1] - constant
    for current in polygon:
        current_value = normal[0] * current[0] + normal[1] * current[1] - constant
        previous_inside, current_inside = previous_value <= 1e-9, current_value <= 1e-9
        if previous_inside != current_inside:
            ratio = previous_value / (previous_value - current_value)
            clipped.append((previous[0] + ratio * (current[0] - previous[0]), previous[1] + ratio * (current[1] - previous[1])))
        if current_inside:
            clipped.append(current)
        previous, previous_value = current, current_value
    return clipped


def voronoi_cell(site: Point, sites: list[Point]) -> list[Point]:
    """Calculate a site's bounded Voronoi cell via repeated half-plane clipping."""
    polygon = [(PADDING, PLOT_TOP), (WIDTH - PADDING, PLOT_TOP), (WIDTH - PADDING, PLOT_BOTTOM), (PADDING, PLOT_BOTTOM)]
    for other in sites:
        if other == site:
            continue
        normal = (other[0] - site[0], other[1] - site[1])
        constant = (other[0] ** 2 + other[1] ** 2 - site[0] ** 2 - site[1] ** 2) / 2
        polygon = clip_polygon(polygon, normal, constant)
    return polygon


def generate_sites(count: int, generator: random.Random) -> list[Point]:
    """Place distinct, comfortably spaced sites for a visually balanced diagram."""
    sites: list[Point] = []
    minimum_distance = max(46, 150 - count * 5)
    attempts = 0
    while len(sites) < count:
        candidate = (generator.uniform(PADDING + 24, WIDTH - PADDING - 24), generator.uniform(PLOT_TOP + 24, PLOT_BOTTOM - 24))
        if all(math.dist(candidate, existing) >= minimum_distance for existing in sites) or attempts > 1_500:
            sites.append(candidate)
            attempts = 0
        else:
            attempts += 1
    return sites


def points_attribute(points: list[Point]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def make_svg(sites: list[Point], seed: int, count: int) -> str:
    polygons = [voronoi_cell(site, sites) for site in sites]
    cells = "\n".join(
        f'    <polygon points="{points_attribute(cell)}" fill="{PALETTE[index % len(PALETTE)]}" fill-opacity="0.60" />'
        for index, cell in enumerate(polygons)
    )
    dots = "\n".join(
        f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#0F172A" stroke="#FFFFFF" stroke-width="3" />'
        for x, y in sites
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">
  <title id="title">Voronoi diagram with {count} sites</title>
  <desc id="description">A clipped Voronoi diagram with {count} randomly generated sites. Seed: {seed}.</desc>
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#F8FAFC"/><stop offset="1" stop-color="#E0F2FE"/></linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#0F172A" flood-opacity=".12"/></filter>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#background)"/>
  <rect x="{PADDING}" y="{PADDING}" width="{WIDTH - 2 * PADDING}" height="{HEIGHT - 2 * PADDING}" rx="20" fill="#FFFFFF" filter="url(#shadow)"/>
  <g font-family="Arial, sans-serif"><text x="72" y="94" font-size="32" font-weight="700" fill="#0F172A">Voronoi Diagram</text><text x="72" y="126" font-size="18" fill="#475569">{count} sites · generated with seed {seed}</text></g>
  <g stroke="#FFFFFF" stroke-width="3" stroke-linejoin="round">
{cells}
  </g>
  <g>
{dots}
  </g>
  <g font-family="Arial, sans-serif" font-size="15" fill="#64748B"><text x="72" y="{HEIGHT - 62}">Each region contains all points closest to its dark site marker.</text><text x="{WIDTH - 202}" y="{HEIGHT - 62}">sites: {count:02d}</text></g>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SVG Voronoi diagrams for 2 through 20 sites.")
    parser.add_argument("--output", type=Path, default=Path("output"), help="directory for SVG files")
    parser.add_argument("--seed", type=int, default=20260905, help="random seed; use a new value for different diagrams")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for count in range(2, 21):
        # Mix the count into the seed so every file is deterministic but distinct.
        diagram_seed = args.seed + count * 10_007
        svg = make_svg(generate_sites(count, random.Random(diagram_seed)), diagram_seed, count)
        (args.output / f"voronoi_{count:02d}_sites.svg").write_text(svg, encoding="utf-8")
    (args.output / "manifest.json").write_text(
        json.dumps({"seed": args.seed, "site_counts": list(range(2, 21))}, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Created 19 SVG diagrams in {args.output}")


if __name__ == "__main__":
    main()
