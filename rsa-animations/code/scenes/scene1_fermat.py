#!/usr/bin/env python3
"""Scene 1: Fermat's Little Theorem with kinetic token movement and residue permutation."""

from manim import *

COLOR_GOLD = "#F59E0B"
COLOR_CYAN = "#06B6D4"
COLOR_EMERALD = "#10B981"
COLOR_CRIMSON = "#EF4444"
COLOR_PURPLE = "#A855F7"
COLOR_DARK_PANEL = "#0F172A"


class FermatsLittleTheoremScene(Scene):
    def construct(self):
        # -----------------------------------------------------------------
        # Act 1: Theorem Statement & Parameters
        # -----------------------------------------------------------------
        title = Text("Fermat's Little Theorem", font_size=32, weight=BOLD, color=WHITE).to_edge(UP, buff=0.4)
        subtitle = Text("Pierre de Fermat (1640) • Residue Permutation Proof", font_size=18, color=COLOR_GOLD).next_to(title, DOWN, buff=0.15)
        self.play(FadeIn(title), FadeIn(subtitle))
        self.wait(0.5)

        thm_box = Rectangle(width=11.0, height=1.3, color=COLOR_CYAN, fill_color=COLOR_DARK_PANEL, fill_opacity=0.9).next_to(subtitle, DOWN, buff=0.3)
        thm_eq = MathTex(r"a^{p-1} \equiv 1 \pmod{p} \quad \text{for prime } p \text{ and } \gcd(a, p) = 1", font_size=28, color=YELLOW).move_to(thm_box)
        self.play(Create(thm_box), Write(thm_eq))
        self.wait(1.0)

        demo_badge = Text("Demonstration with prime p = 7 and multiplier a = 3", font_size=20, color=COLOR_EMERALD, weight=BOLD).next_to(thm_box, DOWN, buff=0.35)
        self.play(FadeIn(demo_badge))
        self.wait(1.0)

        # Clear Act 1 completely
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(thm_box), FadeOut(thm_eq), FadeOut(demo_badge))

        # -----------------------------------------------------------------
        # Act 2: Kinetic Set S and Multiplication by a = 3
        # -----------------------------------------------------------------
        act2_title = Text("Step 1: The Non-Zero Residue Set S (mod 7)", font_size=24, weight=BOLD, color=COLOR_CYAN).to_edge(UP, buff=0.4)
        self.play(FadeIn(act2_title))

        nums = [1, 2, 3, 4, 5, 6]
        products = [3, 6, 2, 5, 1, 4]

        # Top row: Set S
        s_label = MathTex(r"S = \{", font_size=26, color=WHITE)
        s_badges = VGroup()
        for n in nums:
            circ = Circle(radius=0.36, color=BLUE_C, fill_color=BLUE_E, fill_opacity=0.85, stroke_width=2.5)
            txt = Text(str(n), font_size=20, weight=BOLD, color=WHITE).move_to(circ)
            s_badges.add(VGroup(circ, txt))
        s_badges.arrange(RIGHT, buff=0.35)
        s_close = MathTex(r"\}", font_size=26, color=WHITE)
        row_s = VGroup(s_label, s_badges, s_close).arrange(RIGHT, buff=0.15).shift(UP * 1.5)

        self.play(FadeIn(row_s), run_time=1.0)
        self.wait(0.6)

        mult_note = Text("Multiply every element by a = 3 (mod 7):", font_size=18, color=COLOR_GOLD).next_to(row_s, DOWN, buff=0.4)
        self.play(FadeIn(mult_note))

        # Bottom row: Transformed products
        prod_label = MathTex(r"3 \cdot S \equiv \{", font_size=26, color=COLOR_GOLD)
        prod_badges = VGroup()
        for p in products:
            circ = Circle(radius=0.36, color=COLOR_GOLD, fill_color="#78350F", fill_opacity=0.85, stroke_width=2.5)
            txt = Text(str(p), font_size=20, weight=BOLD, color=WHITE).move_to(circ)
            prod_badges.add(VGroup(circ, txt))
        prod_badges.arrange(RIGHT, buff=0.35)
        prod_close = MathTex(r"\}", font_size=26, color=COLOR_GOLD)
        row_prod = VGroup(prod_label, prod_badges, prod_close).arrange(RIGHT, buff=0.15).shift(DOWN * 0.1)

        # Kinetic movement: tokens clone and fly down into product row!
        clones = VGroup(*[b.copy() for b in s_badges])
        fly_anims = [FadeIn(prod_label), FadeIn(prod_close)]
        for i in range(6):
            fly_anims.append(clones[i].animate.move_to(prod_badges[i].get_center()))

        self.play(*fly_anims, run_time=1.4)
        self.play(ReplacementTransform(clones, prod_badges), run_time=0.6)
        self.wait(0.8)

        # -----------------------------------------------------------------
        # Act 3: Kinetic Permutation Reordering
        # -----------------------------------------------------------------
        perm_note = Text("Notice: 3*S is an exact PERMUTATION of S!", font_size=20, weight=BOLD, color=COLOR_EMERALD).next_to(row_prod, DOWN, buff=0.4)
        self.play(FadeIn(perm_note))
        self.wait(0.5)

        # Physical sorting animation: rearranging the badges to match S
        # products = [3, 6, 2, 5, 1, 4] -> indices to sort: [1 is at idx 4, 2 at idx 2, 3 at idx 0, 4 at idx 5, 5 at idx 3, 6 at idx 1]
        sorted_pos = [prod_badges[products.index(val)].get_center() for val in nums]
        sort_anims = []
        for val in nums:
            orig_idx = products.index(val)
            target_idx = val - 1
            sort_anims.append(prod_badges[orig_idx].animate.move_to(sorted_pos[target_idx]))

        self.play(*sort_anims, run_time=1.8)
        self.wait(1.0)

        # Clear Act 2 completely
        self.play(FadeOut(act2_title), FadeOut(row_s), FadeOut(mult_note), FadeOut(row_prod), FadeOut(perm_note))

        # -----------------------------------------------------------------
        # Act 4: Factorial Cancellation & Conclusion
        # -----------------------------------------------------------------
        act4_title = Text("Step 2: Equating Products of Both Sets", font_size=24, weight=BOLD, color=COLOR_GOLD).to_edge(UP, buff=0.4)
        self.play(FadeIn(act4_title))

        eq1 = MathTex(
            r"(3 \cdot 1)(3 \cdot 2)(3 \cdot 3)(3 \cdot 4)(3 \cdot 5)(3 \cdot 6) \equiv 1 \cdot 2 \cdot 3 \cdot 4 \cdot 5 \cdot 6 \pmod{7}",
            font_size=24, color=WHITE
        ).shift(UP * 1.5)
        self.play(Write(eq1), run_time=1.2)
        self.wait(0.6)

        eq2 = MathTex(
            r"3^6 \cdot (6!) \equiv 6! \pmod{7}",
            font_size=30, color=COLOR_CYAN
        ).next_to(eq1, DOWN, buff=0.5)
        self.play(Write(eq2), run_time=1.0)
        self.wait(0.6)

        # Strike-through 6! on both sides
        cancel_note = Text("Since gcd(6!, 7) = 1, divide both sides by 6!:", font_size=18, color=LIGHT_GRAY).next_to(eq2, DOWN, buff=0.4)
        self.play(FadeIn(cancel_note))

        # Strike lines
        line1 = Line(LEFT * 0.4, RIGHT * 0.4, color=COLOR_CRIMSON, stroke_width=4).move_to(eq2.get_center() + LEFT * 0.1)
        line2 = Line(LEFT * 0.4, RIGHT * 0.4, color=COLOR_CRIMSON, stroke_width=4).move_to(eq2.get_center() + RIGHT * 1.1)
        self.play(Create(line1), Create(line2), run_time=0.8)
        self.wait(0.6)

        final_box = Rectangle(width=6.5, height=1.2, color=COLOR_EMERALD, fill_color=COLOR_DARK_PANEL, fill_opacity=0.95).next_to(cancel_note, DOWN, buff=0.4)
        final_eq = MathTex(r"\mathbf{3^6 \equiv 1 \pmod{7}}", font_size=34, color=COLOR_EMERALD).move_to(final_box)
        self.play(Create(final_box), Write(final_eq), run_time=1.0)
        self.wait(1.5)

        footer = Text("General Theorem: a^(p-1) = 1 (mod p) for all coprime a and prime p.", font_size=16, color=WHITE).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(footer))
        self.wait(2.0)
