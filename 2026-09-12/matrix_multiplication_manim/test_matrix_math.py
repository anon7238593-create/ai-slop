#!/usr/bin/env python3
"""Unit tests for matrix mathematics, eigenvalue decomposition, and transformation compositions."""

import math
from pathlib import Path
import unittest

from random_matrix_generator import MatrixPack, generate_matrix_pack


class TestMatrixMath(unittest.TestCase):
    def test_random_seed_determinism(self):
        pack1 = generate_matrix_pack(seed=42)
        pack2 = generate_matrix_pack(seed=42)
        self.assertEqual(pack1.matrix_a, pack2.matrix_a)
        self.assertEqual(pack1.matrix_b, pack2.matrix_b)
        self.assertEqual(pack1.matrix_c, pack2.matrix_c)
        self.assertEqual(pack1.lambda_1, pack2.lambda_1)
        self.assertEqual(pack1.lambda_2, pack2.lambda_2)

    def test_different_seeds_produce_different_matrices(self):
        pack1 = generate_matrix_pack(seed=101)
        pack2 = generate_matrix_pack(seed=202)
        self.assertNotEqual(pack1.matrix_a, pack2.matrix_a)

    def test_eigenvalue_eigenvector_equation(self):
        """Verify A * v1 = lambda1 * v1 and A * v2 = lambda2 * v2 within roundoff tolerance."""
        for seed in (1, 10, 42, 99, 12345):
            pack = generate_matrix_pack(seed=seed)
            A = pack.matrix_a
            l1, l2 = pack.lambda_1, pack.lambda_2
            v1, v2 = pack.v1, pack.v2

            # Compute A @ v1
            av1_x = A[0][0] * v1[0] + A[0][1] * v1[1]
            av1_y = A[1][0] * v1[0] + A[1][1] * v1[1]
            exp1_x = l1 * v1[0]
            exp1_y = l1 * v1[1]
            self.assertAlmostEqual(av1_x, exp1_x, delta=0.08)
            self.assertAlmostEqual(av1_y, exp1_y, delta=0.08)

            # Compute A @ v2
            av2_x = A[0][0] * v2[0] + A[0][1] * v2[1]
            av2_y = A[1][0] * v2[0] + A[1][1] * v2[1]
            exp2_x = l2 * v2[0]
            exp2_y = l2 * v2[1]
            self.assertAlmostEqual(av2_x, exp2_x, delta=0.08)
            self.assertAlmostEqual(av2_y, exp2_y, delta=0.08)

    def test_eigenvectors_orthogonal(self):
        """Eigenvectors v1 and v2 should be orthogonal (dot product near 0)."""
        for seed in (5, 25, 77):
            pack = generate_matrix_pack(seed=seed)
            dot = pack.v1[0] * pack.v2[0] + pack.v1[1] * pack.v2[1]
            self.assertAlmostEqual(dot, 0.0, places=2)

    def test_shear_determinant(self):
        """Shear matrices must have determinant equal to 1.0."""
        for seed in range(10):
            pack = generate_matrix_pack(seed=seed)
            H = pack.shear_matrix
            det_h = H[0][0] * H[1][1] - H[0][1] * H[1][0]
            self.assertAlmostEqual(det_h, 1.0, places=5)

    def test_scale_determinant(self):
        """Scale matrix determinant must equal sx * sy."""
        for seed in range(10):
            pack = generate_matrix_pack(seed=seed)
            S = pack.scale_matrix
            det_s = S[0][0] * S[1][1] - S[0][1] * S[1][0]
            self.assertAlmostEqual(det_s, pack.scale_x * pack.scale_y, places=4)

    def test_matrix_multiplication_equivalence(self):
        """Verify C = B @ A element-wise."""
        for seed in (12, 34, 56, 78):
            pack = generate_matrix_pack(seed=seed)
            A = pack.matrix_a
            B = pack.matrix_b
            C = pack.matrix_c

            c00 = B[0][0] * A[0][0] + B[0][1] * A[1][0]
            c01 = B[0][0] * A[0][1] + B[0][1] * A[1][1]
            c10 = B[1][0] * A[0][0] + B[1][1] * A[1][0]
            c11 = B[1][0] * A[0][1] + B[1][1] * A[1][1]

            self.assertAlmostEqual(C[0][0], c00, delta=0.02)
            self.assertAlmostEqual(C[0][1], c01, delta=0.02)
            self.assertAlmostEqual(C[1][0], c10, delta=0.02)
            self.assertAlmostEqual(C[1][1], c11, delta=0.02)

    def test_determinant_composition(self):
        """Verify det(B @ A) ~= det(B) * det(A)."""
        for seed in (7, 14, 21):
            pack = generate_matrix_pack(seed=seed)
            expected_det = pack.det_b * pack.det_a
            self.assertAlmostEqual(pack.det_c, expected_det, delta=0.08)


if __name__ == "__main__":
    unittest.main()
