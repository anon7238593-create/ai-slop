# Mathematical Fractal SVG Generator & Explorer

A dependency-free Python suite for generating scalable vector graphics (SVG) of mathematical fractals categorized across three difficulty tiers: **Easy** (elementary recursive geometry), **Medium** (branching trees & space-filling curves), and **Hard** (iterated function systems & complex dynamical basins).

---

## Table of Contents

1. [Foundations of Fractal Geometry](#foundations-of-fractal-geometry)
   - [Hausdorff & Similarity Dimension](#hausdorff--similarity-dimension)
   - [The Contraction Mapping Principle](#the-contraction-mapping-principle)
   - [Difficulty Classification Taxonomy](#difficulty-classification-taxonomy)
2. [Level 1: Easy (Elementary Recursive Geometry)](#level-1-easy-elementary-recursive-geometry)
   - [1. Cantor Set Ladder](#1-cantor-set-ladder)
   - [2. Koch Snowflake](#2-koch-snowflake)
   - [3. Sierpiński Triangle (Gasket)](#3-sierpiński-triangle-gasket)
   - [4. Sierpiński Carpet](#4-sierpiński-carpet)
   - [5. Vicsek Box Fractal](#5-vicsek-box-fractal)
3. [Level 2: Medium (Branching Trees & Space-Filling Curves)](#level-2-medium-branching-trees--space-filling-curves)
   - [6. Pythagoras Tree](#6-pythagoras-tree)
   - [7. Heighway Dragon Curve](#7-heighway-dragon-curve)
   - [8. Hilbert Space-Filling Curve](#8-hilbert-space-filling-curve)
   - [9. Fractal Binary Canopy](#9-fractal-binary-canopy)
   - [10. Lévy C Curve](#10-lévy-c-curve)
4. [Level 3: Hard (Iterated Function Systems & Complex Dynamics)](#level-3-hard-iterated-function-systems--complex-dynamics)
   - [11. Barnsley Fern (Chaos Game IFS)](#11-barnsley-fern-chaos-game-ifs)
   - [12. Gosper Curve (Flowsnake)](#12-gosper-curve-flowsnake)
   - [13. Mandelbrot Set Boundary Contours](#13-mandelbrot-set-boundary-contours)
   - [14. Julia Set (Douady's Rabbit)](#14-julia-set-douadys-rabbit)
   - [15. Newton-Raphson Basins of Attraction](#15-newton-raphson-basins-of-attraction)
5. [CLI Reference & Generator Guide](#cli-reference--generator-guide)
6. [Color Palettes & SVG Design Principles](#color-palettes--svg-design-principles)
7. [Unit Testing & Verification](#unit-testing--verification)

---

## Foundations of Fractal Geometry

The word **fractal** was coined by mathematician **Benoît Mandelbrot** in 1975 from the Latin *fractus* ("broken" or "fractured"). A fractal is a subset of Euclidean space whose topological dimension is strictly exceeded by its Hausdorff dimension:

$$\dim_{\text{top}}(E) < \dim_H(E)$$

Unlike smooth Euclidean shapes (lines, circles, polyhedra) whose scaling behavior is integer-dimensional, fractals possess fine structure at arbitrarily small scales and exhibit **exact**, **quasi-**, or **statistical self-similarity**.

### Hausdorff & Similarity Dimension

For a strictly self-similar fractal constructed by replacing an initial geometric shape with $N$ non-overlapping copies, each scaled by a factor of $s < 1$, the **similarity dimension** $D$ satisfies:

$$N \cdot s^D = 1 \implies D = \frac{\log N}{\log(1/s)}$$

For arbitrary geometric sets $E \subset \mathbb{R}^n$, the **Hausdorff dimension** $\dim_H(E)$ is defined via the $d$-dimensional Hausdorff outer measure:

$$\mathcal{H}^d(E) = \lim_{\delta \to 0} \inf \left\{ \sum_{i=1}^\infty (\text{diam}\, U_i)^d : E \subseteq \bigcup_{i=1}^\infty U_i,\; \text{diam}\, U_i \le \delta \right\}$$

The critical exponent at which $\mathcal{H}^d(E)$ drops from $\infty$ to $0$ is $\dim_H(E)$:

$$\dim_H(E) = \inf \{ d \ge 0 : \mathcal{H}^d(E) = 0 \} = \sup \{ d \ge 0 : \mathcal{H}^d(E) = \infty \}$$

### The Contraction Mapping Principle

An **Iterated Function System (IFS)** consists of a finite collection of contraction mappings $\{f_1, f_2, \dots, f_m\}$ on a complete metric space $(X, d)$, where each mapping has Lipschitz constant $c_i < 1$:

$$d(f_i(x), f_i(y)) \le c_i \cdot d(x, y) \quad \forall x, y \in X$$

By **Hutchinson's Theorem (1981)**, there exists a unique non-empty compact attractor $K \subset X$ such that:

$$K = \bigcup_{i=1}^m f_i(K)$$

### Difficulty Classification Taxonomy

| Tier | Characteristics | Mathematical Complexity | Memory & Recursion Pattern |
|---|---|---|---|
| **Level 1: Easy** | Exact self-similarity, fixed-ratio planar subdivisions, segment excision | Direct geometric substitution, simple logarithmic ratios | Depth-first or breadth-first tree recursion ($O(b^d)$ nodes) |
| **Level 2: Medium** | Rotation matrices, stateful angle tracking, space-filling continuity, paper folding | Orthogonal transformations $SO(2)$, continuous surjections $\mathbb{R} \to \mathbb{R}^2$, bit-interleaving | Lindenmayer grammars, quadrant mapping bit-shifts |
| **Level 3: Hard** | Non-linear complex mapping $z \mapsto z^2 + c$, affine probability distributions, multi-root convergence basins | Quadratic Julia sets, Fatou sets, Chaos Game invariant measures, Newton-Raphson vector fields | Adaptive grid sampling, iterative floating-point dynamics, contour grouping |

---

## Level 1: Easy (Elementary Recursive Geometry)

### 1. Cantor Set Ladder
- **ID**: `cantor_set`
- **Difficulty**: Easy
- **Hausdorff Dimension**: $D = \frac{\log 2}{\log 3} \approx 0.6309$
- **Axiom**: Unit interval $C_0 = [0, 1]$

#### How It Works
1. Let $C_0 = [0, 1]$.
2. At step 1, remove the open middle third: $C_1 = [0, 1/3] \cup [2/3, 1]$.
3. At step $n$, remove the open middle third of each of the $2^{n-1}$ remaining intervals:
   $$C_n = \frac{C_{n-1}}{3} \cup \left(\frac{C_{n-1}}{3} + \frac{2}{3}\right)$$
4. The limiting Cantor set $C_\infty = \bigcap_{n=0}^\infty C_n$ is:
   - **Uncountable** (has cardinality $2^{\aleph_0}$, identical to the continuum $\mathbb{R}$).
   - **Zero Lebesgue Measure**:
     $$\mu(C_\infty) = 1 - \sum_{k=1}^\infty \frac{2^{k-1}}{3^k} = 1 - \frac{1/3}{1 - 2/3} = 0$$
   - **Nowhere Dense**: Contains no isolated points and no open intervals.

---

### 2. Koch Snowflake
- **ID**: `koch_snowflake`
- **Difficulty**: Easy
- **Hausdorff Dimension**: $D = \frac{\log 4}{\log 3} \approx 1.2619$
- **Axiom**: Equilateral triangle with perimeter $P_0 = 3s_0$ and area $A_0 = \frac{\sqrt{3}}{4} s_0^2$

#### How It Works
1. Each straight line segment of length $L$ is divided into 3 equal sub-segments of length $L/3$.
2. An outward-pointing equilateral triangle of side $L/3$ is constructed over the middle third.
3. The original base segment is removed, yielding 4 new segments each scaled by factor $s = 1/3$.
4. **Perimeter Divergence**:
   $$P_n = P_0 \left(\frac{4}{3}\right)^n \xrightarrow{n \to \infty} \infty$$
5. **Bounded Area**:
   Each iteration adds $3 \cdot 4^{n-1}$ smaller triangles of area $A_n = A_0 / 9^n$. Summing the geometric series:
   $$A_\infty = A_0 \left(1 + \frac{1}{3} \sum_{k=1}^\infty \left(\frac{4}{9}\right)^k\right) = \frac{8}{5} A_0$$
   The Koch snowflake proves that a curve of **infinite length** can enclose a **strictly finite area**.

---

### 3. Sierpiński Triangle (Gasket)
- **ID**: `sierpinski_triangle`
- **Difficulty**: Easy
- **Hausdorff Dimension**: $D = \frac{\log 3}{\log 2} \approx 1.5850$
- **Axiom**: Filled equilateral triangle $T_0$

#### How It Works
1. Connect the midpoints of the three edges of triangle $T$.
2. Remove the central inverted triangle of area $1/4 \cdot \text{Area}(T)$.
3. Recursively apply the same procedure to the remaining 3 corner triangles:
   $$N = 3, \quad s = \frac{1}{2} \implies D = \frac{\log 3}{\log 2} \approx 1.5850$$
4. **Lebesgue Measure**:
   $$\text{Area}(T_n) = A_0 \left(\frac{3}{4}\right)^n \xrightarrow{n \to \infty} 0$$
   The Sierpiński gasket is also isomorphic to:
   - Pascal's triangle modulo 2 (odd binomial coefficients $\binom{n}{k} \equiv 1 \pmod 2$).
   - Cellular automaton Rule 90.

---

### 4. Sierpiński Carpet
- **ID**: `sierpinski_carpet`
- **Difficulty**: Easy
- **Hausdorff Dimension**: $D = \frac{\log 8}{\log 3} \approx 1.8928$
- **Axiom**: Solid square $[0, 1] \times [0, 1]$

#### How It Works
1. Divide the square into a $3 \times 3$ grid of 9 identical sub-squares of side $s = 1/3$.
2. Cut out the open central square $(1/3, 2/3) \times (1/3, 2/3)$.
3. Repeat recursively on the remaining 8 squares:
   $$N = 8, \quad s = \frac{1}{3} \implies D = \frac{\log 8}{\log 3} \approx 1.8928$$
4. **Universal Curve Property**:
   By Menger's universal curve theorem, the 3D Menger sponge (and its 2D cross-section, the Sierpiński carpet) can embed any 1-dimensional compact metric space topologically!

---

### 5. Vicsek Box Fractal
- **ID**: `vicsek_fractal`
- **Difficulty**: Easy
- **Hausdorff Dimension**: $D = \frac{\log 5}{\log 3} \approx 1.4650$
- **Axiom**: Solid square $[0, 1] \times [0, 1]$

#### How It Works
1. Subdivide the square into a $3 \times 3$ grid of 9 congruent squares.
2. Retain only 5 squares: the central square and the 4 orthogonal edge/corner squares (forming a plus/cross symbol).
3. The remaining 4 corner squares are removed:
   $$N = 5, \quad s = \frac{1}{3} \implies D = \frac{\log 5}{\log 3} \approx 1.4650$$
4. Widely used in antenna engineering to construct compact multiband electromagnetic resonators.

---

## Level 2: Medium (Branching Trees & Space-Filling Curves)

### 6. Pythagoras Tree
- **ID**: `pythagoras_tree`
- **Difficulty**: Medium
- **Hausdorff Dimension**: $D = 2.0000$ (with boundary self-intersections)
- **Axiom**: Base square on the horizontal axis

#### How It Works
1. Start with a square of side $s$.
2. On its top edge, erect a right-angled triangle with acute angles $\alpha$ and $90^\circ - \alpha$.
3. Construct two new squares on the catheti (legs) of lengths $s \cos \alpha$ and $s \sin \alpha$.
4. By the Pythagorean theorem:
   $$(s \cos \alpha)^2 + (s \sin \alpha)^2 = s^2 (\cos^2 \alpha + \sin^2 \alpha) = s^2$$
   The total area of the two new squares precisely equals the area of the parent square!
5. In symmetric mode ($\alpha = 45^\circ$), each step scales by factor $1/\sqrt{2}$.

---

### 7. Heighway Dragon Curve
- **ID**: `dragon_curve`
- **Difficulty**: Medium
- **Hausdorff Dimension**:
  - Full curve dimension: $D = 2$ (fills a planar tile)
  - Boundary fractal dimension: $D = \frac{\log \lambda}{\log \sqrt{2}} \approx 1.5236$ (where $\lambda \approx 1.6956$ is the real root of $x^3 - x^2 - 2 = 0$)

#### How It Works
1. Repeatedly fold a strip of paper in half in the same direction $n$ times.
2. Unfold every fold to a right angle ($90^\circ$).
3. **Lindenmayer Rewrite Grammar**:
   - Variables: $X, Y$
   - Constants: $F, +, -$
   - Axiom: $FX$
   - Rules:
     $$X \to X + YF +$$
     $$Y \to - FX - Y$$
   Here $+$ denotes turn $+90^\circ$, $-$ denotes turn $-90^\circ$, and $F$ denotes step forward.
4. Four copies of the Heighway dragon curve meet at a central point and tile the entire 2D plane without any gaps or overlaps.

---

### 8. Hilbert Space-Filling Curve
- **ID**: `hilbert_curve`
- **Difficulty**: Medium
- **Hausdorff Dimension**: $D = \frac{\log 4}{\log 2} = 2.0000$
- **Axiom**: Unit square $[0, 1] \times [0, 1]$

#### How It Works
1. Discovered by David Hilbert in 1891, it is a continuous mapping $h: [0, 1] \to [0, 1]^2$ whose image is the entire unit square.
2. At order $k$, the curve partitions the square into $2^k \times 2^k$ grid cells and threads a continuous path through all $4^k$ cell centers.
3. **Locality-Preserving Property**:
   Points close in 1D along the curve remain close in 2D space.
4. **Computational Applications**:
   - Spatial database R-trees and geo-indexing (Geohash / Uber H3).
   - CPU memory layout cache optimization for multidimensional matrices.

---

### 9. Fractal Binary Canopy
- **ID**: `fractal_canopy`
- **Difficulty**: Medium
- **Dimension Parameter**: Da Vinci vascular conservation
- **Axiom**: Vertical trunk line segment

#### How It Works
1. From the tip of a parent branch of length $L$ and diameter $d$, spawn two child branches.
2. Branch lengths shrink by ratio $r \approx 0.74$: $L_{\text{child}} = r \cdot L_{\text{parent}}$.
3. Child angles diverge symmetrically by $\pm \theta$ (typically $\theta \approx 25^\circ \dots 35^\circ$).
4. **Leonardo da Vinci's Branching Law (1500)**:
   All the branches of a tree at every stage of its height when put together are equal in thickness to the trunk:
   $$d_{\text{parent}}^2 = d_{\text{left}}^2 + d_{\text{right}}^2 \implies d_{\text{child}} = \frac{d_{\text{parent}}}{\sqrt{2}}$$
   This minimizes hydrodynamic fluid resistance according to the Hagen-Poiseuille law for sap flow.

---

### 10. Lévy C Curve
- **ID**: `levy_c_curve`
- **Difficulty**: Medium
- **Hausdorff Dimension**: $D = \frac{\log 2}{\log \sqrt{2}} = 2$ (curve boundary $D \approx 1.934$)
- **Axiom**: Line segment connecting $(x_1, y_1)$ to $(x_2, y_2)$

#### How It Works
1. Given a segment $AB$, construct an isosceles right triangle with hypotenuse $AB$.
2. Replace segment $AB$ with the two legs $AC$ and $CB$.
3. The coordinates of apex $C$ rotated $45^\circ$:
   $$x_C = \frac{x_A + x_B}{2} - \frac{y_B - y_A}{2}, \quad y_C = \frac{y_A + y_B}{2} + \frac{x_B - x_A}{2}$$
4. Iterating recursively produces an intricate shoreline fractal with internal self-similar spiral chambers.

---

## Level 3: Hard (Iterated Function Systems & Complex Dynamics)

### 11. Barnsley Fern (Chaos Game IFS)
- **ID**: `barnsley_fern`
- **Difficulty**: Hard
- **Hausdorff Dimension**: $D \approx 1.8600$
- **Axiom**: Point $(0, 0) \in \mathbb{R}^2$

#### How It Works
Michael Barnsley described this Iterated Function System in 1988 to model the natural black spleenwort fern (*Asplenium adiantum-nigrum*). It uses 4 affine transformations $f_i(\mathbf{x}) = A_i \mathbf{x} + \mathbf{b}_i$:

$$\begin{bmatrix} x_{n+1} \\ y_{n+1} \end{bmatrix} = \begin{bmatrix} a & b \\ c & d \end{bmatrix} \begin{bmatrix} x_n \\ y_n \end{bmatrix} + \begin{bmatrix} e \\ f \end{bmatrix}$$

| Transformation | $a$ | $b$ | $c$ | $d$ | $e$ | $f$ | Probability $p$ | Anatomical Feature |
|---|---|---|---|---|---|---|---|---|
| $f_1$ | $0$ | $0$ | $0$ | $0.16$ | $0$ | $0$ | $0.01$ | Stem base |
| $f_2$ | $0.85$ | $0.04$ | $-0.04$ | $0.85$ | $0$ | $1.60$ | $0.85$ | Successively smaller fronds |
| $f_3$ | $0.20$ | $-0.26$ | $0.23$ | $0.22$ | $0$ | $1.60$ | $0.07$ | Largest left leaflet |
| $f_4$ | $-0.15$ | $0.28$ | $0.26$ | $0.24$ | $0$ | $0.44$ | $0.07$ | Largest right leaflet |

By playing the **Chaos Game**, a random sequence of transformations is selected according to probabilities $p_i$. The trajectory asymptotically visits the unique invariant measure supported on the fractal fern attractor.

---

### 12. Gosper Curve (Flowsnake)
- **ID**: `gosper_curve`
- **Difficulty**: Hard
- **Hausdorff Dimension**: $D = \frac{\log 7}{\log \sqrt{7}} = 2.0000$ (Fractal boundary $D = \frac{\log 3}{\log \sqrt{7}} \approx 1.129$)
- **Axiom**: $A$

#### How It Works
A hexagonal space-filling curve discovered by Bill Gosper. It uses an L-system alphabet where the angle increment is $\delta = 60^\circ$:
- **Grammar**:
  $$A \to A - B - - B + A + + A A + B -$$
  $$B \to + A - B B - - B - A + + A + B$$
- Fills a regular hexagon-like region called the **Gosper island** or **flowsnake**.
- Seven Gosper flakes tile together to form an exact scaled-up replica of the island.

---

### 13. Mandelbrot Set Boundary Contours
- **ID**: `mandelbrot_set`
- **Difficulty**: Hard
- **Hausdorff Dimension**: $\dim_H(\partial M) = 2.0000$ (proved by Mitsuhiro Shishikura, 1998)
- **Definition**: The set of complex parameters $c \in \mathbb{C}$ for which the orbit of 0 under $f_c(z) = z^2 + c$ remains bounded:
  $$M = \{ c \in \mathbb{C} : \lim_{n \to \infty} |f_c^{(n)}(0)| \not= \infty \}$$

#### How It Works
1. For each point $c = x + iy$, initialize $z_0 = 0$.
2. Compute recurrence:
   $$z_{n+1} = z_n^2 + c \implies \begin{cases} x_{n+1} = x_n^2 - y_n^2 + x_0 \\ y_{n+1} = 2 x_n y_n + y_0 \end{cases}$$
3. If $|z_n|^2 = x_n^2 + y_n^2 > 4$, the point is guaranteed to escape to $\infty$.
4. **Smooth Fractional Escape Time**:
   $$\nu(c) = n + 1 - \frac{\ln(\ln |z_n|)}{\ln 2}$$
5. The generator extracts vector isoline contours grouping points by escape rates, revealing the main cardioid, period bulbs, and antenna filaments.

---

### 14. Julia Set (Douady's Rabbit)
- **ID**: `julia_set`
- **Difficulty**: Hard
- **Hausdorff Dimension**: $D \approx 1.4100$
- **Parameter**: $c = -0.123 + 0.745i$

#### How It Works
1. Unlike the Mandelbrot set (where $c$ varies and $z_0 = 0$), a **Julia set** fixes $c \in \mathbb{C}$ and varies the initial starting value $z_0 \in \mathbb{C}$:
   $$z_{n+1} = z_n^2 + c$$
2. The Julia set $J(f_c)$ is the boundary between points whose orbits escape to $\infty$ and points whose orbits remain bounded.
3. For $c = -0.123 + 0.745i$, the parameter lies inside a period-3 bulb of the Mandelbrot set, yielding a filled Julia set known as **Douady's Rabbit** with 3-fold rotational dendritic ears.

---

### 15. Newton-Raphson Basins of Attraction
- **ID**: `newton_fractal`
- **Difficulty**: Hard
- **Hausdorff Dimension**: $\dim_H(\partial B) = 2.0000$
- **Polynomial**: $p(z) = z^3 - 1 = 0$

#### How It Works
1. The Newton-Raphson method finds roots of $p(z)$ by iterating:
   $$z_{n+1} = z_n - \frac{p(z_n)}{p'(z_n)} = z_n - \frac{z_n^3 - 1}{3 z_n^2} = \frac{2 z_n^3 + 1}{3 z_n^2}$$
2. The three roots of unity in the complex plane are:
   $$\xi_1 = 1, \quad \xi_2 = e^{i 2\pi/3} = -\frac{1}{2} + i \frac{\sqrt{3}}{2}, \quad \xi_3 = e^{i 4\pi/3} = -\frac{1}{2} - i \frac{\sqrt{3}}{2}$$
3. Every point $z_0 \in \mathbb{C}$ converges to one of these three roots.
4. The boundary separating the three basins of attraction is a **Julia set**: any neighborhood of a boundary point intersects **all three** basins simultaneously!
5. This demonstrates deterministic chaos in simple polynomial root finding.

---

## CLI Reference & Generator Guide

The CLI generator is completely dependency-free and requires only Python 3.

```bash
# Navigate to project directory
cd 2026-09-17/fractals

# 1. Display all available fractals with difficulty tiers and dimensions
python3 fractals.py --list

# 2. Generate a single fractal
python3 fractals.py --fractal koch_snowflake --palette neon --output koch.svg

# 3. Generate all Level 1 (Easy) fractals
python3 fractals.py --difficulty easy --output-dir ./easy_fractals

# 4. Generate all Level 2 (Medium) fractals
python3 fractals.py --difficulty medium --output-dir ./medium_fractals

# 5. Generate all Level 3 (Hard) fractals
python3 fractals.py --difficulty hard --output-dir ./hard_fractals

# 6. Generate the entire suite of 15 fractals with a JSON manifest
python3 fractals.py --all --output-dir ./gallery --palette sunset --manifest

# 7. Reproducible procedural variations using explicit seeds
python3 fractals.py --fractal fractal_canopy --seed 12345 --palette emerald -o tree.svg
```

### Supported CLI Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--list` | Flag | `False` | Prints formatted terminal table of all registered fractals. |
| `--fractal <ID>` | String | `None` | Target fractal identifier to generate. |
| `--all` | Flag | `False` | Generates all 15 fractals in one batch. |
| `--difficulty <TIER>` | Choice | `all` | Filter by `easy`, `medium`, `hard`, or `all`. |
| `--depth <INT>` | Integer | Spec default | Override recursive iteration depth. |
| `--seed <INT>` | Integer | `42` | Random seed for procedural variations. |
| `--palette <NAME>` | Choice | `neon` | Theme: `neon`, `cyberpunk`, `sunset`, `emerald`, `ocean`, `fire`, `gold`. |
| `--width <INT>` | Integer | `1200` | SVG canvas width in pixels. |
| `--height <INT>` | Integer | `1200` | SVG canvas height in pixels. |
| `--output-dir <DIR>` | Path | `.` | Destination folder for SVGs. |
| `--output <FILE>` | Path | `None` | Explicit output SVG path for single generation. |
| `--manifest` | Flag | `False` | Generates `manifest.json` cataloging metadata. |

---

## Color Palettes & SVG Design Principles

All generated SVGs follow clean, modern visualization standards:
1. **Responsive Viewports**: Configured with `viewBox="0 0 W H"` and `style="max-width: 100%; height: auto;"` for flawless rendering on any mobile, tablet, or desktop screen.
2. **Dark Theme Architecture**: Dark `#0b0f19` canvas background with radial ambient vignettes `#1f293d` to make vector curves glow.
3. **Typography & Info Badges**: Each SVG includes an integrated header badge detailing the fractal title, difficulty tier, and Hausdorff dimension.
4. **Vibrant Palettes**:
   - `neon`: Electric Cyan (`#00f0ff`), Neon Green (`#00ff66`), Hot Pink (`#ff007f`), Violet (`#9d00ff`).
   - `cyberpunk`: Solar Yellow (`#fcee0a`), Bright Cyan (`#00f0ff`), Deep Violet (`#01012b`).
   - `sunset`: Hot Magenta (`#f72585`), Indigo (`#480ca8`), Neon Blue (`#4cc9f0`).
   - `emerald`: Forest Green (`#059669`), Mint (`#10b981`), Seafoam (`#6ee7b7`).
   - `ocean`: Deep Navy (`#03045e`), Azure (`#0077b6`), Cyan (`#48cae4`).
   - `fire`: Dark Ember (`#ff4800`), Flame Orange (`#ff7900`), Solar Gold (`#ffaa00`).

---

## Unit Testing & Verification

The suite includes comprehensive unit tests verifying XML compliance, CLI options, mathematical metadata, and deterministic seeding:

```bash
# Run test suite
python3 -m unittest test_fractals.py

# Run via unittest discovery
python3 -m unittest discover -s . -p "test_*.py"
```
