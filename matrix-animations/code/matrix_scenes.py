#!/usr/bin/env python3
"""Manim animation scenes visualizing linear transformations and matrix multiplication.

Demonstrates:
1. Space Transformations: Pure 2D Scaling, Shearing, and General Stretching
   - Multi-shape deformation: Unit Square, Unit Circle (ellipse), Asymmetric Triangle, Basis Vectors
2. Eigenvectors & Eigenvalues: Invariant directions that scale without rotating (A*v = lambda*v)
   - Unit circle transforming into an ellipse whose principal axes align with eigenvectors
3. Matrix Multiplication: Composition of transformations (A then B vs single product C = B @ A)
   - Multi-shape composition, ghost outlines preserved, exact coincidence on direct product map
4. Master Story: Combined cinematic educational presentation

All parameters and matrices are mathematically consistent, 1.0 unit = 1 grid spacing,
with pure 2D planar maps and zero unneeded z-axis rotations.
"""

from __future__ import annotations

import dataclasses
import json
import math
import os
from pathlib import Path
import sys

from manim import *
import numpy as np

# Add parent/current directory to path to import random_matrix_generator
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from random_matrix_generator import (
    MatrixPack,
    format_latex_num,
    generate_matrix_pack,
    matrix_to_latex,
    vector_to_latex,
)


def get_current_matrix_pack() -> MatrixPack:
    """Retrieve or generate the matrix configuration for the current scene run."""
    config_file = current_dir / "matrix_config.json"
    env_seed = os.environ.get("MATRIX_ANIM_SEED")

    if env_seed is not None:
        try:
            return generate_matrix_pack(int(env_seed))
        except ValueError:
            pass

    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                field_names = {f.name for f in dataclasses.fields(MatrixPack)}
                filtered_data = {k: v for k, v in data.items() if k in field_names}
                return MatrixPack(**filtered_data)
        except Exception:
            pass

    return generate_matrix_pack(None)


# Visual Styling Constants
COLOR_I_HAT = "#10B981"         # Emerald Green for basis vector i-hat
COLOR_J_HAT = "#EF4444"         # Crimson Red for basis vector j-hat
COLOR_SQUARE = YELLOW           # Yellow for Unit Square
COLOR_CIRCLE = "#06B6D4"        # Electric Cyan for Unit Circle
COLOR_TRIANGLE = "#A855F7"      # Vivid Purple for Asymmetric Triangle
COLOR_V1 = "#F59E0B"            # Radiant Gold for Eigenvector 1
COLOR_V2 = "#06B6D4"            # Electric Cyan for Eigenvector 2
COLOR_TEST_VEC = "#EC4899"      # Hot Pink for non-eigenvector test vector
COLOR_PANEL_BG = "#0B0F19"      # Dark slate HUD banner background
COLOR_PANEL_BORDER = "#334155"  # Slate border for HUD panels


# =====================================================================
# Geometry and HUD Helpers
# =====================================================================

def create_coordinate_plane() -> NumberPlane:
    """Create coordinate plane with exact 1.0 unit spacing matching basis vectors."""
    return NumberPlane(
        x_range=[-8, 8, 1],
        y_range=[-5, 5, 1],
        background_line_style={"stroke_color": TEAL_E, "stroke_width": 1.2, "stroke_opacity": 0.40},
        faded_line_style={"stroke_color": TEAL_E, "stroke_width": 0.6, "stroke_opacity": 0.18},
    )


def create_basis_vectors() -> tuple[Arrow, Arrow, MathTex, MathTex]:
    """Create canonical basis vectors i-hat and j-hat of exact length 1.0."""
    i_hat = Arrow(
        ORIGIN, RIGHT, buff=0, color=COLOR_I_HAT,
        stroke_width=4.5, max_tip_length_to_length_ratio=0.22
    )
    j_hat = Arrow(
        ORIGIN, UP, buff=0, color=COLOR_J_HAT,
        stroke_width=4.5, max_tip_length_to_length_ratio=0.22
    )
    i_label = MathTex(r"\hat{i}", color=COLOR_I_HAT, font_size=24).next_to(RIGHT, DOWN, buff=0.12)
    j_label = MathTex(r"\hat{j}", color=COLOR_J_HAT, font_size=24).next_to(UP, LEFT, buff=0.12)
    return i_hat, j_hat, i_label, j_label


def create_shape_ensemble() -> tuple[Polygon, Circle, Polygon]:
    """Create canonical unit scale geometric probes:

    1. Unit Square [0,1]x[0,1]
    2. Unit Circle radius=1.0 centered at origin
    3. Asymmetric Triangle [(0,0), (1.2, 0.2), (0.4, 1.0)]
    """
    unit_square = Polygon(
        ORIGIN, RIGHT, RIGHT + UP, UP,
        color=COLOR_SQUARE, fill_color=COLOR_SQUARE, fill_opacity=0.25,
        stroke_color=YELLOW_D, stroke_width=2.5
    )
    unit_circle = Circle(
        radius=1.0, color=COLOR_CIRCLE, fill_color=COLOR_CIRCLE, fill_opacity=0.20,
        stroke_color="#38BDF8", stroke_width=2.5
    )
    triangle = Polygon(
        ORIGIN, np.array([1.2, 0.2, 0.0]), np.array([0.4, 1.0, 0.0]),
        color=COLOR_TRIANGLE, fill_color=COLOR_TRIANGLE, fill_opacity=0.25,
        stroke_color="#C084FC", stroke_width=2.5
    )
    return unit_square, unit_circle, triangle


def mat_vec_mul(matrix: list[list[float]] | np.ndarray, vec: list[float] | np.ndarray) -> np.ndarray:
    """Multiply 2D vector by 2x2 matrix and return 3D vector with z=0."""
    x = float(matrix[0][0] * vec[0] + matrix[0][1] * vec[1])
    y = float(matrix[1][0] * vec[0] + matrix[1][1] * vec[1])
    return np.array([x, y, 0.0])


def get_label_pos(v_end: np.ndarray, label_type: str = "i") -> np.ndarray:
    """Dynamically determine non-overlapping label position for a transformed vector."""
    if label_type == "i":
        offset = np.array([0.16, -0.18, 0.0]) if v_end[1] >= -0.05 else np.array([0.16, 0.18, 0.0])
    elif label_type == "j":
        offset = np.array([-0.20, 0.16, 0.0]) if v_end[0] >= -0.05 else np.array([0.20, 0.16, 0.0])
    elif label_type == "v1":
        offset = np.array([0.18, 0.18, 0.0])
    elif label_type == "v2":
        offset = np.array([-0.18, 0.18, 0.0])
    else:  # "w"
        offset = np.array([0.22, 0.02, 0.0])
    return v_end + offset


