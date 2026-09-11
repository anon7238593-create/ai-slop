#!/usr/bin/env python3
import unittest
import math
from pathlib import Path
import sys

# Ensure current dir in path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rsa_math import (
    is_prime,
    gcd,
    extended_gcd_with_steps,
    modular_inverse,
    get_fermat_residues,
    get_euler_totient_data,
    generate_rsa_demo_keys,
)


class TestRSAMath(unittest.TestCase):
    def test_primes(self):
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 61, 53]
        for p in primes:
            self.assertTrue(is_prime(p), f"{p} should be prime")
        composites = [0, 1, 4, 6, 8, 9, 10, 15, 21, 25, 27]
        for c in composites:
            self.assertFalse(is_prime(c), f"{c} should not be prime")

    def test_extended_gcd_and_bezout(self):
        cases = [(17, 40), (7, 120), (35, 15), (252, 105), (65537, 3120)]
        for a, b in cases:
            g, x, y, steps, rows = extended_gcd_with_steps(a, b)
            self.assertEqual(g, math.gcd(a, b))
            self.assertEqual(a * x + b * y, g)
            self.assertGreater(len(steps), 0)
            self.assertGreater(len(rows), 2)

    def test_modular_inverse(self):
        # 17 * 33 = 561 = 14 * 40 + 1 == 1 mod 40
        inv, rows = modular_inverse(17, 40)
        self.assertEqual(inv, 33)
        self.assertEqual((17 * inv) % 40, 1)

        # 7 * 103 = 721 = 6 * 120 + 1 == 1 mod 120
        inv2, _ = modular_inverse(7, 120)
        self.assertEqual(inv2, 103)
        self.assertEqual((7 * inv2) % 120, 1)

        # Non-coprime raises ValueError
        with self.assertRaises(ValueError):
            modular_inverse(6, 15)

    def test_fermat_residues(self):
        data = get_fermat_residues(3, 7)
        self.assertTrue(data["is_permutation"])
        self.assertTrue(data["final_power_is_one"])
        self.assertEqual(data["powers"][-1][1], 1)
        self.assertEqual(data["powers"][-1][0], 6)

    def test_euler_totient(self):
        data = get_euler_totient_data(3, 5)
        self.assertEqual(data["n"], 15)
        self.assertEqual(data["phi"], 8)
        self.assertEqual(len(data["coprime_residues"]), 8)
        self.assertEqual(data["non_coprime_count"], 7)

    def test_rsa_demo_keys(self):
        keys = generate_rsa_demo_keys(11, 13, 7)
        self.assertEqual(keys["n"], 143)
        self.assertEqual(keys["phi"], 120)
        self.assertEqual(keys["e"], 7)
        self.assertEqual(keys["d"], 103)
        self.assertEqual(keys["recovered_m"], keys["sample_m"])
        self.assertEqual(keys["e"] * keys["d"], 1 + keys["k"] * keys["phi"])


if __name__ == "__main__":
    unittest.main()
