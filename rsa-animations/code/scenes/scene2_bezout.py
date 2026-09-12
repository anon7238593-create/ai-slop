#!/usr/bin/env python3
"""Scene 2: Bézout's Identity & Extended Euclidean Algorithm with kinetic substitution."""

from manim import *

COLOR_GOLD = "#F59E0B"
COLOR_CYAN = "#06B6D4"
COLOR_EMERALD = "#10B981"
COLOR_CRIMSON = "#EF4444"
COLOR_PURPLE = "#A855F7"
COLOR_DARK_PANEL = "#0F172A"


class BezoutsIdentityScene(Scene):
    def construct(self):
        # -----------------------------------------------------------------
        # Act 1: Forward Euclidean Division
        # -----------------------------------------------------------------
        title = Text("Bézout's Identity & Extended Euclidean Algorithm", font_size=28, weight=BOLD, color=WHITE).to_edge(UP, buff=0.4)
        subtitle = Text("Étienne Bézout (1766) • Finding ax + by = gcd(a, b)", font_size=18, color=COLOR_GOLD).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(0.5)

        target_badge = Text("Goal for RSA: Solve 17*d = 1 (mod 40) where a = 17, b = 40", font_size=19, color=COLOR_CYAN, weight=BOLD).next_to(subtitle, DOWN, buff=0.3)
        self.play(FadeIn(target_badge))
        self.wait(0.6)

        div_header = Text("Phase 1: Forward Euclidean Division", font_size=20, weight=BOLD, color=COLOR_GOLD).shift(UP * 0.8)
        self.play(FadeIn(div_header))

        eq_div1 = MathTex(r"40 = 2 \times 17 + 6 \quad \implies \quad 6 = 40 - 2 \times 17", font_size=24, color=WHITE).shift(UP * 0.1)
        eq_div2 = MathTex(r"17 = 2 \times 6 + 5 \quad \implies \quad 5 = 17 - 2 \times 6", font_size=24, color=WHITE).next_to(eq_div1, DOWN, buff=0.3)
        eq_div3 = MathTex(r"6 = 1 \times 5 + \mathbf{1} \quad \implies \quad \mathbf{1 = 6 - 1 \times 5}", font_size=24, color=COLOR_EMERALD).next_to(eq_div2, DOWN, buff=0.3)

        box_focus = SurroundingRectangle(eq_div1, color=COLOR_CYAN, buff=0.15)
        self.play(Write(eq_div1), Create(box_focus), run_time=1.0)
        self.wait(0.4)
        self.play(box_focus.animate.move_to(eq_div2), Write(eq_div2), run_time=0.9)
        self.wait(0.4)
        self.play(box_focus.animate.move_to(eq_div3), Write(eq_div3), run_time=0.9)
        self.wait(1.0)

        # Clear Act 1 completely
        self.play(
            FadeOut(title), FadeOut(subtitle), FadeOut(target_badge),
            FadeOut(div_header), FadeOut(eq_div1), FadeOut(eq_div2),
            FadeOut(eq_div3), FadeOut(box_focus)
        )

        # -----------------------------------------------------------------
        # Act 2: Kinetic Backward Substitution
        # -----------------------------------------------------------------
        act2_title = Text("Phase 2: Backward Substitution (Unrolling Remainders)", font_size=24, weight=BOLD, color=COLOR_PURPLE).to_edge(UP, buff=0.4)
        self.play(FadeIn(act2_title))
        self.wait(0.5)

        # Base equation
        base_eq = MathTex(r"1 = 6 - 1 \cdot", r"5", font_size=28, color=WHITE).shift(UP * 1.6)
        self.play(Write(base_eq), run_time=1.0)
        self.wait(0.5)

        # Substitution 1: 5 = 17 - 2*6
        sub1_card = Rectangle(width=5.5, height=0.9, color=COLOR_CYAN, fill_color=COLOR_DARK_PANEL, fill_opacity=0.9).shift(UP * 0.5)
        sub1_txt = MathTex(r"\text{Substitute } 5 = (17 - 2 \cdot 6)", font_size=22, color=COLOR_CYAN).move_to(sub1_card)
        sub1_group = VGroup(sub1_card, sub1_txt)
        self.play(FadeIn(sub1_group))
        self.wait(0.5)

        eq_sub1 = MathTex(r"1 = 6 - 1 \cdot (17 - 2 \cdot 6)", font_size=28, color=WHITE).shift(DOWN * 0.4)
        self.play(TransformFromCopy(sub1_txt, eq_sub1), run_time=1.0)
        self.wait(0.5)

        eq_simp1 = MathTex(r"1 = 3 \cdot", r"6", r"- 1 \cdot 17", font_size=28, color=YELLOW).next_to(eq_sub1, DOWN, buff=0.4)
        self.play(Write(eq_simp1), run_time=1.0)
        self.wait(0.8)

        # Clear first substitution step
        self.play(FadeOut(base_eq), FadeOut(sub1_group), FadeOut(eq_sub1), eq_simp1.animate.shift(UP * 2.2))

        # Substitution 2: 6 = 40 - 2*17
        sub2_card = Rectangle(width=5.5, height=0.9, color=COLOR_GOLD, fill_color=COLOR_DARK_PANEL, fill_opacity=0.9).shift(UP * 0.5)
        sub2_txt = MathTex(r"\text{Substitute } 6 = (40 - 2 \cdot 17)", font_size=22, color=COLOR_GOLD).move_to(sub2_card)
        sub2_group = VGroup(sub2_card, sub2_txt)
        self.play(FadeIn(sub2_group))
        self.wait(0.5)

        eq_sub2 = MathTex(r"1 = 3 \cdot (40 - 2 \cdot 17) - 1 \cdot 17", font_size=28, color=WHITE).shift(DOWN * 0.4)
        self.play(TransformFromCopy(sub2_txt, eq_sub2), run_time=1.0)
        self.wait(0.5)

        eq_final_bezout = MathTex(r"\mathbf{1 = 3 \times 40 - 7 \times 17}", font_size=32, color=COLOR_EMERALD).next_to(eq_sub2, DOWN, buff=0.5)
        bezout_rect = SurroundingRectangle(eq_final_bezout, color=COLOR_EMERALD, buff=0.2)
        self.play(Write(eq_final_bezout), Create(bezout_rect), run_time=1.2)
        self.wait(1.2)

        # Clear Act 2 completely
        self.play(
            FadeOut(act2_title), FadeOut(eq_simp1), FadeOut(sub2_group),
            FadeOut(eq_sub2), FadeOut(eq_final_bezout), FadeOut(bezout_rect)
        )

        # -----------------------------------------------------------------
        # Act 3: Modular Inverse Extraction
        # -----------------------------------------------------------------
        act3_title = Text("Phase 3: Extracting the Modular Inverse", font_size=24, weight=BOLD, color=COLOR_GOLD).to_edge(UP, buff=0.4)
        self.play(FadeIn(act3_title))

        step_mod1 = MathTex(r"3 \cdot 40 - 7 \cdot 17 = 1", font_size=28, color=WHITE).shift(UP * 1.5)
        self.play(Write(step_mod1))
        self.wait(0.5)

        step_mod2 = MathTex(r"\implies \quad -7 \cdot 17 \equiv 1 \pmod{40}", font_size=28, color=COLOR_CYAN).next_to(step_mod1, DOWN, buff=0.5)
        self.play(Write(step_mod2))
        self.wait(0.5)

        step_mod3 = MathTex(r"\text{Modulo 40: } -7 \equiv -7 + 40 = \mathbf{33} \pmod{40}", font_size=26, color=YELLOW).next_to(step_mod2, DOWN, buff=0.5)
        self.play(Write(step_mod3))
        self.wait(0.6)

        ans_box = Rectangle(width=7.5, height=1.3, color=COLOR_EMERALD, fill_color=COLOR_DARK_PANEL, fill_opacity=0.95).next_to(step_mod3, DOWN, buff=0.5)
        ans_txt = VGroup(
            Text("Modular Inverse Found (Private Exponent d):", font_size=16, color=LIGHT_GRAY),
            MathTex(r"\mathbf{d = 17^{-1} \equiv 33 \pmod{40}}", font_size=30, color=COLOR_EMERALD)
        ).arrange(DOWN, buff=0.1).move_to(ans_box)

        self.play(Create(ans_box), FadeIn(ans_txt), run_time=1.0)
        self.wait(1.0)

        check_note = Text("Verification: 17 * 33 = 561 = 14 * 40 + 1 == 1 (mod 40)", font_size=16, color=COLOR_GOLD).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(check_note))
        self.wait(2.0)
