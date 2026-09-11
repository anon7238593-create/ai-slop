# Interactive Probability Lab

A comprehensive, intuitive web application for exploring probability theory through real-time physics simulations, counter-intuitive paradoxes, and mathematical sandboxes.

Deployed on GitHub Pages at: `https://anon7238593-create.github.io/ai-slop/probability.html`

---

## 10 Interactive Learning Modules

1. **Law of Large Numbers (LLN) & Coin Flipping Lab**:
   - Dynamic 3D coin tossing simulation with adjustable bias $p \in [0.01, 0.99]$.
   - Real-time convergence plot tracking running proportion $\hat{p}_n = \frac{H}{n} \to p$.
   - Live 95% error margin envelope $p \pm 1.96 \sqrt{\frac{p(1-p)}{n}}$ and maximum streak tracking.

2. **The Galton Board (Quincunx / Bean Machine)**:
   - 60fps HTML5 canvas 2D particle physics simulation of balls dropping through triangular rows of pegs ($R = 6 \dots 14$).
   - Visual physical proof of the Central Limit Theorem: binomial bin accumulation $B(R, p)$ converging into a smooth Gaussian bell curve.

3. **Dice Rolling & The Central Limit Theorem (CLT)**:
   - Roll $k = 1 \dots 8$ dice simultaneously from various input distributions (uniform, loaded, bimodal, exponential).
   - Demonstrates transition from uniform ($k=1$) to triangular ($k=2$) to Gaussian ($k \ge 3$).
   - Computes empirical vs theoretical sample mean $\mu$, variance $\sigma^2$, and standard deviation.

4. **The Monty Hall Paradox**:
   - Playable 3-door game show interface (Pick Door $\to$ Goat Revealed $\to$ Prompt: Switch or Stay?).
   - High-speed Monte Carlo simulator running up to 10,000 automated rounds comparing Stay (~33.3%) vs Switch (~66.7%).
   - Step-by-step intuitive tree explanation of why the host's selective reveal concentrates the remaining probability on the unopened door.

5. **Bayes' Theorem & Diagnostic Screener (Base Rate Fallacy)**:
   - 1,000-person interactive waffle chart color-coded by True Positives, False Positives, False Negatives, and True Negatives.
   - Sliders for Disease Prevalence $P(D)$, Test Sensitivity $P(+|D)$, and Specificity $P(-|\neg D)$.
   - Demonstrates why rare conditions lead to high False Discovery Rates despite 99% test accuracy.

6. **The Birthday Paradox & Collision Probability**:
   - Room generator visualizing people and their calendar birthdays with automatic collision detection and glowing alerts.
   - Plots the exact probability curve $P(N) = 1 - \prod_{k=0}^{N-1}\left(1 - \frac{k}{365}\right)$.
   - Highlights $N=23$ ($50.7\%$) and $N=50$ ($97.0\%$) milestones with $\binom{N}{2}$ pair comparison counter.

7. **Buffon's Needle ($\pi$ via Monte Carlo)**:
   - 2D canvas simulation of needles dropping on parallel floorboards.
   - Calculates $\pi \approx \frac{2L \cdot N}{D \cdot C}$ with live error tracking against true $\pi = 3.14159265...$

8. **Gambler's Ruin & Random Walk**:
   - 2D trajectory tracking of gambler balance between $\$0$ (Ruin) and $\$N$ (Goal).
   - Analytical absorption probabilities $P(\text{Ruin}) = \frac{(q/p)^N - (q/p)^k}{(q/p)^N - 1}$ demonstrating the devastating impact of even a 1% house edge.

9. **Probability Distributions Sandbox**:
   - Real-time parameter controls for Normal, Binomial, Poisson, Exponential, and Uniform distributions.
   - Dynamic integration calculating shaded area under the curve $P(x_1 \le X \le x_2)$.
   - Analytical displays for Expected Value $\mathbb{E}[X]$ and Variance $\text{Var}(X)$.

10. **Marble Urn Sampling (With vs. Without Replacement)**:
    - Urn containing Red, Green, and Blue marbles.
    - Compares independent sampling with replacement against dependent hypergeometric sampling without replacement.
    - Live tracking of dynamically updating probability fractions for subsequent draws.

---

## Technical Architecture

- **Zero External Dependencies**: Pure native modern HTML5, CSS3 Glassmorphism, Canvas 2D, and ES6 JavaScript.
- **High Performance**: Particle physics and animations run at 60 FPS using `requestAnimationFrame`.
- **Integrated & Standalone**: Accessible both as a dedicated full-page experience at `/probability.html` and directly embedded within the main `ai-slop` media showcase tab navigation.
