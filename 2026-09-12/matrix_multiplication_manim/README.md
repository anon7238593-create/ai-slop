# Linear Transformations, Eigenvectors & Matrix Multiplication in Manim

An interactive, high-definition mathematical visualization engine built with **Manim Community (v0.21.0)** demonstrating the geometric essence of linear algebra:

1. **How Space Transforms**: Continuous 2D coordinate grid deformation under scaling, shearing, and general stretching.
2. **Eigenvectors & Invariant Directions**: Visualizing the special vectors that undergo pure scaling ($\lambda$) without rotating off their directional span ($A\vec{v} = \lambda\vec{v}$).
3. **Matrix Multiplication as Composition**: Demonstrating why matrix multiplication $C = B \cdot A$ represents the composition of two spatial transformations applied sequentially.
4. **Dynamic Randomization**: Every run produces randomized, mathematically well-behaved matrices with real eigenvalues and distinct orthogonal eigenvectors, or can be pinned using `--seed`.

---

## Mathematical Concepts Demonstrated

### 1. Linear Transformations & Basis Vectors
A $2 \times 2$ matrix $M = \begin{bmatrix} m_{11} & m_{12} \\ m_{21} & m_{22} \end{bmatrix}$ defines a transformation of 2D space where:
- The first column $\begin{bmatrix} m_{11} \\ m_{21} \end{bmatrix}$ is the final coordinate of the standard basis vector $\hat{i} = \begin{bmatrix} 1 \\ 0 \end{bmatrix}$.
- The second column $\begin{bmatrix} m_{12} \\ m_{22} \end{bmatrix}$ is the final coordinate of the standard basis vector $\hat{j} = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$.

Any point $\begin{bmatrix} x \\ y \end{bmatrix}$ transforms linearly to $x M\hat{i} + y M\hat{j}$.

### 2. Space Deformations: Scaling, Shearing, and Stretching
- **Scaling Matrix**:
  $$S = \begin{bmatrix} s_x & 0 \\ 0 & s_y \end{bmatrix}$$
  Stretches or compresses space along the coordinate axes independently. The area of any region scales by $\det(S) = s_x \cdot s_y$.
- **Shear Matrix**:
  $$H = \begin{bmatrix} 1 & k \\ 0 & 1 \end{bmatrix}$$
  Slides grid lines parallel to the $x$-axis proportionally to their $y$-coordinate. The area is strictly preserved because $\det(H) = 1$.
- **General Matrix**:
  $$A = \begin{bmatrix} a & b \\ c & d \end{bmatrix}$$
  Combines rotation, non-uniform scaling, and shearing into a unified transformation.

### 3. Eigenvectors & Eigenvalues: Invariant Spans
Under almost all transformations, an arbitrary vector $\vec{w}$ changes both its length and its direction.

However, an **Eigenvector** $\vec{v}$ satisfies:
$$A \vec{v} = \lambda \vec{v}$$

- $\vec{v}$ lies on an **invariant line** through the origin.
- Under the transformation $A$, $\vec{v}$ never tilts or rotates; it only stretches or shrinks by the scalar factor $\lambda$ (the **eigenvalue**).
- In our generator, matrices $A$ are constructed via spectral decomposition $A = P D P^T$ with random rotation angle $\theta$ and real eigenvalues $\lambda_1, \lambda_2$. This guarantees clean, non-degenerate, orthogonal eigenspaces that are clearly visible on screen.

### 4. Matrix Multiplication as Sequential Composition
When transformation $A$ is applied first, followed by transformation $B$:
$$\vec{x}' = A \vec{x} \implies \vec{x}'' = B \vec{x}' = B (A \vec{x}) = (B \cdot A) \vec{x}$$

Matrix multiplication is therefore defined precisely to encode composition:
$$C = B \cdot A = \begin{bmatrix} b_{11} & b_{12} \\ b_{21} & b_{22} \end{bmatrix} \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} = \begin{bmatrix} b_{11}a_{11} + b_{12}a_{21} & b_{11}a_{12} + b_{12}a_{22} \\ b_{21}a_{11} + b_{22}a_{21} & b_{21}a_{12} + b_{22}a_{22} \end{bmatrix}$$

The animation visually proves this theorem by resetting space to identity and applying product matrix $C$ directly in **one single step**, demonstrating that the final grid lines and basis vectors match the sequential application of $A$ then $B$ down to the pixel!

---

## Scenes Included

| Scene Class | Output Video | Description |
| :--- | :--- | :--- |
| `SpaceTransformationsScene` | `space_transformations.mp4` | Step-by-step demonstration of scaling, shearing, and general transformation of a unit square and grid. |
| `EigenvectorsScene` | `eigenvectors_invariant_directions.mp4` | Visualizes eigen-lines, eigenvectors $\vec{v}_1, \vec{v}_2$ scaling by $\lambda_1, \lambda_2$, and a test vector $\vec{w}$ rotating off its span. |
| `MatrixMultiplicationScene` | `matrix_multiplication_composition.mp4` | Compares applying $A$ then $B$ sequentially against applying product matrix $C = B \cdot A$ in a single shot. |
| `MasterMatrixMultiplicationStory` | `master_matrix_multiplication_story.mp4` | Complete cinematic presentation combining all three acts into a unified educational film. |

---

## Quickstart

### Run with the CLI Driver
```bash
# Render all 4 scenes in medium quality (720p30) with random parameters
python3 generate_matrix_animation.py --scene all --quality m

# Render a specific scene in high definition (1080p60) with reproducible seed
python3 generate_matrix_animation.py --seed 20260912 --scene eigenvectors --quality h

# Render to custom output directory
python3 generate_matrix_animation.py --seed 42 --quality m --output-dir rendered_videos/
```

### Run Manim Directly
```bash
# Render master story scene in 720p
manim -qm matrix_scenes.py MasterMatrixMultiplicationStory

# Render with specific seed
MATRIX_ANIM_SEED=12345 manim -qm matrix_scenes.py EigenvectorsScene
```

### Run Unit Tests
```bash
python3 test_matrix_math.py
```
