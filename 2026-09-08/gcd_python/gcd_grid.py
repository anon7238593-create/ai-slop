#!/usr/bin/env python3
"""Visualize the Euclidean algorithm by filling a rectangle with shrinking squares.

For a by b, the program takes as many squares as possible with the shorter
remaining side, then repeats on the leftover rectangle.  The final square side
is gcd(a, b), so the visual makes the GCD calculation visible.
"""

from __future__ import annotations

import argparse
import html
import math
import webbrowser
from dataclasses import dataclass
from pathlib import Path

PALETTE = ("#ff6b6b", "#4dabf7", "#51cf66", "#ffd43b", "#cc5de8", "#ff922b", "#20c997", "#f06595")


@dataclass(frozen=True)
class Tile:
    """One square placed during one Euclidean-algorithm step."""

    x: int
    y: int
    side: int
    step: int


def positive_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("numbers must be positive")
    return number


def euclidean_square_tiling(a: int, b: int) -> list[Tile]:
    """Fill an a-by-b rectangle using the Euclidean algorithm's square steps."""
    if a <= 0 or b <= 0:
        raise ValueError("rectangle dimensions must be positive")

    tiles: list[Tile] = []
    x = y = step = 0
    width, height = a, b
    while width and height:
        side = min(width, height)
        if width >= height:
            count = width // side
            tiles.extend(Tile(x + index * side, y, side, step) for index in range(count))
            x += count * side
            width %= side
        else:
            count = height // side
            tiles.extend(Tile(x, y + index * side, side, step) for index in range(count))
            y += count * side
            height %= side
        step += 1
    return tiles


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Visualize the Euclidean algorithm with progressively smaller squares."
    )
    parser.add_argument("a", nargs="?", type=positive_integer, default=84, help="rectangle width (default: 84)")
    parser.add_argument("b", nargs="?", type=positive_integer, default=60, help="rectangle height (default: 60)")
    parser.add_argument("--save", metavar="FILE", type=Path, default=Path("gcd_visualization.svg"), help="SVG destination")
    parser.add_argument("--open", action="store_true", help="open the created SVG in the default browser")
    return parser


def svg_visualization(a: int, b: int) -> tuple[str, int, int, int]:
    """Return an SVG plus GCD, number of Euclidean steps, and number of squares."""
    tiles = euclidean_square_tiling(a, b)
    divisor = math.gcd(a, b)
    step_count = max(tile.step for tile in tiles) + 1
    scale = min(620 / a, 430 / b)
    width, height = a * scale, b * scale
    left, top, bottom = 100, 115, 120
    canvas_width, canvas_height = width + left + 45, height + top + bottom
    title = f"Euclidean algorithm: gcd({a}, {b}) = {divisor}"
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width:.0f}" height="{canvas_height:.0f}" viewBox="0 0 {canvas_width:.0f} {canvas_height:.0f}">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="{canvas_width / 2:.1f}" y="38" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="bold" fill="#172033">{html.escape(title)}</text>
  <text x="{canvas_width / 2:.1f}" y="68" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#475569">Take the biggest squares first; each remaining strip creates a smaller square size.</text>
  <g>''']

    for tile in tiles:
        x = left + tile.x * scale
        y = top + (b - tile.y - tile.side) * scale
        color = PALETTE[tile.step % len(PALETTE)]
        parts.append(f'    <rect x="{x:.2f}" y="{y:.2f}" width="{tile.side * scale:.2f}" height="{tile.side * scale:.2f}" fill="{color}" stroke="#172033" stroke-width="2"/>')
        if tile.side * scale >= 46:
            parts.append(f'    <text x="{x + tile.side * scale / 2:.2f}" y="{y + tile.side * scale / 2 + 5:.2f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#172033">{tile.side}×{tile.side}</text>')

    parts.append("  </g>")
    for step in range(step_count):
        side = next(tile.side for tile in tiles if tile.step == step)
        count = sum(tile.step == step for tile in tiles)
        legend_x = left + (step % 3) * 205
        legend_y = top + height + 35 + (step // 3) * 25
        parts.append(f'  <rect x="{legend_x}" y="{legend_y - 13:.1f}" width="15" height="15" fill="{PALETTE[step % len(PALETTE)]}" stroke="#172033"/>')
        parts.append(f'  <text x="{legend_x + 22}" y="{legend_y:.1f}" font-family="Arial, sans-serif" font-size="14" fill="#172033">Step {step + 1}: {count} square(s) of {side}×{side}</text>')
    parts.extend([f'''  <text x="{left + width / 2:.1f}" y="{top + height + 100:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="bold" fill="#172033">Width = {a}</text>
  <text x="30" y="{top + height / 2:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="bold" fill="#172033" transform="rotate(-90 30 {top + height / 2:.1f})">Height = {b}</text>
</svg>'''])
    return "\n".join(parts), divisor, step_count, len(tiles)


def main() -> None:
    args = build_parser().parse_args()
    svg, divisor, steps, squares = svg_visualization(args.a, args.b)
    args.save.parent.mkdir(parents=True, exist_ok=True)
    args.save.write_text(svg, encoding="utf-8")
    print(f"gcd({args.a}, {args.b}) = {divisor}")
    print(f"Euclidean breakdown: {steps} colored size levels, {squares} total squares")
    print(f"Saved visualization to: {args.save.resolve()}")
    if args.open:
        webbrowser.open(args.save.resolve().as_uri())


if __name__ == "__main__":
    main()
