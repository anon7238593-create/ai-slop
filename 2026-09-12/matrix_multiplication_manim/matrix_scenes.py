#!/usr/bin/env python3
"""Manim animation scenes visualizing linear transformations and matrix multiplication.

Demonstrates:
1. Space Transformations: Scale, Shear, and General Stretching
2. Eigenvectors & Eigenvalues: Invariant directions that scale without rotating
3. Matrix Multiplication: Composition of transformations (A then B vs C = B @ A)
4. Master Story: Combined cinematic educational presentation

All parameters and matrices are randomly generated per execution, or seed-controlled.
"""

from __future__ import annotations

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

from random_matrix_generator import MatrixPack, generate_matrix_pack


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
                return MatrixPack(**data)
        except Exception:
            pass

    # Default: fresh random configuration
    return generate_matrix_pack(None)


# Visual Styling Constants
COLOR_I_HAT = "#10B981"      # Emerald Green for basis vector i-hat
COLOR_J_HAT = "#EF4444"      # Crimson Red for basis vector j-hat
COLOR_V1 = "#F59E0B"         # Radiant Gold for Eigenvector 1
COLOR_V2 = "#06B6D4"         # Electric Cyan for Eigenvector 2
COLOR_TEST_VEC = "#EC4899"   # Magenta for non-eigenvector test vector
COLOR_GRID_BASE = "#1E293B"  # Slate Blue for background coordinate grid
COLOR_PANEL_BG = "#0B0F19"   # Dark slate HUD banner background


