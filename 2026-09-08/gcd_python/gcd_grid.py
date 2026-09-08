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
import random
import secrets
import webbrowser
from dataclasses import dataclass
from pathlib import Path

PALETTE = ("#ff6b6b", "#4dabf7", "#51cf66", "#ffd43b", "#cc5de8", "#ff922b", "#20c997", "#f06595")
MIN_MULTIPLIER = 2
MAX_MULTIPLIER = 12
MIN_DIVISOR = 2
MAX_DIVISOR = 18


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


def fresh_seed() -> int:
    """Return a new 32-bit seed from OS entropy so each run can differ."""
    return secrets.randbits(32)


def random_dimensions(seed: int) -> tuple[int, int]:
    """Build a seeded Euclidean example whose GCD is greater than 1.

    Multipliers stay coprime so the chosen divisor is the true GCD, and the
    sides stay unequal so the visualization is more than a single square.
    """
    rng = random.Random(seed)
    divisor = rng.randint(MIN_DIVISOR, MAX_DIVISOR)
    first = rng.randint(MIN_MULTIPLIER, MAX_MULTIPLIER)
    second = rng.randint(MIN_MULTIPLIER, MAX_MULTIPLIER)
    while second == first or math.gcd(first, second) != 1:
        second = rng.randint(MIN_MULTIPLIER, MAX_MULTIPLIER)
    width, height = divisor * first, divisor * second
    if rng.choice((True, False)):
        width, height = height, width
    return width, height


def choose_dimensions(a: int | None, b: int | None, seed: int | None = None) -> tuple[int, int, int | None]:
    """Return width, height, and the seed used when the pair was generated."""
    if a is None and b is None:
        used_seed = seed if seed is not None else fresh_seed()
        width, height = random_dimensions(used_seed)
        return width, height, used_seed
    if a is None or b is None:
        raise ValueError("provide both dimensions, or neither for a random pair")
    return a, b, None


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
    parser.add_argument("a", nargs="?", type=positive_integer, help="rectangle width (random if omitted)")
    parser.add_argument("b", nargs="?", type=positive_integer, help="rectangle height (random if omitted)")
    parser.add_argument("--seed", type=int, default=None, help="seed for a reproducible random pair; ignored when a and b are given")
    parser.add_argument("--save", metavar="FILE", type=Path, default=Path("gcd_visualization.svg"), help="SVG destination")
    parser.add_argument("--open", action="store_true", help="open the created SVG in the default browser")
    return parser


def svg_visualization(a: int, b: int, seed: int | None = None) -> tuple[str, int, int, int]:
    """Return an SVG plus GCD, number of Euclidean steps, and number of squares."""
    tiles = euclidean_square_tiling(a, b)
    divisor = math.gcd(a, b)
    step_count = max(tile.step for tile in tiles) + 1

    # Dynamic scaling: do not limit the grid to a fixed default box.
    # Allow the grid to take as much space as it needs, while ensuring
    # that the smallest GCD squares have sufficient room for dimension labels.
    scale = max(10, math.ceil(48 / divisor))
    width, height = a * scale, b * scale

    left = 100
    top = 115
    right = 60
    min_canvas_width = 780
    canvas_width = max(width + left + right, min_canvas_width)
    grid_x = left + (canvas_width - left - right - width) / 2

    width_label_y = top + height + 35
    legend_start_y = width_label_y + 35

    cols = max(1, min(3, int((canvas_width - left - 40) // 230)))
    total_legend_rows = math.ceil(step_count / cols)
    canvas_height = legend_start_y + total_legend_rows * 28 + 40

    title = f"Euclidean algorithm: gcd({a}, {b}) = {divisor}"
    subtitle = "Take the biggest squares first; each remaining strip creates a smaller square size."
    if seed is not None:
        subtitle += f" Seed {seed}."

    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_width:.0f} {canvas_height:.0f}" width="100%" height="100%">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="{canvas_width / 2:.1f}" y="38" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="bold" fill="#172033">{html.escape(title)}</text>
  <text x="{canvas_width / 2:.1f}" y="68" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#475569">{html.escape(subtitle)}</text>
  <g>''']

    for tile in tiles:
        x = grid_x + tile.x * scale
        y = top + (b - tile.y - tile.side) * scale
        tile_px = tile.side * scale
        color = PALETTE[tile.step % len(PALETTE)]
        parts.append(f'    <rect x="{x:.2f}" y="{y:.2f}" width="{tile_px:.2f}" height="{tile_px:.2f}" fill="{color}" stroke="#172033" stroke-width="2"/>')
        if tile_px >= 36:
            font_size = min(14, max(10, int(tile_px / 5)))
            parts.append(f'    <text x="{x + tile_px / 2:.2f}" y="{y + tile_px / 2 + 5:.2f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="{font_size}" font-weight="bold" fill="#172033">{tile.side}×{tile.side}</text>')

    parts.append("  </g>")

    col_width = (canvas_width - left - right) / cols
    for step in range(step_count):
        side = next(tile.side for tile in tiles if tile.step == step)
        count = sum(tile.step == step for tile in tiles)
        legend_col = step % cols
        legend_row = step // cols
        legend_x = left + legend_col * col_width
        legend_y = legend_start_y + legend_row * 28
        parts.append(f'  <rect x="{legend_x:.1f}" y="{legend_y - 13:.1f}" width="15" height="15" fill="{PALETTE[step % len(PALETTE)]}" stroke="#172033"/>')
        parts.append(f'  <text x="{legend_x + 22:.1f}" y="{legend_y:.1f}" font-family="Arial, sans-serif" font-size="14" fill="#172033">Step {step + 1}: {count} square(s) of {side}×{side}</text>')

    parts.extend([
        f'  <text x="{grid_x + width / 2:.1f}" y="{width_label_y:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="bold" fill="#172033">Width = {a}</text>',
        f'  <text x="{grid_x - 30:.1f}" y="{top + height / 2:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="bold" fill="#172033" transform="rotate(-90 {grid_x - 30:.1f} {top + height / 2:.1f})">Height = {b}</text>',
        '</svg>',
    ])
    return "\n".join(parts), divisor, step_count, len(tiles)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        width, height, seed = choose_dimensions(args.a, args.b, args.seed)
    except ValueError as error:
        parser.error(str(error))
    svg, divisor, steps, squares = svg_visualization(width, height, seed)
    args.save.parent.mkdir(parents=True, exist_ok=True)
    args.save.write_text(svg, encoding="utf-8")
    if seed is not None:
        print(f"Random pair seed={seed}: {width} × {height}")
    print(f"gcd({width}, {height}) = {divisor}")
    print(f"Euclidean breakdown: {steps} colored size levels, {squares} total squares")
    print(f"Saved visualization to: {args.save.resolve()}")
    if args.open:
        webbrowser.open(args.save.resolve().as_uri())


if __name__ == "__main__":
    main()
