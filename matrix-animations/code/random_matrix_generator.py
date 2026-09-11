#!/usr/bin/env python3
"""Random matrix generator for linear algebra and space transformation animations.

Generates random, well-conditioned 2x2 matrices with:
- Scaling and shearing parameters
- Guaranteed real, distinct eigenvalues and orthogonal eigenvectors
- Secondary matrix B and composite product C = B @ A
- LaTeX and text representations for Manim MathTex and Matrix objects
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
import os
import random
import sys
import time
from typing import Any, Dict, List, Tuple


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
    # Matrix B
    phi_rad: float
    phi_deg: float
    matrix_b: list[list[float]]
    det_b: float
    # Product C = B @ A
    matrix_c: list[list[float]]
    det_c: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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

    # 2. Shear factor (horizontal or vertical)
    k_choices = [-1.2, -1.0, -0.8, -0.6, 0.6, 0.8, 1.0, 1.2]
    shear_k = rng.choice(k_choices)
    shear_axis = rng.choice(["x", "y"])
    if shear_axis == "x":
        H = [[1.0, shear_k], [0.0, 1.0]]
    else:
        H = [[1.0, 0.0], [shear_k, 1.0]]

    # 3. Matrix A with guaranteed real, distinct eigenvalues
    # Choose eigenvalues between 0.5 and 2.0 with gap >= 0.5
    eigen_pool = [0.5, 0.6, 0.7, 0.8, 1.2, 1.4, 1.6, 1.8, 2.0]
    l1 = rng.choice([1.3, 1.5, 1.7, 1.9, 2.0])  # Dominant eigenvalue
    l2 = rng.choice([0.5, 0.6, 0.7, 0.8])        # Smaller eigenvalue

    # Random angle between 22 and 68 degrees
    theta_deg = round(rng.uniform(22.0, 68.0), 1)
    theta_rad = math.radians(theta_deg)
    cos_t = math.cos(theta_rad)
    sin_t = math.sin(theta_rad)

    # Eigenvectors:
    # v1 = [cos, sin], v2 = [-sin, cos]
    v1 = [round(cos_t, 3), round(sin_t, 3)]
    v2 = [round(-sin_t, 3), round(cos_t, 3)]

    # A = P @ D @ P^T
    # [ [cos, -sin], [sin, cos] ] @ [ [l1, 0], [0, l2] ] @ [ [cos, sin], [-sin, cos] ]
    a11 = l1 * cos_t * cos_t + l2 * sin_t * sin_t
    a12 = (l1 - l2) * cos_t * sin_t
    a21 = a12
    a22 = l1 * sin_t * sin_t + l2 * cos_t * cos_t

    matrix_a = [[round(a11, 2), round(a12, 2)], [round(a21, 2), round(a22, 2)]]
    det_a = round(matrix_a[0][0] * matrix_a[1][1] - matrix_a[0][1] * matrix_a[1][0], 3)
    trace_a = round(matrix_a[0][0] + matrix_a[1][1], 3)

    # Non-eigenvector test vector w (oriented between v1 and v2, e.g. theta + 45 deg or [1, 0])
    w_angle = theta_rad + math.pi / 4.0
    test_w = [round(math.cos(w_angle) * 1.3, 2), round(math.sin(w_angle) * 1.3, 2)]

    # 4. Matrix B (secondary transformation: rotation by phi with mild scale)
    phi_deg = round(rng.uniform(25.0, 55.0) * rng.choice([-1, 1]), 1)
    phi_rad = math.radians(phi_deg)
    scale_b = rng.choice([0.8, 0.9, 1.0, 1.1])
    b11 = round(scale_b * math.cos(phi_rad), 2)
    b12 = round(-scale_b * math.sin(phi_rad), 2)
    b21 = round(scale_b * math.sin(phi_rad), 2)
    b22 = round(scale_b * math.cos(phi_rad), 2)
    matrix_b = [[b11, b12], [b21, b22]]
    det_b = round(matrix_b[0][0] * matrix_b[1][1] - matrix_b[0][1] * matrix_b[1][0], 3)

    # 5. Composite Matrix C = B @ A
    c11 = round(matrix_b[0][0] * matrix_a[0][0] + matrix_b[0][1] * matrix_a[1][0], 2)
    c12 = round(matrix_b[0][0] * matrix_a[0][1] + matrix_b[0][1] * matrix_a[1][1], 2)
    c21 = round(matrix_b[1][0] * matrix_a[0][0] + matrix_b[1][1] * matrix_a[1][0], 2)
    c22 = round(matrix_b[1][0] * matrix_a[0][1] + matrix_b[1][1] * matrix_a[1][1], 2)
    matrix_c = [[c11, c12], [c21, c22]]
    det_c = round(matrix_c[0][0] * matrix_c[1][1] - matrix_c[0][1] * matrix_c[1][0], 3)

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
