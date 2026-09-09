#!/usr/bin/env python3
"""
Batch Video Generator for 90-Degree Ball Collisions
===================================================
Generates a collection of unique, randomized ball collision videos.
Each video features:
- Different random target ball count (N)
- Different random starting ball launch angle (direction)
- Different random video length / duration / speed
- Randomized canvas aspect ratio and neon color palette
- Spatial pentatonic audio track
- Generates manifest.json and README.md index
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import math
import os
import random
import secrets
import sys
import time
from typing import Any, Dict, List

# Ensure local module is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ball_collision import SimulationConfig, generate_video


def get_random_valid_angle(rng: random.Random) -> float:
    """Generate a random starting angle in [0, 360) avoiding axis alignment."""
    while True:
        angle = round(rng.uniform(10.0, 350.0), 1)
        mod90 = angle % 90.0
        # Ensure at least 8 degrees away from horizontal/vertical
        if 8.0 <= mod90 <= 82.0:
            return angle


def build_random_video_spec(index: int, base_seed: int) -> Dict[str, Any]:
    """Construct randomized specification for video number index."""
    # Deterministic per-index randomness using base_seed
    rng = random.Random(base_seed + index * 1013)

    # 1. Random number of balls: varied between 12 and 36 (optimal for clear viewer analysis)
    n_balls = rng.randint(12, 36)

    # 2. Random starting ball launch direction (angle in degrees)
    initial_angle = get_random_valid_angle(rng)

    # 3. Random speed & duration (slow and easy for viewers to track and analyze)
    speed = round(rng.uniform(160.0, 260.0), 1)
    duration_after = round(rng.uniform(2.5, 4.0), 1)
    max_duration = round(rng.uniform(12.0, 22.0), 1)

    # 4. Canvas resolution preset
    # Defaulting mainly to 720p landscape (1280x720) for batch efficiency,
    # with variations for vertical (720x1280) and square (720x720).
    aspect_choice = rng.choices(
        ["landscape_720p", "square_720p", "vertical_720p", "landscape_1080p"],
        weights=[0.60, 0.15, 0.15, 0.10],
        k=1,
    )[0]

    if aspect_choice == "landscape_720p":
        w, h = 1280, 720
    elif aspect_choice == "square_720p":
        w, h = 720, 720
    elif aspect_choice == "vertical_720p":
        w, h = 720, 1280
    else:
        w, h = 1920, 1080

    filename = f"collision_{index:03d}.mp4"
    video_seed = rng.randint(1, 1000000)

    return {
        "index": index,
        "filename": filename,
        "n_balls": n_balls,
        "initial_angle": initial_angle,
        "speed": speed,
        "duration_after": duration_after,
        "max_duration": max_duration,
        "width": w,
        "height": h,
        "aspect_choice": aspect_choice,
        "seed": video_seed,
    }


def render_worker(spec: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Worker task that executes a single video generation."""
    out_path = os.path.join(output_dir, spec["filename"])
    cfg = SimulationConfig(
        n_target=spec["n_balls"],
        width=spec["width"],
        height=spec["height"],
        fps=30,  # 30 fps for batch speed and compact artifact storage
        speed=spec["speed"],
        radius=12.0 if spec["width"] <= 1280 else 14.0,
        turn_angle_mode="random",
        initial_angle_deg=spec["initial_angle"],
        duration_after=spec["duration_after"],
        max_duration=spec["max_duration"],
        seed=spec["seed"],
        enable_audio=True,
        enable_trails=True,
        enable_hud=True,
        output_path=out_path,
    )

    t0 = time.time()
    generate_video(cfg)
    render_time = time.time() - t0

    file_size_bytes = os.path.getsize(out_path)
    file_size_mb = file_size_bytes / (1024 * 1024)

    return {
        **spec,
        "file_size_bytes": file_size_bytes,
        "file_size_mb": round(file_size_mb, 2),
        "render_time_s": round(render_time, 2),
    }


def generate_batch(count: int, output_dir: str, workers: int = 2) -> None:
    """Generate count videos in parallel and produce manifest.json and README.md."""
    os.makedirs(output_dir, exist_ok=True)
    base_seed = secrets.randbits(32)

    print("=" * 65)
    print(f"BATCH VIDEO GENERATOR: {count} RANDOM VIDEOS")
    print(f"Output Directory: {output_dir}")
    print(f"Base Seed:        {base_seed}")
    print(f"Worker Processes: {workers}")
    print("=" * 65)

    specs = [build_random_video_spec(i + 1, base_seed) for i in range(count)]
    results: List[Dict[str, Any]] = []

    t_start = time.time()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(render_worker, spec, output_dir): spec for spec in specs}
        completed = 0
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            completed += 1
            print(
                f"[{completed:3d}/{count}] Generated {res['filename']} | "
                f"N={res['n_balls']:2d} balls | "
                f"Angle={res['initial_angle']:5.1f}° | "
                f"Dims={res['width']}x{res['height']} | "
                f"Size={res['file_size_mb']:.2f} MB | "
                f"Time={res['render_time_s']}s"
            )

    results.sort(key=lambda r: r["index"])
    total_time = time.time() - t_start
    total_size_mb = sum(r["file_size_mb"] for r in results)

    # 1. Write manifest.json
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = {
        "generated_at": generated_at,
        "total_videos": len(results),
        "total_size_mb": round(total_size_mb, 2),
        "base_seed": base_seed,
        "videos": results,
    }
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # 2. Write README.md table
    table_rows = "\n".join(
        f"| `{r['filename']}` | {r['n_balls']} | {r['initial_angle']}° | {r['width']}×{r['height']} | "
        f"{r['speed']} px/s | {r['file_size_mb']} MB |"
        for r in results
    )

    readme_content = f"""# Collision Video Visualizations

Collection of {len(results)} distinct, randomized ball collision simulations with slow, analytical speeds and organic random inward deflection angles.

- **Generated at**: `{generated_at}`
- **Total Videos**: {len(results)}
- **Total Storage**: {total_size_mb:.2f} MB
- **Base Entropy Seed**: `{base_seed}`

Each simulation varies randomly across:
1. **Target Balls ($N$)**: Varied between 12 and 36 balls for optimal visual tracking.
2. **Initial Launch Angle**: Unique heading in [10°, 350°].
3. **Random Inward Deflections**: Every border collision spawns a new ball at a fresh random inward angle into the arena.
4. **Analytical Slow Speed**: Paced at $160 - 260$ px/s so viewers can clearly follow each bounce and spawn trajectory.
5. **Spatial Audio & Color**: Multi-octave pentatonic stereo audio with golden-angle rainbow palettes.

| File | Balls ($N$) | Starting Angle | Canvas | Speed | File Size |
|---|---|---|---|---|---|
{table_rows}
"""
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("\n" + "=" * 65)
    print(f"BATCH GENERATION COMPLETE: {len(results)} videos in {total_time:.1f}s")
    print(f"Total Output Size: {total_size_mb:.2f} MB")
    print(f"Manifest: {manifest_path}")
    print(f"README:   {readme_path}")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(
        description="Batch generator for 100 randomized ball collision videos."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of videos to generate (default: 100)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./collision-videos",
        help="Output directory path (default: ./collision-videos)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=min(os.cpu_count() or 2, 4),
        help="Number of parallel worker processes (default: min(CPUs, 4))",
    )

    args = parser.parse_args()
    generate_batch(args.count, args.output_dir, args.workers)


if __name__ == "__main__":
    main()
