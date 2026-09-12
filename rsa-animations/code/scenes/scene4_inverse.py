#!/usr/bin/env python3
"""Scene 4: Modular Multiplicative Inverse with animated clock hand and coprimality check."""

import math
from manim import *
import numpy as np

COLOR_GOLD = "#F59E0B"
COLOR_CYAN = "#06B6D4"
COLOR_EMERALD = "#10B981"
COLOR_CRIMSON = "#EF4444"
COLOR_DARK_PANEL = "#0F172A"


class ModularInverseScene(Scene):
    def construct(self):
        # -----------------------------------------------------------------
        # Act 1: Clock Stepping mod 11 (Success Case: 3^-1 mod 11)
        # -----------------------------------------------------------------
        title = Text("The Modular Multiplicative Inverse", font_size=28, weight=BOLD, color=WHITE).to_edge(UP, buff=0.35)
        subtitle = Text("Finding x such that a * x = 1 (mod m)", font_size=18, color=COLOR_GOLD).next_to(title, DOWN, buff=0.12)
        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(0.5)

        radius = 1.8
        center = LEFT * 2.2 + DOWN * 0.4
        circle = Circle(radius=radius, color=BLUE_C, stroke_width=3).move_to(center)
        self.play(Create(circle), run_time=0.8)

        # Dial positions mod 11
        m1 = 11
        labels = VGroup()
        ticks = VGroup()
        dot_positions = []
        for i in range(m1):
            angle = math.pi / 2 - i * (2 * math.pi / m1)
            pos = center + np.array([radius * math.cos(angle), radius * math.sin(angle), 0])
            lbl_pos = center + np.array([(radius + 0.35) * math.cos(angle), (radius + 0.35) * math.sin(angle), 0])
            dot = Dot(pos, radius=0.06, color=COLOR_CYAN)
            lbl = Text(str(i), font_size=16, weight=BOLD, color=WHITE).move_to(lbl_pos)
            labels.add(lbl)
            ticks.add(dot)
            dot_positions.append(pos)

        self.play(FadeIn(labels), FadeIn(ticks), run_time=0.8)

        # Needle pointer
        ptr_end = center + np.array([radius * 0.75 * math.cos(math.pi/2), radius * 0.75 * math.sin(math.pi/2), 0])
        pointer = Arrow(center, ptr_end, buff=0, color=COLOR_GOLD, stroke_width=4, max_tip_length_to_length_ratio=0.25)
        self.play(GrowArrow(pointer), run_time=0.6)

        # Right side info panel
        info_title = Text("Stepping by 3 (mod 11):", font_size=20, weight=BOLD, color=COLOR_CYAN).shift(RIGHT * 3.0 + UP * 1.5)
        self.play(FadeIn(info_title))

        jumps = [3, 6, 9, 1]
        step_texts = [
            r"k = 1 : \quad 3 \times 1 = 3 \equiv \mathbf{3}",
            r"k = 2 : \quad 3 \times 2 = 6 \equiv \mathbf{6}",
            r"k = 3 : \quad 3 \times 3 = 9 \equiv \mathbf{9}",
            r"k = 4 : \quad 3 \times 4 = 12 \equiv \mathbf{1} \quad \text{TARGET!}",
        ]
        step_colors = [WHITE, WHITE, WHITE, COLOR_EMERALD]

        info_group = VGroup()
        for idx, (jump_target, txt, col) in enumerate(zip(jumps, step_texts, step_colors)):
            angle = math.pi / 2 - jump_target * (2 * math.pi / m1)
            new_end = center + np.array([radius * 0.75 * math.cos(angle), radius * 0.75 * math.sin(angle), 0])
            new_ptr = Arrow(center, new_end, buff=0, color=col, stroke_width=4, max_tip_length_to_length_ratio=0.25)

            line_item = MathTex(txt, font_size=22, color=col).shift(RIGHT * 3.0 + UP * (0.8 - idx * 0.6))
            info_group.add(line_item)

            self.play(
                Transform(pointer, new_ptr),
                labels[jump_target].animate.set_color(col),
                Write(line_item),
                run_time=0.9
            )

            if idx == 3:
                # Target hit! Pulse on 1
                target_ring = Circle(radius=0.45, color=COLOR_EMERALD, stroke_width=4).move_to(labels[1].get_center())
                self.play(Create(target_ring), run_time=0.5)
                self.play(FadeOut(target_ring, scale=1.5), run_time=0.5)

            self.wait(0.4)

        concl_card = Rectangle(width=5.5, height=1.0, color=COLOR_EMERALD, fill_color=COLOR_DARK_PANEL, fill_opacity=0.95).shift(RIGHT * 3.0 + DOWN * 1.8)
        concl_txt = MathTex(r"\mathbf{3^{-1} \equiv 4 \pmod{11}}", font_size=28, color=COLOR_EMERALD).move_to(concl_card)
        self.play(Create(concl_card), Write(concl_txt))
        self.wait(1.5)

        # Clear Act 1 completely
        self.play(
            FadeOut(title), FadeOut(subtitle), FadeOut(circle), FadeOut(labels),
            FadeOut(ticks), FadeOut(pointer), FadeOut(info_title), FadeOut(info_group),
            FadeOut(concl_card), FadeOut(concl_txt)
        )

        # -----------------------------------------------------------------
        # Act 2: Failure Case: Non-Coprime (4^-1 mod 12)
        # -----------------------------------------------------------------
        act2_title = Text("Why gcd(a, m) = 1 is Mandatory (Counterexample)", font_size=24, weight=BOLD, color=COLOR_CRIMSON).to_edge(UP, buff=0.35)
        act2_sub = Text("Attempting to find 4^(-1) mod 12 where gcd(4, 12) = 4 != 1", font_size=17, color=LIGHT_GRAY).next_to(act2_title, DOWN, buff=0.12)
        self.play(FadeIn(act2_title), FadeIn(act2_sub))

        circle2 = Circle(radius=radius, color=COLOR_CRIMSON, stroke_width=3).move_to(center)
        self.play(Create(circle2), run_time=0.8)

        m2 = 12
        labels2 = VGroup()
        ticks2 = VGroup()
        for i in range(m2):
            angle = math.pi / 2 - i * (2 * math.pi / m2)
            pos = center + np.array([radius * math.cos(angle), radius * math.sin(angle), 0])
            lbl_pos = center + np.array([(radius + 0.35) * math.cos(angle), (radius + 0.35) * math.sin(angle), 0])
            dot = Dot(pos, radius=0.06, color=COLOR_CRIMSON if i in (0, 4, 8) else GRAY)
            lbl = Text(str(i), font_size=16, weight=BOLD, color=COLOR_CRIMSON if i in (0, 4, 8) else GRAY).move_to(lbl_pos)
            labels2.add(lbl)
            ticks2.add(dot)

        self.play(FadeIn(labels2), FadeIn(ticks2), run_time=0.8)

        ptr2_end = center + np.array([radius * 0.75 * math.cos(math.pi/2), radius * 0.75 * math.sin(math.pi/2), 0])
        pointer2 = Arrow(center, ptr2_end, buff=0, color=COLOR_CRIMSON, stroke_width=4, max_tip_length_to_length_ratio=0.25)
        self.play(GrowArrow(pointer2), run_time=0.6)

        # Loop: 0 -> 4 -> 8 -> 0
        loop_jumps = [4, 8, 0, 4]
        for jump in loop_jumps:
            angle = math.pi / 2 - jump * (2 * math.pi / m2)
            new_end = center + np.array([radius * 0.75 * math.cos(angle), radius * 0.75 * math.sin(angle), 0])
            new_ptr = Arrow(center, new_end, buff=0, color=COLOR_CRIMSON, stroke_width=4, max_tip_length_to_length_ratio=0.25)
            self.play(Transform(pointer2, new_ptr), run_time=0.6)

        # Explanation Card
        fail_card = Rectangle(width=6.2, height=2.4, color=COLOR_CRIMSON, fill_color=COLOR_DARK_PANEL, fill_opacity=0.95).shift(RIGHT * 3.0 + DOWN * 0.4)
        fail_txt = VGroup(
            Text("Trapped in Subgroup {0, 4, 8}!", font_size=18, weight=BOLD, color=COLOR_CRIMSON),
            Text("All multiples 4*x are multiples of 4.", font_size=15, color=LIGHT_GRAY),
            Text("Positions {1, 2, 3, 5, 6, 7, 9, 10, 11} are NEVER touched!", font_size=14, color=YELLOW),
            Text("Position 1 is impossible to reach.", font_size=15, color=WHITE),
            MathTex(r"\mathbf{\gcd(a, m) = 1 \text{ is strictly mandatory!}}", font_size=20, color=COLOR_EMERALD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(fail_card)

        self.play(Create(fail_card), FadeIn(fail_txt), run_time=1.2)
        self.wait(2.0)
