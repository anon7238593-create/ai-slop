# Euclidean Algorithm Grid Visualizer

A dependency-free Python demonstration of how the Euclidean algorithm finds a
GCD. It starts with the **largest squares** that fit in an `a × b` rectangle.
It then fills the leftover strip with the next smaller square size, continuing
until the final square size is the GCD.

For `84 × 60`, the visual shows:

1. one `60 × 60` square;
2. two `24 × 24` squares in the remainder;
3. two `12 × 12` squares — so `gcd(84, 60) = 12`.

Each size level has its own color and a legend below the grid.

## Run

Omit the dimensions to get a **new random pair on every run**. The program
prints the seed it used so you can recreate a pair you liked:

```bash
cd 2026-09-08/gcd_python
python3 gcd_grid.py --open
```

Pass `--seed` for a reproducible random pair, or give both numbers explicitly:

```bash
python3 gcd_grid.py --seed 20260908 --open
python3 gcd_grid.py 84 60 --open
```

This writes `gcd_visualization.svg` and opens it in the default browser. To
save a named example without opening a browser:

```bash
python3 gcd_grid.py 48 36 --save gcd_48_36.svg
python3 -m unittest test_gcd_grid.py
```

Only Python 3's standard library is required.
