# RSA Key Generation & Foundational Number Theory Animations (Manim)

An educational and rigorous mathematical animation suite built using **Manim Community** (`v0.21.0`), illustrating the complete mathematical foundations of the **RSA Cryptosystem** (Rivest, Shamir, Adleman, 1977).

Before RSA key generation can be understood, four classical theorems of number theory must be grasped. This project provides **dedicated, highly detailed animations** for all four prerequisite theorems, culminating in the **full RSA key generation, encryption, decryption, and algebraic correctness proof**.

---

## The 5 Animation Scenes

| Scene Name | Primary Topic | Core Equation / Principle | File Output |
|---|---|---|---|
| **`FermatsLittleTheoremScene`** | **Fermat's Little Theorem** | $a^{p-1} \equiv 1 \pmod p$ | `FermatsLittleTheoremScene.mp4` |
| **`BezoutsIdentityScene`** | **Bézout's Identity & Extended Euclidean** | $a x + b y = \gcd(a, b)$ | `BezoutsIdentityScene.mp4` |
| **`EulersTheoremScene`** | **Euler's Totient Theorem & Grid Sieve** | $a^{\phi(n)} \equiv 1 \pmod n$, $\phi(pq) = (p-1)(q-1)$ | `EulersTheoremScene.mp4` |
| **`ModularInverseScene`** | **Modular Multiplicative Inverse** | $a \cdot x \equiv 1 \pmod m \iff x \equiv a^{-1} \pmod m$ | `ModularInverseScene.mp4` |
| **`RSAKeyGenerationScene`** | **Full RSA Protocol & Correctness Proof** | $M^{ed} = M^{1 + k\phi(n)} \equiv M \pmod n$ | `RSAKeyGenerationScene.mp4` |

---

## Detailed Mathematical Exposition

### 1. Fermat's Little Theorem (Pierre de Fermat, 1640)
- **Statement**: If $p$ is a prime number and $\gcd(a, p) = 1$, then:
  $$a^{p-1} \equiv 1 \pmod p \quad \Longleftrightarrow \quad a^p \equiv a \pmod p$$
- **Residue Permutation Proof**:
  1. Consider the set of non-zero residues modulo $p$:
     $$S = \{1, 2, 3, \dots, p-1\}$$
  2. Multiply each element by $a$:
     $$a \cdot S = \{a \cdot 1, a \cdot 2, \dots, a \cdot (p-1)\} \pmod p$$
  3. **Distinctness**: If $a \cdot x \equiv a \cdot y \pmod p$, then $a(x - y) \equiv 0 \pmod p$. Since $\gcd(a, p) = 1$, $p \mid (x - y) \implies x \equiv y \pmod p$. Therefore, $a \cdot S$ contains $p-1$ distinct non-zero residues, forming a **permutation** of $S$.
  4. Equating the product of elements:
     $$\prod_{x=1}^{p-1} (a \cdot x) \equiv \prod_{x=1}^{p-1} x \pmod p \implies a^{p-1} \cdot (p-1)! \equiv (p-1)! \pmod p$$
  5. Since $\gcd((p-1)!, p) = 1$, we divide by $(p-1)!$, yielding:
     $$a^{p-1} \equiv 1 \pmod p$$

---

### 2. Bézout's Identity & Extended Euclidean Algorithm (Étienne Bézout, 1766)
- **Statement**: For any integers $a$ and $b$ with $d = \gcd(a, b)$, there exist integers $x$ and $y$ such that:
  $$a x + b y = \gcd(a, b)$$
- **Role in RSA**:
  We require a private exponent $d$ such that $e \cdot d \equiv 1 \pmod{\phi(n)}$, which is equivalent to:
  $$e \cdot d + \phi(n) \cdot y = 1$$
  Bézout's identity guarantees such integers $d, y$ exist whenever $\gcd(e, \phi(n)) = 1$.
- **Extended Euclidean Algorithm**:
  Traces successive Euclidean division steps $r_{i-2} = q_{i-1} r_{i-1} + r_i$ forward until remainder $r_k = 1$, then back-substitutes to isolate $1$ as a linear combination of $a$ and $b$.

---

### 3. Euler's Totient Theorem (Leonhard Euler, 1736)
- **Euler's Totient Function $\phi(n)$**:
  Counts integers $1 \le k \le n$ that are coprime to $n$ ($\gcd(k, n) = 1$).
  - For prime $p$: $\phi(p) = p - 1$.
  - For $n = p \cdot q$ where $p, q$ are distinct primes:
    $$\phi(p \cdot q) = (p - 1)(q - 1)$$