def create_hud_card(
    title: str,
    subtitle: str | None = None,
    formula: Mobject | None = None,
    extra_text: str | None = None,
    title_color: str = BLUE_C,
    font_scale: float = 0.88,
) -> VGroup:
    """Create a high-contrast HUD card enclosed with BackgroundRectangle."""
    elements: list[Mobject] = [
        Text(title, font_size=int(16 * font_scale), weight=BOLD, color=title_color)
    ]
    if subtitle:
        elements.append(Text(subtitle, font_size=int(13 * font_scale), color=LIGHT_GRAY))
    if formula:
        elements.append(formula)
    if extra_text:
        if any(tok in extra_text for tok in ["\\", "\\det", "\\lambda", "\\text", "\\quad", "_", "^"]):
            elements.append(MathTex(extra_text, font_size=int(16 * font_scale), color=YELLOW_B))
        else:
            elements.append(Text(extra_text, font_size=int(12 * font_scale), color=YELLOW_B))

    content = VGroup(*elements).arrange(DOWN, aligned_edge=LEFT, buff=0.10 * font_scale)
    bg = BackgroundRectangle(
        content,
        color=COLOR_PANEL_BG,
        fill_opacity=0.92,
        buff=0.18,
        stroke_width=1.0,
        stroke_color=COLOR_PANEL_BORDER,
    )
    return VGroup(bg, content)


# =====================================================================
# Scene 1: Space Transformations
# =====================================================================

