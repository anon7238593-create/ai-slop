from manim import *

class EulersTheoremScene(Scene):
    def construct(self):
        title = Title("Euler's Totient Theorem: $\phi(15) = 8$")
        self.play(Write(title))

        # 3x5 grid for 1 to 15
        numbers = VGroup(*[Integer(i) for i in range(1, 16)])
        numbers.arrange_in_grid(rows=3, cols=5, buff=1.0)
        numbers.next_to(title, DOWN, buff=1.0)

        # Create cards around numbers
        cards = VGroup(*[SurroundingRectangle(n, corner_radius=0.1, color=WHITE) for n in numbers])
        grid = VGroup(*[VGroup(c, n) for c, n in zip(cards, numbers)])

        self.play(FadeIn(grid, lag_ratio=0.1))
        self.wait(1)

        # Multiples of 3 turn red and dissolve
        mult3 = [2, 5, 8, 11, 14] # indices 0-based
        mult5 = [4, 9] # excluding 14 (15) which is also mult3
        
        # turn red
        self.play(*[grid[i][0].animate.set_color(RED) for i in mult3],
                  *[grid[i][1].animate.set_color(RED) for i in mult3])
        self.play(*[FadeOut(grid[i], shift=UP) for i in mult3])
        
        # turn orange
        self.play(*[grid[i][0].animate.set_color(ORANGE) for i in mult5],
                  *[grid[i][1].animate.set_color(ORANGE) for i in mult5])
        self.play(*[FadeOut(grid[i], shift=UP) for i in mult5])
        
        coprimes = [0, 1, 3, 6, 7, 10, 12, 13]
        coprime_grid = VGroup(*[grid[i] for i in coprimes])
        
        self.play(*[cg[0].animate.set_color(GREEN) for cg in coprime_grid],
                  *[cg[1].animate.set_color(GREEN) for cg in coprime_grid])
        
        self.wait(1)

        # arrange in horizontal row
        row_R_title = MathTex("R = \\{").scale(0.8)
        row_R_close = MathTex("\\}").scale(0.8)
        
        new_row = VGroup(*[Integer(numbers[i].get_value(), color=GREEN) for i in coprimes])
        new_row.arrange(RIGHT, buff=0.5)
        
        row_group = VGroup(row_R_title, new_row, row_R_close)
        row_group.arrange(RIGHT, buff=0.2)
        row_group.move_to(ORIGIN)

        self.play(
            FadeOut(title),
            Transform(coprime_grid, new_row)
        )
        self.play(FadeIn(row_R_title), FadeIn(row_R_close))
        self.wait(1)

        # Multiplier * 2
        mult_title = MathTex("R \\times 2 \\pmod{15} = \\{").scale(0.8)
        mult_close = MathTex("\\}").scale(0.8)
        
        vals_after = [(numbers[i].get_value() * 2) % 15 for i in coprimes]
        new_row_2 = VGroup(*[Integer(v, color=YELLOW) for v in vals_after])
        new_row_2.arrange(RIGHT, buff=0.5)
        
        row_group_2 = VGroup(mult_title, new_row_2, mult_close)
        row_group_2.arrange(RIGHT, buff=0.2)
        row_group_2.next_to(row_group, DOWN, buff=1.0)
        
        self.play(FadeIn(mult_title), FadeIn(mult_close))
        
        # Animate permutation
        self.play(TransformFromCopy(new_row, new_row_2), run_time=2)
        self.wait(1)
        
        self.play(FadeOut(row_group), FadeOut(row_group_2), FadeOut(coprime_grid))
        
        # Product cancellation
        simple_eq1 = MathTex(r"a^{\phi(n)} \prod r_i \equiv \prod r_i \pmod{n}")
        simple_eq2 = MathTex(r"a^{\phi(n)} \equiv 1 \pmod{n}")
        
        self.play(Write(simple_eq1))
        self.wait(1)
        
        # Cancel prod r_i
        cross1 = Cross(simple_eq1[0][4:8])
        cross2 = Cross(simple_eq1[0][9:13])
        self.play(Create(cross1), Create(cross2))
        self.wait(1)
        self.play(Transform(simple_eq1, simple_eq2), FadeOut(cross1), FadeOut(cross2))
        self.wait(2)