- **Visual Grid Sieve Proof**:
  In a $p \times q$ grid of integers $1 \dots pq$:
  - Multiples of $p$: $\{p, 2p, \dots, qp\}$ ($q$ elements)
  - Multiples of $q$: $\{q, 2q, \dots, pq\}$ ($p$ elements)
  - Common multiple: $\{pq\}$ ($1$ element, counted twice)
  - Total non-coprime numbers: $p + q - 1$.
  - Remaining coprime residues:
    $$\phi(pq) = pq - (p + q - 1) = pq - p - q + 1 = (p - 1)(q - 1)$$
- **Generalization**:
  If $\gcd(a, n) = 1$, then:
  $$a^{\phi(n)} \equiv 1 \pmod n$$

---

### 4. Modular Multiplicative Inverse
- **Definition**: The modular inverse of an integer $a$ modulo $m$ is an integer $x$ such that:
  $$a \cdot x \equiv 1 \pmod m \quad \text{written as } x \equiv a^{-1} \pmod m$$
- **Coprimality Criterion**:
  $a^{-1} \pmod m$ exists if and only if $\gcd(a, m) = 1$.
  - If $\gcd(a, m) = g > 1$, every multiple $a \cdot x$ is a multiple of $g$, trapping the sequence in the subgroup of multiples of $g$, making it impossible to ever equal $1 \pmod m$.
- **Clock Stepping Visualization**:
  Displays $m$ hours on a modular wheel and demonstrates successive jumps $a, 2a, 3a, \dots$ until striking position $1$.

---

### 5. RSA Cryptosystem Protocol & Synthesis
1. **Prime Selection**: Choose two secret primes $p, q$ (e.g., $p = 11, q = 13$).
2. **Modulus Calculation**: Compute public modulus $n = p \cdot q = 143$.
3. **Totient Calculation**: Compute $\phi(n) = (p-1)(q-1) = 10 \cdot 12 = 120$.
4. **Public Exponent**: Choose $e = 7$ such that $1 < e < \phi(n)$ and $\gcd(7, 120) = 1$.
5. **Private Exponent**: Compute $d \equiv e^{-1} \pmod{\phi(n)}$ via Bézout's identity:
   $$7 d \equiv 1 \pmod{120} \implies 7 \cdot 103 = 721 = 6 \cdot 120 + 1 \implies d = 103$$
6. **Key Assignment**:
   - **Public Key**: $(e, n) = (7, 143)$
   - **Private Key**: $(d, n) = (103, 143)$
7. **Encryption**: Plaintext message $M = 9$:
   $$C = M^e \pmod n = 9^7 \pmod{143} = 48$$
8. **Decryption**:
   $$M' = C^d \pmod n = 48^{103} \pmod{143} = 9$$
9. **Correctness Proof**:
   Since $ed \equiv 1 \pmod{\phi(n)}$, there exists $k \in \mathbb{Z}$ such that $ed = 1 + k\phi(n)$:
   $$M^{ed} = M^{1 + k\phi(n)} = M \cdot \left(M^{\phi(n)}\right)^k \equiv M \cdot (1)^k \equiv M \pmod n \quad \blacksquare$$

---

## Directory Structure

```
2026-09-12/rsa_key_generation_manim/
├── README.md                     # Technical guide and mathematical proofs
├── rsa_math.py                   # Algorithmic engine and step-by-step tracers
├── test_rsa_math.py              # Unit test suite verifying mathematical properties
├── rsa_scenes.py                 # 5 Manim animation scenes
├── generate_rsa_animation.py     # CLI driver and rendering pipeline
└── rendered_animations/          # Output directory for rendered videos and manifest
    ├── FermatsLittleTheoremScene.mp4
    ├── BezoutsIdentityScene.mp4
    ├── EulersTheoremScene.mp4
    ├── ModularInverseScene.mp4
    ├── RSAKeyGenerationScene.mp4
    └── rsa_manifest.json
```

---

## Running Locally

### 1. Run Unit Tests
```bash
python3 test_rsa_math.py
```

### 2. Render Animations
```bash
# Render all scenes at 720p 30fps:
python3 generate_rsa_animation.py --scene all --quality m

# Render a single theorem:
python3 generate_rsa_animation.py --scene flt --quality m
python3 generate_rsa_animation.py --scene bezout --quality m
python3 generate_rsa_animation.py --scene euler --quality m
python3 generate_rsa_animation.py --scene inverse --quality m
python3 generate_rsa_animation.py --scene rsa --quality m
```
