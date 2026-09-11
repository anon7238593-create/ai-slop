#!/usr/bin/env python3
"""CLI driver for rendering randomized Manim matrix transformation animations.

Renders high-definition mathematical animations demonstrating:
- Scaling, shearing, and stretching
- Invariant eigenvector directions (A*v = lambda*v)
- Composition of transformations: A then B vs single product C = B @ A

Usage:
    # Render with a new random configuration:
    python3 generate_matrix_animation.py --scene all --quality m

    # Render with a reproducible seed:
    python3 generate_matrix_animation.py --seed 20260912 --quality h --output-dir videos/
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

from random_matrix_generator import MatrixPack, generate_matrix_pack


def find_manim_bin(custom_path: str | None = None) -> str:
    """Locate the manim binary across PATH and Nix store paths."""
    if custom_path and os.path.exists(custom_path) and os.access(custom_path, os.X_OK):
        return custom_path

    which_path = shutil.which("manim")
    if which_path:
        return which_path

    # Check Nix store matches
    nix_matches = glob.glob("/nix/store/*manim*/bin/manim")
    for m in nix_matches:
        if os.path.exists(m) and os.access(m, os.X_OK):
            return m

    raise RuntimeError("Manim executable not found. Please install manim or specify --manim-bin.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render randomized Manim matrix multiplication animations.")
    parser.add_argument("--seed", type=int, help="optional integer seed for reproducible generation")
    parser.add_argument(
        "--scene",
        choices=("all", "master", "transformations", "eigenvectors", "multiplication"),
        default="all",
        help="scene to render (default: all)",
    )
    parser.add_argument(
        "--quality",
        choices=("l", "m", "h", "k"),
        default="m",
        help="rendering quality: l (480p15), m (720p30), h (1080p60), k (4k60) - default: m",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "rendered_animations",
        help="directory to save final MP4 animations and metadata",
    )
    parser.add_argument("--manim-bin", help="path to manim executable")

    args = parser.parse_args()
    manim_bin = find_manim_bin(args.manim_bin)

    # Generate or reuse matrix pack
    current_dir = Path(__file__).resolve().parent
    pack = generate_matrix_pack(args.seed)
    config_file = current_dir / "matrix_config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(pack.to_dict(), f, indent=2)

    print(f"================================================================")
    print(f"MANIM MATRIX MULTIPLICATION & TRANSFORMATION ANIMATOR")
    print(f"Seed: {pack.seed}")
    print(f"Matrix A: {pack.matrix_a} (Eigenvalues: {pack.lambda_1}, {pack.lambda_2})")
    print(f"Matrix B: {pack.matrix_b}")
    print(f"Product C = B @ A: {pack.matrix_c}")
    print(f"Quality: -q{args.quality}  |  Scene Target: {args.scene}")
    print(f"================================================================")

    # Scenes map
    scene_map = {
        "transformations": ("SpaceTransformationsScene", "space_transformations.mp4"),
        "eigenvectors": ("EigenvectorsScene", "eigenvectors_invariant_directions.mp4"),
        "multiplication": ("MatrixMultiplicationScene", "matrix_multiplication_composition.mp4"),
        "master": ("MasterMatrixMultiplicationStory", "master_matrix_multiplication_story.mp4"),
    }

    if args.scene == "all":
        scenes_to_run = list(scene_map.items())
    else:
        scenes_to_run = [(args.scene, scene_map[args.scene])]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_videos = []

    scene_py = current_dir / "matrix_scenes.py"
    env = os.environ.copy()
    env["MATRIX_ANIM_SEED"] = str(pack.seed)

    for key, (scene_class, target_filename) in scenes_to_run:
        target_path = args.output_dir / target_filename
        print(f"\nRendering [{scene_class}] -> {target_path.name}...")
        t0 = time.time()

        cmd = [
            manim_bin,
            f"-q{args.quality}",
            str(scene_py),
            scene_class,
            "-o", target_filename,
            "--media_dir", str(current_dir / "media"),
        ]

        proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if proc.returncode != 0:
            print(f"Error rendering {scene_class}:\n{proc.stdout[-800:]}", file=sys.stderr)
            sys.exit(proc.returncode)

        # Locate produced video file in media/videos/matrix_scenes/...
        found_files = list((current_dir / "media" / "videos" / "matrix_scenes").glob(f"**/{target_filename}"))
        if not found_files:
            # Fallback search for any mp4 with similar name
            found_files = list((current_dir / "media").glob(f"**/{target_filename}"))

        if found_files:
            source_file = found_files[0]
            shutil.copy2(source_file, target_path)
            duration_s = round(time.time() - t0, 1)
            size_mb = round(os.path.getsize(target_path) / (1024 * 1024), 2)
            print(f"Rendered {target_filename} in {duration_s}s ({size_mb} MB)")

            manifest_videos.append({
                "scene": scene_class,
                "filename": target_filename,
                "size_mb": size_mb,
                "render_duration_s": duration_s,
            })
        else:
            print(f"Warning: could not locate produced file {target_filename}", file=sys.stderr)

    # Save manifest
    manifest = {
        "configuration": pack.to_dict(),
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "quality": args.quality,
        "videos": manifest_videos,
    }
    with open(args.output_dir / "animation_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\nAll requested Manim matrix animations rendered successfully!")


if __name__ == "__main__":
    main()