class SpaceTransformationsScene(Scene):
    """Act 1: Pure 2D Planar Scaling, Shearing, and General Transformation."""

    def construct(self):
        pack = get_current_matrix_pack()

        # Title Card
        title = Text("Linear Transformations: How Space Transforms", font_size=24, weight=BOLD, color=WHITE).to_edge(UP, buff=0.20)
        subtitle = Text(f"Random Seed: {pack.seed}  •  Multi-Shape Deformation & Basis Vectors", font_size=14, color=GRAY).next_to(title, DOWN, buff=0.08)
        title_group = VGroup(title, subtitle)
        self.play(FadeIn(title_group), run_time=1.0)
        self.wait(0.4)

        # Coordinate Plane
        plane = create_coordinate_plane()
        self.play(Create(plane), run_time=1.2)

        # Canonical Multi-Shapes and Basis Vectors
        unit_square, unit_circle, triangle = create_shape_ensemble()
        i_hat, j_hat, i_label, j_label = create_basis_vectors()

        # Shape Legend
        legend_content = VGroup(
            Text("Geometric Probes:", font_size=14, weight=BOLD, color=WHITE),
            Text("• Unit Square (Yellow): Area & Parallelogram Shear", font_size=11, color=YELLOW),
            Text("• Unit Circle (Cyan): Curvature & Ellipse Axes", font_size=11, color=COLOR_CIRCLE),
            Text("• Triangle (Purple): Collinearity & Asymmetry", font_size=11, color=COLOR_TRIANGLE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
        legend_bg = BackgroundRectangle(legend_content, color=COLOR_PANEL_BG, fill_opacity=0.88, buff=0.16, stroke_width=1, stroke_color=COLOR_PANEL_BORDER)
        legend_card = VGroup(legend_bg, legend_content).next_to(title_group, DOWN, buff=0.15).to_edge(RIGHT, buff=0.35)

        self.play(
            FadeIn(unit_square),
            FadeIn(unit_circle),
            FadeIn(triangle),
            GrowArrow(i_hat), FadeIn(i_label),
            GrowArrow(j_hat), FadeIn(j_label),
            FadeIn(legend_card),
            run_time=1.4
        )
        self.wait(1.0)
        self.play(FadeOut(legend_card), run_time=0.5)

        # -------------------------------------------------------------
        # Part A: Scaling Transformation
        # -------------------------------------------------------------
        scale_mat = pack.scale_matrix
        det_s = pack.scale_x * pack.scale_y
        scale_card = create_hud_card(
            title="1. Scaling Transformation (Matrix S)",
            subtitle=f"Stretch x by {pack.scale_x:.2f}x, y by {pack.scale_y:.2f}x",
            formula=MathTex(r"S = " + pack.latex_scale_matrix, font_size=21, color=YELLOW),
            extra_text=f"det(S) = {det_s:.2f} (Area Scaling Multiplier)",
            title_color=BLUE_C,
        ).next_to(title_group, DOWN, buff=0.15).to_edge(LEFT, buff=0.35)

        self.play(FadeIn(scale_card), run_time=0.8)

        new_i_scale = mat_vec_mul(scale_mat, [1.0, 0.0])
        new_j_scale = mat_vec_mul(scale_mat, [0.0, 1.0])

        obs_a_text = Text(f"Circle stretches into an axis-aligned ellipse! Area multiplied by {det_s:.2f}x.", font_size=15, color=YELLOW_A)
        obs_a_bg = BackgroundRectangle(obs_a_text, color=COLOR_PANEL_BG, fill_opacity=0.9, buff=0.15)
        obs_a = VGroup(obs_a_bg, obs_a_text).to_edge(DOWN, buff=0.35)

        self.play(
            plane.animate.apply_matrix(scale_mat),
            unit_square.animate.apply_matrix(scale_mat),
            unit_circle.animate.apply_matrix(scale_mat),
            triangle.animate.apply_matrix(scale_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, new_i_scale),
            j_hat.animate.put_start_and_end_on(ORIGIN, new_j_scale),
            i_label.animate.move_to(get_label_pos(new_i_scale, "i")),
            j_label.animate.move_to(get_label_pos(new_j_scale, "j")),
            FadeIn(obs_a),
            run_time=2.2
        )
        self.wait(1.5)

        # Reset smoothly back to identity with S^(-1)
        inv_scale = np.linalg.inv(np.array(scale_mat)).tolist()
        self.play(
            plane.animate.apply_matrix(inv_scale),
            unit_square.animate.apply_matrix(inv_scale),
            unit_circle.animate.apply_matrix(inv_scale),
            triangle.animate.apply_matrix(inv_scale),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP),
            i_label.animate.move_to(get_label_pos(RIGHT, "i")),
            j_label.animate.move_to(get_label_pos(UP, "j")),
            FadeOut(scale_card), FadeOut(obs_a),
            run_time=1.5
        )
        self.wait(0.4)

        # -------------------------------------------------------------
        # Part B: Shearing Transformation
        # -------------------------------------------------------------
        shear_mat = pack.shear_matrix
        shear_card = create_hud_card(
            title="2. Shearing Transformation (Matrix H)",
            subtitle=f"Shear along {pack.shear_axis}-axis by factor k = {pack.shear_k:.2f}",
            formula=MathTex(r"H = " + pack.latex_shear_matrix, font_size=21, color=PURPLE_A),
            extra_text=r"\det(H) = 1.00 \text{ (Area Strictly Preserved!)}",
            title_color=PURPLE_B,
        ).next_to(title_group, DOWN, buff=0.15).to_edge(LEFT, buff=0.35)

        self.play(FadeIn(shear_card), run_time=0.8)

        new_i_shear = mat_vec_mul(shear_mat, [1.0, 0.0])
        new_j_shear = mat_vec_mul(shear_mat, [0.0, 1.0])

        obs_b_text = Text("Square tilts to parallelogram, circle to tilted ellipse — Area is 100% PRESERVED!", font_size=14, color=PURPLE_A)
        obs_b_bg = BackgroundRectangle(obs_b_text, color=COLOR_PANEL_BG, fill_opacity=0.9, buff=0.15)
        obs_b = VGroup(obs_b_bg, obs_b_text).to_edge(DOWN, buff=0.35)

        self.play(
            plane.animate.apply_matrix(shear_mat),
            unit_square.animate.apply_matrix(shear_mat),
            unit_circle.animate.apply_matrix(shear_mat),
            triangle.animate.apply_matrix(shear_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, new_i_shear),
            j_hat.animate.put_start_and_end_on(ORIGIN, new_j_shear),
            i_label.animate.move_to(get_label_pos(new_i_shear, "i")),
            j_label.animate.move_to(get_label_pos(new_j_shear, "j")),
            FadeIn(obs_b),
            run_time=2.2
        )
        self.wait(1.5)

        # Reset smoothly back to identity with H^(-1)
        inv_shear = np.linalg.inv(np.array(shear_mat)).tolist()
        self.play(
            plane.animate.apply_matrix(inv_shear),
            unit_square.animate.apply_matrix(inv_shear),
            unit_circle.animate.apply_matrix(inv_shear),
            triangle.animate.apply_matrix(inv_shear),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP),
            i_label.animate.move_to(get_label_pos(RIGHT, "i")),
            j_label.animate.move_to(get_label_pos(UP, "j")),
            FadeOut(shear_card), FadeOut(obs_b),
            run_time=1.5
        )
        self.wait(0.4)

        # -------------------------------------------------------------
        # Part C: General Linear Transformation (Matrix A)
        # -------------------------------------------------------------
        mat_a = pack.matrix_a
        general_card = create_hud_card(
            title="3. General Linear Transformation (Matrix A)",
            subtitle="Matrix columns dictate where basis vectors land!",
            formula=MathTex(r"A = " + pack.latex_matrix_a, font_size=21, color=GOLD_A),
            extra_text=rf"\det(A) = {pack.det_a:.2f}, \quad \text{{Trace}} = {pack.trace_a:.2f}",
            title_color=GOLD_B,
        ).next_to(title_group, DOWN, buff=0.15).to_edge(LEFT, buff=0.35)

        self.play(FadeIn(general_card), run_time=0.8)

        new_i_a = mat_vec_mul(mat_a, [1.0, 0.0])
        new_j_a = mat_vec_mul(mat_a, [0.0, 1.0])

        obs_c_formula = MathTex(
            r"\text{Transformed } \hat{i} = \text{Col } 1\ " + vector_to_latex(new_i_a[:2]) +
            r",\quad \text{Transformed } \hat{j} = \text{Col } 2\ " + vector_to_latex(new_j_a[:2]),
            font_size=18, color=GOLD_B
        )
        obs_c_bg = BackgroundRectangle(obs_c_formula, color=COLOR_PANEL_BG, fill_opacity=0.92, buff=0.18)
        obs_c = VGroup(obs_c_bg, obs_c_formula).to_edge(DOWN, buff=0.35)

        self.play(
            plane.animate.apply_matrix(mat_a),
            unit_square.animate.apply_matrix(mat_a),
            unit_circle.animate.apply_matrix(mat_a),
            triangle.animate.apply_matrix(mat_a),
            i_hat.animate.put_start_and_end_on(ORIGIN, new_i_a),
            j_hat.animate.put_start_and_end_on(ORIGIN, new_j_a),
            i_label.animate.move_to(get_label_pos(new_i_a, "i")),
            j_label.animate.move_to(get_label_pos(new_j_a, "j")),
            FadeIn(obs_c),
            run_time=2.4
        )
        self.wait(2.0)

        # Fade out
        self.play(
            FadeOut(plane), FadeOut(unit_square), FadeOut(unit_circle), FadeOut(triangle),
            FadeOut(i_hat), FadeOut(j_hat), FadeOut(i_label), FadeOut(j_label),
            FadeOut(general_card), FadeOut(obs_c), FadeOut(title), FadeOut(subtitle),
            run_time=1.2
        )


# =====================================================================
# Scene 2: Eigenvectors & Eigenvalues
# =====================================================================

