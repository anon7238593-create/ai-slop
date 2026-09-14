import json
import os
import math
from pathlib import Path
import sys
import numpy as np
import cairo

# Add current dir to sys.path for robust imports
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from manim import *
from manim.camera.camera import Camera
from random_matrix_generator import (
    generate_matrix_pack, 
    MatrixPack, 
    matrix_to_latex, 
    format_latex_num
)

# ---------------------------------------------------------------------
# Anti-Aliasing Enhancement: Force Cairo to use ANTIALIAS_BEST
# ---------------------------------------------------------------------
_orig_get_cairo_context = Camera.get_cairo_context

def _antialias_best_get_cairo_context(self, pixel_array):
    ctx = _orig_get_cairo_context(self, pixel_array)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    return ctx

Camera.get_cairo_context = _antialias_best_get_cairo_context


def get_current_matrix_pack() -> MatrixPack:
    """Retrieve or generate the matrix configuration for the current scene run."""
    env_seed = os.environ.get("MATRIX_ANIM_SEED")
    if env_seed is not None:
        try:
            return generate_matrix_pack(int(env_seed))
        except ValueError:
            pass

    config_file = Path(__file__).resolve().parent / "matrix_config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return MatrixPack(**data)
        except Exception:
            pass

    return generate_matrix_pack(42)

# Configuration for glassmorphic HUD cards
HUD_BG_COLOR = "#0B0F19"
HUD_BORDER_COLOR = "#334155"

def create_hud_card(title, formula_tex, extra_text=None, title_color=WHITE):
    title_text = Text(title, font_size=16, weight=BOLD, color=title_color)
    elements = [title_text, formula_tex]
    if extra_text:
        elements.append(Text(extra_text, font_size=13, color=LIGHT_GRAY))
    
    group = VGroup(*elements).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
    
    bg = BackgroundRectangle(
        group,
        color=HUD_BG_COLOR,
        fill_opacity=0.92,
        buff=0.25,
        stroke_width=1.0,
        stroke_color=HUD_BORDER_COLOR,
        corner_radius=0.1
    )
    return VGroup(bg, group)

def get_label_pos(vec, label_str, buff=0.2):
    vec_norm = np.linalg.norm(vec)
    if vec_norm < 1e-5:
        return ORIGIN
    direction = np.array(vec) / vec_norm
    return np.array(vec) + direction * buff

def mat_vec_mul(mat, vec):
    return [
        mat[0][0] * vec[0] + mat[0][1] * vec[1],
        mat[1][0] * vec[0] + mat[1][1] * vec[1],
        0.0
    ]

