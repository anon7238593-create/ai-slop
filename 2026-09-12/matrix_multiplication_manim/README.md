# Linear Transformations, Eigenvectors & Matrix Multiplication in Manim

An interactive, mathematically rigorous visualization engine built with **Manim Community (v0.21.0)** demonstrating the geometric foundation of 2D linear algebra:

1. **How Space Transforms (Pure 2D Planar Maps)**: Coordinate grid deformations and multi-shape transformations under scaling, shearing, and general stretching without artificial z-axis rotation.
2. **Multi-Shape Geometric Probes**: Real-time transformation of distinct geometric shapes demonstrating area scaling, curvature deformation, and collinearity preservation:
   - **Unit Square** (Yellow): Demonstrates area scaling ($|\det M|$) and parallelogram shear.
   - **Unit Circle** (Cyan): Transforms into an exact **Ellipse** whose principal axes align with transformation eigenvectors/singular values.
   - **Asymmetric Triangle** (Purple): Demonstrates collinearity, parallelism preservation, and asymmetric skewing.
   - **Basis Vectors** ($\hat{i}, \hat{j}$): Standard unit vectors demonstrating column mapping ($M\hat{i} = \text{Col } 1, M\hat{j} = \text{Col } 2$).
3. **Eigenvectors & Invariant Directions**: Special directions that undergo pure scaling ($\lambda$) without tilting off their directional span ($A\vec{v} = \lambda\vec{v}$), aligning with ellipse principal axes.
4. **Matrix Multiplication as Composition**: Visual proof that applying $A$ then $B$ sequentially is identical to applying composite product matrix $C = B \cdot A$ in a single shot.
5. **Deterministic Seed Control**: Fully reproducible runs via `--seed <int>`, or randomized parameters per execution.

---

## Mathematical Foundations

### 1. Linear Transformations & Column Geometry
A $2 \times 2$ real matrix $M = \begin{bmatrix} m_{11} & m_{12} \\ m_{21} & m_{22} \end{bmatrix}$ defines a linear map $T: \mathbb{R}^2 \to \mathbb{R}^2$:
- **Column 1** $\begin{bmatrix} m_{11} \\ m_{21} \end{bmatrix}$ is the transformed landing point of canonical basis vector $\hat{i} = \begin{bmatrix} 1 \\ 0 \end{bmatrix}$.
- **Column 2** $\begin{bmatrix} m_{12} \\ m_{22} \end{bmatrix}$ is the transformed landing point of canonical basis vector $\hat{j} = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$.

Any point $\begin{bmatrix} x \\ y \end{bmatrix}$ transforms linearly to:
$$T\left(\begin{bmatrix} x \\ y \end{bmatrix}\right) = x M\hat{i} + y M\hat{j} = \begin{bmatrix} m_{11}x + m_{12}y \\ m_{21}x + m_{22}y \end{bmatrix}$$

Coordinate scale is 1:1 consistent with the grid ($1.0\text{ unit} = 1\text{ grid division}$).

---

### 2. Multi-Shape Deformation Laws

Under any invertible linear map $M$:
- **Unit Square** $[0, 1] \times [0, 1]$:
  Vertices $(0,0), (1,0), (1,1), (0,1)$ transform to the parallelogram spanned by $M\hat{i}$ and $M\hat{j}$.
  $$\text{Area}(\text{Transformed Square}) = |\det(M)| \cdot \text{Area}(\text{Original Square}) = |\det(M)|$$

- **Unit Circle** $x^2 + y^2 \le 1$:
  Transforms into an **Ellipse** defined by $\vec{x}^T (M M^T)^{-1} \vec{x} \le 1$.
  - Semi-major axis $a = \sigma_1 = \sqrt{\mu_1}$
  - Semi-minor axis $b = \sigma_2 = \sqrt{\mu_2}$
  where $\mu_1, \mu_2$ are eigenvalues of $K = M M^T$.
  $$\text{Area}(\text{Ellipse}) = \pi a b = \pi |\det(M)|$$

- **Asymmetric Triangle** $[(0,0), (1.2, 0.2), (0.4, 1.0)]$:
  Demonstrates that:
  1. Straight lines remain straight lines (collinearity preservation).
  2. Parallel lines remain parallel.
  3. Orientation is preserved when $\det(M) > 0$.

---

### 3. Pure 2D Planar Transformations (No Z-Axis Rotation)

All transformations are pure planar maps confined to the 2D $xy$-plane ($z = 0$):
- **Scaling Matrix**:
  $$S = \begin{bmatrix} s_x & 0 \\ 0 & s_y \end{bmatrix}, \quad \det(S) = s_x \cdot s_y$$
  Stretches $x$ by $s_x$ and $y$ by $s_y$. Circle becomes an axis-aligned ellipse.

