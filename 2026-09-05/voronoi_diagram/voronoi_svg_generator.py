#!/usr/bin/env python3
"""Create presentation-ready high-resolution Voronoi diagram SVGs.

Generates clipped Voronoi diagrams at very high resolution (4K UHD+ by default)
with aesthetically balanced site distributions and modern styling.

Example:
    python3 voronoi_svg_generator.py --seed 20260905 --count 100 --width 3840 --height 2400
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import random
from pathlib import Path

DEFAULT_WIDTH, DEFAULT_HEIGHT = 3840, 2400
PALETTE = (
    "#38BDF8", "#A78BFA", "#F472B6", "#FB923C", "#FACC15",
    "#4ADE80", "#2DD4BF", "#60A5FA", "#E879F9", "#34D399",
    "#F87171", "#818CF8", "#FBBF24", "#A3E635", "#C084FC",
    "#FB7185", "#22D3EE", "#86EFAC", "#FCD34D", "#38BDF8",
)

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
            denominator = previous_value - current_value
            if abs(denominator) > 1e-12:
                ratio = previous_value / denominator
                clipped.append((
                    previous[0] + ratio * (current[0] - previous[0]),
                    previous[1] + ratio * (current[1] - previous[1]),
                ))
        if current_inside:
            clipped.append(current)
        previous, previous_value = current, current_value
    return clipped


def voronoi_cell(site: Point, sites: list[Point], bounds: tuple[float, float, float, float]) -> list[Point]:
    """Calculate a site's bounded Voronoi cell via repeated half-plane clipping."""
    left, top, right, bottom = bounds
    polygon = [(left, top), (right, top), (right, bottom), (left, bottom)]
    for other in sites:
        if other == site:
            continue
        normal = (other[0] - site[0], other[1] - site[1])
        constant = (other[0] ** 2 + other[1] ** 2 - site[0] ** 2 - site[1] ** 2) / 2
        polygon = clip_polygon(polygon, normal, constant)
        if not polygon:
            break
    return polygon


def generate_sites(count: int, generator: random.Random, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT) -> list[Point]:
    """Place distinct, comfortably spaced sites for a visually balanced diagram."""
    scale = min(width / 1200, height / 760)
    padding = int(38 * scale)
    plot_top = int(160 * scale)
    plot_bottom = height - padding - int(72 * scale)
    left_bound = padding + int(24 * scale)
    right_bound = width - padding - int(24 * scale)
    top_bound = plot_top + int(24 * scale)
    bottom_bound = plot_bottom - int(24 * scale)

    if count == 1:
        return [(width / 2, (plot_top + plot_bottom) / 2)]

    plot_w = right_bound - left_bound
    plot_h = bottom_bound - top_bound
    area = plot_w * plot_h
    min_dist = 0.52 * math.sqrt(area / count)

    sites: list[Point] = []
    attempts = 0
    while len(sites) < count:
        candidate = (generator.uniform(left_bound, right_bound), generator.uniform(top_bound, bottom_bound))
        if all(math.dist(candidate, existing) >= min_dist for existing in sites):
            sites.append(candidate)
            attempts = 0
        else:
            attempts += 1
            if attempts > 60:
                min_dist *= 0.95
                attempts = 0
    return sites


