import math
import unittest

from gcd_grid import euclidean_square_tiling, svg_visualization


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


if __name__ == "__main__":
    unittest.main()
