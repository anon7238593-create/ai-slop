#!/usr/bin/env python3
"""Manim scenes visualizing RSA key generation and its foundational number theory theorems:

1. FermatsLittleTheoremScene: Residue permutation and cyclic modular power proof
2. BezoutsIdentityScene: Extended Euclidean Algorithm tableau and back-substitution
3. EulersTheoremScene: Multiplicative totient grid sieve and generalized totient proof
4. ModularInverseScene: Modular clock stepping, coprimality condition, and inverse calculation
5. RSAKeyGenerationScene: Complete end-to-end keypair generation, encryption, decryption, and proof
"""

from __future__ import annotations

import math
from pathlib import Path
import sys
from manim import *

# Add current directory to path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from rsa_math import (
    extended_gcd_with_steps,
    modular_inverse,
    get_fermat_residues,
    get_euler_totient_data,
    generate_rsa_demo_keys,
)

# Visual styling constants
COLOR_GOLD = "#F59E0B"
COLOR_CYAN = "#06B6D4"
COLOR_EMERALD = "#10B981"
COLOR_CRIMSON = "#EF4444"
COLOR_PURPLE = "#A855F7"
COLOR_BLUE = "#3B82F6"
COLOR_DARK_PANEL = "#0F172A"


class FermatsLittleTheoremScene(Scene):
    """Scene 1: Fermat's Little Theorem and Residue Permutation Proof."""

    def construct(self):
        # 1. Header
        title = Text("Fermat's Little Theorem", font_size=32, weight=BOLD, color=WHITE).to_edge(UP, buff=0.35)
        subtitle = Text("If p is prime and gcd(a, p) = 1, then a^(p-1) = 1 (mod p)", font_size=18, color=COLOR_GOLD).next_to(title, DOWN, buff=0.12)
        self.play(FadeIn(title), FadeIn(subtitle), run_time=1.0)

        # 2. Main Theorem Card
        thm_box = Rectangle(width=11.5, height=1.3, color=COLOR_CYAN, fill_color=COLOR_DARK_PANEL, fill_opacity=0.9).next_to(subtitle, DOWN, buff=0.25)
        thm_eq = MathTex(r"a^{p-1} \equiv 1 \pmod{p} \quad \Longleftrightarrow \quad a^p \equiv a \pmod{p}", font_size=32, color=YELLOW).move_to(thm_box)
        self.play(Create(thm_box), Write(thm_eq), run_time=1.2)
        self.wait(0.5)

        # 3. Setup Concrete Example: p = 7 (prime), a = 3 (coprime)
        ex_label = Text("Step 1: Consider Non-Zero Residues mod 7 with multiplier a = 3", font_size=19, color=COLOR_CYAN, weight=BOLD).next_to(thm_box, DOWN, buff=0.3)
        self.play(FadeIn(ex_label), run_time=0.8)

        p = 7
        a = 3
        data = get_fermat_residues(a, p)
        
        # Display base set S = {1, 2, 3, 4, 5, 6}
        s_group = VGroup()
        s_label = MathTex(r"S = \{", font_size=26, color=WHITE)
        s_group.add(s_label)
        
        circles_s = VGroup()
        for idx, val in enumerate(data["base_set"]):
            circ = Circle(radius=0.32, color=BLUE_C, fill_color=BLUE_E, fill_opacity=0.8)
            num = Text(str(val), font_size=18, weight=BOLD, color=WHITE).move_to(circ)
            item = VGroup(circ, num)
            circles_s.add(item)
        circles_s.arrange(RIGHT, buff=0.25)
        s_group.add(circles_s)
        s_close = MathTex(r"\}", font_size=26, color=WHITE)
        s_group.add(s_close)
        s_group.arrange(RIGHT, buff=0.15).next_to(ex_label, DOWN, buff=0.25)
        
        self.play(FadeIn(s_group), run_time=1.0)
        self.wait(0.5)

        # Multiply by a = 3 mod 7
        mult_label = Text("Step 2: Multiply each element by 3 (mod 7):", font_size=19, color=COLOR_GOLD, weight=BOLD).next_to(s_group, DOWN, buff=0.3)
        self.play(FadeIn(mult_label), run_time=0.8)

        prod_group = VGroup()
        prod_label = MathTex(r"3 \cdot S \equiv \{", font_size=26, color=COLOR_GOLD)
        prod_group.add(prod_label)

        circles_prod = VGroup()
        for idx, mod_val in enumerate(data["multiplied_mod"]):
            circ = Circle(radius=0.32, color=COLOR_GOLD, fill_color="#78350F", fill_opacity=0.85)
            num = Text(str(mod_val), font_size=18, weight=BOLD, color=WHITE).move_to(circ)
            item = VGroup(circ, num)
            circles_prod.add(item)
        circles_prod.arrange(RIGHT, buff=0.25)
        prod_group.add(circles_prod)
        prod_close = MathTex(r"\}", font_size=26, color=COLOR_GOLD)
        prod_group.add(prod_close)
        prod_group.arrange(RIGHT, buff=0.15).next_to(mult_label, DOWN, buff=0.25)

        self.play(FadeIn(prod_group), run_time=1.0)
        self.wait(0.6)

        # 4. Highlight Permutation insight
        self.play(
            FadeOut(ex_label), FadeOut(mult_label),
            s_group.animate.to_edge(LEFT, buff=0.8).shift(UP * 0.2),
            prod_group.animate.to_edge(LEFT, buff=0.8).shift(DOWN * 0.8),
            run_time=0.8
        )

        perm_text = VGroup(
            Text("Crucial Lemma: Permutation of Residues", font_size=20, weight=BOLD, color=COLOR_EMERALD),
            Text("Multiplying by coprime 'a' simply permutes the set!", font_size=16, color=LIGHT_GRAY),
            MathTex(r"\prod_{x \in S} (3x) \equiv \prod_{x \in S} x \pmod{7}", font_size=26, color=YELLOW),
            MathTex(r"3^6 \cdot (6!) \equiv 6! \pmod{7}", font_size=26, color=COLOR_CYAN),
            MathTex(r"\gcd(6!, 7) = 1 \implies 3^6 \equiv 1 \pmod{7}", font_size=28, color=COLOR_EMERALD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_edge(RIGHT, buff=0.8).shift(DOWN * 0.3)

        perm_box = BackgroundRectangle(perm_text, color=COLOR_DARK_PANEL, fill_opacity=0.9, buff=0.2)
        self.play(FadeIn(perm_box), FadeIn(perm_text), run_time=1.5)
        self.wait(1.5)

        # Conclusion banner
        qed_box = Rectangle(width=11.5, height=0.9, color=COLOR_EMERALD, fill_color=COLOR_DARK_PANEL, fill_opacity=0.95).to_edge(DOWN, buff=0.3)
        qed_text = Text("Fermat's Theorem guarantees a^(p-1) = 1 (mod p) for all coprime a!", font_size=18, color=WHITE).move_to(qed_box)
        self.play(Create(qed_box), FadeIn(qed_text), run_time=0.8)
        self.wait(1.5)


class BezoutsIdentityScene(Scene):
    """Scene 2: Bézout's Identity & Extended Euclidean Algorithm."""

    def construct(self):
        title = Text("Bézout's Identity & Extended Euclidean Algorithm", font_size=30, weight=BOLD, color=WHITE).to_edge(UP, buff=0.35)
        subtitle = Text("For any integers a, b: there exist integers x, y such that a*x + b*y = gcd(a, b)", font_size=17, color=COLOR_GOLD).next_to(title, DOWN, buff=0.12)
        self.play(FadeIn(title), FadeIn(subtitle), run_time=1.0)

        # Role in RSA
        rsa_role = VGroup(
            Text("Why Bézout's Identity powers RSA Key Generation:", font_size=19, weight=BOLD, color=COLOR_CYAN),
            MathTex(r"e \cdot d \equiv 1 \pmod{\phi(n)} \iff e \cdot d + \phi(n) \cdot y = 1", font_size=26, color=YELLOW),
            Text("When gcd(e, phi(n)) = 1, Bézout guarantees private key 'd' exists!", font_size=16, color=LIGHT_GRAY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(LEFT, buff=0.8).shift(UP * 0.8)
        self.play(FadeIn(rsa_role), run_time=1.2)
        self.wait(0.5)

        # Concrete Demonstration: e = 17, phi(n) = 40
        calc_box = VGroup(
            Text("Concrete Example: e = 17, phi(n) = 40", font_size=20, weight=BOLD, color=COLOR_GOLD),
            Text("Step 1: Forward Euclidean Division Steps:", font_size=16, color=WHITE),
            MathTex(r"40 = 2 \times 17 + 6 \quad (\text{rem } 6)", font_size=22, color=LIGHT_GRAY),
            MathTex(r"17 = 2 \times 6 + 5 \quad (\text{rem } 5)", font_size=22, color=LIGHT_GRAY),
            MathTex(r"6 = 1 \times 5 + \mathbf{1} \quad (\gcd = 1)", font_size=22, color=COLOR_EMERALD),
            MathTex(r"5 = 5 \times 1 + 0", font_size=22, color=GRAY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14).to_edge(RIGHT, buff=0.8).shift(UP * 0.7)
        self.play(FadeIn(calc_box), run_time=1.5)
        self.wait(1.0)

        # Back Substitution Section
        back_sub = VGroup(
            Text("Step 2: Backward Substitution (Unrolling the GCD):", font_size=18, weight=BOLD, color=COLOR_PURPLE),
            MathTex(r"1 = 6 - 1 \times 5", font_size=24, color=WHITE),
            MathTex(r"1 = 6 - 1 \times (17 - 2 \times 6) = 3 \times 6 - 1 \times 17", font_size=24, color=COLOR_CYAN),
            MathTex(r"1 = 3 \times (40 - 2 \times 17) - 1 \times 17", font_size=24, color=WHITE),
            MathTex(r"\mathbf{1 = 3 \times 40 - 7 \times 17}", font_size=26, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(LEFT, buff=0.8).shift(DOWN * 1.5)
        
        self.play(FadeIn(back_sub), run_time=1.8)
        self.wait(1.0)

        # Result Banner
        res_box = VGroup(
            Text("Bézout Solution:", font_size=18, weight=BOLD, color=COLOR_EMERALD),
            MathTex(r"17 \times (-7) + 40 \times 3 = 1", font_size=24, color=COLOR_GOLD),
            MathTex(r"-7 \equiv 33 \pmod{40} \implies d = 33", font_size=24, color=COLOR_EMERALD),
            Text("Check: 17 * 33 = 561 = 14*40 + 1", font_size=16, color=LIGHT_GRAY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(RIGHT, buff=0.8).shift(DOWN * 1.5)
        self.play(FadeIn(res_box), run_time=1.2)
        self.wait(1.5)


class EulersTheoremScene(Scene):
    """Scene 3: Euler's Totient Theorem & Multiplicativity Grid."""

    def construct(self):
        title = Text("Euler's Totient Theorem & The Sieve Grid", font_size=30, weight=BOLD, color=WHITE).to_edge(UP, buff=0.35)
        subtitle = Text("If gcd(a, n) = 1, then a^(phi(n)) = 1 (mod n)", font_size=17, color=COLOR_GOLD).next_to(title, DOWN, buff=0.12)
        self.play(FadeIn(title), FadeIn(subtitle), run_time=1.0)

        # Part 1: Definition of phi(n)
        def_card = VGroup(
            Text("Euler's Totient Function phi(n):", font_size=19, weight=BOLD, color=COLOR_CYAN),
            Text("Counts integers 1 <= k <= n that share NO common factor with n (gcd(k, n) = 1)", font_size=16, color=LIGHT_GRAY),
            MathTex(r"\text{For prime } p: \quad \phi(p) = p - 1", font_size=24, color=YELLOW),
            MathTex(r"\text{For RSA modulus } n = p \cdot q: \quad \phi(p \cdot q) = (p - 1)(q - 1)", font_size=24, color=COLOR_EMERALD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(LEFT, buff=0.8).shift(UP * 0.9)
        self.play(FadeIn(def_card), run_time=1.2)
        self.wait(0.5)

        # Part 2: Visual Grid Proof for phi(p*q) = (p-1)(q-1)
        # Take p = 3, q = 5 -> n = 15
        grid_title = Text("Visual Sieve: n = 3 * 5 = 15", font_size=18, weight=BOLD, color=COLOR_GOLD).to_edge(RIGHT, buff=1.8).shift(UP * 1.9)
        self.play(FadeIn(grid_title), run_time=0.6)

        grid_group = VGroup()
        p_val, q_val = 3, 5
        data = get_euler_totient_data(p_val, q_val)

        for row in range(p_val):
            row_grp = VGroup()
            for col in range(q_val):
                num = row * q_val + col + 1
                is_mult_p = (num % p_val == 0)
                is_mult_q = (num % q_val == 0)
                
                if num in data["coprime_residues"]:
                    c_color = COLOR_EMERALD
                    fill_c = "#064E3B"
                elif is_mult_p and is_mult_q:
                    c_color = COLOR_CRIMSON
                    fill_c = "#7F1D1D"
                elif is_mult_p:
                    c_color = COLOR_CRIMSON
                    fill_c = "#7F1D1D"
                else:
                    c_color = COLOR_GOLD
                    fill_c = "#78350F"
                    
                sq = Square(side_length=0.65, color=c_color, fill_color=fill_c, fill_opacity=0.85)
                lbl = Text(str(num), font_size=16, weight=BOLD, color=WHITE).move_to(sq)
                cell = VGroup(sq, lbl)
                row_grp.add(cell)
            row_grp.arrange(RIGHT, buff=0.1)
            grid_group.add(row_grp)
        grid_group.arrange(DOWN, buff=0.1).next_to(grid_title, DOWN, buff=0.25)
        
        self.play(FadeIn(grid_group), run_time=1.5)
        self.wait(0.6)

        # Count explanation below grid
        sieve_explain = VGroup(
            Text("Eliminate Multiples of 3: {3, 6, 9, 12, 15} (5 numbers)", font_size=14, color=COLOR_CRIMSON),
            Text("Eliminate Multiples of 5: {5, 10, 15} (3 numbers)", font_size=14, color=COLOR_GOLD),
            Text("Double counted 15 -> Total eliminated = 3 + 5 - 1 = 7", font_size=14, color=LIGHT_GRAY),
            MathTex(r"\phi(15) = 15 - 7 = 8 = (3 - 1)(5 - 1)", font_size=20, color=COLOR_EMERALD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(grid_group, DOWN, buff=0.25)
        self.play(FadeIn(sieve_explain), run_time=1.2)
        self.wait(0.8)

        # Part 3: Proof of Euler's Totient Theorem
        proof_card = VGroup(
            Text("Proof of Euler's Generalization:", font_size=18, weight=BOLD, color=COLOR_CYAN),
            Text("Let R = {r1, r2, ..., r_phi(n)} be residues coprime to n.", font_size=15, color=LIGHT_GRAY),
            MathTex(r"\prod_{i=1}^{\phi(n)} (a \cdot r_i) \equiv \prod_{i=1}^{\phi(n)} r_i \pmod{n}", font_size=22, color=YELLOW),
            MathTex(r"a^{\phi(n)} \cdot \prod r_i \equiv \prod r_i \pmod{n} \implies \mathbf{a^{\phi(n)} \equiv 1 \pmod{n}}", font_size=24, color=COLOR_EMERALD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14).to_edge(LEFT, buff=0.8).shift(DOWN * 1.5)
        self.play(FadeIn(proof_card), run_time=1.5)
        self.wait(1.5)


class ModularInverseScene(Scene):
    """Scene 4: Modular Multiplicative Inverse & Clock Stepping."""

    def construct(self):
        title = Text("The Modular Multiplicative Inverse", font_size=30, weight=BOLD, color=WHITE).to_edge(UP, buff=0.35)
        subtitle = Text("Finding x = a^(-1) (mod m) such that a * x = 1 (mod m)", font_size=17, color=COLOR_GOLD).next_to(title, DOWN, buff=0.12)
        self.play(FadeIn(title), FadeIn(subtitle), run_time=1.0)

        # Concept
        concept = VGroup(
            Text("Division Does Not Exist in Modular Arithmetic!", font_size=19, weight=BOLD, color=COLOR_CRIMSON),
            Text("Integers cannot be fractions. Instead, we multiply by the modular inverse:", font_size=16, color=LIGHT_GRAY),
            MathTex(r"a \cdot x \equiv 1 \pmod{m} \iff x \equiv a^{-1} \pmod{m}", font_size=26, color=YELLOW),
            Text("Exists IF AND ONLY IF gcd(a, m) = 1 (coprime)!", font_size=17, color=COLOR_EMERALD, weight=BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(LEFT, buff=0.8).shift(UP * 0.8)
        self.play(FadeIn(concept), run_time=1.2)
        self.wait(0.6)

        # Clock Visual: Modulo 11 Clock
        m = 11
        a = 3
        clock_radius = 1.8
        center = RIGHT * 3.5 + DOWN * 0.2
        clock_circ = Circle(radius=clock_radius, color=BLUE_C, stroke_width=3).move_to(center)
        self.play(Create(clock_circ), run_time=0.8)

        ticks = VGroup()
        angles = []
        for i in range(m):
            # Clock angle: 0 at top, clockwise
            angle = math.pi / 2 - (2 * math.pi * i / m)
            angles.append(angle)
            pos = center + np.array([math.cos(angle) * clock_radius, math.sin(angle) * clock_radius, 0])
            lbl_pos = center + np.array([math.cos(angle) * (clock_radius + 0.35), math.sin(angle) * (clock_radius + 0.35), 0])
            dot = Dot(pos, radius=0.06, color=COLOR_CYAN)
            lbl = Text(str(i), font_size=16, weight=BOLD, color=WHITE).move_to(lbl_pos)
            ticks.add(VGroup(dot, lbl))
        self.play(FadeIn(ticks), run_time=1.0)

        # Animate steps: 3 * k mod 11
        step_box = VGroup(
            Text("Stepping by 3 mod 11:", font_size=18, weight=BOLD, color=COLOR_GOLD),
            MathTex(r"3 \times 1 = 3 \equiv 3 \pmod{11}", font_size=20, color=WHITE),
            MathTex(r"3 \times 2 = 6 \equiv 6 \pmod{11}", font_size=20, color=WHITE),
            MathTex(r"3 \times 3 = 9 \equiv 9 \pmod{11}", font_size=20, color=WHITE),
            MathTex(r"3 \times \mathbf{4} = 12 \equiv \mathbf{1} \pmod{11} \quad \text{SUCCESS!}", font_size=22, color=COLOR_EMERALD),
            MathTex(r"\mathbf{3^{-1} \equiv 4 \pmod{11}}", font_size=26, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14).to_edge(LEFT, buff=0.8).shift(DOWN * 1.5)

        self.play(FadeIn(step_box), run_time=1.5)

        # Highlight position 1 on clock
        pos_1 = center + np.array([math.cos(angles[1]) * clock_radius, math.sin(angles[1]) * clock_radius, 0])
        hit_target = Circle(radius=0.25, color=COLOR_EMERALD, stroke_width=4).move_to(pos_1)
        hit_label = Text("Target = 1", font_size=14, color=COLOR_EMERALD, weight=BOLD).next_to(hit_target, UP, buff=0.1)
        self.play(Create(hit_target), FadeIn(hit_label), run_time=0.8)
        self.wait(1.0)

        # Counterexample failure when gcd > 1
        fail_box = VGroup(
            Text("Why gcd(a, m) = 1 is strictly mandatory:", font_size=16, weight=BOLD, color=COLOR_CRIMSON),
            Text("Try finding 4^(-1) mod 12: gcd(4, 12) = 4 != 1", font_size=14, color=LIGHT_GRAY),
            Text("Multiples: {0, 4, 8, 0, 4, 8...} NEVER hits 1!", font_size=14, color=COLOR_CRIMSON),
            Text("Trapped in subgroup of multiples of gcd!", font_size=14, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(clock_circ, DOWN, buff=0.6)
        self.play(FadeIn(fail_box), run_time=1.0)
        self.wait(1.5)


class RSAKeyGenerationScene(Scene):
    """Scene 5: Complete RSA Key Generation, Encryption, Decryption & Proof."""

    def construct(self):
        # 1. Master Title
        title = Text("RSA Cryptosystem: Key Generation & Verification", font_size=30, weight=BOLD, color=WHITE).to_edge(UP, buff=0.35)
        subtitle = Text("Rivest, Shamir, Adleman (1977) • Powered by Number Theory", font_size=17, color=COLOR_GOLD).next_to(title, DOWN, buff=0.12)
        self.play(FadeIn(title), FadeIn(subtitle), run_time=1.0)

        # 2. Key Generation Protocol (Left Column)
        keys = generate_rsa_demo_keys(11, 13, 7)
        p, q, n, phi, e, d = keys["p"], keys["q"], keys["n"], keys["phi"], keys["e"], keys["d"]

        keygen_card = VGroup(
            Text("Key Generation Protocol:", font_size=20, weight=BOLD, color=COLOR_CYAN),
            MathTex(r"1.\ \text{Select distinct primes: } p = 11, \ q = 13", font_size=22, color=WHITE),
            MathTex(r"2.\ \text{Compute public modulus: } n = p \cdot q = 11 \times 13 = \mathbf{143}", font_size=22, color=COLOR_GOLD),
            MathTex(r"3.\ \text{Euler Totient: } \phi(n) = (p-1)(q-1) = 10 \times 12 = \mathbf{120}", font_size=22, color=COLOR_CYAN),
            MathTex(r"4.\ \text{Choose public exponent: } e = 7 \quad (\gcd(7, 120) = 1)", font_size=22, color=YELLOW),
            MathTex(r"5.\ \text{Compute private exponent via Bézout: } 7 d \equiv 1 \pmod{120}", font_size=22, color=COLOR_PURPLE),
            MathTex(r"   \quad 7 \times 103 = 721 = 6 \times 120 + 1 \implies \mathbf{d = 103}", font_size=22, color=COLOR_EMERALD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(LEFT, buff=0.7).shift(UP * 0.3)

        self.play(FadeIn(keygen_card), run_time=2.0)
        self.wait(0.8)

        # Public & Private Key Badges
        key_badges = VGroup()
        
        pub_box = Rectangle(width=4.8, height=1.1, color=COLOR_GOLD, fill_color=COLOR_DARK_PANEL, fill_opacity=0.9)
        pub_txt = VGroup(
            Text("PUBLIC KEY (Share with world):", font_size=14, weight=BOLD, color=COLOR_GOLD),
            MathTex(r"(e, n) = (\mathbf{7}, \mathbf{143})", font_size=24, color=WHITE),
        ).arrange(DOWN, buff=0.08).move_to(pub_box)
        pub_badge = VGroup(pub_box, pub_txt)

        priv_box = Rectangle(width=4.8, height=1.1, color=COLOR_CRIMSON, fill_color=COLOR_DARK_PANEL, fill_opacity=0.9)
        priv_txt = VGroup(
            Text("PRIVATE KEY (Keep strictly secret!):", font_size=14, weight=BOLD, color=COLOR_CRIMSON),
            MathTex(r"(d, n) = (\mathbf{103}, \mathbf{143})", font_size=24, color=WHITE),
        ).arrange(DOWN, buff=0.08).move_to(priv_box)
        priv_badge = VGroup(priv_box, priv_txt)

        key_badges.add(pub_badge, priv_badge).arrange(DOWN, buff=0.25).to_edge(RIGHT, buff=0.7).shift(UP * 0.9)
        self.play(FadeIn(key_badges), run_time=1.2)
        self.wait(0.8)

        # 3. Encryption & Decryption Live Demonstration
        crypto_demo = VGroup(
            Text("Encryption & Decryption Demonstration:", font_size=18, weight=BOLD, color=COLOR_EMERALD),
            MathTex(r"\text{Plaintext Message: } M = \mathbf{9}", font_size=22, color=COLOR_CYAN),
            MathTex(r"\text{Encrypt: } C = M^e \pmod{n} = 9^7 \pmod{143} = \mathbf{48}", font_size=22, color=COLOR_PURPLE),
            MathTex(r"\text{Transmit Ciphertext: } C = 48 \text{ over public network}", font_size=18, color=LIGHT_GRAY),
            MathTex(r"\text{Decrypt: } M' = C^d \pmod{n} = 48^{103} \pmod{143} = \mathbf{9}", font_size=22, color=COLOR_EMERALD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(key_badges, DOWN, buff=0.25)
        self.play(FadeIn(crypto_demo), run_time=1.5)
        self.wait(1.0)

        # 4. Transition to Mathematical Correctness Proof
        self.play(
            FadeOut(keygen_card), FadeOut(key_badges), FadeOut(crypto_demo),
            run_time=0.8
        )

        proof_header = Text("Mathematical Proof of Correctness (Synthesizing All Theorems)", font_size=22, weight=BOLD, color=COLOR_GOLD).to_edge(UP, buff=1.2)
        self.play(FadeIn(proof_header), run_time=0.6)

        proof_steps = VGroup(
            MathTex(r"\text{By definition of Decryption: } M' \equiv C^d \equiv (M^e)^d \equiv M^{e \cdot d} \pmod{n}", font_size=24, color=WHITE),
            MathTex(r"\text{Since } e \cdot d \equiv 1 \pmod{\phi(n)}, \text{ there exists integer } k \text{ such that:}", font_size=22, color=COLOR_CYAN),
            MathTex(r"e \cdot d = 1 + k \cdot \phi(n)", font_size=28, color=YELLOW),
            MathTex(r"M^{e \cdot d} = M^{1 + k \cdot \phi(n)} = M^1 \cdot \left( M^{\phi(n)} \right)^k \pmod{n}", font_size=24, color=WHITE),
            MathTex(r"\text{By Euler's Totient Theorem: } M^{\phi(n)} \equiv 1 \pmod{n}", font_size=24, color=COLOR_GOLD),
            MathTex(r"M \cdot (1)^k \equiv \mathbf{M} \pmod{n} \quad \blacksquare", font_size=28, color=COLOR_EMERALD),
        ).arrange(DOWN, buff=0.22).next_to(proof_header, DOWN, buff=0.3)

        for step in proof_steps:
            self.play(FadeIn(step), run_time=0.9)
            self.wait(0.3)

        # Summary footer connecting all 4 theorems
        summary_footer = Rectangle(width=12.0, height=0.85, color=COLOR_CYAN, fill_color=COLOR_DARK_PANEL, fill_opacity=0.95).to_edge(DOWN, buff=0.25)
        summary_txt = Text("Fermat's + Euler's Totient + Bézout's Identity + Modular Inverse = Unbreakable RSA", font_size=16, color=WHITE).move_to(summary_footer)
        self.play(Create(summary_footer), FadeIn(summary_txt), run_time=0.8)
        self.wait(2.0)