def points_attribute(points: list[Point]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def make_svg(sites: list[Point], seed: int, count: int, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT) -> str:
    scale = min(width / 1200, height / 760)
    padding = int(38 * scale)
    plot_top = int(160 * scale)
    plot_bottom = height - padding - int(72 * scale)
    bounds = (float(padding), float(plot_top), float(width - padding), float(plot_bottom))

    polygons = [voronoi_cell(site, sites, bounds) for site in sites]

    cell_stroke = max(2, int(2.5 * scale))
    dot_radius = max(6, int(8 * scale * (1.0 - 0.35 * (count / 100))))
    dot_stroke = max(2, int(2.5 * scale))
    card_rx = int(20 * scale)
    title_x = int(72 * scale)
    title_y = int(94 * scale)
    title_fs = int(32 * scale)
    subtitle_y = int(126 * scale)
    subtitle_fs = int(18 * scale)
    footer_fs = int(15 * scale)
    footer_y = height - int(62 * scale)
    footer_right_x = width - int(240 * scale)
    shadow_dy = int(5 * scale)
    shadow_std = int(7 * scale)

    cells = "\n".join(
        f'    <polygon points="{points_attribute(cell)}" fill="{PALETTE[index % len(PALETTE)]}" fill-opacity="0.65" />'
        for index, cell in enumerate(polygons)
        if cell
    )
    dots = "\n".join(
        f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="{dot_radius}" fill="#0F172A" stroke="#FFFFFF" stroke-width="{dot_stroke}" />'
        for x, y in sites
    )

    site_text = f"{count} {'sites' if count != 1 else 'site'}"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">Voronoi diagram with {site_text}</title>
  <desc id="description">A high-resolution {width}x{height} clipped Voronoi diagram with {site_text}. Seed: {seed}.</desc>
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#F8FAFC"/><stop offset="1" stop-color="#E0F2FE"/></linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%"><feDropShadow dx="0" dy="{shadow_dy}" stdDeviation="{shadow_std}" flood-color="#0F172A" flood-opacity=".12"/></filter>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#background)"/>
  <rect x="{padding}" y="{padding}" width="{width - 2 * padding}" height="{height - 2 * padding}" rx="{card_rx}" fill="#FFFFFF" filter="url(#shadow)"/>
  <g font-family="Arial, sans-serif"><text x="{title_x}" y="{title_y}" font-size="{title_fs}" font-weight="700" fill="#0F172A">Voronoi Diagram</text><text x="{title_x}" y="{subtitle_y}" font-size="{subtitle_fs}" fill="#475569">{site_text} · generated with seed {seed} · Ultra HD ({width}x{height})</text></g>
  <g stroke="#FFFFFF" stroke-width="{cell_stroke}" stroke-linejoin="round">
{cells}
  </g>
  <g>
{dots}
  </g>
  <g font-family="Arial, sans-serif" font-size="{footer_fs}" fill="#64748B"><text x="{title_x}" y="{footer_y}">Each region contains all points closest to its dark site marker.</text><text x="{footer_right_x}" y="{footer_y}">sites: {count:02d}</text></g>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate high-resolution SVG Voronoi diagrams.")
    parser.add_argument("--output", type=Path, default=Path("output"), help="directory for SVG files")
    parser.add_argument("--seed", type=int, default=20260905, help="random seed; use a new value for different diagrams")
    parser.add_argument("--count", type=int, default=100, help="total number of diagrams to generate (default: 100)")
    parser.add_argument("--min-sites", type=int, default=1, help="minimum site count (default: 1)")
    parser.add_argument("--max-sites", type=int, default=None, help="maximum site count (default: min_sites + count - 1)")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help=f"canvas width in pixels (default: {DEFAULT_WIDTH})")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help=f"canvas height in pixels (default: {DEFAULT_HEIGHT})")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    if args.max_sites is not None:
        site_counts = list(range(args.min_sites, args.max_sites + 1))
    else:
        site_counts = list(range(args.min_sites, args.min_sites + args.count))

    files_manifest = []
    for count in site_counts:
        diagram_seed = args.seed + count * 10_007
        sites = generate_sites(count, random.Random(diagram_seed), args.width, args.height)
        svg = make_svg(sites, diagram_seed, count, args.width, args.height)
        filename = f"voronoi_{count:02d}_sites.svg"
        (args.output / filename).write_text(svg, encoding="utf-8")
        files_manifest.append({"sites": count, "file": filename})

    manifest = {
        "seed": args.seed,
        "width": args.width,
        "height": args.height,
        "total": len(site_counts),
        "site_counts": site_counts,
        "files": files_manifest,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{entry['file']}` | {entry['sites']} | {args.width}x{args.height} | {args.seed + entry['sites'] * 10_007} |"
        for entry in files_manifest
    )
    readme = (
        f"# Voronoi Diagram High-Resolution Collection\n\n"
        f"Contains {len(site_counts)} high-resolution ({args.width}x{args.height}) Voronoi diagram SVGs "
        f"spanning {site_counts[0]} to {site_counts[-1]} sites.\n\n"
        f"Base seed: `{args.seed}`\n\n"
        f"| File | Sites | Resolution | Seed |\n"
        f"| --- | --- | --- | --- |\n"
        f"{rows}\n"
    )
    (args.output / "README.md").write_text(readme, encoding="utf-8")

    print(f"Created {len(site_counts)} high-resolution ({args.width}x{args.height}) SVG diagrams in {args.output}")


if __name__ == "__main__":
    main()
