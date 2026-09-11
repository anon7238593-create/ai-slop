#!/usr/bin/env python3
"""Random matrix generator for linear algebra and space transformation animations.

Generates mathematically rigorous, well-conditioned 2D linear transformations with:
- Scaling and shearing parameters
- Guaranteed real, positive, distinct eigenvalues and orthogonal eigenvectors
- Non-rotating, well-conditioned planar secondary matrix B (vertical shear or combined stretch/shear)
- Product matrix C = B @ A composition
- Canonical geometry and transformed coordinates for Unit Square, Circle/Ellipse, Triangle/Asymmetric Polygon, and Basis Vectors
- Helper methods for point/shape transformation, ellipse axis/tilt calculation, and LaTeX MathTex rendering
- 100% reproducible generation via --seed
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import json
import math
import os
import random
import sys
import time
from typing import Any, Dict, List, Tuple


# =====================================================================
# Canonical Multi-Shape Geometries in Base Coordinates
# =====================================================================

# 1. Unit Square: 4 vertices [(0, 0), (1, 0), (1, 1), (0, 1)]
UNIT_SQUARE_VERTICES: list[list[float]] = [
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.0, 1.0],
]

# 2. Triangle / Asymmetric Polygon: [(0, 0), (1.2, 0.2), (0.4, 1.0)]
# Demonstrates preservation of straight lines, parallelism, and skewing without reflection
ASYMMETRIC_TRIANGLE_VERTICES: list[list[float]] = [
    [0.0, 0.0],
    [1.2, 0.2],
    [0.4, 1.0],
]

# 3. Canonical Basis Vectors (unit length 1.0)
BASIS_VECTORS: dict[str, list[float]] = {
    "i_hat": [1.0, 0.0],
    "j_hat": [0.0, 1.0],
}


def sample_unit_circle(num_samples: int = 64) -> list[list[float]]:
    """Sample perimeter points of the canonical unit circle x^2 + y^2 = 1.0."""
    pts: list[list[float]] = []
    for i in range(num_samples):
        theta = 2.0 * math.pi * i / num_samples
        pts.append([round(math.cos(theta), 4), round(math.sin(theta), 4)])
    return pts


def get_canonical_shapes(circle_samples: int = 64) -> dict[str, Any]:
    """Return dictionary of canonical 2D geometric shapes in base coordinates."""
    return {
        "unit_square": [list(pt) for pt in UNIT_SQUARE_VERTICES],
        "triangle": [list(pt) for pt in ASYMMETRIC_TRIANGLE_VERTICES],
        "basis_vectors": {
            "i_hat": list(BASIS_VECTORS["i_hat"]),
            "j_hat": list(BASIS_VECTORS["j_hat"]),
        },
        "unit_circle": {
            "radius": 1.0,
            "center": [0.0, 0.0],
            "sample_points": sample_unit_circle(circle_samples),
        },
    }


# =====================================================================
# Core Geometric & Linear Algebra Transformations
# =====================================================================

def transform_point(matrix: list[list[float]], pt: list[float] | tuple[float, float]) -> list[float]:
    """Transform a 2D point [x, y] using a 2x2 matrix: pt' = M @ pt."""
    x = float(matrix[0][0] * pt[0] + matrix[0][1] * pt[1])
    y = float(matrix[1][0] * pt[0] + matrix[1][1] * pt[1])
    return [round(x, 4), round(y, 4)]


def transform_shape(matrix: list[list[float]], pts: list[Any]) -> list[list[float]]:
    """Transform a list of 2D points [[x, y], ...] under a 2x2 matrix."""
    return [transform_point(matrix, pt) for pt in pts]


