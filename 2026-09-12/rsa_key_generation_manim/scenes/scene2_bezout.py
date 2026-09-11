from manim import *

class BezoutsIdentityScene(Scene):
    def construct(self):
        # Act 1: Forward steps
        title = Tex("Extended Euclidean Algorithm").to_edge(UP)
        self.play(Write(title))
        
        step1 = MathTex("40 = 2 \\cdot 17 + 6")
        step2 = MathTex("17 = 2 \\cdot 6 + 5")
        step3 = MathTex("6 = 1 \\cdot 5 + 1")
        
        steps = VGroup(step1, step2, step3).arrange(DOWN, buff=0.5).next_to(title, DOWN, buff=1)
        
        box = SurroundingRectangle(step1, color=YELLOW)
        self.play(Write(step1), Create(box))
        self.wait(1)
        self.play(box.animate.move_to(step2), Write(step2))
        self.wait(1)
        self.play(box.animate.move_to(step3), Write(step3))
        self.wait(1)
        
        self.play(FadeOut(box))
        
        # Rewriting for substitution
        rewrites = VGroup(
            MathTex("6 = 40 - 2 \\cdot 17"),
            MathTex("5 = 17 - 2 \\cdot 6"),
            MathTex("1 = 6 - 1 \\cdot 5")
        ).arrange(DOWN, buff=0.5).next_to(steps, RIGHT, buff=1)
        
        for s, r in zip([step1, step2, step3], rewrites):
            self.play(TransformFromCopy(s, r))
            
        self.wait(2)
        self.clear()
        
        # Act 2: Backward substitution
        title2 = Tex("Backward Substitution").to_edge(UP)
        self.play(Write(title2))
        
        # We will use explicit positions to prevent overlaps
        eq_base = MathTex("1 = 6 - 1 \\cdot", "5").scale(1.2).shift(UP*1.5)
        self.play(Write(eq_base))
        self.wait(1)
        
        hl_5 = SurroundingRectangle(eq_base[1], color=BLUE)
        self.play(Create(hl_5))
        
        sub5_label = MathTex("5 = 17 - 2 \\cdot 6").to_edge(DOWN)
        self.play(Write(sub5_label))
        
        # new equation after substitution
        eq_sub5 = MathTex("1 = 6 - 1 \\cdot", "(17 - 2 \\cdot 6)").scale(1.2).shift(UP*1.5)
        self.play(
            Transform(eq_base[1], eq_sub5[1]),
            Transform(eq_base[0], eq_sub5[0]),
            FadeOut(hl_5),
            TransformFromCopy(sub5_label, eq_sub5[1])
        )
        self.remove(eq_base)
        self.add(eq_sub5)
        self.wait(1)
        
        eq_simp1 = MathTex("1 = 3 \\cdot", "6", "- 1 \\cdot 17").scale(1.2).shift(UP*0.5)
        self.play(Write(eq_simp1))
        self.wait(1)
        self.play(FadeOut(sub5_label))
        
        hl_6 = SurroundingRectangle(eq_simp1[1], color=GREEN)
        self.play(Create(hl_6))
        
        sub6_label = MathTex("6 = 40 - 2 \\cdot 17").to_edge(DOWN)
        self.play(Write(sub6_label))
        
        eq_sub6 = MathTex("1 = 3 \\cdot", "(40 - 2 \\cdot 17)", "- 1 \\cdot 17").scale(1.2).shift(UP*0.5)
        self.play(
            Transform(eq_simp1[1], eq_sub6[1]),
            Transform(eq_simp1[0], eq_sub6[0]),
            Transform(eq_simp1[2], eq_sub6[2]),
            FadeOut(hl_6),
            TransformFromCopy(sub6_label, eq_sub6[1])
        )
        self.remove(eq_simp1)
        self.add(eq_sub6)
        self.wait(1)
        
        eq_simp2 = MathTex("1 = 3 \\cdot 40 - 7 \\cdot 17").scale(1.5).shift(DOWN*1)
        self.play(Write(eq_simp2))
        self.wait(1)
        self.play(FadeOut(sub6_label))
        
        self.wait(1)
        self.clear()
        
        # Final Act: modular inverse
        final_title = Tex("Modular Inverse").to_edge(UP)
        final_eq1 = MathTex("3 \\cdot 40 - 7 \\cdot 17 = 1").scale(1.5).shift(UP*1)
        self.play(Write(final_title), Write(final_eq1))
        
        mod_text = MathTex("\\implies -7 \\cdot 17 \\equiv 1 \\pmod{40}").scale(1.2).next_to(final_eq1, DOWN, buff=1)
        self.play(Write(mod_text))
        
        pos_text = MathTex("-7 \\equiv 33 \\pmod{40}").scale(1.2).next_to(mod_text, DOWN, buff=0.5)
        self.play(Write(pos_text))
        
        final_ans = Tex("Inverse of 17 mod 40 is 33").scale(1.5).color(YELLOW).next_to(pos_text, DOWN, buff=1)
        self.play(Write(final_ans))
        self.wait(2)