class EigenvectorsScene(Scene):
    """Act 2: Eigenvalues, Invariant Directions, and Unit Circle to Ellipse Alignment."""

    def construct(self):
        pack = get_current_matrix_pack()
        mat_a = pack.matrix_a
        l1, l2 = pack.lambda_1, pack.lambda_2
        v1, v2 = pack.v1, pack.v2

        # Title Card
        title = Text("Eigenvectors: Invariant Directions in Space", font_size=24, weight=BOLD, color=WHITE).to_edge(UP, buff=0.20)
        subtitle = MathTex(
            r"A\vec{v} = \lambda \vec{v} \quad \text{Vectors that ONLY scale along their line, never rotate!}",
            font_size=17, color=GOLD_B
        ).next_to(title, DOWN, buff=0.08)
        title_group = VGroup(title, subtitle)
        self.play(FadeIn(title_group), run_time=1.0)

        # Coordinate Plane
        plane = create_coordinate_plane()
        self.play(Create(plane), run_time=1.2)

        # Canonical Multi-Shapes and Basis Vectors
        unit_square, unit_circle, triangle = create_shape_ensemble()
        i_hat, j_hat, i_label, j_label = create_basis_vectors()

        # HUD Info Card: Matrix A and Eigenvalues
        info_card = create_hud_card(
            title=f"Matrix A (det = {pack.det_a:.2f})",
            formula=MathTex(r"A = " + pack.latex_matrix_a, font_size=20, color=LIGHT_GRAY),
            extra_text=rf"\lambda_1 = {l1:.2f} \text{{ (Gold)}}, \quad \lambda_2 = {l2:.2f} \text{{ (Cyan)}}",
            title_color=WHITE,
        ).next_to(title_group, DOWN, buff=0.15).to_edge(LEFT, buff=0.35)
        self.play(FadeIn(info_card), run_time=0.8)

        # Draw the two Eigen-Lines (infinite dashed lines through origin)
        v1_dir = np.array([v1[0], v1[1], 0.0])
        v2_dir = np.array([v2[0], v2[1], 0.0])

        eigen_line1 = DashedLine(start=-v1_dir * 7.5, end=v1_dir * 7.5, color=COLOR_V1, stroke_width=2.5, dash_length=0.15)
        eigen_line2 = DashedLine(start=-v2_dir * 7.5, end=v2_dir * 7.5, color=COLOR_V2, stroke_width=2.5, dash_length=0.15)
        self.play(Create(eigen_line1), Create(eigen_line2), run_time=1.2)

        # Place Eigenvectors (length 1.0, touching unit circle perimeter!)
        v1_vec = Arrow(ORIGIN, v1_dir, buff=0, color=COLOR_V1, stroke_width=5.0, max_tip_length_to_length_ratio=0.22)
        v2_vec = Arrow(ORIGIN, v2_dir, buff=0, color=COLOR_V2, stroke_width=5.0, max_tip_length_to_length_ratio=0.22)
        v1_label = MathTex(r"\vec{v}_1", color=COLOR_V1, font_size=22).move_to(get_label_pos(v1_dir, "v1"))
        v2_label = MathTex(r"\vec{v}_2", color=COLOR_V2, font_size=22).move_to(get_label_pos(v2_dir, "v2"))

        # Add generic non-eigenvector test vector w
        w = np.array([pack.test_vector_w[0], pack.test_vector_w[1], 0.0])
        w_line = DashedLine(start=-w * 3.5, end=w * 3.5, color=COLOR_TEST_VEC, stroke_width=1.5, stroke_opacity=0.45, dash_length=0.12)
        w_vec = Arrow(ORIGIN, w, buff=0, color=COLOR_TEST_VEC, stroke_width=4.2, max_tip_length_to_length_ratio=0.2)
        w_label = MathTex(r"\vec{w}\text{ (Generic)}", color=COLOR_TEST_VEC, font_size=18).move_to(get_label_pos(w, "w"))

        # Introduce shapes and vectors together
        self.play(
            FadeIn(unit_square), FadeIn(unit_circle), FadeIn(triangle),
            GrowArrow(i_hat), FadeIn(i_label), GrowArrow(j_hat), FadeIn(j_label),
            GrowArrow(v1_vec), FadeIn(v1_label),
            GrowArrow(v2_vec), FadeIn(v2_label),
            Create(w_line), GrowArrow(w_vec), FadeIn(w_label),
            run_time=1.5
        )
        self.wait(1.0)

        # Observation prompt
        obs_text = Text(
            "Notice: v1 and v2 lie ON the unit circle. Watch how they and the circle transform!",
            font_size=15, color=YELLOW
        )
        obs_bg = BackgroundRectangle(obs_text, color=COLOR_PANEL_BG, fill_opacity=0.92, buff=0.15)
        obs_banner = VGroup(obs_bg, obs_text).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(obs_banner), run_time=0.8)
        self.wait(0.8)

        # Transformed positions:
        # A @ v1 = lambda1 * v1
        # A @ v2 = lambda2 * v2
        # A @ w rotates off span
        new_v1 = v1_dir * l1
        new_v2 = v2_dir * l2
        new_w = mat_vec_mul(mat_a, w)
        new_i = mat_vec_mul(mat_a, [1.0, 0.0])
        new_j = mat_vec_mul(mat_a, [0.0, 1.0])

        self.play(
            plane.animate.apply_matrix(mat_a),
            unit_square.animate.apply_matrix(mat_a),
            unit_circle.animate.apply_matrix(mat_a),
            triangle.animate.apply_matrix(mat_a),
            i_hat.animate.put_start_and_end_on(ORIGIN, new_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, new_j),
            v1_vec.animate.put_start_and_end_on(ORIGIN, new_v1),
            v2_vec.animate.put_start_and_end_on(ORIGIN, new_v2),
            w_vec.animate.put_start_and_end_on(ORIGIN, new_w),
            i_label.animate.move_to(get_label_pos(new_i, "i")),
            j_label.animate.move_to(get_label_pos(new_j, "j")),
            v1_label.animate.move_to(get_label_pos(new_v1, "v1")),
            v2_label.animate.move_to(get_label_pos(new_v2, "v2")),
            w_label.animate.move_to(get_label_pos(new_w, "w")),
            run_time=2.8
        )
        self.wait(1.0)

        # Highlight formula callout and geometric alignment
        callout_lines = VGroup(
            MathTex(rf"A\vec{{v}}_1 = {format_latex_num(l1)}\vec{{v}}_1 \quad (\text{{Stays on Gold line, scaled by }}{format_latex_num(l1)}\times)", color=COLOR_V1, font_size=18),
            MathTex(rf"A\vec{{v}}_2 = {format_latex_num(l2)}\vec{{v}}_2 \quad (\text{{Stays on Cyan line, scaled by }}{format_latex_num(l2)}\times)", color=COLOR_V2, font_size=18),
            MathTex(r"A\vec{w} \ne \lambda \vec{w} \quad (\text{Rotated away from pink line!})", color=COLOR_TEST_VEC, font_size=18),
            Text(f"Ellipse principal axes align EXACTLY with eigenvectors v1 and v2!", font_size=14, color=WHITE),
            Text(f"Semi-major axis = {l1:.2f} along v1  •  Semi-minor axis = {l2:.2f} along v2", font_size=13, color=YELLOW_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        callout_bg = BackgroundRectangle(callout_lines, color=COLOR_PANEL_BG, fill_opacity=0.92, buff=0.20, stroke_width=1, stroke_color=COLOR_PANEL_BORDER)
        callout_card = VGroup(callout_bg, callout_lines).next_to(title_group, DOWN, buff=0.15).to_edge(RIGHT, buff=0.35)

        self.play(FadeIn(callout_card), run_time=1.0)
        self.wait(2.5)

        # Fade out
        self.play(
            FadeOut(plane), FadeOut(unit_square), FadeOut(unit_circle), FadeOut(triangle),
            FadeOut(eigen_line1), FadeOut(eigen_line2),
            FadeOut(v1_vec), FadeOut(v2_vec), FadeOut(w_vec), FadeOut(w_line),
            FadeOut(i_hat), FadeOut(j_hat), FadeOut(i_label), FadeOut(j_label),
            FadeOut(v1_label), FadeOut(v2_label), FadeOut(w_label),
            FadeOut(info_card), FadeOut(callout_card), FadeOut(obs_banner),
            FadeOut(title_group),
            run_time=1.2
        )


# =====================================================================
# Scene 3: Matrix Multiplication
# =====================================================================

class MatrixMultiplicationScene(Scene):
    """Act 3: Matrix Multiplication as Composition of Transformations (A then B vs C = B @ A)."""

    def construct(self):
        pack = get_current_matrix_pack()
        mat_a = pack.matrix_a
        mat_b = pack.matrix_b
        mat_c = pack.matrix_c

        # Title
        title = Text("Matrix Multiplication: Composition of Transformations", font_size=24, weight=BOLD, color=WHITE).to_edge(UP, buff=0.20)
        subtitle = MathTex(
            r"\text{Applying } A \text{ then } B \text{ is IDENTICAL to applying } C = B \cdot A \text{ directly in one step!}",
            font_size=17, color=BLUE_C
        ).next_to(title, DOWN, buff=0.08)
        title_group = VGroup(title, subtitle)
        self.play(FadeIn(title_group), run_time=1.0)

        # Coordinate Plane
        plane = create_coordinate_plane()
        self.play(Create(plane), run_time=1.2)

        # Canonical Multi-Shapes and Basis Vectors
        unit_square, unit_circle, triangle = create_shape_ensemble()
        i_hat, j_hat, i_label, j_label = create_basis_vectors()

        self.play(
            FadeIn(unit_square), FadeIn(unit_circle), FadeIn(triangle),
            GrowArrow(i_hat), FadeIn(i_label), GrowArrow(j_hat), FadeIn(j_label),
            run_time=1.2
        )
        self.wait(0.6)

        # -------------------------------------------------------------
        # Step 1: Apply Transformation Matrix A
        # -------------------------------------------------------------
        step1_card = create_hud_card(
            title="Step 1: Apply Matrix A",
            formula=MathTex(r"A = " + pack.latex_matrix_a, font_size=21, color=YELLOW_B),
            extra_text=rf"\det(A) = {pack.det_a:.2f}",
            title_color=YELLOW,
        ).next_to(title_group, DOWN, buff=0.15).to_edge(LEFT, buff=0.35)
        self.play(FadeIn(step1_card), run_time=0.8)

        a_i = mat_vec_mul(mat_a, [1.0, 0.0])
        a_j = mat_vec_mul(mat_a, [0.0, 1.0])

        self.play(
            plane.animate.apply_matrix(mat_a),
            unit_square.animate.apply_matrix(mat_a),
            unit_circle.animate.apply_matrix(mat_a),
            triangle.animate.apply_matrix(mat_a),
            i_hat.animate.put_start_and_end_on(ORIGIN, a_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, a_j),
            i_label.animate.move_to(get_label_pos(a_i, "i")),
            j_label.animate.move_to(get_label_pos(a_j, "j")),
            run_time=2.2
        )
        self.wait(0.8)

        # -------------------------------------------------------------
        # Step 2: Apply Transformation Matrix B to Transformed Space
        # -------------------------------------------------------------
        b_desc = pack.b_description if pack.b_description else "Pure 2D planar map (no z-rotation)"
        step2_card = create_hud_card(
            title="Step 2: Apply Matrix B",
            subtitle=b_desc,
            formula=MathTex(r"B = " + pack.latex_matrix_b, font_size=21, color=RED_A),
            extra_text=rf"\det(B) = {pack.det_b:.2f}",
            title_color=RED_B,
        ).next_to(step1_card, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(FadeIn(step2_card), run_time=0.8)

        c_i = mat_vec_mul(mat_c, [1.0, 0.0])
        c_j = mat_vec_mul(mat_c, [0.0, 1.0])

        self.play(
            plane.animate.apply_matrix(mat_b),
            unit_square.animate.apply_matrix(mat_b),
            unit_circle.animate.apply_matrix(mat_b),
            triangle.animate.apply_matrix(mat_b),
            i_hat.animate.put_start_and_end_on(ORIGIN, c_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, c_j),
            i_label.animate.move_to(get_label_pos(c_i, "i")),
            j_label.animate.move_to(get_label_pos(c_j, "j")),
            run_time=2.2
        )
        self.wait(1.0)

        # -------------------------------------------------------------
        # Preserve Ghost Outlines of Composite State (B @ A)
        # -------------------------------------------------------------
        ghost_square = unit_square.copy().set_stroke(YELLOW_A, width=2.5, opacity=0.55).set_fill(YELLOW, opacity=0.08)
        ghost_circle = unit_circle.copy().set_stroke("#38BDF8", width=2.5, opacity=0.55).set_fill(COLOR_CIRCLE, opacity=0.08)
        ghost_triangle = triangle.copy().set_stroke("#C084FC", width=2.5, opacity=0.55).set_fill(COLOR_TRIANGLE, opacity=0.08)
        ghost_i = Arrow(ORIGIN, c_i, buff=0, color=COLOR_I_HAT, stroke_width=2.5, stroke_opacity=0.45, max_tip_length_to_length_ratio=0.22)
        ghost_j = Arrow(ORIGIN, c_j, buff=0, color=COLOR_J_HAT, stroke_width=2.5, stroke_opacity=0.45, max_tip_length_to_length_ratio=0.22)
        ghost_group = VGroup(ghost_square, ghost_circle, ghost_triangle, ghost_i, ghost_j)
        self.add(ghost_group)

        ghost_msg = Text("Ghost outlines recorded for composite state B(A(x)). Resetting space...", font_size=15, color=YELLOW_A)
        ghost_bg = BackgroundRectangle(ghost_msg, color=COLOR_PANEL_BG, fill_opacity=0.92, buff=0.15)
        ghost_banner = VGroup(ghost_bg, ghost_msg).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(ghost_banner), run_time=0.6)
        self.wait(1.0)

        # -------------------------------------------------------------
        # Step 3: Matrix Multiplication Formula HUD & Reset to Identity
        # -------------------------------------------------------------
        formula_lines = VGroup(
            Text("Matrix Composition: C = B · A", font_size=18, weight=BOLD, color=WHITE),
            MathTex(
                matrix_to_latex(mat_b) + r"\cdot" + matrix_to_latex(mat_a) + r"=" + matrix_to_latex(mat_c),
                font_size=20, color=GREEN_B
            ),
            MathTex(
                rf"\det(C) = \det(B)\det(A) = {pack.det_b:.2f} \times {pack.det_a:.2f} = {pack.det_c:.2f}",
                font_size=17, color=LIGHT_GRAY
            ),
            Text("Now demonstrating ONE-STEP direct product transformation C...", font_size=14, color=YELLOW)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        formula_bg = BackgroundRectangle(formula_lines, color=COLOR_PANEL_BG, fill_opacity=0.92, buff=0.20, stroke_width=1, stroke_color=COLOR_PANEL_BORDER)
        formula_card = VGroup(formula_bg, formula_lines).next_to(title_group, DOWN, buff=0.15).to_edge(RIGHT, buff=0.35)

        self.play(FadeIn(formula_card), run_time=1.0)
        self.wait(1.5)

        # Reset space back to identity using inv(C)
        inv_c = np.linalg.inv(np.array(mat_c)).tolist()
        self.play(
            plane.animate.apply_matrix(inv_c),
            unit_square.animate.apply_matrix(inv_c),
            unit_circle.animate.apply_matrix(inv_c),
            triangle.animate.apply_matrix(inv_c),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP),
            i_label.animate.move_to(get_label_pos(RIGHT, "i")),
            j_label.animate.move_to(get_label_pos(UP, "j")),
            FadeOut(step1_card), FadeOut(step2_card), FadeOut(ghost_banner),
            run_time=1.8
        )
        self.wait(0.8)

        # -------------------------------------------------------------
        # Step 4: Single-Step Transformation by Product Matrix C Directly
        # -------------------------------------------------------------
        direct_card = create_hud_card(
            title="Single-Step: Apply Product Matrix C",
            subtitle="Watch shapes directly snap into the ghost outlines!",
            formula=MathTex(r"C = " + pack.latex_matrix_c, font_size=21, color=GREEN_A),
            extra_text=rf"\det(C) = {pack.det_c:.2f}",
            title_color=GREEN_C,
        ).next_to(title_group, DOWN, buff=0.15).to_edge(LEFT, buff=0.35)

        self.play(FadeIn(direct_card), run_time=0.8)

        self.play(
            plane.animate.apply_matrix(mat_c),
            unit_square.animate.apply_matrix(mat_c),
            unit_circle.animate.apply_matrix(mat_c),
            triangle.animate.apply_matrix(mat_c),
            i_hat.animate.put_start_and_end_on(ORIGIN, c_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, c_j),
            i_label.animate.move_to(get_label_pos(c_i, "i")),
            j_label.animate.move_to(get_label_pos(c_j, "j")),
            run_time=2.4
        )
        self.wait(1.0)

        # Match Verification Callout
        verification_text = Text(
            "MATCH! Single transformation C lands exactly onto the composite ghost outlines!",
            font_size=16, color=GREEN_B
        )
        verification_bg = BackgroundRectangle(verification_text, color=COLOR_PANEL_BG, fill_opacity=0.92, buff=0.18)
        verification = VGroup(verification_bg, verification_text).to_edge(DOWN, buff=0.35)

        self.play(FadeIn(verification), run_time=0.8)
        self.wait(2.2)

        # Clean Exit
        self.play(
            FadeOut(plane), FadeOut(unit_square), FadeOut(unit_circle), FadeOut(triangle),
            FadeOut(i_hat), FadeOut(j_hat), FadeOut(i_label), FadeOut(j_label),
            FadeOut(ghost_group), FadeOut(formula_card), FadeOut(direct_card),
            FadeOut(verification), FadeOut(title_group),
            run_time=1.2
        )


# =====================================================================
# Scene 4: Master Matrix Multiplication Story
# =====================================================================

class MasterMatrixMultiplicationStory(Scene):
    """Grand cinematic educational presentation combining all three acts."""

    def construct(self):
        pack = get_current_matrix_pack()
        mat_a = pack.matrix_a
        mat_b = pack.matrix_b
        mat_c = pack.matrix_c
        l1, l2 = pack.lambda_1, pack.lambda_2
        v1, v2 = pack.v1, pack.v2

        # -------------------------------------------------------------
        # Prologue: Grand Title Card
        # -------------------------------------------------------------
        main_title = Text("The Geometry of Matrix Multiplication", font_size=34, weight=BOLD, color=WHITE)
        sub_title = Text("Space Transformations • Eigenvectors • Compositional Multiplication", font_size=18, color=BLUE_C).next_to(main_title, DOWN, buff=0.22)
        seed_label = Text(f"Randomized Run Seed: {pack.seed}  •  Pure 2D Planar Maps", font_size=14, color=GRAY).next_to(sub_title, DOWN, buff=0.18)

        self.play(FadeIn(main_title, shift=UP * 0.25), FadeIn(sub_title), FadeIn(seed_label), run_time=1.4)
        self.wait(1.5)
        self.play(FadeOut(main_title), FadeOut(sub_title), FadeOut(seed_label), run_time=0.8)

        # -------------------------------------------------------------
        # Act 1: Basis Vectors & Multi-Shape Deformation
        # -------------------------------------------------------------
        act1_title = Text("Part 1: Basis Vectors & Space Deformation", font_size=24, weight=BOLD, color=GOLD_B).to_edge(UP, buff=0.20)
        self.play(FadeIn(act1_title), run_time=0.8)

        plane = create_coordinate_plane()
        self.play(Create(plane), run_time=1.2)

        unit_square, unit_circle, triangle = create_shape_ensemble()
        i_hat, j_hat, i_label, j_label = create_basis_vectors()

        self.play(
            FadeIn(unit_square), FadeIn(unit_circle), FadeIn(triangle),
            GrowArrow(i_hat), FadeIn(i_label), GrowArrow(j_hat), FadeIn(j_label),
            run_time=1.2
        )
        self.wait(0.6)

        # Transformation under Matrix A
        a_card = create_hud_card(
            title="Applying Linear Transformation A",
            subtitle="Col 1 = transformed i-hat, Col 2 = transformed j-hat",
            formula=MathTex(r"A = " + pack.latex_matrix_a, font_size=21, color=GOLD_A),
            extra_text=rf"\det(A) = {pack.det_a:.2f}",
            title_color=GOLD_B,
        ).next_to(act1_title, DOWN, buff=0.15).to_edge(LEFT, buff=0.35)
        self.play(FadeIn(a_card), run_time=0.8)

        a_i = mat_vec_mul(mat_a, [1.0, 0.0])
        a_j = mat_vec_mul(mat_a, [0.0, 1.0])

        self.play(
            plane.animate.apply_matrix(mat_a),
            unit_square.animate.apply_matrix(mat_a),
            unit_circle.animate.apply_matrix(mat_a),
            triangle.animate.apply_matrix(mat_a),
            i_hat.animate.put_start_and_end_on(ORIGIN, a_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, a_j),
            i_label.animate.move_to(get_label_pos(a_i, "i")),
            j_label.animate.move_to(get_label_pos(a_j, "j")),
            run_time=2.4
        )
        self.wait(1.2)

        # -------------------------------------------------------------
        # Act 2: Eigenvalues & Invariant Directions
        # -------------------------------------------------------------
        self.play(FadeOut(a_card), FadeOut(act1_title), run_time=0.6)

        act2_title = Text("Part 2: Eigenvectors & Invariant Directions", font_size=24, weight=BOLD, color=COLOR_V1).to_edge(UP, buff=0.20)
        self.play(FadeIn(act2_title), run_time=0.6)

        # Reset back to identity to show eigenvectors clearly
        inv_a = np.linalg.inv(np.array(mat_a)).tolist()
        self.play(
            plane.animate.apply_matrix(inv_a),
            unit_square.animate.apply_matrix(inv_a),
            unit_circle.animate.apply_matrix(inv_a),
            triangle.animate.apply_matrix(inv_a),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP),
            i_label.animate.move_to(get_label_pos(RIGHT, "i")),
            j_label.animate.move_to(get_label_pos(UP, "j")),
            run_time=1.5
        )

        v1_dir = np.array([v1[0], v1[1], 0.0])
        v2_dir = np.array([v2[0], v2[1], 0.0])
        eigen_line1 = DashedLine(start=-v1_dir * 7.5, end=v1_dir * 7.5, color=COLOR_V1, stroke_width=2.5, dash_length=0.15)
        eigen_line2 = DashedLine(start=-v2_dir * 7.5, end=v2_dir * 7.5, color=COLOR_V2, stroke_width=2.5, dash_length=0.15)

        v1_vec = Arrow(ORIGIN, v1_dir, buff=0, color=COLOR_V1, stroke_width=5.0, max_tip_length_to_length_ratio=0.22)
        v2_vec = Arrow(ORIGIN, v2_dir, buff=0, color=COLOR_V2, stroke_width=5.0, max_tip_length_to_length_ratio=0.22)
        v1_label = MathTex(r"\vec{v}_1", color=COLOR_V1, font_size=22).move_to(get_label_pos(v1_dir, "v1"))
        v2_label = MathTex(r"\vec{v}_2", color=COLOR_V2, font_size=22).move_to(get_label_pos(v2_dir, "v2"))

        w = np.array([pack.test_vector_w[0], pack.test_vector_w[1], 0.0])
        w_line = DashedLine(start=-w * 3.5, end=w * 3.5, color=COLOR_TEST_VEC, stroke_width=1.5, stroke_opacity=0.45, dash_length=0.12)
        w_vec = Arrow(ORIGIN, w, buff=0, color=COLOR_TEST_VEC, stroke_width=4.2, max_tip_length_to_length_ratio=0.2)
        w_label = MathTex(r"\vec{w}\text{ (tilts)}", color=COLOR_TEST_VEC, font_size=18).move_to(get_label_pos(w, "w"))

        eigen_hud = create_hud_card(
            title="Eigenvalues & Invariant Directions",
            formula=MathTex(
                rf"\lambda_1 = {l1:.2f}\ (\vec{{v}}_1\text{{ Gold}}), \quad \lambda_2 = {l2:.2f}\ (\vec{{v}}_2\text{{ Cyan}})",
                font_size=18, color=LIGHT_GRAY
            ),
            extra_text="Circle transforms to ellipse whose axes align with v1 & v2!",
            title_color=COLOR_V1,
        ).next_to(act2_title, DOWN, buff=0.15).to_edge(LEFT, buff=0.35)

        self.play(
            Create(eigen_line1), Create(eigen_line2),
            GrowArrow(v1_vec), FadeIn(v1_label),
            GrowArrow(v2_vec), FadeIn(v2_label),
            Create(w_line), GrowArrow(w_vec), FadeIn(w_label),
            FadeIn(eigen_hud),
            run_time=1.5
        )
        self.wait(0.8)

        new_v1 = v1_dir * l1
        new_v2 = v2_dir * l2
        new_w = mat_vec_mul(mat_a, w)

        self.play(
            plane.animate.apply_matrix(mat_a),
            unit_square.animate.apply_matrix(mat_a),
            unit_circle.animate.apply_matrix(mat_a),
            triangle.animate.apply_matrix(mat_a),
            i_hat.animate.put_start_and_end_on(ORIGIN, a_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, a_j),
            v1_vec.animate.put_start_and_end_on(ORIGIN, new_v1),
            v2_vec.animate.put_start_and_end_on(ORIGIN, new_v2),
            w_vec.animate.put_start_and_end_on(ORIGIN, new_w),
            i_label.animate.move_to(get_label_pos(a_i, "i")),
            j_label.animate.move_to(get_label_pos(a_j, "j")),
            v1_label.animate.move_to(get_label_pos(new_v1, "v1")),
            v2_label.animate.move_to(get_label_pos(new_v2, "v2")),
            w_label.animate.move_to(get_label_pos(new_w, "w")),
            run_time=2.8
        )
        self.wait(1.5)

        # -------------------------------------------------------------
        # Act 3: Matrix Multiplication Composition (A then B vs C)
        # -------------------------------------------------------------
        self.play(
            FadeOut(eigen_hud), FadeOut(act2_title),
            FadeOut(eigen_line1), FadeOut(eigen_line2),
            FadeOut(v1_vec), FadeOut(v2_vec), FadeOut(w_vec), FadeOut(w_line),
            FadeOut(v1_label), FadeOut(v2_label), FadeOut(w_label),
            run_time=0.6
        )

        act3_title = Text("Part 3: Matrix Multiplication is Transformation Composition", font_size=22, weight=BOLD, color=BLUE_B).to_edge(UP, buff=0.20)
        self.play(FadeIn(act3_title), run_time=0.6)

        # Apply second matrix B from state A
        b_desc = pack.b_description if pack.b_description else "Pure 2D planar map"
        b_hud = create_hud_card(
            title="Applying Matrix B to Transformed Space",
            subtitle=b_desc,
            formula=MathTex(r"B = " + pack.latex_matrix_b, font_size=21, color=RED_A),
            extra_text=rf"\det(B) = {pack.det_b:.2f}",
            title_color=RED_B,
        ).next_to(act3_title, DOWN, buff=0.15).to_edge(LEFT, buff=0.35)
        self.play(FadeIn(b_hud), run_time=0.8)

        c_i = mat_vec_mul(mat_c, [1.0, 0.0])
        c_j = mat_vec_mul(mat_c, [0.0, 1.0])

        self.play(
            plane.animate.apply_matrix(mat_b),
            unit_square.animate.apply_matrix(mat_b),
            unit_circle.animate.apply_matrix(mat_b),
            triangle.animate.apply_matrix(mat_b),
            i_hat.animate.put_start_and_end_on(ORIGIN, c_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, c_j),
            i_label.animate.move_to(get_label_pos(c_i, "i")),
            j_label.animate.move_to(get_label_pos(c_j, "j")),
            run_time=2.2
        )
        self.wait(1.0)

        # Ghost markers
        ghost_square = unit_square.copy().set_stroke(YELLOW_A, width=2.5, opacity=0.55).set_fill(YELLOW, opacity=0.08)
        ghost_circle = unit_circle.copy().set_stroke("#38BDF8", width=2.5, opacity=0.55).set_fill(COLOR_CIRCLE, opacity=0.08)
        ghost_triangle = triangle.copy().set_stroke("#C084FC", width=2.5, opacity=0.55).set_fill(COLOR_TRIANGLE, opacity=0.08)
        ghost_i = Arrow(ORIGIN, c_i, buff=0, color=COLOR_I_HAT, stroke_width=2.5, stroke_opacity=0.45, max_tip_length_to_length_ratio=0.22)
        ghost_j = Arrow(ORIGIN, c_j, buff=0, color=COLOR_J_HAT, stroke_width=2.5, stroke_opacity=0.45, max_tip_length_to_length_ratio=0.22)
        ghost_group = VGroup(ghost_square, ghost_circle, ghost_triangle, ghost_i, ghost_j)
        self.add(ghost_group)

        prod_formula = VGroup(
            Text("Matrix Composition: C = B · A", font_size=18, weight=BOLD, color=WHITE),
            MathTex(
                matrix_to_latex(mat_b) + r"\cdot" + matrix_to_latex(mat_a) + r"=" + matrix_to_latex(mat_c),
                font_size=20, color=GREEN_B
            ),
            Text("Single-step transformation C exactly matches composite B · A!", font_size=14, color=YELLOW)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        prod_bg = BackgroundRectangle(prod_formula, color=COLOR_PANEL_BG, fill_opacity=0.92, buff=0.20, stroke_width=1, stroke_color=COLOR_PANEL_BORDER)
        prod_card = VGroup(prod_bg, prod_formula).next_to(act3_title, DOWN, buff=0.15).to_edge(RIGHT, buff=0.35)

        self.play(FadeIn(prod_card), run_time=1.0)
        self.wait(1.5)

        # Reset to identity
        inv_c = np.linalg.inv(np.array(mat_c)).tolist()
        self.play(
            plane.animate.apply_matrix(inv_c),
            unit_square.animate.apply_matrix(inv_c),
            unit_circle.animate.apply_matrix(inv_c),
            triangle.animate.apply_matrix(inv_c),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP),
            i_label.animate.move_to(get_label_pos(RIGHT, "i")),
            j_label.animate.move_to(get_label_pos(UP, "j")),
            FadeOut(b_hud),
            run_time=1.8
        )
        self.wait(0.6)

        # Direct product transformation
        direct_banner = create_hud_card(
            title="Direct Transformation: Apply Matrix C",
            formula=MathTex(r"C = " + pack.latex_matrix_c, font_size=21, color=GREEN_A),
            extra_text="Shapes and basis vectors snap directly into ghost outlines!",
            title_color=GREEN_C,
        ).next_to(act3_title, DOWN, buff=0.15).to_edge(LEFT, buff=0.35)

        self.play(FadeIn(direct_banner), run_time=0.8)

        self.play(
            plane.animate.apply_matrix(mat_c),
            unit_square.animate.apply_matrix(mat_c),
            unit_circle.animate.apply_matrix(mat_c),
            triangle.animate.apply_matrix(mat_c),
            i_hat.animate.put_start_and_end_on(ORIGIN, c_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, c_j),
            i_label.animate.move_to(get_label_pos(c_i, "i")),
            j_label.animate.move_to(get_label_pos(c_j, "j")),
            run_time=2.4
        )
        self.wait(1.2)

        # -------------------------------------------------------------
        # Epilogue: Grand Summary Card
        # -------------------------------------------------------------
        summary_text = Text(
            "Matrix Multiplication: Not just arithmetic, but the composition of spatial transformations!",
            font_size=16, color=WHITE
        )
        summary_bg = BackgroundRectangle(summary_text, color=COLOR_PANEL_BG, fill_opacity=0.92, buff=0.18)
        summary = VGroup(summary_bg, summary_text).to_edge(DOWN, buff=0.35)

        self.play(FadeIn(summary), run_time=0.8)
        self.wait(2.5)

        self.play(
            FadeOut(plane), FadeOut(unit_square), FadeOut(unit_circle), FadeOut(triangle),
            FadeOut(i_hat), FadeOut(j_hat), FadeOut(i_label), FadeOut(j_label),
            FadeOut(ghost_group), FadeOut(prod_card), FadeOut(direct_banner),
            FadeOut(act3_title), FadeOut(summary),
            run_time=1.5
        )
