#!/usr/bin/env python3
"""
Unit tests for Fractal SVG Generator
====================================
Validates mathematical correctness, XML conformance, seed determinism,
palette interpolation, difficulty classifications, and CLI interfaces.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fractals import (
    PALETTES,
    REGISTRY,
    FractalSpec,
    SvgCanvas,
    generate_single_fractal,
    get_gradient_color,
    main,
)


class FractalRegistryTests(unittest.TestCase):
    """Test registry completeness and metadata invariants."""

    def test_registry_contains_all_15_fractals(self):
        self.assertEqual(len(REGISTRY), 15)

    def test_difficulty_tiers_are_categorized(self):
        difficulties = {spec.difficulty for spec in REGISTRY.values()}
        self.assertEqual(difficulties, {"easy", "medium", "hard"})

        easy = [fid for fid, s in REGISTRY.items() if s.difficulty == "easy"]
        medium = [fid for fid, s in REGISTRY.items() if s.difficulty == "medium"]
        hard = [fid for fid, s in REGISTRY.items() if s.difficulty == "hard"]

        self.assertEqual(len(easy), 5)
        self.assertEqual(len(medium), 5)
        self.assertEqual(len(hard), 5)

    def test_all_specs_have_valid_metadata(self):
        for fid, spec in REGISTRY.items():
            self.assertTrue(spec.title, f"{fid} has empty title")
            self.assertTrue(spec.dimension_formula, f"{fid} has empty dimension formula")
            self.assertTrue(spec.dimension_val, f"{fid} has empty dimension value")
            self.assertGreater(spec.default_depth, 0, f"{fid} depth <= 0")
            self.assertTrue(spec.description, f"{fid} description is empty")
            self.assertTrue(callable(spec.func), f"{fid} function is not callable")


class ColorPaletteTests(unittest.TestCase):
    """Test palette generation and color interpolation."""

    def test_palettes_defined(self):
        required_palettes = ["neon", "cyberpunk", "sunset", "emerald", "ocean", "fire", "gold"]
        for p in required_palettes:
            self.assertIn(p, PALETTES)
            self.assertGreaterEqual(len(PALETTES[p]), 2)

    def test_get_gradient_color_boundary_and_interpolation(self):
        palette = ["#000000", "#ffffff"]
        self.assertEqual(get_gradient_color(palette, 0.0), "#000000")
        self.assertEqual(get_gradient_color(palette, 1.0), "#ffffff")
        self.assertEqual(get_gradient_color(palette, 0.5), "#808080")

    def test_clamping(self):
        palette = ["#102030", "#405060"]
        self.assertEqual(get_gradient_color(palette, -1.0), "#102030")
        self.assertEqual(get_gradient_color(palette, 2.0), "#405060")


class SvgGenerationXmlTests(unittest.TestCase):
    """Test XML validity and structure of generated SVGs."""

    def test_all_fractals_generate_valid_xml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            for fid, spec in REGISTRY.items():
                out_file = tmppath / f"{fid}.svg"
                meta = generate_single_fractal(
                    fid=fid,
                    output_path=out_file,
                    width=600,
                    height=600,
                    depth=min(spec.default_depth, 6) if spec.difficulty != "hard" else min(spec.default_depth, 1000),
                    seed=12345,
                    palette="neon",
                )
                self.assertTrue(out_file.exists())
                self.assertGreater(meta["size_bytes"], 500)

                # Parse XML
                tree = ET.parse(out_file)
                root = tree.getroot()
                self.assertTrue(root.tag.endswith("svg"))
                self.assertEqual(root.attrib.get("viewBox"), "0 0 600 600")

                # Verify text presence
                content = out_file.read_text(encoding="utf-8")
                self.assertIn(spec.title, content)
                self.assertIn(spec.dimension_val, content)

    def test_seed_determinism(self):
        """Identical seeds must yield identical SVG files for procedural fractals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            file1 = tmppath / "canopy1.svg"
            file2 = tmppath / "canopy2.svg"

            generate_single_fractal("fractal_canopy", file1, 600, 600, depth=6, seed=999, palette="emerald")
            generate_single_fractal("fractal_canopy", file2, 600, 600, depth=6, seed=999, palette="emerald")

            self.assertEqual(file1.read_text(encoding="utf-8"), file2.read_text(encoding="utf-8"))

    def test_unknown_fractal_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "fake.svg"
            with self.assertRaises(ValueError):
                generate_single_fractal("non_existent_fractal", out_file, 600, 600, 2, 42, "neon")


class CliInterfaceTests(unittest.TestCase):
    """Test CLI execution and arguments."""

    def test_cli_list(self):
        res = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "fractals.py"), "--list"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("cantor_set", res.stdout)
        self.assertIn("koch_snowflake", res.stdout)
        self.assertIn("mandelbrot_set", res.stdout)

    def test_cli_generate_single_with_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).parent / "fractals.py"),
                    "--fractal",
                    "koch_snowflake",
                    "--output-dir",
                    tmpdir,
                    "--manifest",
                    "--depth",
                    "3",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0)
            self.assertTrue((Path(tmpdir) / "koch_snowflake.svg").exists())
            manifest_file = Path(tmpdir) / "manifest.json"
            self.assertTrue(manifest_file.exists())
            data = json.loads(manifest_file.read_text(encoding="utf-8"))
            self.assertEqual(data["total"], 1)
            self.assertEqual(data["fractals"][0]["id"], "koch_snowflake")

    def test_cli_filter_difficulty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).parent / "fractals.py"),
                    "--difficulty",
                    "easy",
                    "--output-dir",
                    tmpdir,
                    "--depth",
                    "2",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0)
            svgs = list(Path(tmpdir).glob("*.svg"))
            self.assertEqual(len(svgs), 5)


if __name__ == "__main__":
    unittest.main()
