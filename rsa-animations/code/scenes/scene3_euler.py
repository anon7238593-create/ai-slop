#!/usr/bin/env python3
"""Scene 3: Euler's Totient Theorem & Multiplicativity Grid Sieve."""

from manim import *

COLOR_GOLD = "#F59E0B"
COLOR_CYAN = "#06B6D4"
COLOR_EMERALD = "#10B981"
COLOR_CRIMSON = "#EF4444"
COLOR_DARK_PANEL = "#0F172A"


class EulersTheoremScene(Scene):
    def construct(self):
        # -----------------------------------------------------------------
        # Act 1: Theorem Definition
        # -----------------------------------------------------------------
        title = Text("Euler's Totient Theorem & Sieve Grid", font_size=28, weight=BOLD, color=WHITE).to_edge(UP, buff=0.4)
        subtitle = Text(r"If gcd(a, n) = 1, then a^(phi(n)) = 1 (mod n)", font_size=18, color=COLOR_GOLD).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(0.5)

        thm_box = Rectangle(width=11.0, height=1.3, color=COLOR_CYAN, fill_color=COLOR_DARK_PANEL, fill_opacity=0.9).next_to(subtitle, DOWN, buff=0.3)
        thm_eq = MathTex(
            r"\phi(p \cdot q) = (p-1)(q-1) \quad \text{and} \quad a^{\phi(n)} \equiv 1 \pmod{n}",
            font_size=26, color=YELLOW
        ).move_to(thm_box)
        self.play(Create(thm_box), Write(thm_eq))
        self.wait(1.0)

        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(thm_box), FadeOut(thm_eq))

        # -----------------------------------------------------------------
        # Act 2: The 3x5 Grid Sieve (n = 15)
        # -----------------------------------------------------------------
        act2_title = Text("Visual Sieve: Why phi(3 * 5) = (3 - 1)(5 - 1) = 8", font_size=22, weight=BOLD, color=COLOR_CYAN).to_edge(UP, buff=0.4)
        self.play(FadeIn(act2_title))

        # Build 3x5 grid of cards (1 to 15)
        grid_cards = []
        card_w, card_h = 1.0, 0.75
        start_x, start_y = -2.8, 1.2

        all_cards = VGroup()
        for i in range(15):
            val = i + 1
            row = i // 5
            col = i % 5
            cx = start_x + col * 1.4
            cy = start_y - row * 1.1

            rect = Rectangle(width=card_w, height=card_h, color=BLUE_C, fill_color="#1E293B", fill_opacity=0.85, stroke_width=2)
            txt = Text(str(val), font_size=20, weight=BOLD, color=WHITE).move_to(rect)
            card = VGroup(rect, txt).move_to([cx, cy, 0])
            all_cards.add(card)

        self.play(FadeIn(all_cards, lag_ratio=0.04), run_time=1.2)
        self.wait(0.6)

        # Multiples of 3: {3, 6, 9, 12, 15} -> turn red & cross
        m3_indices = [2, 5, 8, 11, 14]
        # Multiples of 5: {5, 10, 15} -> turn orange & cross
        m5_indices = [4, 9]  # 15 already in m3

        sieve_label = Text("Sifting out non-coprime numbers:", font_size=18, color=COLOR_GOLD).shift(DOWN * 2.2)
        self.play(FadeIn(sieve_label))

        red_anims = []
        for idx in m3_indices:
            red_anims.append(all_cards[idx][0].animate.set_color(COLOR_CRIMSON).set_fill("#7F1D1D", opacity=0.9))
        self.play(*red_anims, run_time=0.8)

        orange_anims = []
        for idx in m5_indices:
            orange_anims.append(all_cards[idx][0].animate.set_color(COLOR_GOLD).set_fill("#78350F", opacity=0.9))
        self.play(*orange_anims, run_time=0.8)
        self.wait(0.5)

        # Discard non-coprimes with animation
        discard_group = VGroup(*[all_cards[idx] for idx in (m3_indices + m5_indices)])
        self.play(FadeOut(discard_group, shift=UP * 0.5), run_time=0.8)

        # Highlight remaining 8 coprime cards in green
        coprime_indices = [0, 1, 3, 6, 7, 10, 12, 13]  # {1, 2, 4, 7, 8, 11, 13, 14}
        coprime_cards = VGroup(*[all_cards[idx] for idx in coprime_indices])
        green_anims = []
        for c in coprime_cards:
            green_anims.append(c[0].animate.set_color(COLOR_EMERALD).set_fill("#064E3B", opacity=0.9))
        self.play(*green_anims, run_time=0.8)
        self.wait(0.6)

        res_count = Text("Exactly 8 coprime residues remain: phi(15) = 8!", font_size=20, weight=BOLD, color=COLOR_EMERALD).move_to(sieve_label)
        self.play(Transform(sieve_label, res_count))
        self.wait(1.0)

        # Clear Act 2 completely
        self.play(FadeOut(act2_title), FadeOut(coprime_cards), FadeOut(sieve_label))

        # -----------------------------------------------------------------
        # Act 3: Permutation of Reduced Residue Set & Proof
        # -----------------------------------------------------------------
        act3_title = Text("Step 2: Permutation of Coprime Residues (R)", font_size=22, weight=BOLD, color=COLOR_CYAN).to_edge(UP, buff=0.4)
        self.play(FadeIn(act3_title))

        c_vals = [1, 2, 4, 7, 8, 11, 13, 14]
        # Multiplied by 2 mod 15:
        # 1*2=2, 2*2=4, 4*2=8, 7*2=14, 8*2=16=1, 11*2=22=7, 13*2=26=11, 14*2=28=13
        p_vals = [2, 4, 8, 14, 1, 7, 11, 13]

        row_r_cards = VGroup()
        for val in c_vals:
            rect = Rectangle(width=0.8, height=0.65, color=COLOR_EMERALD, fill_color="#064E3B", fill_opacity=0.85, stroke_width=2)
            txt = Text(str(val), font_size=18, weight=BOLD, color=WHITE).move_to(rect)
            row_r_cards.add(VGroup(rect, txt))
        row_r_cards.arrange(RIGHT, buff=0.25).shift(UP * 1.5)

        r_lbl = MathTex(r"R = ", font_size=24, color=COLOR_EMERALD).next_to(row_r_cards, LEFT, buff=0.2)
        self.play(FadeIn(r_lbl), FadeIn(row_r_cards), run_time=1.0)
        self.wait(0.5)

        mult_banner = Text("Multiply each by a = 2 (mod 15):", font_size=18, color=COLOR_GOLD).next_to(row_r_cards, DOWN, buff=0.35)
        self.play(FadeIn(mult_banner))

        row_mult_cards = VGroup()
        for val in p_vals:
            rect = Rectangle(width=0.8, height=0.65, color=COLOR_GOLD, fill_color="#78350F", fill_opacity=0.85, stroke_width=2)
            txt = Text(str(val), font_size=18, weight=BOLD, color=WHITE).move_to(rect)
            row_mult_cards.add(VGroup(rect, txt))
        row_mult_cards.arrange(RIGHT, buff=0.25).next_to(mult_banner, DOWN, buff=0.35)

        mult_lbl = MathTex(r"2 \cdot R \equiv ", font_size=24, color=COLOR_GOLD).next_to(row_mult_cards, LEFT, buff=0.2)

        # Kinetic flight: cards clone and fly down!
        clones = VGroup(*[c.copy() for c in row_r_cards])
        self.play(FadeIn(mult_lbl), *[clones[i].animate.move_to(row_mult_cards[i].get_center()) for i in range(8)], run_time=1.2)
        self.play(ReplacementTransform(clones, row_mult_cards), run_time=0.6)
        self.wait(0.8)

        # Proof formula
        proof_eq = MathTex(r"a^{\phi(n)} \cdot \prod_{r \in R} r \equiv \prod_{r \in R} r \pmod{n}", font_size=26, color=WHITE).shift(DOWN * 1.5)
        self.play(Write(proof_eq), run_time=1.0)
        self.wait(0.6)

        line_cancel = Line(LEFT * 0.5, RIGHT * 0.5, color=COLOR_CRIMSON, stroke_width=4).move_to(proof_eq.get_center() + LEFT * 0.1)
        line_cancel2 = Line(LEFT * 0.5, RIGHT * 0.5, color=COLOR_CRIMSON, stroke_width=4).move_to(proof_eq.get_center() + RIGHT * 1.4)
        self.play(Create(line_cancel), Create(line_cancel2), run_time=0.6)
        self.wait(0.5)

        final_box = Rectangle(width=5.5, height=1.1, color=COLOR_EMERALD, fill_color=COLOR_DARK_PANEL, fill_opacity=0.95).shift(DOWN * 2.6)
        final_thm = MathTex(r"\mathbf{a^{\phi(n)} \equiv 1 \pmod{n}}", font_size=30, color=COLOR_EMERALD).move_to(final_box)
        self.play(Create(final_box), Write(final_thm), run_time=1.0)
        self.wait(2.0)
