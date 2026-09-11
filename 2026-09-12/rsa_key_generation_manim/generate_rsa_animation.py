#!/usr/bin/env python3
"""CLI driver for rendering RSA key generation and foundational theorem animations via Manim.

Scenes:
1. flt     -> FermatsLittleTheoremScene (Fermat's Little Theorem & Residue Permutation)
2. bezout  -> BezoutsIdentityScene (Bézout's Identity & Extended Euclidean Algorithm)
3. euler   -> EulersTheoremScene (Euler's Totient Grid Sieve & Totient Theorem)
4. inverse -> ModularInverseScene (Modular Multiplicative Inverse & Clock Stepping)
5. rsa     -> RSAKeyGenerationScene (Complete RSA Keypair Generation, Encryption & Decryption)
6. all     -> Renders all 5 scenes in sequence

Usage:
    # Render all scenes at medium quality (720p 30fps):
    python3 generate_rsa_animation.py --scene all --quality m

    # Render a single theorem:
    python3 generate_rsa_animation.py --scene flt --quality m --output-dir rendered_videos/
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

current_dir = Path(__file__).resolve().parent

SCENE_MAPPING = {
    "flt": ("FermatsLittleTheoremScene", "Fermat's Little Theorem (Residue Permutation & Cyclic Powers)"),
    "bezout": ("BezoutsIdentityScene", "Bézout's Identity & Extended Euclidean Algorithm"),
    "euler": ("EulersTheoremScene", "Euler's Totient Theorem & Multiplicativity Grid"),
    "inverse": ("ModularInverseScene", "Modular Multiplicative Inverse & Coprimality Condition"),
    "rsa": ("RSAKeyGenerationScene", "RSA Key Generation, Encryption, Decryption & Correctness Proof"),
}


def find_manim_bin(custom_path: str | None = None) -> str:
    """Locate the manim binary across PATH and Nix store paths."""
    if custom_path and os.path.exists(custom_path) and os.access(custom_path, os.X_OK):
        return custom_path

    which_path = shutil.which("manim")
    if which_path:
        return which_path

    nix_matches = glob.glob("/nix/store/*manim*/bin/manim")
    for m in nix_matches:
        if os.path.exists(m) and os.access(m, os.X_OK):
            return m

    raise RuntimeError("Manim executable not found. Please install manim or specify --manim-bin.")


def render_scene(
    scene_name: str,
    scene_description: str,
    manim_bin: str,
    quality_flag: str,
    output_dir: Path,
) -> dict:
    """Render a single Manim scene and move the resulting video to output_dir."""
    scenes_file = current_dir / "rsa_scenes.py"
    cmd = [
        manim_bin,
        f"-q{quality_flag}",
        str(scenes_file),
        scene_name,
    ]

    print(f"\n=======================================================")
    print(f"Rendering {scene_name} ({scene_description})...")
    print(f"Command: {' '.join(cmd)}")
    print(f"=======================================================")

    t0 = time.time()
    res = subprocess.run(cmd, cwd=str(current_dir), capture_output=True, text=True)
    duration_render = time.time() - t0

    if res.returncode != 0:
        print(f"STDERR:\n{res.stderr[-800:]}")
        print(f"STDOUT:\n{res.stdout[-800:]}")
        raise RuntimeError(f"Failed to render scene {scene_name} (exit code {res.returncode})")

    # Manim saves videos under current_dir / media / videos / rsa_scenes / <res> / <scene_name>.mp4
    found_videos = list(current_dir.glob(f"media/videos/rsa_scenes/**/{scene_name}.mp4"))
    if not found_videos:
        # Check parent media directory
        found_videos = list(Path("media").glob(f"videos/rsa_scenes/**/{scene_name}.mp4"))

    if not found_videos:
        raise FileNotFoundError(f"Could not locate output video file for scene {scene_name}")

    # Pick the most recently modified video
    found_videos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    source_video = found_videos[0]

    output_dir.mkdir(parents=True, exist_ok=True)
    dest_video = output_dir / f"{scene_name}.mp4"
    shutil.copy2(source_video, dest_video)

    size_bytes = dest_video.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    print(f"Successfully generated: {dest_video.name} ({size_mb:.2f} MB in {duration_render:.1f}s)")

    return {
        "scene_name": scene_name,
        "description": scene_description,
        "file_name": dest_video.name,
        "file_path": str(dest_video.resolve()),
        "size_bytes": size_bytes,
        "size_mb": round(size_mb, 2),
        "render_time_sec": round(duration_render, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Manim RSA key generation and theorem animations.")
    parser.add_argument(
        "--scene",
        choices=("all", "flt", "bezout", "euler", "inverse", "rsa"),
        default="all",
        help="scene to render (default: all)",
    )
    parser.add_argument(
        "--quality",
        choices=("l", "m", "h", "k"),
        default="m",
        help="quality flag: l (480p15), m (720p30), h (1080p60), k (4k60) (default: m)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=current_dir / "rendered_animations",
        help="output directory for MP4 videos (default: ./rendered_animations)",
    )
    parser.add_argument(
        "--manim-bin",
        type=str,
        default=None,
        help="explicit path to manim executable",
    )

    args = parser.parse_args()
    manim_bin = find_manim_bin(args.manim_bin)
    print(f"Using Manim binary: {manim_bin}")

    scenes_to_render = []
    if args.scene == "all":
        scenes_to_render = list(SCENE_MAPPING.values())
    else:
        scenes_to_render = [SCENE_MAPPING[args.scene]]

    manifest_entries = []
    total_start = time.time()

    for scene_cls, scene_desc in scenes_to_render:
        info = render_scene(
            scene_name=scene_cls,
            scene_description=scene_desc,
            manim_bin=manim_bin,
            quality_flag=args.quality,
            output_dir=args.output_dir,
        )
        manifest_entries.append(info)

    total_time = time.time() - total_start

    manifest_path = args.output_dir / "rsa_manifest.json"
    manifest_data = {
        "topic": "RSA Key Generation and Foundational Number Theory",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_scenes": len(manifest_entries),
        "total_render_time_sec": round(total_time, 2),
        "quality": args.quality,
        "scenes": manifest_entries,
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print("\n=======================================================")
    print(f"ALL SCENES COMPLETED! ({len(manifest_entries)} videos in {total_time:.1f}s)")
    print(f"Manifest written to: {manifest_path}")
    print("=======================================================\n")


if __name__ == "__main__":
    main()