class SpaceTransformationsScene(Scene):
    """Act 1: How Space Transforms under Scaling, Shearing, and Stretching."""

    def construct(self):
        pack = get_current_matrix_pack()

        # Title Card
        title = Text("Linear Transformations: How Space Transforms", font_size=32, weight=BOLD, color=WHITE).to_edge(UP, buff=0.4)
        subtitle = Text(f"Random Seed: {pack.seed}  •  Grid, Basis Vectors & Deformation", font_size=18, color=GRAY).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(title), FadeIn(subtitle), run_time=1)
        self.wait(0.5)

        # Coordinate Plane
        plane = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            background_line_style={"stroke_color": TEAL_E, "stroke_width": 1.2, "stroke_opacity": 0.5},
            faded_line_style={"stroke_color": TEAL_E, "stroke_width": 0.6, "stroke_opacity": 0.25},
        )
        self.play(Create(plane), run_time=1.5)

        # Basis Vectors: i-hat = [1, 0], j-hat = [0, 1]
        i_hat = Arrow(ORIGIN, RIGHT * 2.0, buff=0, color=COLOR_I_HAT, stroke_width=4, max_tip_length_to_length_ratio=0.25)
        j_hat = Arrow(ORIGIN, UP * 2.0, buff=0, color=COLOR_J_HAT, stroke_width=4, max_tip_length_to_length_ratio=0.25)
        i_label = MathTex(r"\hat{i}", color=COLOR_I_HAT, font_size=24).next_to(i_hat.get_end(), DOWN, buff=0.1)
        j_label = MathTex(r"\hat{j}", color=COLOR_J_HAT, font_size=24).next_to(j_hat.get_end(), LEFT, buff=0.1)

        # Unit Square
        unit_square = Polygon(
            ORIGIN, RIGHT * 2.0, RIGHT * 2.0 + UP * 2.0, UP * 2.0,
            fill_color=YELLOW, fill_opacity=0.2, stroke_color=YELLOW_D, stroke_width=2
        )

        self.play(
            GrowArrow(i_hat), FadeIn(i_label),
            GrowArrow(j_hat), FadeIn(j_label),
            FadeIn(unit_square),
            run_time=1.2
        )
        self.wait(0.8)

        # -------------------------------------------------------------
        # Part A: Scaling Transformation
        # -------------------------------------------------------------
        scale_card = VGroup(
            Text("1. Scaling Transformation", font_size=20, weight=BOLD, color=BLUE_C),
            Text(f"Stretch x by {pack.scale_x}x, y by {pack.scale_y}x", font_size=16, color=LIGHT_GRAY),
            MathTex(
                r"S = \begin{bmatrix} " + f"{pack.scale_x} & 0.0 \\\\ 0.0 & {pack.scale_y}" + r" \end{bmatrix}",
                font_size=24, color=YELLOW
            )
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UL, buff=0.8)

        scale_bg = BackgroundRectangle(scale_card, color=COLOR_PANEL_BG, fill_opacity=0.85, buff=0.2)
        scale_group = VGroup(scale_bg, scale_card)
        self.play(FadeIn(scale_group), run_time=0.8)

        # Apply scaling
        scale_mat = pack.scale_matrix
        new_i_end = np.array([scale_mat[0][0] * 2.0, scale_mat[1][0] * 2.0, 0])
        new_j_end = np.array([scale_mat[0][1] * 2.0, scale_mat[1][1] * 2.0, 0])
        new_sq_points = [
            ORIGIN,
            new_i_end,
            new_i_end + new_j_end,
            new_j_end
        ]

        self.play(
            plane.animate.apply_matrix(scale_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, new_i_end),
            j_hat.animate.put_start_and_end_on(ORIGIN, new_j_end),
            unit_square.animate.set_points_as_corners(new_sq_points + [ORIGIN]),
            i_label.animate.next_to(new_i_end, DOWN, buff=0.1),
            j_label.animate.next_to(new_j_end, LEFT, buff=0.1),
            run_time=2
        )
        self.wait(1)

        # Revert back to identity
        inv_scale = [[1.0 / scale_mat[0][0], 0.0], [0.0, 1.0 / scale_mat[1][1]]]
        self.play(
            plane.animate.apply_matrix(inv_scale),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT * 2.0),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP * 2.0),
            unit_square.animate.set_points_as_corners([ORIGIN, RIGHT * 2.0, RIGHT * 2.0 + UP * 2.0, UP * 2.0, ORIGIN]),
            i_label.animate.next_to(RIGHT * 2.0, DOWN, buff=0.1),
            j_label.animate.next_to(UP * 2.0, LEFT, buff=0.1),
            FadeOut(scale_group),
            run_time=1.5
        )

        # -------------------------------------------------------------
        # Part B: Shearing Transformation
        # -------------------------------------------------------------
        shear_card = VGroup(
            Text("2. Shearing Transformation", font_size=20, weight=BOLD, color=PURPLE_B),
            Text(f"Shear factor k = {pack.shear_k} (Area preserved: det = 1)", font_size=16, color=LIGHT_GRAY),
            MathTex(
                r"H = \begin{bmatrix} " + f"{pack.shear_matrix[0][0]} & {pack.shear_matrix[0][1]} \\\\ {pack.shear_matrix[1][0]} & {pack.shear_matrix[1][1]}" + r" \end{bmatrix}",
                font_size=24, color=PURPLE_A
            )
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UL, buff=0.8)

        shear_bg = BackgroundRectangle(shear_card, color=COLOR_PANEL_BG, fill_opacity=0.85, buff=0.2)
        shear_group = VGroup(shear_bg, shear_card)
        self.play(FadeIn(shear_group), run_time=0.8)

        shear_mat = pack.shear_matrix
        new_i_end = np.array([shear_mat[0][0] * 2.0, shear_mat[1][0] * 2.0, 0])
        new_j_end = np.array([shear_mat[0][1] * 2.0, shear_mat[1][1] * 2.0, 0])
        new_sq_points = [ORIGIN, new_i_end, new_i_end + new_j_end, new_j_end]

        self.play(
            plane.animate.apply_matrix(shear_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, new_i_end),
            j_hat.animate.put_start_and_end_on(ORIGIN, new_j_end),
            unit_square.animate.set_points_as_corners(new_sq_points + [ORIGIN]),
            i_label.animate.next_to(new_i_end, DOWN, buff=0.1),
            j_label.animate.next_to(new_j_end, LEFT, buff=0.1),
            run_time=2
        )
        self.wait(1)

        # -------------------------------------------------------------
        # Part C: General Stretching & Rotation (Matrix A)
        # -------------------------------------------------------------
        mat_a = pack.matrix_a
        # Invert shear to go from shear to matrix A: inv(shear) then A
        inv_shear = [[shear_mat[1][1], -shear_mat[0][1]], [-shear_mat[1][0], shear_mat[0][0]]]
        transition_mat = [
            [mat_a[0][0] * inv_shear[0][0] + mat_a[0][1] * inv_shear[1][0], mat_a[0][0] * inv_shear[0][1] + mat_a[0][1] * inv_shear[1][1]],
            [mat_a[1][0] * inv_shear[0][0] + mat_a[1][1] * inv_shear[1][0], mat_a[1][0] * inv_shear[0][1] + mat_a[1][1] * inv_shear[1][1]],
        ]

        general_card = VGroup(
            Text("3. General Linear Transformation (Matrix A)", font_size=20, weight=BOLD, color=GOLD_B),
            Text(f"Columns dictate where basis vectors land!", font_size=16, color=LIGHT_GRAY),
            MathTex(
                r"A = \begin{bmatrix} " + f"{mat_a[0][0]} & {mat_a[0][1]} \\\\ {mat_a[1][0]} & {mat_a[1][1]}" + r" \end{bmatrix}",
                font_size=24, color=GOLD_A
            )
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UL, buff=0.8)
        general_bg = BackgroundRectangle(general_card, color=COLOR_PANEL_BG, fill_opacity=0.85, buff=0.2)
        general_group = VGroup(general_bg, general_card)

        self.play(ReplacementTransform(shear_group, general_group), run_time=0.8)

        final_i_end = np.array([mat_a[0][0] * 2.0, mat_a[1][0] * 2.0, 0])
        final_j_end = np.array([mat_a[0][1] * 2.0, mat_a[1][1] * 2.0, 0])
        final_sq = [ORIGIN, final_i_end, final_i_end + final_j_end, final_j_end]

        self.play(
            plane.animate.apply_matrix(transition_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, final_i_end),
            j_hat.animate.put_start_and_end_on(ORIGIN, final_j_end),
            unit_square.animate.set_points_as_corners(final_sq + [ORIGIN]),
            i_label.animate.next_to(final_i_end, RIGHT, buff=0.1),
            j_label.animate.next_to(final_j_end, UP, buff=0.1),
            run_time=2.2
        )
        self.wait(1.5)

        # Fade out
        self.play(
            FadeOut(plane), FadeOut(i_hat), FadeOut(j_hat),
            FadeOut(i_label), FadeOut(j_label), FadeOut(unit_square),
            FadeOut(general_group), FadeOut(title), FadeOut(subtitle),
            run_time=1
        )


