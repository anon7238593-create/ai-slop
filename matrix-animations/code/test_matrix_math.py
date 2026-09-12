#!/usr/bin/env python3
"""Unit tests for matrix mathematics, eigenvalue decomposition, and transformation compositions."""

import math
import os
from pathlib import Path
import sys
import unittest

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from random_matrix_generator import (
    ASYMMETRIC_TRIANGLE_VERTICES,
    BASIS_VECTORS,
    MatrixPack,
    UNIT_SQUARE_VERTICES,
    generate_matrix_pack,
    get_canonical_shapes,
    get_ellipse_parameters,
    matrix_to_latex,
    sample_unit_circle,
    transform_point,
    transform_shape,
)


class TestMatrixMath(unittest.TestCase):
    def test_random_seed_determinism(self):
        pack1 = generate_matrix_pack(seed=42)
        pack2 = generate_matrix_pack(seed=42)
        self.assertEqual(pack1.matrix_a, pack2.matrix_a)
        self.assertEqual(pack1.matrix_b, pack2.matrix_b)
        self.assertEqual(pack1.matrix_c, pack2.matrix_c)
        self.assertEqual(pack1.lambda_1, pack2.lambda_1)
        self.assertEqual(pack1.lambda_2, pack2.lambda_2)
        self.assertEqual(pack1.canonical_shapes, pack2.canonical_shapes)
        self.assertEqual(pack1.transformed_shapes_a, pack2.transformed_shapes_a)
        self.assertEqual(pack1.ellipse_a, pack2.ellipse_a)
        self.assertEqual(pack1.latex_matrix_a, pack2.latex_matrix_a)

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

    def test_matrix_a_properties(self):
        """Verify Matrix A has positive distinct eigenvalues and det(A) in [0.8, 2.5]."""
        for seed in (3, 17, 45, 88, 123):
            pack = generate_matrix_pack(seed=seed)
            self.assertGreater(pack.lambda_1, pack.lambda_2)
            self.assertGreaterEqual(pack.lambda_1 - pack.lambda_2, 0.35)
            self.assertGreaterEqual(pack.det_a, 0.75)
            self.assertLessEqual(pack.det_a, 2.55)

    def test_matrix_b_planar_properties(self):
        """Verify Matrix B is a well-conditioned planar transformation (det(B) in [0.8, 1.5])."""
        for seed in (5, 19, 52, 91, 142):
            pack = generate_matrix_pack(seed=seed)
            self.assertGreater(pack.det_b, 0.0)
            self.assertGreaterEqual(pack.det_b, 0.75)
            self.assertLessEqual(pack.det_b, 1.55)
            # Ensure no z-axis spinning angle
            self.assertEqual(pack.phi_rad, 0.0)
            self.assertEqual(pack.phi_deg, 0.0)

    def test_canonical_shapes_definition(self):
        """Verify canonical geometries for Unit Square, Triangle, Circle, and Basis Vectors."""
        canonical = get_canonical_shapes()
        # Unit square: 4 vertices
        self.assertEqual(canonical["unit_square"], [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
        # Asymmetric triangle: 3 vertices
        self.assertEqual(canonical["triangle"], [[0.0, 0.0], [1.2, 0.2], [0.4, 1.0]])
        # Basis vectors: unit length
        i_hat = canonical["basis_vectors"]["i_hat"]
        j_hat = canonical["basis_vectors"]["j_hat"]
        self.assertEqual(i_hat, [1.0, 0.0])
        self.assertEqual(j_hat, [0.0, 1.0])
        self.assertAlmostEqual(math.hypot(*i_hat), 1.0)
        self.assertAlmostEqual(math.hypot(*j_hat), 1.0)
        # Unit circle
        self.assertEqual(canonical["unit_circle"]["radius"], 1.0)
        self.assertGreater(len(canonical["unit_circle"]["sample_points"]), 10)

    def test_transform_point_and_shape_methods(self):
        """Verify transform_point and transform_shape on MatrixPack and standalone."""
        pack = generate_matrix_pack(seed=42)
        A = pack.matrix_a

        # Test basis vector mapping to column 1 and column 2
        col1 = pack.transform_point(A, [1.0, 0.0])
        col2 = pack.transform_point(A, [0.0, 1.0])
        self.assertAlmostEqual(col1[0], A[0][0])
        self.assertAlmostEqual(col1[1], A[1][0])
        self.assertAlmostEqual(col2[0], A[0][1])
        self.assertAlmostEqual(col2[1], A[1][1])

        # Test transform_shape
        transformed_sq = pack.transform_shape(A, UNIT_SQUARE_VERTICES)
        self.assertEqual(len(transformed_sq), 4)
        self.assertEqual(transformed_sq[0], [0.0, 0.0])
        self.assertEqual(transformed_sq[1], col1)
        self.assertEqual(transformed_sq[3], col2)

    def test_ellipse_parameters(self):
        """Verify transformed circle ellipse semi-axes match singular values and det."""
        for seed in (2, 22, 62):
            pack = generate_matrix_pack(seed=seed)
            A = pack.matrix_a
            params = pack.get_ellipse_parameters(A)

            semi_major = params["semi_major_axis"]
            semi_minor = params["semi_minor_axis"]
            self.assertGreater(semi_major, semi_minor)
            # Area of ellipse = pi * a * b = pi * det(A)
            expected_area = math.pi * pack.det_a
            self.assertAlmostEqual(params["area"], expected_area, delta=0.1)

    def test_latex_formatting(self):
        """Verify LaTeX MathTex strings are properly generated."""
        pack = generate_matrix_pack(seed=42)
        self.assertTrue(pack.latex_matrix_a.startswith(r"\begin{bmatrix}"))
        self.assertTrue(pack.latex_matrix_b.startswith(r"\begin{bmatrix}"))
        self.assertTrue(pack.latex_matrix_c.startswith(r"\begin{bmatrix}"))
        self.assertIn(r"\cdot", pack.latex_product_formula)
        manifest = pack.get_latex_manifest()
        self.assertIn("matrix_a", manifest)
        self.assertIn("eigenvalues", manifest)
        self.assertIn("product_formula", manifest)

    def test_shape_composition_multiplication_equivalence(self):
        """Verify that B @ (A @ v) == (B @ A) @ v for all vertices of all shapes."""
        for seed in (42, 108, 999):
            pack = generate_matrix_pack(seed=seed)
            A = pack.matrix_a
            B = pack.matrix_b
            C = pack.matrix_c

            test_points = (
                UNIT_SQUARE_VERTICES
                + ASYMMETRIC_TRIANGLE_VERTICES
                + [BASIS_VECTORS["i_hat"], BASIS_VECTORS["j_hat"]]
                + sample_unit_circle(16)
            )

            for pt in test_points:
                # Step 1: v' = A @ v
                v_prime = transform_point(A, pt)
                # Step 2: v'' = B @ v' = B @ (A @ v)
                v_double_prime = transform_point(B, v_prime)
                # Direct single step: v_direct = C @ v = (B @ A) @ v
                v_direct = transform_point(C, pt)

                self.assertAlmostEqual(v_double_prime[0], v_direct[0], delta=0.03)
                self.assertAlmostEqual(v_double_prime[1], v_direct[1], delta=0.03)

    def test_collinearity_preservation(self):
        """Linear transformations must preserve collinearity: points on a line remain on a line."""
        pack = generate_matrix_pack(seed=42)
        for M in (pack.scale_matrix, pack.shear_matrix, pack.matrix_a, pack.matrix_b, pack.matrix_c):
            # 3 points on line y = 2x + 1
            p1 = [0.0, 1.0]
            p2 = [1.0, 3.0]
            p3 = [2.0, 5.0]

            tp1 = transform_point(M, p1)
            tp2 = transform_point(M, p2)
            tp3 = transform_point(M, p3)

            # Cross product (area of triangle formed by 3 points) should be 0
            cross = (tp2[0] - tp1[0]) * (tp3[1] - tp1[1]) - (tp2[1] - tp1[1]) * (tp3[0] - tp1[0])
            self.assertAlmostEqual(cross, 0.0, delta=1e-5)

    def test_area_scaling_law(self):
        """Area of unit square under transformation M must equal |det(M)|."""
        def polygon_area_2d(pts):
            n = len(pts)
            area = 0.0
            for i in range(n):
                j = (i + 1) % n
                area += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
            return abs(area) / 2.0

        for seed in (11, 22, 33, 44):
            pack = generate_matrix_pack(seed=seed)
            orig_area = polygon_area_2d(UNIT_SQUARE_VERTICES)
            self.assertAlmostEqual(orig_area, 1.0, places=5)

            # Transformed under A
            sq_a = transform_shape(pack.matrix_a, UNIT_SQUARE_VERTICES)
            area_a = polygon_area_2d(sq_a)
            self.assertAlmostEqual(area_a, abs(pack.det_a), delta=0.05)

            # Transformed under Shear H
            sq_h = transform_shape(pack.shear_matrix, UNIT_SQUARE_VERTICES)
            area_h = polygon_area_2d(sq_h)
            self.assertAlmostEqual(area_h, 1.0, delta=0.02)

            # Transformed under C = B @ A
            sq_c = transform_shape(pack.matrix_c, UNIT_SQUARE_VERTICES)
            area_c = polygon_area_2d(sq_c)
            self.assertAlmostEqual(area_c, abs(pack.det_c), delta=0.08)


if __name__ == "__main__":
    unittest.main()

