from manim import *

class FermatsLittleTheoremScene(Scene):
    def construct(self):
        # Act 1: Intro and S
        title = Tex("Fermat's Little Theorem").scale(1.5).to_edge(UP)
        self.play(Write(title))
        
        eq = MathTex("a^{p-1} \\equiv 1 \\pmod p").next_to(title, DOWN)
        self.play(FadeIn(eq))
        
        example = Tex("Let $p=7$, $a=3$").next_to(eq, DOWN)
        self.play(Write(example))
        self.wait(1)
        
        self.play(FadeOut(title), FadeOut(eq), FadeOut(example))
        
        # Act 2: Set S and Multiply
        set_text = Tex("Consider the set $S = \\{1, 2, 3, 4, 5, 6\\}$").to_edge(UP)
        self.play(Write(set_text))
        
        # Circular badges
        nums = [1, 2, 3, 4, 5, 6]
        badges_group = VGroup()
        for n in nums:
            circ = Circle(radius=0.4, color=BLUE, fill_opacity=0.2)
            txt = MathTex(str(n))
            badge = VGroup(circ, txt)
            badges_group.add(badge)
            
        badges_group.arrange(RIGHT, buff=0.5).next_to(set_text, DOWN, buff=1)
        self.play(FadeIn(badges_group))
        self.wait(1)
        
        mult_text = Tex("Multiply each by $a=3 \\pmod 7$").next_to(badges_group, DOWN, buff=1)
        self.play(Write(mult_text))
        self.wait(1)
        
        # Duplicate and move down to compute products
        products = [3, 6, 2, 5, 1, 4]
        prod_badges = VGroup()
        for p in products:
            circ = Circle(radius=0.4, color=RED, fill_opacity=0.2)
            txt = MathTex(str(p))
            badge = VGroup(circ, txt)
            prod_badges.add(badge)
            
        prod_badges.arrange(RIGHT, buff=0.5).next_to(mult_text, DOWN, buff=1)
        
        animations = []
        copied_badges = VGroup()
        for i in range(6):
            copy_badge = badges_group[i].copy()
            copied_badges.add(copy_badge)
            animations.append(Transform(copy_badge, prod_badges[i]))
            
        self.play(*animations, run_time=2)
        self.wait(1)
        
        self.play(FadeOut(mult_text))
        
        # Reorder product tokens to show it's a permutation
        reorder_text = Tex("Notice it's just a permutation of $S$!").next_to(badges_group, DOWN, buff=1)
        self.play(Write(reorder_text))
        self.wait(1)
        
        # Sort prod_badges visually by transforming the copies again
        sorted_indices = [products.index(i) for i in nums]
        target_positions = [copied_badges[i].get_center() + DOWN*2 for i in range(6)]
        
        reorder_anims = []
        for i, idx in enumerate(sorted_indices):
            reorder_anims.append(copied_badges[idx].animate.move_to(target_positions[i]))
            
        self.play(*reorder_anims, run_time=2)
        self.wait(1)
        
        self.play(FadeOut(set_text), FadeOut(badges_group), FadeOut(copied_badges), FadeOut(reorder_text))
        self.clear()
        
        # Act 3: Factoring out
        eq1 = MathTex("(1\\cdot 3)(2\\cdot 3)(3\\cdot 3)(4\\cdot 3)(5\\cdot 3)(6\\cdot 3) \\equiv 1\\cdot 2\\cdot 3\\cdot 4\\cdot 5\\cdot 6 \\pmod 7").scale(0.8).to_edge(UP)
        self.play(Write(eq1))
        self.wait(1)
        
        eq2 = MathTex("3^6 \\cdot (1\\cdot 2\\cdot 3\\cdot 4\\cdot 5\\cdot 6) \\equiv 6! \\pmod 7").scale(0.8).next_to(eq1, DOWN, buff=0.5)
        self.play(Write(eq2))
        self.wait(1)
        
        eq3 = MathTex("3^6", "\\cdot", "6!", "\\equiv", "6!", "\\pmod 7").scale(1.5).next_to(eq2, DOWN, buff=0.5)
        self.play(Write(eq3))
        self.wait(1)
        
        # Strike through 6!
        strike1 = Line(eq3[2].get_left() + DOWN*0.2 + LEFT*0.2, eq3[2].get_right() + UP*0.2 + RIGHT*0.2, color=RED)
        strike2 = Line(eq3[4].get_left() + DOWN*0.2 + LEFT*0.2, eq3[4].get_right() + UP*0.2 + RIGHT*0.2, color=RED)
        self.play(Create(strike1), Create(strike2))
        self.wait(1)
        
        final_eq = MathTex("3^6 \\equiv 1 \\pmod 7").scale(1.5).next_to(eq3, DOWN, buff=1)
        final_box = SurroundingRectangle(final_eq, color=YELLOW)
        self.play(Write(final_eq), Create(final_box))
        self.wait(2)
