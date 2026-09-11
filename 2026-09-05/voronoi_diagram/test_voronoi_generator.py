import json
import random
import tempfile
import unittest
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from voronoi_svg_generator import (
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    clip_polygon,
    generate_sites,
    main,
    make_svg,
    voronoi_cell,
)


class VoronoiGeneratorTests(unittest.TestCase):
    def test_clip_polygon_horizontal(self):
        polygon = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
        normal = (1.0, 0.0)
        constant = 5.0
        clipped = clip_polygon(polygon, normal, constant)
        self.assertEqual(len(clipped), 4)
        for x, y in clipped:
            self.assertLessEqual(x, 5.0 + 1e-6)

    def test_single_site_generates_full_cell(self):
        bounds = (100.0, 100.0, 1000.0, 700.0)
        sites = [(500.0, 400.0)]
        cell = voronoi_cell(sites[0], sites, bounds)
        self.assertEqual(len(cell), 4)
        svg = make_svg(sites, 12345, 1, 3840, 2400)
        self.assertIn('width="3840"', svg)
        self.assertIn('height="2400"', svg)
        self.assertIn("1 site", svg)

    def test_high_resolution_canvas_dimensions(self):
        sites = generate_sites(10, random.Random(42), 3840, 2400)
        self.assertEqual(len(sites), 10)
        svg = make_svg(sites, 42, 10, 3840, 2400)
        self.assertIn('viewBox="0 0 3840 2400"', svg)
        self.assertIn('width="3840"', svg)
        self.assertIn('height="2400"', svg)

    def test_generate_100_sites(self):
        sites = generate_sites(100, random.Random(999), 3840, 2400)
        self.assertEqual(len(sites), 100)
        svg = make_svg(sites, 999, 100, 3840, 2400)
        self.assertIn("100 sites", svg)
        self.assertIn('sites: 100', svg)

    def test_main_cli_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            outpath = Path(tmpdir)
            with patch("sys.argv", ["voronoi_svg_generator.py", "--output", str(outpath), "--count", "5", "--min-sites", "1", "--seed", "42"]):
                main()
            svgs = sorted(outpath.glob("*.svg"))
            self.assertEqual(len(svgs), 5)
            self.assertTrue((outpath / "manifest.json").exists())
            self.assertTrue((outpath / "README.md").exists())
            manifest = json.loads((outpath / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["total"], 5)
            self.assertEqual(manifest["width"], DEFAULT_WIDTH)
            self.assertEqual(manifest["height"], DEFAULT_HEIGHT)


if __name__ == "__main__":
    unittest.main()