def get_ellipse_parameters(matrix: list[list[float]]) -> dict[str, Any]:
    """Calculate semi-major axis, semi-minor axis, and tilt angle of transformed unit circle.

    A unit circle under 2D linear transformation M maps to an ellipse defined by:
    v^T (M M^T)^(-1) v = 1.
    The semi-major and semi-minor axes correspond to singular values of M (square roots of
    eigenvalues of K = M @ M^T).
    The tilt angle is the orientation of the principal eigenvector of K.
    """
    m11, m12 = matrix[0][0], matrix[0][1]
    m21, m22 = matrix[1][0], matrix[1][1]

    # K = M @ M^T = [[E, F], [F, G]]
    E = m11 * m11 + m12 * m12
    F = m11 * m21 + m12 * m22
    G = m21 * m21 + m22 * m22

    trace_k = E + G
    discriminant = max(0.0, (E - G) ** 2 + 4.0 * F * F)
    sqrt_disc = math.sqrt(discriminant)

    mu1 = (trace_k + sqrt_disc) / 2.0
    mu2 = max(0.0, (trace_k - sqrt_disc) / 2.0)

    semi_major = math.sqrt(max(0.0, mu1))
    semi_minor = math.sqrt(max(0.0, mu2))

    # Orientation of major axis
    tilt_rad = 0.5 * math.atan2(2.0 * F, E - G)
    tilt_deg = math.degrees(tilt_rad)

    eccentricity = 0.0
    if semi_major > 1e-9:
        eccentricity = math.sqrt(max(0.0, 1.0 - (semi_minor / semi_major) ** 2))

    major_vec = [round(semi_major * math.cos(tilt_rad), 4), round(semi_major * math.sin(tilt_rad), 4)]
    minor_vec = [round(-semi_minor * math.sin(tilt_rad), 4), round(semi_minor * math.cos(tilt_rad), 4)]

    return {
        "semi_major_axis": round(semi_major, 4),
        "semi_minor_axis": round(semi_minor, 4),
        "tilt_angle_rad": round(tilt_rad, 4),
        "tilt_angle_deg": round(tilt_deg, 2),
        "area": round(math.pi * semi_major * semi_minor, 4),
        "eccentricity": round(eccentricity, 4),
        "singular_values": [round(semi_major, 4), round(semi_minor, 4)],
        "major_axis_vector": major_vec,
        "minor_axis_vector": minor_vec,
    }


def transform_all_shapes(matrix: list[list[float]], circle_samples: int = 64) -> dict[str, Any]:
    """Compute geometric transformations of all canonical shapes under a 2x2 matrix."""
    canonical = get_canonical_shapes(circle_samples)
    return {
        "unit_square": transform_shape(matrix, canonical["unit_square"]),
        "triangle": transform_shape(matrix, canonical["triangle"]),
        "basis_vectors": {
            "i_hat": transform_point(matrix, canonical["basis_vectors"]["i_hat"]),
            "j_hat": transform_point(matrix, canonical["basis_vectors"]["j_hat"]),
        },
        "unit_circle": {
            "ellipse_parameters": get_ellipse_parameters(matrix),
            "sample_points": transform_shape(matrix, canonical["unit_circle"]["sample_points"]),
        },
    }


# =====================================================================
# LaTeX MathTex Formatting Helpers
# =====================================================================

def format_latex_num(val: float, precision: int = 2) -> str:
    """Format a float value cleanly for LaTeX MathTex, avoiding -0.00."""
    if abs(val) < 1e-9:
        val = 0.0
    formatted = f"{val:.{precision}f}"
    if formatted in ("-0.0", "-0.00", "-0"):
        formatted = f"{0.0:.{precision}f}"
    return formatted


def matrix_to_latex(mat: list[list[float]], precision: int = 2) -> str:
    """Format a 2x2 matrix as a LaTeX bmatrix string."""
    r0 = f"{format_latex_num(mat[0][0], precision)} & {format_latex_num(mat[0][1], precision)}"
    r1 = f"{format_latex_num(mat[1][0], precision)} & {format_latex_num(mat[1][1], precision)}"
    return rf"\begin{{bmatrix}} {r0} \\ {r1} \end{{bmatrix}}"