class SpaceTransformationsScene(Scene):
    def construct(self):
        pack = get_current_matrix_pack()
        
        # Elements
        title = Text("Linear Transformations: How Space Transforms", font_size=24, weight=BOLD)
        title_bg = BackgroundRectangle(title, color=HUD_BG_COLOR, fill_opacity=0.92, buff=0.15, stroke_width=1.0, stroke_color=HUD_BORDER_COLOR)
        title_card = VGroup(title_bg, title).to_edge(UP, buff=0.2)
        
        plane = NumberPlane(
            background_line_style={'stroke_color': '#1E293B', 'stroke_width': 1.2, 'stroke_opacity': 0.60},
            axis_config={'stroke_color': '#475569'}
        )
        
        i_hat = Arrow(ORIGIN, RIGHT, buff=0, color="#10B981", stroke_width=4, max_tip_length_to_length_ratio=0.15)
        j_hat = Arrow(ORIGIN, UP, buff=0, color="#F43F5E", stroke_width=4, max_tip_length_to_length_ratio=0.15)
        
        i_label = MathTex(r"\hat{\imath}", color="#10B981", font_size=24).next_to(RIGHT, RIGHT, buff=0.1)
        j_label = MathTex(r"\hat{\jmath}", color="#F43F5E", font_size=24).next_to(UP, UP, buff=0.1)
        
        unit_square = Polygon(ORIGIN, RIGHT, RIGHT+UP, UP, color="#FACC15", fill_color="#FACC15", fill_opacity=0.22, stroke_width=2.5)
        unit_circle = Circle(radius=1.0, color="#38BDF8", fill_color="#38BDF8", fill_opacity=0.18, stroke_width=2.5)
        
        self.play(FadeIn(plane), FadeIn(title_card))
        self.play(Create(unit_square), Create(unit_circle))
        self.play(GrowArrow(i_hat), GrowArrow(j_hat), FadeIn(i_label), FadeIn(j_label))
        self.wait(1)
        
        # Part A: Scaling S
        s_mat = pack.scale_matrix
        s_hud = create_hud_card(
            "Scaling (S)",
            MathTex("S = " + pack.latex_scale_matrix, font_size=20),
            rf"Area multiplier: \det(S) = {pack.scale_x * pack.scale_y:.2f}",
            title_color="#FACC15"
        ).to_corner(UL, buff=0.3).shift(DOWN * 0.8)
        
        self.play(FadeIn(s_hud))
        self.play(
            plane.animate.apply_matrix(s_mat),
            unit_square.animate.apply_matrix(s_mat),
            unit_circle.animate.apply_matrix(s_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, mat_vec_mul(s_mat, RIGHT)),
            j_hat.animate.put_start_and_end_on(ORIGIN, mat_vec_mul(s_mat, UP)),
            i_label.animate.move_to(get_label_pos(mat_vec_mul(s_mat, RIGHT), "i")),
            j_label.animate.move_to(get_label_pos(mat_vec_mul(s_mat, UP), "j")),
            run_time=2, rate_func=smooth
        )
        self.wait(1)
        
        # Reset A
        s_inv = np.linalg.inv(np.array(s_mat)).tolist()
        self.play(
            plane.animate.apply_matrix(s_inv),
            unit_square.animate.apply_matrix(s_inv),
            unit_circle.animate.apply_matrix(s_inv),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP),
            i_label.animate.move_to(get_label_pos(RIGHT, "i")),
            j_label.animate.move_to(get_label_pos(UP, "j")),
            FadeOut(s_hud),
            run_time=1.5, rate_func=smooth
        )
        
        # Part B: Shearing H
        h_mat = pack.shear_matrix
        h_hud = create_hud_card(
            "Shearing (H)",
            MathTex("H = " + pack.latex_shear_matrix, font_size=20),
            r"\det(H) = 1.00 (Area preserved!)",
            title_color="#38BDF8"
        ).to_corner(UL, buff=0.3).shift(DOWN * 0.8)
        
        self.play(FadeIn(h_hud))
        self.play(
            plane.animate.apply_matrix(h_mat),
            unit_square.animate.apply_matrix(h_mat),
            unit_circle.animate.apply_matrix(h_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, mat_vec_mul(h_mat, RIGHT)),
            j_hat.animate.put_start_and_end_on(ORIGIN, mat_vec_mul(h_mat, UP)),
            i_label.animate.move_to(get_label_pos(mat_vec_mul(h_mat, RIGHT), "i")),
            j_label.animate.move_to(get_label_pos(mat_vec_mul(h_mat, UP), "j")),
            run_time=2, rate_func=smooth
        )
        self.wait(1)
        
        # Reset B
        h_inv = np.linalg.inv(np.array(h_mat)).tolist()
        self.play(
            plane.animate.apply_matrix(h_inv),
            unit_square.animate.apply_matrix(h_inv),
            unit_circle.animate.apply_matrix(h_inv),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP),
            i_label.animate.move_to(get_label_pos(RIGHT, "i")),
            j_label.animate.move_to(get_label_pos(UP, "j")),
            FadeOut(h_hud),
            run_time=1.5, rate_func=smooth
        )

        # Part C: General Map A
        a_mat = pack.matrix_a
        a_hud = create_hud_card(
            "General Transformation (A)",
            MathTex("A = " + pack.latex_matrix_a, font_size=20),
            rf"Columns dictate transformed basis vectors.",
            title_color="#10B981"
        ).to_corner(UL, buff=0.3).shift(DOWN * 0.8)
        
        self.play(FadeIn(a_hud))
        self.play(
            plane.animate.apply_matrix(a_mat),
            unit_square.animate.apply_matrix(a_mat),
            unit_circle.animate.apply_matrix(a_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, mat_vec_mul(a_mat, RIGHT)),
            j_hat.animate.put_start_and_end_on(ORIGIN, mat_vec_mul(a_mat, UP)),
            i_label.animate.move_to(get_label_pos(mat_vec_mul(a_mat, RIGHT), "i")),
            j_label.animate.move_to(get_label_pos(mat_vec_mul(a_mat, UP), "j")),
            run_time=2, rate_func=smooth
        )
        self.wait(2)


