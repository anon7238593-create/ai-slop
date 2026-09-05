# Voronoi SVG diagrams

This dependency-free Python program produces attractive SVG Voronoi diagrams for every number of sites from 2 through 20. Each cell is calculated by clipping the canvas against the perpendicular bisector of every other site.

```bash
cd 2026-09-05/voronoi_diagram
python3 voronoi_svg_generator.py --seed 20260905
```

The SVGs are written to `output/`. Change `--seed` for a different collection, or use `--output` to choose another directory.

The `generate_voronoi_diagrams.yml` GitHub workflow generates a new seeded collection on every repository push and daily at 12:00 UTC, then publishes it to the `artifacts` branch.
