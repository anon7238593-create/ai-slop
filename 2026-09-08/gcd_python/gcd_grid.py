#!/usr/bin/env python3
"""Find gcd(a, b) and visualize it as colored squares filling a 2D rectangle.

The generated SVG needs no third-party Python packages and opens in any modern
web browser. Each tile is a gcd(a, b) by gcd(a, b) square.
"""

from __future__ import annotations

import argparse
import html
import math
import webbrowser
from pathlib import Path

PALETTE = (
    "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#a29bfe",
    "#ff9ff3", "#54a0ff", "#5f27cd", "#00d2d3", "#ff9f43",
    "#10ac84", "#ee5253",
)


def positive_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("numbers must be positive")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Draw an a × b rectangle tiled by gcd(a, b) squares."
    )
    parser.add_argument("a", nargs="?", type=positive_integer, default=84,
                        help="rectangle width (default: 84)")
    parser.add_argument("b", nargs="?", type=positive_integer, default=60,
                        help="rectangle height (default: 60)")
    parser.add_argument("--save", metavar="FILE", type=Path,
                        default=Path("gcd_visualization.svg"),
                        help="SVG destination (default: gcd_visualization.svg)")
    parser.add_argument("--open", action="store_true",
                        help="open the created SVG in the default browser")
    return parser


def svg_visualization(a: int, b: int) -> tuple[str, int, int, int]:
    """Return an SVG and the GCD, column count, and row count."""
    divisor = math.gcd(a, b)
    columns, rows = a // divisor, b // divisor
    scale = min(620 / a, 460 / b)
    width, height = a * scale, b * scale
    margin_left, margin_top, margin_bottom = 85, 100, 85
    canvas_width, canvas_height = width + margin_left + 35, height + margin_top + margin_bottom
    title = f"gcd({a}, {b}) = {divisor} — {columns} × {rows} squares fill the rectangle"

    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width:.0f}" height="{canvas_height:.0f}" viewBox="0 0 {canvas_width:.0f} {canvas_height:.0f}">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="{canvas_width / 2:.1f}" y="38" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" font-weight="bold" fill="#172033">{html.escape(title)}</text>
  <text x="{canvas_width / 2:.1f}" y="68" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#475569">Every colored tile is {divisor} × {divisor}; no gaps remain.</text>
  <g transform="translate({margin_left},{margin_top})">''']

    for row in range(rows):
        for column in range(columns):
            x, y = column * divisor * scale, (rows - row - 1) * divisor * scale
            color = PALETTE[(row * columns + column) % len(PALETTE)]
            parts.append(
                f'    <rect x="{x:.2f}" y="{y:.2f}" width="{divisor * scale:.2f}" height="{divisor * scale:.2f}" fill="{color}" stroke="#18202a" stroke-width="1.5"/>'
            )
            if min(divisor * scale, divisor * scale) >= 52:
                parts.append(
                    f'    <text x="{x + divisor * scale / 2:.2f}" y="{y + divisor * scale / 2 + 5:.2f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#172033">{divisor}²</text>'
                )

    parts.extend([f'''  </g>
  <text x="{margin_left + width / 2:.1f}" y="{margin_top + height + 33:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="bold" fill="#172033">Width = {a}</text>
  <text x="27" y="{margin_top + height / 2:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="bold" fill="#172033" transform="rotate(-90 27 {margin_top + height / 2:.1f})">Height = {b}</text>
</svg>'''])
    return "\n".join(parts), divisor, columns, rows


def main() -> None:
    args = build_parser().parse_args()
    svg, divisor, columns, rows = svg_visualization(args.a, args.b)
    args.save.parent.mkdir(parents=True, exist_ok=True)
    args.save.write_text(svg, encoding="utf-8")
    print(f"gcd({args.a}, {args.b}) = {divisor}")
    print(f"Tiling: {columns} columns × {rows} rows of {divisor}×{divisor} colored squares")
    print(f"Saved visualization to: {args.save.resolve()}")
    if args.open:
        webbrowser.open(args.save.resolve().as_uri())


if __name__ == "__main__":
    main()