class EigenvectorsScene(Scene):
    def construct(self):
        pack = get_current_matrix_pack()
        
        title = Text("Eigenvectors: Directions That Never Tilt", font_size=24, weight=BOLD)
        title_bg = BackgroundRectangle(title, color=HUD_BG_COLOR, fill_opacity=0.92, buff=0.15, stroke_width=1.0, stroke_color=HUD_BORDER_COLOR)
        title_card = VGroup(title_bg, title).to_edge(UP, buff=0.2)
        
        plane = NumberPlane(
            background_line_style={'stroke_color': '#1E293B', 'stroke_width': 1.2, 'stroke_opacity': 0.60},
            axis_config={'stroke_color': '#475569'}
        )
        unit_circle = Circle(radius=1.0, color="#06B6D4", fill_color="#06B6D4", fill_opacity=0.15, stroke_width=2)
        
        self.play(FadeIn(plane), FadeIn(title_card), Create(unit_circle))
        
        v1_dir = np.array([pack.v1[0], pack.v1[1], 0.0])
        v2_dir = np.array([pack.v2[0], pack.v2[1], 0.0])
        w_dir = np.array([pack.test_vector_w[0], pack.test_vector_w[1], 0.0])
        w_dir = w_dir / np.linalg.norm(w_dir)
        
        eigen_line1 = Line(-v1_dir * 10, v1_dir * 10, color="#F59E0B", stroke_width=2).set_opacity(0.4)
        eigen_line2 = Line(-v2_dir * 10, v2_dir * 10, color="#06B6D4", stroke_width=2).set_opacity(0.4)
        w_line = Line(-w_dir * 10, w_dir * 10, color="#C084FC", stroke_width=2).set_opacity(0.4)
        
        v1_vec = Arrow(ORIGIN, v1_dir, buff=0, color="#F59E0B", stroke_width=4, max_tip_length_to_length_ratio=0.2)
        v2_vec = Arrow(ORIGIN, v2_dir, buff=0, color="#06B6D4", stroke_width=4, max_tip_length_to_length_ratio=0.2)
        w_vec = Arrow(ORIGIN, w_dir, buff=0, color="#C084FC", stroke_width=4, max_tip_length_to_length_ratio=0.2)
        
        v1_label = MathTex(r"\vec{v}_1", color="#F59E0B", font_size=24).move_to(get_label_pos(v1_dir, "v1"))
        v2_label = MathTex(r"\vec{v}_2", color="#06B6D4", font_size=24).move_to(get_label_pos(v2_dir, "v2"))
        w_label = MathTex(r"\vec{w}", color="#C084FC", font_size=24).move_to(get_label_pos(w_dir, "w"))
        
        callout_text = VGroup(
            MathTex(rf"A \vec{{v}}_1 = {pack.lambda_1:.2f} \vec{{v}}_1\ \text{{(Stays on span)}}", font_size=18, color="#F59E0B"),
            MathTex(rf"A \vec{{v}}_2 = {pack.lambda_2:.2f} \vec{{v}}_2\ \text{{(Stays on span)}}", font_size=18, color="#06B6D4"),
            MathTex(r"A \vec{w} \neq \lambda \vec{w}\ \text{(Rotates off span)}", font_size=18, color="#C084FC"),
            Text("Eigenvectors = Principal Axes of the Transformed Ellipse!", font_size=14, color=WHITE)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        
        callout_bg = BackgroundRectangle(callout_text, color=HUD_BG_COLOR, fill_opacity=0.92, buff=0.25, stroke_width=1.0, stroke_color=HUD_BORDER_COLOR)
        callout = VGroup(callout_bg, callout_text).to_corner(UL, buff=0.3).shift(DOWN * 0.8)
        
        self.play(
            Create(eigen_line1), Create(eigen_line2), Create(w_line),
            GrowArrow(v1_vec), GrowArrow(v2_vec), GrowArrow(w_vec),
            FadeIn(v1_label), FadeIn(v2_label), FadeIn(w_label),
            FadeIn(callout)
        )
        self.wait(1)
        
        a_mat = pack.matrix_a
        new_v1 = mat_vec_mul(a_mat, v1_dir)
        new_v2 = mat_vec_mul(a_mat, v2_dir)
        new_w = mat_vec_mul(a_mat, w_dir)
        
        self.play(
            plane.animate.apply_matrix(a_mat),
            unit_circle.animate.apply_matrix(a_mat),
            v1_vec.animate.put_start_and_end_on(ORIGIN, new_v1),
            v2_vec.animate.put_start_and_end_on(ORIGIN, new_v2),
            w_vec.animate.put_start_and_end_on(ORIGIN, new_w),
            v1_label.animate.move_to(get_label_pos(new_v1, "v1")),
            v2_label.animate.move_to(get_label_pos(new_v2, "v2")),
            w_label.animate.move_to(get_label_pos(new_w, "w")),
            run_time=3, rate_func=smooth
        )
        self.wait(2)


class MatrixMultiplicationScene(Scene):
    def construct(self):
        pack = get_current_matrix_pack()
        
        title = Text("Matrix Multiplication: Composition of Transformations", font_size=24, weight=BOLD)
        title_bg = BackgroundRectangle(title, color=HUD_BG_COLOR, fill_opacity=0.92, buff=0.15, stroke_width=1.0, stroke_color=HUD_BORDER_COLOR)
        title_card = VGroup(title_bg, title).to_edge(UP, buff=0.2)
        
        plane = NumberPlane(
            background_line_style={'stroke_color': '#1E293B', 'stroke_width': 1.2, 'stroke_opacity': 0.60},
            axis_config={'stroke_color': '#475569'}
        )
        
        unit_square = Polygon(ORIGIN, RIGHT, RIGHT+UP, UP, color="#FACC15", fill_color="#FACC15", fill_opacity=0.22, stroke_width=2.5)
        unit_circle = Circle(radius=1.0, color="#38BDF8", fill_color="#38BDF8", fill_opacity=0.18, stroke_width=2.5)
        
        i_hat = Arrow(ORIGIN, RIGHT, buff=0, color="#10B981", stroke_width=4, max_tip_length_to_length_ratio=0.15)
        j_hat = Arrow(ORIGIN, UP, buff=0, color="#F43F5E", stroke_width=4, max_tip_length_to_length_ratio=0.15)
        
        self.play(FadeIn(plane), FadeIn(title_card))
        self.play(Create(unit_square), Create(unit_circle), GrowArrow(i_hat), GrowArrow(j_hat))
        self.wait(0.5)
        
        a_mat = pack.matrix_a
        b_mat = pack.matrix_b
        c_mat = pack.matrix_c
        
        # Step 1: Matrix A
        hud_a = create_hud_card(
            "Step 1: Apply Matrix A",
            MathTex("A = " + pack.latex_matrix_a, font_size=20),
            None,
            title_color="#10B981"
        ).to_corner(UL, buff=0.3).shift(DOWN * 0.8)
        
        self.play(FadeIn(hud_a))
        self.play(
            plane.animate.apply_matrix(a_mat),
            unit_square.animate.apply_matrix(a_mat),
            unit_circle.animate.apply_matrix(a_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, mat_vec_mul(a_mat, RIGHT)),
            j_hat.animate.put_start_and_end_on(ORIGIN, mat_vec_mul(a_mat, UP)),
            run_time=2, rate_func=smooth
        )
        self.wait(1)
        
        # Step 2: Matrix B
        hud_b = create_hud_card(
            "Step 2: Apply Matrix B",
            MathTex("B = " + pack.latex_matrix_b, font_size=20),
            None,
            title_color="#F43F5E"
        ).to_corner(UR, buff=0.3).shift(DOWN * 0.8)
        
        self.play(FadeIn(hud_b))
        
        c_i = mat_vec_mul(c_mat, RIGHT)
        c_j = mat_vec_mul(c_mat, UP)
        
        self.play(
            plane.animate.apply_matrix(b_mat),
            unit_square.animate.apply_matrix(b_mat),
            unit_circle.animate.apply_matrix(b_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, c_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, c_j),
            run_time=2, rate_func=smooth
        )
        self.wait(1)
        
        # Ghost Outlines
        ghost_square = DashedVMobject(unit_square.copy().set_stroke("#FACC15", width=2.5, opacity=0.8).set_fill(opacity=0))
        ghost_circle = DashedVMobject(unit_circle.copy().set_stroke("#38BDF8", width=2.5, opacity=0.8).set_fill(opacity=0))
        ghost_i = Arrow(ORIGIN, c_i, buff=0, color="#10B981", stroke_width=2.5, stroke_opacity=0.6, max_tip_length_to_length_ratio=0.15)
        ghost_j = Arrow(ORIGIN, c_j, buff=0, color="#F43F5E", stroke_width=2.5, stroke_opacity=0.6, max_tip_length_to_length_ratio=0.15)
        
        ghost_group = VGroup(ghost_square, ghost_circle, ghost_i, ghost_j)
        self.add(ghost_group)
        
        # Smooth Reset
        inv_c = np.linalg.inv(np.array(c_mat)).tolist()
        self.play(
            FadeOut(hud_a), FadeOut(hud_b),
            plane.animate.apply_matrix(inv_c),
            unit_square.animate.apply_matrix(inv_c),
            unit_circle.animate.apply_matrix(inv_c),
            i_hat.animate.put_start_and_end_on(ORIGIN, RIGHT),
            j_hat.animate.put_start_and_end_on(ORIGIN, UP),
            run_time=1.5, rate_func=smooth
        )
        
        # Step 3: Direct Product Map C
        hud_c = create_hud_card(
            "Direct Transformation (C = B @ A)",
            MathTex(pack.latex_matrix_b + r"\cdot" + pack.latex_matrix_a + r"=" + pack.latex_matrix_c, font_size=18),
            rf"\det(C) = \det(B) \times \det(A) = {pack.det_c:.2f}",
            title_color="#FACC15"
        ).to_corner(UL, buff=0.3).shift(DOWN * 0.8)
        
        self.play(FadeIn(hud_c))
        
        self.play(
            plane.animate.apply_matrix(c_mat),
            unit_square.animate.apply_matrix(c_mat),
            unit_circle.animate.apply_matrix(c_mat),
            i_hat.animate.put_start_and_end_on(ORIGIN, c_i),
            j_hat.animate.put_start_and_end_on(ORIGIN, c_j),
            run_time=2.5, rate_func=smooth
        )
        
        # Flash animation
        flash_group = VGroup(unit_square, unit_circle)
        self.play(Indicate(flash_group, color=WHITE, scale_factor=1.05), run_time=1)
        self.wait(2)


class MasterMatrixMultiplicationStory(Scene):
    def construct(self):
        SpaceTransformationsScene.construct(self)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        self.wait(0.3)
        EigenvectorsScene.construct(self)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        self.wait(0.3)
        MatrixMultiplicationScene.construct(self)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
