# GCD 2D Grid Visualizer

A dependency-free Python demonstration: it finds `gcd(a, b)` and generates a
colored SVG where GCD-sized squares exactly tile an `a × b` rectangle.

## Run

```bash
cd 2026-09-08/gcd_python
python3 gcd_grid.py 84 60 --open
```

This reports `gcd(84, 60) = 12`, writes `gcd_visualization.svg`, and opens it
in the default browser. Every colored tile is `12 × 12`.

Create another demonstration without opening a browser:

```bash
python3 gcd_grid.py 48 36 --save gcd_48_36.svg
```

Only Python 3's standard library is required.
