#!/usr/bin/env python3
"""Mathematical utilities and algorithms for RSA key generation and foundational theorems.

Implements:
1. Fermat's Little Theorem verification and residue set permutation
2. Bézout's Identity and Extended Euclidean Algorithm with detailed step tracking
3. Euler's Totient Function, coprimality filtering, and grid decomposition
4. Modular Multiplicative Inverse computation and failure condition analysis
5. RSA key generation, encryption, decryption, and algebraic proof validation
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


def is_prime(n: int) -> bool:
    """Check if n is a prime number."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w
    return True


def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor of a and b."""
    return math.gcd(a, b)


class EuclideanStep:
    """Represents a single step in the Euclidean division algorithm: a = q * b + r."""

    def __init__(self, a: int, b: int, q: int, r: int, step_num: int):
        self.a = a
        self.b = b
        self.q = q
        self.r = r
        self.step_num = step_num

    def __repr__(self) -> str:
        return f"Step {self.step_num}: {self.a} = {self.q} × {self.b} + {self.r}"


class BezoutRow:
    """Represents a row in the extended Euclidean algorithm table."""

    def __init__(self, step: int, r: int, q: Optional[int], x: int, y: int):
        self.step = step
        self.r = r
        self.q = q
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        q_str = str(self.q) if self.q is not None else "-"
        return f"Row(step={self.step}, r={self.r}, q={q_str}, x={self.x}, y={self.y})"


def extended_gcd_with_steps(a: int, b: int) -> Tuple[int, int, int, List[EuclideanStep], List[BezoutRow]]:
    """Compute gcd(a, b) and Bézout coefficients x, y such that a*x + b*y = gcd(a, b).
    
    Returns:
        gcd_val: Greatest common divisor
        x: Bézout coefficient for a
        y: Bézout coefficient for b
        division_steps: List of forward Euclidean division steps
        tableau_rows: Full tableau rows showing (r, q, x, y)
    """
    division_steps: List[EuclideanStep] = []
    
    # Store division steps
    orig_a, orig_b = a, b
    rem_a, rem_b = a, b
    step_idx = 1
    while rem_b != 0:
        q = rem_a // rem_b
        r = rem_a % rem_b
        division_steps.append(EuclideanStep(rem_a, rem_b, q, r, step_idx))
        rem_a, rem_b = rem_b, r
        step_idx += 1

    gcd_val = rem_a

    # Standard Extended Euclidean Algorithm with tableau tracking
    tableau_rows: List[BezoutRow] = []
    
    r0, r1 = a, b
    x0, x1 = 1, 0
    y0, y1 = 0, 1
    
    tableau_rows.append(BezoutRow(0, r0, None, x0, y0))
    tableau_rows.append(BezoutRow(1, r1, None, x1, y1))
    
    row_idx = 2
    for step in division_steps:
        q = step.q
        r_next = r0 - q * r1
        x_next = x0 - q * x1
        y_next = y0 - q * y1
        tableau_rows.append(BezoutRow(row_idx, r_next, q, x_next, y_next))
        r0, r1 = r1, r_next
        x0, x1 = x1, x_next
        y0, y1 = y1, y_next
        row_idx += 1

    final_x, final_y = x0, y0
    assert orig_a * final_x + orig_b * final_y == gcd_val, f"Bézout identity check failed: {orig_a}*{final_x} + {orig_b}*{final_y} != {gcd_val}"
    
    return gcd_val, final_x, final_y, division_steps, tableau_rows


def modular_inverse(a: int, m: int) -> Tuple[int, List[BezoutRow]]:
    """Compute modular multiplicative inverse x such that (a * x) % m == 1.
    
    Returns (x, rows) where 0 < x < m.
    Raises ValueError if gcd(a, m) != 1.
    """
    gcd_val, x, _, _, rows = extended_gcd_with_steps(a, m)
    if gcd_val != 1:
        raise ValueError(f"Modular inverse does not exist: gcd({a}, {m}) = {gcd_val} != 1")
    return (x % m + m) % m, rows


def get_fermat_residues(a: int, p: int) -> Dict[str, Any]:
    """Generate the set permutation data for Fermat's Little Theorem."""
    if not is_prime(p):
        raise ValueError(f"{p} must be prime")
    if a % p == 0:
        raise ValueError(f"gcd({a}, {p}) must be 1")

    base_set = list(range(1, p))
    multiplied_raw = [a * x for x in base_set]
    multiplied_mod = [(a * x) % p for x in base_set]
    
    powers = []
    curr = 1
    for k in range(1, p):
        curr = (curr * a) % p
        powers.append((k, curr))

    return {
        "p": p,
        "a": a,
        "base_set": base_set,
        "multiplied_raw": multiplied_raw,
        "multiplied_mod": multiplied_mod,
        "is_permutation": sorted(multiplied_mod) == base_set,
        "powers": powers,
        "final_power_is_one": powers[-1][1] == 1,
    }


def get_euler_totient_data(p: int, q: int) -> Dict[str, Any]:
    """Compute Euler's totient data for n = p * q with grid decomposition."""
    if not (is_prime(p) and is_prime(q)):
        raise ValueError("Both p and q must be prime")
    if p == q:
        raise ValueError("p and q must be distinct primes for RSA standard totient")

    n = p * q
    multiples_of_p = [k * p for k in range(1, q + 1)]
    multiples_of_q = [k * q for k in range(1, p + 1)]
    intersection = [n]
    
    non_coprime = sorted(list(set(multiples_of_p + multiples_of_q)))
    coprime = [k for k in range(1, n) if math.gcd(k, n) == 1]
    
    phi = (p - 1) * (q - 1)
    assert len(coprime) == phi, f"Totient count mismatch: {len(coprime)} != {phi}"
    
    return {
        "p": p,
        "q": q,
        "n": n,
        "phi": phi,
        "multiples_of_p": multiples_of_p,
        "multiples_of_q": multiples_of_q,
        "intersection": intersection,
        "non_coprime_count": len(non_coprime),
        "coprime_count": len(coprime),
        "coprime_residues": coprime,
    }


def generate_rsa_demo_keys(p: int = 11, q: int = 13, e: int = 7) -> Dict[str, Any]:
    """Generate complete RSA keys and step-by-step trace for educational demonstration."""
    if not (is_prime(p) and is_prime(q)):
        raise ValueError(f"p={p} and q={q} must be prime")
    n = p * q
    phi = (p - 1) * (q - 1)
    
    if math.gcd(e, phi) != 1:
        raise ValueError(f"Public exponent e={e} must be coprime to phi={phi}")
        
    d, tableau = modular_inverse(e, phi)
    
    sample_m = 9
    c = pow(sample_m, e, n)
    m_recovered = pow(c, d, n)
    assert m_recovered == sample_m, f"Decryption check failed: {m_recovered} != {sample_m}"
    
    k = (e * d - 1) // phi
    assert e * d == 1 + k * phi
    
    return {
        "p": p,
        "q": q,
        "n": n,
        "phi": phi,
        "e": e,
        "d": d,
        "k": k,
        "public_key": (e, n),
        "private_key": (d, n),
        "tableau": tableau,
        "sample_m": sample_m,
        "sample_c": c,
        "recovered_m": m_recovered,
    }