- **Shearing Matrix**:
  $$H_x = \begin{bmatrix} 1 & k \\ 0 & 1 \end{bmatrix} \quad \text{or} \quad H_y = \begin{bmatrix} 1 & 0 \\ k & 1 \end{bmatrix}, \quad \det(H) = 1.00$$
  Slides space parallel to axes proportionally to distance. Area is 100% strictly conserved.

- **General Map $A$**:
  Constructed via symmetric spectral decomposition $A = P D P^T$ with real eigenvalues $\lambda_1, \lambda_2$ and orthonormal eigenvectors $\vec{v}_1, \vec{v}_2$.

- **Secondary Map $B$**:
  Constructed as a well-conditioned planar transformation (scaled horizontal/vertical shear) without artificial z-axis rotation.

---

### 4. Eigenvectors & Ellipse Principal Axes

An eigenvector $\vec{v}$ satisfies:
$$A \vec{v} = \lambda \vec{v}$$

1. $\vec{v}_1$ and $\vec{v}_2$ stay strictly on their invariant dashed lines, scaling by $\lambda_1$ and $\lambda_2$.
2. Any generic non-eigenvector $\vec{w}$ rotates off its span ($A\vec{w} \ne \lambda \vec{w}$).
3. **The Ellipse Theorem**: The unit circle deforms into an ellipse whose semi-major and semi-minor axes line up **EXACTLY** with eigenvectors $\vec{v}_1$ and $\vec{v}_2$!

---

### 5. Matrix Multiplication as Composition ($C = B \cdot A$)

When applying transformation $A$ followed by $B$:
$$\vec{x}' = A \vec{x}, \quad \vec{x}'' = B \vec{x}' = B (A \vec{x}) = (B \cdot A) \vec{x}$$

$$\begin{bmatrix} b_{11} & b_{12} \\ b_{21} & b_{22} \end{bmatrix} \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} = \begin{bmatrix} b_{11}a_{11} + b_{12}a_{21} & b_{11}a_{12} + b_{12}a_{22} \\ b_{21}a_{11} + b_{22}a_{21} & b_{21}a_{12} + b_{22}a_{22} \end{bmatrix}$$

$$\det(C) = \det(B) \cdot \det(A)$$

The animation records ghost outlines of all shapes after $A$ and $B$, resets to identity, and applies $C$ in **one single step**, proving that all shapes snap directly onto the composite ghost outlines.

---

## Animation Suite Overview

| Scene Class | Target File | Core Visualizations |
| :--- | :--- | :--- |
| `SpaceTransformationsScene` | `space_transformations.mp4` | Unit square, circle $\to$ ellipse, triangle, and basis vectors deforming under Scaling, Shearing, and General Map $A$. |
| `EigenvectorsScene` | `eigenvectors_invariant_directions.mp4` | Eigen-lines, eigenvectors scaling along span, test vector tilting, and unit circle transforming into an ellipse whose axes match eigenvectors. |
| `MatrixMultiplicationScene` | `matrix_multiplication_composition.mp4` | Multi-shape sequential composition ($A$ then $B$) vs single-step product matrix $C = B \cdot A$ with ghost outline verification. |
| `MasterMatrixMultiplicationStory` | `master_matrix_multiplication_story.mp4` | Unified cinematic master presentation combining all three acts into one film. |

---

## Quickstart & CLI Usage

### Render Animations
```bash
# Render all scenes in medium quality (720p30):
python3 generate_matrix_animation.py --scene all --quality m

# Render with reproducible seed in low quality (fast preview):
python3 generate_matrix_animation.py --seed 42 --quality l --scene all

# Render individual scenes:
python3 generate_matrix_animation.py --scene transformations --quality l --seed 42
python3 generate_matrix_animation.py --scene eigenvectors --quality l --seed 42
python3 generate_matrix_animation.py --scene multiplication --quality l --seed 42
python3 generate_matrix_animation.py --scene master --quality l --seed 42
```

### Run Mathematical Test Suite
```bash
python3 -m unittest discover -s . -p "test_*.py" -v
```
All 17 mathematical and geometric assertions are verified:
- Seed determinism
- Real, positive eigenvalues and orthogonal eigenvectors
- Determinants ($\det H = 1.0$, $\det S = s_x s_y$, $\det C = \det B \cdot \det A$)
- Canonical shape geometry & vertex mapping
- Transformed circle ellipse semi-axes & singular values
- Shape composition equivalence ($B(A(\vec{v})) == (B \cdot A)\vec{v}$)
- Collinearity preservation
- Area deformation scaling laws