def vector_to_latex(vec: list[float], precision: int = 2) -> str:
    """Format a 2D vector as a LaTeX column bmatrix string."""
    return rf"\begin{{bmatrix}} {format_latex_num(vec[0], precision)} \\ {format_latex_num(vec[1], precision)} \end{{bmatrix}}"


# =====================================================================
# MatrixPack Data Model & Generation
# =====================================================================

@dataclass
class MatrixPack:
    seed: int
    # Scaling
    scale_x: float
    scale_y: float
    scale_matrix: list[list[float]]
    # Shear
    shear_k: float
    shear_axis: str  # "x" or "y"
    shear_matrix: list[list[float]]
    # Matrix A with Eigenvalues/Eigenvectors
    lambda_1: float
    lambda_2: float
    v1: list[float]
    v2: list[float]
    theta_rad: float
    theta_deg: float
    matrix_a: list[list[float]]
    det_a: float
    trace_a: float
    test_vector_w: list[float]
    # Matrix B (planar stretch / shear, no artificial z-axis rotation)
    phi_rad: float
    phi_deg: float
    matrix_b: list[list[float]]
    det_b: float
    # Product C = B @ A
    matrix_c: list[list[float]]
    det_c: float
    # Additional B descriptors
    b_mode: str = "vertical_shear"
    b_scale_x: float = 1.0
    b_scale_y: float = 1.0
    b_shear_k: float = 0.0
    b_description: str = ""
    # Geometric shapes (canonical and transformed)
    canonical_shapes: dict[str, Any] = field(default_factory=dict)
    transformed_shapes_a: dict[str, Any] = field(default_factory=dict)
    transformed_shapes_b: dict[str, Any] = field(default_factory=dict)
    transformed_shapes_c: dict[str, Any] = field(default_factory=dict)
    # Ellipse parameters for unit circle transformation
    ellipse_a: dict[str, Any] = field(default_factory=dict)
    ellipse_b: dict[str, Any] = field(default_factory=dict)
    ellipse_c: dict[str, Any] = field(default_factory=dict)
    # LaTeX strings for MathTex
    latex_matrix_a: str = ""
    latex_matrix_b: str = ""
    latex_matrix_c: str = ""
    latex_scale_matrix: str = ""
    latex_shear_matrix: str = ""
    latex_eigenvalues: str = ""
    latex_eigen_equation_1: str = ""
    latex_eigen_equation_2: str = ""
    latex_product_formula: str = ""
    latex_manifest: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def transform_point(self_or_matrix: Any, matrix_or_pt: Any = None, pt: Any = None) -> list[float]:
        """Transform a point pt [x, y].

        Usage:
            pack.transform_point(matrix, pt)
            pack.transform_point(pt)  # defaults to pack.matrix_a
            MatrixPack.transform_point(matrix, pt)
        """
        if isinstance(self_or_matrix, MatrixPack):
            if pt is not None:
                mat = matrix_or_pt
                target_pt = pt
            elif matrix_or_pt is not None:
                mat = self_or_matrix.matrix_a
                target_pt = matrix_or_pt
            else:
                raise ValueError("Expected pt or (matrix, pt)")
        else:
            mat = self_or_matrix
            target_pt = matrix_or_pt
        return transform_point(mat, target_pt)

    def transform_shape(self_or_matrix: Any, matrix_or_pts: Any = None, pts: Any = None) -> list[list[float]]:
        """Transform multiple points [[x, y], ...].

        Usage:
            pack.transform_shape(matrix, pts)
            pack.transform_shape(pts)  # defaults to pack.matrix_a
            MatrixPack.transform_shape(matrix, pts)
        """
        if isinstance(self_or_matrix, MatrixPack):
            if pts is not None:
                mat = matrix_or_pts
                target_pts = pts
            elif matrix_or_pts is not None:
                mat = self_or_matrix.matrix_a
                target_pts = matrix_or_pts
            else:
                raise ValueError("Expected pts or (matrix, pts)")
        else:
            mat = self_or_matrix
            target_pts = matrix_or_pts
        return transform_shape(mat, target_pts)

    def get_ellipse_parameters(self_or_matrix: Any, matrix: list[list[float]] | None = None) -> dict[str, Any]:
        """Calculate semi-major, semi-minor, and tilt angle of transformed unit circle.

        Usage:
            pack.get_ellipse_parameters(matrix)
            pack.get_ellipse_parameters()  # defaults to pack.matrix_a
            MatrixPack.get_ellipse_parameters(matrix)
        """
        if isinstance(self_or_matrix, MatrixPack):
            mat = matrix if matrix is not None else self_or_matrix.matrix_a
        else:
            mat = self_or_matrix
        return get_ellipse_parameters(mat)

    def get_matrix_latex(self, which: str = "A", precision: int = 2) -> str:
        """Return LaTeX bmatrix representation for specified matrix ('A', 'B', 'C', 'S', 'H')."""
        w = which.upper()
        if w == "A":
            return matrix_to_latex(self.matrix_a, precision)
        elif w == "B":
            return matrix_to_latex(self.matrix_b, precision)
        elif w == "C":
            return matrix_to_latex(self.matrix_c, precision)
        elif w in ("S", "SCALE"):
            return matrix_to_latex(self.scale_matrix, precision)
        elif w in ("H", "SHEAR"):
            return matrix_to_latex(self.shear_matrix, precision)
        else:
            raise ValueError(f"Unknown matrix identifier '{which}'. Choose 'A', 'B', 'C', 'S', or 'H'.")

    def get_latex_manifest(self) -> dict[str, str]:
        """Return dictionary of all LaTeX MathTex formulas and snippets."""
        return dict(self.latex_manifest)


