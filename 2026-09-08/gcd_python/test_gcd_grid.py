import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gcd_grid import (
    choose_dimensions,
    euclidean_square_tiling,
    fresh_seed,
    main,
    random_dimensions,
    svg_visualization,
)


class EuclideanTilingTests(unittest.TestCase):
    def test_breaks_84_by_60_into_progressively_smaller_squares(self):
        tiles = euclidean_square_tiling(84, 60)
        self.assertEqual([(tile.side, tile.step) for tile in tiles], [(60, 0), (24, 1), (24, 1), (12, 2), (12, 2)])
        self.assertEqual(sum(tile.side * tile.side for tile in tiles), 84 * 60)

    def test_last_square_size_is_the_gcd(self):
        for a, b in [(48, 36), (49, 35), (144, 96), (105, 70)]:
            tiles = euclidean_square_tiling(a, b)
            self.assertEqual(tiles[-1].side, math.gcd(a, b))

    def test_svg_has_a_legend_for_each_euclidean_step(self):
        svg, divisor, steps, squares = svg_visualization(84, 60)
        self.assertEqual((divisor, steps, squares), (12, 3, 5))
        self.assertIn("Step 1: 1 square(s) of 60×60", svg)
        self.assertIn("Step 2: 2 square(s) of 24×24", svg)
        self.assertIn("Step 3: 2 square(s) of 12×12", svg)
        self.assertNotIn("Seed ", svg)


class SeededRandomPairTests(unittest.TestCase):
    def test_same_seed_reproduces_the_same_pair(self):
        self.assertEqual(random_dimensions(20260908), random_dimensions(20260908))
        self.assertEqual(choose_dimensions(None, None, 17), choose_dimensions(None, None, 17))

    def test_fresh_seeds_change_across_calls(self):
        seeds = {fresh_seed() for _ in range(40)}
        self.assertGreater(len(seeds), 1)

    def test_unseeded_pairs_are_not_stuck_on_one_example(self):
        pairs = {choose_dimensions(None, None)[:2] for _ in range(30)}
        self.assertGreater(len(pairs), 1)

    def test_different_seeds_cover_more_than_one_pair(self):
        pairs = {random_dimensions(seed) for seed in range(80)}
        self.assertGreater(len(pairs), 10)

    def test_generated_gcd_matches_the_constructed_divisor(self):
        width, height = random_dimensions(99)
        self.assertGreater(math.gcd(width, height), 1)
        self.assertNotEqual(width, height)

    def test_explicit_dimensions_ignore_the_seed(self):
        self.assertEqual(choose_dimensions(84, 60, seed=1), (84, 60, None))

    def test_one_missing_dimension_is_an_error(self):
        with self.assertRaises(ValueError):
            choose_dimensions(84, None)
        with self.assertRaises(ValueError):
            choose_dimensions(None, 60)

    def test_svg_records_the_seed_for_a_random_pair(self):
        svg, *_ = svg_visualization(48, 36, seed=7)
        self.assertIn("Seed 7.", svg)

    def test_cli_without_args_uses_a_new_seed_each_run(self):
        pairs = set()
        for _ in range(8):
            with tempfile.TemporaryDirectory() as directory:
                destination = Path(directory) / "out.svg"
                with patch("sys.argv", ["gcd_grid.py", "--save", str(destination)]):
                    main()
                text = destination.read_text(encoding="utf-8")
                title = next(line for line in text.splitlines() if "Euclidean algorithm: gcd(" in line)
                pairs.add(title)
        self.assertGreater(len(pairs), 1)


if __name__ == "__main__":
    unittest.main()
