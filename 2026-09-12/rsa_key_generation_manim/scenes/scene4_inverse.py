from manim import *

class ModularInverseScene(Scene):
    def construct(self):
        # Part 1: mod 11, jump +3
        title1 = Title("Modular Inverse: $3^{-1} \pmod{11}$")
        self.play(Write(title1))
        
        radius = 2.5
        circle = Circle(radius=radius, color=WHITE)
        self.play(Create(circle))
        
        # Dial labels mod 11
        labels = VGroup()
        for i in range(11):
            angle = PI/2 - i * (2 * PI / 11)
            pos = [radius * 1.2 * np.cos(angle), radius * 1.2 * np.sin(angle), 0]
            label = Integer(i).move_to(pos)
            labels.add(label)
            
        ticks = VGroup()
        for i in range(11):
            angle = PI/2 - i * (2 * PI / 11)
            start_pos = [radius * 0.9 * np.cos(angle), radius * 0.9 * np.sin(angle), 0]
            end_pos = [radius * 1.0 * np.cos(angle), radius * 1.0 * np.sin(angle), 0]
            tick = Line(start_pos, end_pos, color=WHITE)
            ticks.add(tick)
            
        self.play(FadeIn(labels), FadeIn(ticks))
        
        # Pointer
        pointer = Arrow(start=ORIGIN, end=[radius * 0.8 * np.cos(PI/2), radius * 0.8 * np.sin(PI/2), 0], color=YELLOW, buff=0)
        self.play(GrowArrow(pointer))
        self.wait(1)
        
        # Jumps
        jumps = [3, 6, 9, 1]
        for k, jump in enumerate(jumps):
            target_angle = PI/2 - jump * (2 * PI / 11)
            target_end = [radius * 0.8 * np.cos(target_angle), radius * 0.8 * np.sin(target_angle), 0]
            new_pointer = Arrow(start=ORIGIN, end=target_end, color=YELLOW, buff=0)
            
            label_color = YELLOW
            if k == 3: label_color = GREEN
            
            self.play(Transform(pointer, new_pointer), labels[jump].animate.set_color(label_color))
            if k == 3:
                # Target hit! Pulse on 1
                pulse = Circle(radius=0.5, color=GREEN).move_to(labels[1].get_center())
                self.play(Create(pulse))
                self.play(FadeOut(pulse, scale=2))
            self.wait(0.5)
            
        concl1 = MathTex("3 \\times 4 \equiv 1 \pmod{11} \implies 3^{-1} \equiv 4").scale(0.8)
        concl1.to_edge(DOWN)
        self.play(Write(concl1))
        self.wait(2)
        
        # Clear Part 1
        self.play(FadeOut(title1), FadeOut(circle), FadeOut(labels), FadeOut(ticks), FadeOut(pointer), FadeOut(concl1))
        self.wait(1)
        
        # Part 2: mod 12, jump +4
        title2 = Title("Non-coprime Failure: $4^{-1} \pmod{12}$")
        self.play(Write(title2))
        
        circle2 = Circle(radius=radius, color=WHITE)
        self.play(Create(circle2))
        
        labels2 = VGroup()
        for i in range(12):
            angle = PI/2 - i * (2 * PI / 12)
            pos = [radius * 1.2 * np.cos(angle), radius * 1.2 * np.sin(angle), 0]
            label = Integer(i).move_to(pos)
            labels2.add(label)
            
        ticks2 = VGroup()
        for i in range(12):
            angle = PI/2 - i * (2 * PI / 12)
            start_pos = [radius * 0.9 * np.cos(angle), radius * 0.9 * np.sin(angle), 0]
            end_pos = [radius * 1.0 * np.cos(angle), radius * 1.0 * np.sin(angle), 0]
            tick = Line(start_pos, end_pos, color=WHITE)
            ticks2.add(tick)
            
        self.play(FadeIn(labels2), FadeIn(ticks2))
        
        pointer2 = Arrow(start=ORIGIN, end=[radius * 0.8 * np.cos(PI/2), radius * 0.8 * np.sin(PI/2), 0], color=RED, buff=0)
        self.play(GrowArrow(pointer2))
        
        # Jumps 0 -> 4 -> 8 -> 0
        jumps2 = [4, 8, 0, 4]
        for k, jump in enumerate(jumps2):
            target_angle = PI/2 - jump * (2 * PI / 12)
            target_end = [radius * 0.8 * np.cos(target_angle), radius * 0.8 * np.sin(target_angle), 0]
            new_pointer = Arrow(start=ORIGIN, end=target_end, color=RED, buff=0)
            self.play(Transform(pointer2, new_pointer), labels2[jump].animate.set_color(RED))
            self.wait(0.5)
            
        # Warning text
        warning = Text("Trapped in a loop! Missed: 1, 2, 3, 5, 6, 7, 9, 10, 11", color=RED).scale(0.5)
        warning.next_to(circle2, DOWN, buff=0.5)
        concl2 = Text("gcd(4, 12) = 4 > 1. Inverse does not exist!", color=YELLOW).scale(0.5)
        concl2.next_to(warning, DOWN, buff=0.2)
        
        self.play(Write(warning))
        self.play(Write(concl2))
        self.wait(2)