def generate_matrix_pack(seed: int | None = None) -> MatrixPack:
    """Generate a randomized, well-conditioned transformation pack."""
    if seed is None:
        seed = int(time.time() * 1000) ^ (os.getpid() << 16) ^ random.randint(1, 1_000_000)
    rng = random.Random(seed)

    # 1. Scaling factors (distinct and readable)
    scale_choices = [0.6, 0.7, 0.8, 1.3, 1.4, 1.5, 1.6, 1.8]
    s_x = rng.choice(scale_choices)
    s_y = rng.choice([v for v in scale_choices if abs(v - s_x) >= 0.4])
    S = [[s_x, 0.0], [0.0, s_y]]

    # 2. Shear factor (horizontal or vertical, det = 1.0)
    k_choices = [-1.2, -1.0, -0.8, -0.6, 0.6, 0.8, 1.0, 1.2]
    shear_k = rng.choice(k_choices)
    shear_axis = rng.choice(["x", "y"])
    if shear_axis == "x":
        H = [[1.0, shear_k], [0.0, 1.0]]
    else:
        H = [[1.0, 0.0], [shear_k, 1.0]]

    # 3. Matrix A: Invertible, well-conditioned matrix with real positive eigenvalues
    # (lambda_1, lambda_2) and orthogonal eigenvectors v1, v2.
    # A = P @ D @ P^T where P is an orthogonal matrix with orientation angle theta.
    # Determinant guaranteed between 0.8 and 2.5.
    eigen_dominant = [1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    eigen_smaller = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
    l1 = rng.choice(eigen_dominant)
    valid_l2 = [v for v in eigen_smaller if (l1 - v >= 0.4) and (0.8 <= l1 * v <= 2.5)]
    l2 = rng.choice(valid_l2 if valid_l2 else [0.7])

    theta_deg = round(rng.uniform(22.0, 68.0), 1)
    theta_rad = math.radians(theta_deg)
    cos_t = math.cos(theta_rad)
    sin_t = math.sin(theta_rad)

    # Orthonormal eigenvectors
    v1 = [round(cos_t, 3), round(sin_t, 3)]
    v2 = [round(-sin_t, 3), round(cos_t, 3)]

    # A = P @ D @ P^T
    a11 = l1 * cos_t * cos_t + l2 * sin_t * sin_t
    a12 = (l1 - l2) * cos_t * sin_t
    a21 = a12
    a22 = l1 * sin_t * sin_t + l2 * cos_t * cos_t

    matrix_a = [[round(a11, 2), round(a12, 2)], [round(a21, 2), round(a22, 2)]]
    det_a = round(matrix_a[0][0] * matrix_a[1][1] - matrix_a[0][1] * matrix_a[1][0], 3)
    trace_a = round(matrix_a[0][0] + matrix_a[1][1], 3)

    # Non-eigenvector test vector w (oriented between v1 and v2)
    w_angle = theta_rad + math.pi / 4.0
    test_w = [round(math.cos(w_angle) * 1.3, 2), round(math.sin(w_angle) * 1.3, 2)]

    # 4. Matrix B: Second planar transformation (e.g. vertical shear or combined stretch/shear)
    # with positive determinant between 0.8 and 1.5 that does NOT artificially spin space!
    b_mode = rng.choice(["vertical_shear", "stretch_shear", "horizontal_shear"])
    scale_b_choices = [0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2]
    s_bx = rng.choice(scale_b_choices)
    valid_s_by = [v for v in scale_b_choices if 0.8 <= s_bx * v <= 1.5]
    s_by = rng.choice(valid_s_by if valid_s_by else [1.0])
    shear_pool = [-0.6, -0.5, -0.4, -0.3, 0.3, 0.4, 0.5, 0.6]
    k_shear = rng.choice(shear_pool)

    if b_mode == "vertical_shear":
        b11, b12 = s_bx, 0.0
        b21, b22 = k_shear, s_by
        b_desc = f"Vertical shear (k={k_shear}) with mild scale ({s_bx}x, {s_by}x)"
    elif b_mode == "horizontal_shear":
        b11, b12 = s_bx, k_shear
        b21, b22 = 0.0, s_by
        b_desc = f"Horizontal shear (k={k_shear}) with mild scale ({s_bx}x, {s_by}x)"
    else:  # stretch_shear
        k1 = rng.choice([-0.3, -0.2, 0.2, 0.3])
        k2 = rng.choice([-0.2, 0.0, 0.2])
        det_trial = s_bx * s_by - k1 * k2
        if 0.8 <= det_trial <= 1.5:
            b11, b12 = s_bx, k1
            b21, b22 = k2, s_by
        else:
            b11, b12 = s_bx, 0.0
            b21, b22 = k_shear, s_by
        b_desc = f"Combined stretch/shear [({s_bx}, {b12}), ({b21}, {s_by})]"

    matrix_b = [[round(b11, 2), round(b12, 2)], [round(b21, 2), round(b22, 2)]]
    det_b = round(matrix_b[0][0] * matrix_b[1][1] - matrix_b[0][1] * matrix_b[1][0], 3)

    # Backwards compatibility: phi is 0.0 (no artificial z-axis rotation)
    phi_rad = 0.0
    phi_deg = 0.0

    # 5. Composite Matrix C = B @ A
    c11 = round(matrix_b[0][0] * matrix_a[0][0] + matrix_b[0][1] * matrix_a[1][0], 2)
    c12 = round(matrix_b[0][0] * matrix_a[0][1] + matrix_b[0][1] * matrix_a[1][1], 2)
    c21 = round(matrix_b[1][0] * matrix_a[0][0] + matrix_b[1][1] * matrix_a[1][0], 2)
    c22 = round(matrix_b[1][0] * matrix_a[0][1] + matrix_b[1][1] * matrix_a[1][1], 2)
    matrix_c = [[c11, c12], [c21, c22]]
    det_c = round(matrix_c[0][0] * matrix_c[1][1] - matrix_c[0][1] * matrix_c[1][0], 3)

    # 6. Geometric shape representations and transformations
    canonical_shapes = get_canonical_shapes(64)
    shapes_a = transform_all_shapes(matrix_a, 64)
    shapes_b = transform_all_shapes(matrix_b, 64)
    shapes_c = transform_all_shapes(matrix_c, 64)

    ellipse_a = get_ellipse_parameters(matrix_a)
    ellipse_b = get_ellipse_parameters(matrix_b)
    ellipse_c = get_ellipse_parameters(matrix_c)

    # 7. LaTeX MathTex representations
    latex_a = matrix_to_latex(matrix_a)
    latex_b = matrix_to_latex(matrix_b)
    latex_c = matrix_to_latex(matrix_c)
    latex_s = matrix_to_latex(S)
    latex_h = matrix_to_latex(H)
    latex_eigen_eq1 = rf"A \vec{{v}}_1 = {format_latex_num(l1)} \vec{{v}}_1"
    latex_eigen_eq2 = rf"A \vec{{v}}_2 = {format_latex_num(l2)} \vec{{v}}_2"
    latex_eigenvals = rf"\lambda_1 = {format_latex_num(l1)}, \quad \lambda_2 = {format_latex_num(l2)}"
    latex_prod = rf"{latex_b} \cdot {latex_a} = {latex_c}"

    manifest = {
        "matrix_a": latex_a,
        "matrix_b": latex_b,
        "matrix_c": latex_c,
        "scale_matrix": latex_s,
        "shear_matrix": latex_h,
        "eigenvalues": latex_eigenvals,
        "eigen_equation_1": latex_eigen_eq1,
        "eigen_equation_2": latex_eigen_eq2,
        "product_formula": latex_prod,
        "det_a": rf"\det(A) = {format_latex_num(det_a, 3)}",
        "det_b": rf"\det(B) = {format_latex_num(det_b, 3)}",
        "det_c": rf"\det(C) = {format_latex_num(det_c, 3)}",
    }

    return MatrixPack(
        seed=seed,
        scale_x=s_x,
        scale_y=s_y,
        scale_matrix=S,
        shear_k=shear_k,
        shear_axis=shear_axis,
        shear_matrix=H,
        lambda_1=l1,
        lambda_2=l2,
        v1=v1,
        v2=v2,
        theta_rad=theta_rad,
        theta_deg=theta_deg,
        matrix_a=matrix_a,
        det_a=det_a,
        trace_a=trace_a,
        test_vector_w=test_w,
        phi_rad=phi_rad,
        phi_deg=phi_deg,
        matrix_b=matrix_b,
        det_b=det_b,
        matrix_c=matrix_c,
        det_c=det_c,
        b_mode=b_mode,
        b_scale_x=s_bx,
        b_scale_y=s_by,
        b_shear_k=k_shear if b_mode != "stretch_shear" else b12,
        b_description=b_desc,
        canonical_shapes=canonical_shapes,
        transformed_shapes_a=shapes_a,
        transformed_shapes_b=shapes_b,
        transformed_shapes_c=shapes_c,
        ellipse_a=ellipse_a,
        ellipse_b=ellipse_b,
        ellipse_c=ellipse_c,
        latex_matrix_a=latex_a,
        latex_matrix_b=latex_b,
        latex_matrix_c=latex_c,
        latex_scale_matrix=latex_s,
        latex_shear_matrix=latex_h,
        latex_eigenvalues=latex_eigenvals,
        latex_eigen_equation_1=latex_eigen_eq1,
        latex_eigen_equation_2=latex_eigen_eq2,
        latex_product_formula=latex_prod,
        latex_manifest=manifest,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate random matrix configuration pack.")
    parser.add_argument("--seed", type=int, help="integer seed for reproducible generation")
    parser.add_argument("--output", type=str, help="optional path to save JSON manifest")
    args = parser.parse_args()

    pack = generate_matrix_pack(args.seed)
    data = pack.to_dict()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Matrix pack saved to {args.output}")
    else:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
