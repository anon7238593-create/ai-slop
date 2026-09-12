#!/usr/bin/env python3
"""Unified entry point for all 5 revamped RSA and Number Theory Manim scenes:

1. FermatsLittleTheoremScene: Kinetic token movement, residue permutation & factorial cancellation
2. BezoutsIdentityScene: Forward Euclidean division & kinetic backward substitution
3. EulersTheoremScene: 3x5 number card sieve, reduced residue lifting & permutation
4. ModularInverseScene: Animated clock pointer stepping, target pulse & non-coprime failure
5. RSAKeyGenerationScene: Alice & Bob network terminals, key distribution, encryption, decryption & proof
"""

from __future__ import annotations
import sys
from pathlib import Path

# Add current directory and scenes/ subdirectory to path
current_dir = Path(__file__).resolve().parent
scenes_dir = current_dir / "scenes"
for p in (str(current_dir), str(scenes_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Re-export all 5 scenes
from scene1_fermat import FermatsLittleTheoremScene
from scene2_bezout import BezoutsIdentityScene
from scene3_euler import EulersTheoremScene
from scene4_inverse import ModularInverseScene
from scene5_rsa import RSAKeyGenerationScene

# Ensure Manim CLI discovers classes when running against rsa_scenes.py
for cls in (
    FermatsLittleTheoremScene,
    BezoutsIdentityScene,
    EulersTheoremScene,
    ModularInverseScene,
    RSAKeyGenerationScene,
):
    cls.__module__ = __name__

__all__ = [
    "FermatsLittleTheoremScene",
    "BezoutsIdentityScene",
    "EulersTheoremScene",
    "ModularInverseScene",
    "RSAKeyGenerationScene",
]