class EigenvectorsScene(Scene):
    """Act 2: Eigenvectors and Invariant Directions: A*v = lambda*v."""

    def construct(self):
        pack = get_current_matrix_pack()
        mat_a = pack.matrix_a
        l1, l2 = pack.lambda_1, pack.lambda_2
        v1, v2 = pack.v1, pack.v2

        # Header
        title = Text("Eigenvectors: Invariant Directions in Space", font_size=30, weight=BOLD, color=WHITE).to_edge(UP, buff=0.35)
        subtitle = MathTex(r"A\vec{v} = \lambda \vec{v} \quad \text{Vectors that ONLY scale, never rotate!}", font_size=20, color=GOLD_B).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(title), FadeIn(subtitle), run_time=1)

        # Coordinate Plane
        plane = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            background_line_style={"stroke_color": BLUE_E, "stroke_width": 1.2, "stroke_opacity": 0.5}
        )
        self.play(Create(plane), run_time=1.2)

        # Info Box: Matrix A and Eigenvalues
        info_card = VGroup(
            Text(f"Matrix A (det = {pack.det_a:.2f})", font_size=18, weight=BOLD, color=WHITE),
            MathTex(
                r"A = \begin{bmatrix} " + f"{mat_a[0][0]} & {mat_a[0][1]} \\\\ {mat_a[1][0]} & {mat_a[1][1]}" + r" \end{bmatrix}",
                font_size=22, color=LIGHT_GRAY
            ),
            MathTex(r"\lambda_1 = " + f"{l1:.2f}" + r",\ \vec{v}_1 \text{ (Gold)}", font_size=19, color=COLOR_V1),
            MathTex(r"\lambda_2 = " + f"{l2:.2f}" + r",\ \vec{v}_2 \text{ (Cyan)}", font_size=19, color=COLOR_V2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.6)
        info_bg = BackgroundRectangle(info_card, color=COLOR_PANEL_BG, fill_opacity=0.88, buff=0.2)
        info_group = VGroup(info_bg, info_card)
        self.play(FadeIn(info_group), run_time=0.8)

        # Draw the two Eigen-Lines (infinite dashed lines along eigenvector directions)
        v1_dir = np.array([v1[0], v1[1], 0])
        v2_dir = np.array([v2[0], v2[1], 0])

        eigen_line1 = DashedLine(start=-v1_dir * 8.0, end=v1_dir * 8.0, color=COLOR_V1, stroke_width=2.5, dash_length=0.15)
        eigen_line2 = DashedLine(start=-v2_dir * 8.0, end=v2_dir * 8.0, color=COLOR_V2, stroke_width=2.5, dash_length=0.15)
        self.play(Create(eigen_line1), Create(eigen_line2), run_time=1.5)

        # Place Eigenvectors on their respective lines
        vec_scale = 1.8
        v1_vec = Arrow(ORIGIN, v1_dir * vec_scale, buff=0, color=COLOR_V1, stroke_width=5)
        v2_vec = Arrow(ORIGIN, v2_dir * vec_scale, buff=0, color=COLOR_V2, stroke_width=5)
        v1_label = MathTex(r"\vec{v}_1", color=COLOR_V1, font_size=24).next_to(v1_vec.get_end(), UR, buff=0.1)
        v2_label = MathTex(r"\vec{v}_2", color=COLOR_V2, font_size=24).next_to(v2_vec.get_end(), UL, buff=0.1)

        # Add a non-eigenvector test vector w (oriented in between)
        w = pack.test_vector_w
        w_dir = np.array([w[0], w[1], 0])
        w_vec = Arrow(ORIGIN, w_dir, buff=0, color=COLOR_TEST_VEC, stroke_width=4)
        w_line = DashedLine(start=-w_dir * 3.0, end=w_dir * 3.0, color=COLOR_TEST_VEC, stroke_width=1.5, stroke_opacity=0.5)
        w_label = MathTex(r"\vec{w}\text{ (Generic)}", color=COLOR_TEST_VEC, font_size=20).next_to(w_vec.get_end(), RIGHT, buff=0.1)

        self.play(
            GrowArrow(v1_vec), FadeIn(v1_label),
            GrowArrow(v2_vec), FadeIn(v2_label),
            Create(w_line), GrowArrow(w_vec), FadeIn(w_label),
            run_time=1.5
        )
        self.wait(1.0)

        # Transforming space: Observe how vectors behave!
        # Compute transformed vector positions:
        # A @ v1 = l1 * v1
        # A @ v2 = l2 * v2
        # A @ w = [a11*w1 + a12*w2, a21*w1 + a22*w2]
        new_v1_end = v1_dir * (vec_scale * l1)
        new_v2_end = v2_dir * (vec_scale * l2)
        trans_w = np.array([mat_a[0][0] * w[0] + mat_a[0][1] * w[1], mat_a[1][0] * w[0] + mat_a[1][1] * w[1], 0])

        observation_banner = Text("Watch: v1 and v2 STAY on their lines; w rotates away!", font_size=18, color=YELLOW).to_edge(DOWN, buff=0.4)
        self.play(Write(observation_banner), run_time=0.8)

        self.play(
            plane.animate.apply_matrix(mat_a),
            v1_vec.animate.put_start_and_end_on(ORIGIN, new_v1_end),
            v2_vec.animate.put_start_and_end_on(ORIGIN, new_v2_end),
            w_vec.animate.put_start_and_end_on(ORIGIN, trans_w),
            v1_label.animate.next_to(new_v1_end, UR, buff=0.1),
            v2_label.animate.next_to(new_v2_end, UL, buff=0.1),
            w_label.animate.next_to(trans_w, UR, buff=0.1),
            run_time=2.8
        )
        self.wait(1.2)

        # Highlight formula
        callout = VGroup(
            MathTex(r"A\vec{v}_1 = " + f"{l1:.2f}" + r"\vec{v}_1 \quad (\text{Scaled by }" + f"{l1:.2f}" + r"\times)", color=COLOR_V1, font_size=20),
            MathTex(r"A\vec{v}_2 = " + f"{l2:.2f}" + r"\vec{v}_2 \quad (\text{Scaled by }" + f"{l2:.2f}" + r"\times)", color=COLOR_V2, font_size=20),
            MathTex(r"A\vec{w} \ne \lambda \vec{w} \quad (\text{Rotated off original span!})", color=COLOR_TEST_VEC, font_size=20),
        ).arrange(DOWN, buff=0.15).to_corner(UR, buff=0.6)
        callout_bg = BackgroundRectangle(callout, color=COLOR_PANEL_BG, fill_opacity=0.9, buff=0.2)
        callout_group = VGroup(callout_bg, callout)

        self.play(FadeIn(callout_group), run_time=1)
        self.wait(2.0)

        # Fade out
        self.play(
            FadeOut(plane), FadeOut(eigen_line1), FadeOut(eigen_line2),
            FadeOut(v1_vec), FadeOut(v2_vec), FadeOut(w_vec), FadeOut(w_line),
            FadeOut(v1_label), FadeOut(v2_label), FadeOut(w_label),
            FadeOut(info_group), FadeOut(callout_group), FadeOut(observation_banner),
            FadeOut(title), FadeOut(subtitle),
            run_time=1
        )


class MatrixMultiplicationScene(Scene):
    """Act 3: Matrix Multiplication as Composition of Transformations: A then B vs C = B @ A."""

    def construct(self):
        pack = get_current_matrix_pack()
        mat_a = pack.matrix_a
        mat_b = pack.matrix_b
        mat_c = pack.matrix_c

        # Title
        title = Text("Matrix Multiplication: Composition of Transformations", font_size=28, weight=BOLD, color=WHITE).to_edge(UP, buff=0.35)
        subtitle = MathTex(r"\text{Applying } A \text{ then } B \text{ is IDENTICAL to applying } C = B \cdot A", font_size=20, color=BLUE_C).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(title), FadeIn(subtitle), run_time=1)

        # Coordinate Plane
        plane = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            background_line_style={"stroke_color": TEAL_E, "stroke_width": 1.2, "stroke_opacity": 0.5}
        )
        self.play(Create(plane), run_time=1.2)

        # Basis vectors
        i_hat = Arrow(ORIGIN, RIGHT * 2.0, buff=0, color=COLOR_I_HAT, stroke_width=4)
        j_hat = Arrow(ORIGIN, UP * 2.0, buff=0, color=COLOR_J_HAT, stroke_width=4)
        i_label = MathTex(r"\hat{i}", color=COLOR_I_HAT, font_size=22).next_to(i_hat.get_end(), DOWN, buff=0.1)
        j_label = MathTex(r"\hat{j}", color=COLOR_J_HAT, font_size=22).next_to(j_hat.get_end(), LEFT, buff=0.1)
        self.play(GrowArrow(i_hat), FadeIn(i_label), GrowArrow(j_hat), FadeIn(j_label), run_time=1)

        # -------------------------------------------------------------
        # Step 1: Apply Transformation A
        # -------------------------------------------------------------
        step1_card = VGroup(
            Text("Step 1: Apply Matrix A", font_size=18, weight=BOLD, color=YELLOW),
            MathTex(
                r"A = \begin{bmatrix} " + f"{mat_a[0][0]} & {mat_a[0][1]} \\\\ {mat_a[1][0]} & {mat_a[1][1]}" + r" \end{bmatrix}",
                font_size=22, color=YELLOW_B
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(UL, buff=0.6)
        step1_bg = BackgroundRectangle(step1_card, color=COLOR_PANEL_BG, fill_opacity=0.88, buff=0.2)
        step1_group = VGroup(step1_bg, step1_card)
        self.play(FadeIn(step1_group), run_time=0.6)

        a_i_end = np.array([mat_a[0][0] * 2.0, mat_a[1][0] * 2.0, 0])
        a_j_end = np.array([mat_a[0][1] * 2.0, mat_a[1][1] * 2.0, 0])

        self.play(
            plane.animate.apply_matrix(mat_a),
            i_hat.animate.put_start_and_end_on(ORIGIN, a_i_end),
            j_hat.animate.put_start_and_end_on(ORIGIN, a_j_end),
            i_label.animate.next_to(a_i_end, RIGHT, buff=0.1),
            j_label.animate.next_to(a_j_end, UP, buff=0.1),
            run_time=2
        )
        self.wait(0.8)

        # -------------------------------------------------------------
        # Step 2: Apply Transformation B to the already transformed space
        # -------------------------------------------------------------
        step2_card = VGroup(
            Text("Step 2: Apply Matrix B", font_size=18, weight=BOLD, color=RED_B),
            MathTex(
                r"B = \begin{bmatrix} " + f"{mat_b[0][0]} & {mat_b[0][1]} \\\\ {mat_b[1][0]} & {mat_b[1][1]}" + r" \end{bmatrix}",
                font_size=22, color=RED_A
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).next_to(step1_group, DOWN, buff=0.2)
        step2_bg = BackgroundRectangle(step2_card, color=COLOR_PANEL_BG, fill_opacity=0.88, buff=0.2)
        step2_group = VGroup(step2_bg, step2_card)
        self.play(FadeIn(step2_group), run_time=0.6)

        c_i_end = np.array([mat_c[0][0] * 2.0, mat_c[1][0] * 2.0, 0])
        c_j_end = np.array([mat_c[0][1] * 2.0, mat_c[1][1] * 2.0, 0])

        self.play(
            plane.animate.apply_matrix(mat_b),
            i_hat.animate.put_start_and_end_on(ORIGIN, c_i_end),
            j_hat.animate.put_start_and_end_on(ORIGIN, c_j_end),
            i_label.animate.next_to(c_i_end, RIGHT, buff=0.1),
            j_label.animate.next_to(c_j_end, UP, buff=0.1),
            run_time=2
        )
        self.wait(1.0)

        # Snapshot ghost markers of the final basis vectors
        ghost_i = Arrow(ORIGIN, c_i_end, buff=0, color=COLOR_I_HAT, stroke_width=2, stroke_opacity=0.4)
        ghost_j = Arrow(ORIGIN, c_j_end, buff=0, color=COLOR_J_HAT, stroke_width=2, stroke_opacity=0.4)
        self.add(ghost_i, ghost_j)

        # -------------------------------------------------------------
        # Step 3: Matrix Multiplication Formula & Reset
        # -------------------------------------------------------------
        formula_box = VGroup(
            Text("Algebraic Matrix Multiplication C = B × A", font_size=20, weight=BOLD, color=WHITE),
            MathTex(
                r"\begin{bmatrix} " + f"{mat_b[0][0]} & {mat_b[0][1]} \\\\ {mat_b[1][0]} & {mat_b[1][1]}" + r"\end{bmatrix}"
                r"\begin{bmatrix} " + f"{mat_a[0][0]} & {mat_a[0][1]} \\\\ {mat_a[1][0]} & {mat_a[1][1]}" + r"\end{bmatrix}"
                r"= \begin{bmatrix} " + f"{mat_c[0][0]} & {mat_c[0][1]} \\\\ {mat_c[1][0]} & {mat_c[1][1]}" + r"\end{bmatrix}",
                font_size=22, color=GREEN_B
            ),
            Text("Now resetting space to demonstrate ONE-STEP product transformation C...", font_size=16, color=YELLOW)
        ).arrange(DOWN, buff=0.15).to_corner(UR, buff=0.5)
        formula_bg = BackgroundRectangle(formula_box, color=COLOR_PANEL_BG, fill_opacity=0.92, buff=0.25)
        formula_group = VGroup(formula_bg, formula_box)

        self.play(FadeIn(formula_group), run_time=1)
        self.wait(1.5)

        # Reset grid back to identity: apply inv(C)
        det_c = mat_c[0][0] * mat_c[1][1] - mat_c[0][1] * mat_c[1][0]
        inv_c = [
            [mat_c[1][1] / det_c, -mat_c[0][1] / det_c],
            [-mat_c[1][0] / det_c, mat_c[0][0] / det_c]
        ]

        self.play(
            plane.animate.apply_matrix(inv_c),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT * 2.0),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP * 2.0),
            i_label.animate.next_to(RIGHT * 2.0, DOWN, buff=0.1),
            j_label.animate.next_to(UP * 2.0, LEFT, buff=0.1),
            FadeOut(step1_group), FadeOut(step2_group),
            run_time=1.8
        )
        self.wait(0.8)

        # -------------------------------------------------------------
        # Step 4: Apply Product Matrix C directly in ONE step!
        # -------------------------------------------------------------
        direct_banner = VGroup(
            Text("Single-Step Transformation by Product Matrix C", font_size=19, weight=BOLD, color=GREEN_C),
            MathTex(r"C = \begin{bmatrix} " + f"{mat_c[0][0]} & {mat_c[0][1]} \\\\ {mat_c[1][0]} & {mat_c[1][1]}" + r" \end{bmatrix}", font_size=22, color=GREEN_A)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(UL, buff=0.6)
        direct_bg = BackgroundRectangle(direct_banner, color=COLOR_PANEL_BG, fill_opacity=0.88, buff=0.2)
        direct_group = VGroup(direct_bg, direct_banner)

        self.play(FadeIn(direct_group), run_time=0.8)

        # Animate C directly
        self.play(
            plane.animate.apply_matrix(mat_c),
            i_hat.animate.put_start_and_end_on(ORIGIN, c_i_end),
            j_hat.animate.put_start_and_end_on(ORIGIN, c_j_end),
            i_label.animate.next_to(c_i_end, RIGHT, buff=0.1),
            j_label.animate.next_to(c_j_end, UP, buff=0.1),
            run_time=2.2
        )
        self.wait(1.0)

        # Verification Callout
        verification = Text("Match! Single transformation C achieves the exact resultant of A followed by B.", font_size=17, color=YELLOW_A).to_edge(DOWN, buff=0.4)
        self.play(Write(verification), run_time=1)
        self.wait(2.0)

        # Clean exit
        self.play(
            FadeOut(plane), FadeOut(i_hat), FadeOut(j_hat),
            FadeOut(i_label), FadeOut(j_label), FadeOut(ghost_i), FadeOut(ghost_j),
            FadeOut(formula_group), FadeOut(direct_group), FadeOut(verification),
            FadeOut(title), FadeOut(subtitle),
            run_time=1
        )


class MasterMatrixMultiplicationStory(Scene):
    """Epic unified master scene: Space Transforms + Eigenvectors + Matrix Multiplication."""

    def construct(self):
        pack = get_current_matrix_pack()
        mat_a = pack.matrix_a
        mat_b = pack.matrix_b
        mat_c = pack.matrix_c
        l1, l2 = pack.lambda_1, pack.lambda_2
        v1, v2 = pack.v1, pack.v2

        # -------------------------------------------------------------
        # Prologue: Title Card
        # -------------------------------------------------------------
        main_title = Text("The Geometry of Matrix Multiplication", font_size=36, weight=BOLD, color=WHITE)
        sub_title = Text("Space Transformations • Eigenvectors • Compositional Multiplication", font_size=20, color=BLUE_C).next_to(main_title, DOWN, buff=0.25)
        seed_label = Text(f"Randomized Run Seed: {pack.seed}", font_size=15, color=GRAY).next_to(sub_title, DOWN, buff=0.2)

        self.play(FadeIn(main_title, shift=UP * 0.3), FadeIn(sub_title), FadeIn(seed_label), run_time=1.5)
        self.wait(1.5)
        self.play(FadeOut(main_title), FadeOut(sub_title), FadeOut(seed_label), run_time=0.8)

        # -------------------------------------------------------------
        # Chapter 1: Basis Vectors and Space Deformation
        # -------------------------------------------------------------
        chap1_text = Text("Part 1: Basis Vectors & Space Deformation", font_size=26, weight=BOLD, color=GOLD).to_edge(UP, buff=0.4)
        self.play(FadeIn(chap1_text), run_time=0.8)

        plane = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            background_line_style={"stroke_color": TEAL_E, "stroke_width": 1.2, "stroke_opacity": 0.5}
        )
        self.play(Create(plane), run_time=1.2)

        i_hat = Arrow(ORIGIN, RIGHT * 2.0, buff=0, color=COLOR_I_HAT, stroke_width=4)
        j_hat = Arrow(ORIGIN, UP * 2.0, buff=0, color=COLOR_J_HAT, stroke_width=4)
        i_label = MathTex(r"\hat{i} = \begin{bmatrix}1\\0\end{bmatrix}", color=COLOR_I_HAT, font_size=20).next_to(i_hat.get_end(), DOWN, buff=0.1)
        j_label = MathTex(r"\hat{j} = \begin{bmatrix}0\\1\end{bmatrix}", color=COLOR_J_HAT, font_size=20).next_to(j_hat.get_end(), LEFT, buff=0.1)

        unit_square = Polygon(
            ORIGIN, RIGHT * 2.0, RIGHT * 2.0 + UP * 2.0, UP * 2.0,
            fill_color=YELLOW, fill_opacity=0.18, stroke_color=YELLOW_D, stroke_width=2
        )

        self.play(GrowArrow(i_hat), FadeIn(i_label), GrowArrow(j_hat), FadeIn(j_label), FadeIn(unit_square), run_time=1)
        self.wait(0.8)

        # Demonstrate general stretching under matrix A
        a_card = VGroup(
            Text("Applying Linear Transformation Matrix A", font_size=18, weight=BOLD, color=GOLD_B),
            MathTex(r"A = \begin{bmatrix} " + f"{mat_a[0][0]} & {mat_a[0][1]} \\\\ {mat_a[1][0]} & {mat_a[1][1]}" + r" \end{bmatrix}", font_size=22, color=GOLD_A),
            Text(f"Col 1 = transformed i-hat, Col 2 = transformed j-hat", font_size=14, color=LIGHT_GRAY)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=0.6)
        a_bg = BackgroundRectangle(a_card, color=COLOR_PANEL_BG, fill_opacity=0.88, buff=0.2)
        a_group = VGroup(a_bg, a_card)

        self.play(FadeIn(a_group), run_time=0.8)

        a_i = np.array([mat_a[0][0] * 2.0, mat_a[1][0] * 2.0, 0])
        a_j = np.array([mat_a[0][1] * 2.0, mat_a[1][1] * 2.0, 0])
        sq_a = [ORIGIN, a_i, a_i + a_j, a_j]

        self.play(
            plane.animate.apply_matrix(mat_a),
            i_hat.animate.put_start_and_end_on(ORIGIN, a_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, a_j),
            unit_square.animate.set_points_as_corners(sq_a + [ORIGIN]),
            i_label.animate.next_to(a_i, RIGHT, buff=0.1),
            j_label.animate.next_to(a_j, UP, buff=0.1),
            run_time=2.2
        )
        self.wait(1.0)

        # -------------------------------------------------------------
        # Chapter 2: The Magic of Eigenvectors
        # -------------------------------------------------------------
        self.play(FadeOut(a_group), FadeOut(chap1_text), FadeOut(unit_square), run_time=0.6)

        chap2_text = Text("Part 2: Eigenvectors & Invariant Directions", font_size=26, weight=BOLD, color=COLOR_V1).to_edge(UP, buff=0.4)
        self.play(FadeIn(chap2_text), run_time=0.6)

        # Reset plane back to identity to illustrate eigenvectors clearly
        det_a = mat_a[0][0] * mat_a[1][1] - mat_a[0][1] * mat_a[1][0]
        inv_a = [
            [mat_a[1][1] / det_a, -mat_a[0][1] / det_a],
            [-mat_a[1][0] / det_a, mat_a[0][0] / det_a]
        ]
        self.play(
            plane.animate.apply_matrix(inv_a),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT * 2.0),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP * 2.0),
            i_label.animate.next_to(RIGHT * 2.0, DOWN, buff=0.1),
            j_label.animate.next_to(UP * 2.0, LEFT, buff=0.1),
            run_time=1.5
        )

        # Draw Eigen-Lines
        v1_dir = np.array([v1[0], v1[1], 0])
        v2_dir = np.array([v2[0], v2[1], 0])
        eigen_line1 = DashedLine(start=-v1_dir * 8.0, end=v1_dir * 8.0, color=COLOR_V1, stroke_width=2.5, dash_length=0.15)
        eigen_line2 = DashedLine(start=-v2_dir * 8.0, end=v2_dir * 8.0, color=COLOR_V2, stroke_width=2.5, dash_length=0.15)

        v1_vec = Arrow(ORIGIN, v1_dir * 1.8, buff=0, color=COLOR_V1, stroke_width=4.5)
        v2_vec = Arrow(ORIGIN, v2_dir * 1.8, buff=0, color=COLOR_V2, stroke_width=4.5)

        w = pack.test_vector_w
        w_dir = np.array([w[0], w[1], 0])
        w_vec = Arrow(ORIGIN, w_dir, buff=0, color=COLOR_TEST_VEC, stroke_width=4)
        w_label = MathTex(r"\vec{w}\text{ (tilts)}", color=COLOR_TEST_VEC, font_size=18).next_to(w_vec.get_end(), RIGHT, buff=0.1)

        eigen_hud = VGroup(
            Text("Eigenvalues & Directions:", font_size=17, weight=BOLD, color=WHITE),
            MathTex(r"\lambda_1 = " + f"{l1:.2f}" + r"\quad (\vec{v}_1 \text{ Gold})", color=COLOR_V1, font_size=19),
            MathTex(r"\lambda_2 = " + f"{l2:.2f}" + r"\quad (\vec{v}_2 \text{ Cyan})", color=COLOR_V2, font_size=19),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(UL, buff=0.6)
        eigen_hud_bg = BackgroundRectangle(eigen_hud, color=COLOR_PANEL_BG, fill_opacity=0.88, buff=0.2)
        eigen_hud_group = VGroup(eigen_hud_bg, eigen_hud)

        self.play(
            Create(eigen_line1), Create(eigen_line2),
            GrowArrow(v1_vec), GrowArrow(v2_vec),
            GrowArrow(w_vec), FadeIn(w_label),
            FadeIn(eigen_hud_group),
            run_time=1.5
        )
        self.wait(0.8)

        # Animate transformation under A: notice v1 and v2 stay on their lines!
        new_v1 = v1_dir * (1.8 * l1)
        new_v2 = v2_dir * (1.8 * l2)
        new_w = np.array([mat_a[0][0] * w[0] + mat_a[0][1] * w[1], mat_a[1][0] * w[0] + mat_a[1][1] * w[1], 0])

        self.play(
            plane.animate.apply_matrix(mat_a),
            i_hat.animate.put_start_and_end_on(ORIGIN, a_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, a_j),
            v1_vec.animate.put_start_and_end_on(ORIGIN, new_v1),
            v2_vec.animate.put_start_and_end_on(ORIGIN, new_v2),
            w_vec.animate.put_start_and_end_on(ORIGIN, new_w),
            w_label.animate.next_to(new_w, RIGHT, buff=0.1),
            run_time=2.5
        )
        self.wait(1.2)

        # -------------------------------------------------------------
        # Chapter 3: Matrix Multiplication Composition (A then B vs C)
        # -------------------------------------------------------------
        self.play(
            FadeOut(eigen_hud_group), FadeOut(chap2_text),
            FadeOut(eigen_line1), FadeOut(eigen_line2),
            FadeOut(v1_vec), FadeOut(v2_vec), FadeOut(w_vec), FadeOut(w_label),
            run_time=0.6
        )

        chap3_text = Text("Part 3: Matrix Multiplication is Transformation Composition", font_size=24, weight=BOLD, color=BLUE_B).to_edge(UP, buff=0.4)
        self.play(FadeIn(chap3_text), run_time=0.6)

        # Apply second matrix B
        b_hud = VGroup(
            Text("Applying Second Matrix B to Transformed Space", font_size=18, weight=BOLD, color=RED_B),
            MathTex(r"B = \begin{bmatrix} " + f"{mat_b[0][0]} & {mat_b[0][1]} \\\\ {mat_b[1][0]} & {mat_b[1][1]}" + r" \end{bmatrix}", font_size=22, color=RED_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(UL, buff=0.6)
        b_bg = BackgroundRectangle(b_hud, color=COLOR_PANEL_BG, fill_opacity=0.88, buff=0.2)
        b_group = VGroup(b_bg, b_hud)
        self.play(FadeIn(b_group), run_time=0.6)

        c_i = np.array([mat_c[0][0] * 2.0, mat_c[1][0] * 2.0, 0])
        c_j = np.array([mat_c[0][1] * 2.0, mat_c[1][1] * 2.0, 0])

        self.play(
            plane.animate.apply_matrix(mat_b),
            i_hat.animate.put_start_and_end_on(ORIGIN, c_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, c_j),
            run_time=2.2
        )
        self.wait(1.0)

        # Show product matrix equivalence
        product_hud = VGroup(
            Text("Product Matrix C = B × A", font_size=18, weight=BOLD, color=GREEN_C),
            MathTex(r"C = \begin{bmatrix} " + f"{mat_c[0][0]} & {mat_c[0][1]} \\\\ {mat_c[1][0]} & {mat_c[1][1]}" + r" \end{bmatrix}", font_size=22, color=GREEN_A),
            Text("Applying C directly from Identity reaches this EXACT state!", font_size=15, color=YELLOW)
        ).arrange(DOWN, buff=0.12).to_corner(UR, buff=0.6)
        prod_bg = BackgroundRectangle(product_hud, color=COLOR_PANEL_BG, fill_opacity=0.92, buff=0.2)
        prod_group = VGroup(prod_bg, product_hud)

        self.play(FadeIn(prod_group), run_time=0.8)
        self.wait(2.0)

        # Epilogue
        summary = Text("Matrix Multiplication: Not just numbers, but composition of space!", font_size=20, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(Write(summary), run_time=1)
        self.wait(2.5)

        self.play(
            FadeOut(plane), FadeOut(i_hat), FadeOut(j_hat),
            FadeOut(i_label), FadeOut(j_label), FadeOut(b_group),
            FadeOut(prod_group), FadeOut(chap3_text), FadeOut(summary),
            run_time=1.5
        )
