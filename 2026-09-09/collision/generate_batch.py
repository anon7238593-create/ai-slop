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


MAX_BALLS: int = 1000
DEFAULT_MIN_BALLS: int = 12
DEFAULT_MAX_BALLS: int = 1000


def get_random_valid_angle(rng: random.Random) -> float:
    """Generate a random starting angle in [0, 360) avoiding axis alignment."""
    while True:
        angle = round(rng.uniform(10.0, 350.0), 1)
        mod90 = angle % 90.0
        # Ensure at least 8 degrees away from horizontal/vertical
        if 8.0 <= mod90 <= 82.0:
            return angle


def build_random_video_spec(
    index: int,
    base_seed: int,
    min_balls: int = DEFAULT_MIN_BALLS,
    max_balls: int = DEFAULT_MAX_BALLS,
    width: int = 1920,
    height: int = 1080,
) -> Dict[str, Any]:
    """Construct randomized specification for video number index."""
    # Deterministic per-index randomness using base_seed
    rng = random.Random(base_seed + index * 1013)

    # 1. Random number of balls: varied between min_balls and max_balls (upper limit: 1000)
    n_balls = rng.randint(min_balls, max_balls)

    # 2. Random starting ball launch direction (angle in degrees)
    initial_angle = get_random_valid_angle(rng)

    # 3. Random speed & duration (slow and easy for viewers to track and analyze)
    speed = round(rng.uniform(160.0, 260.0), 1)
    duration_after = round(rng.uniform(28.0, 32.0), 1)  # ~30 seconds post-max floating
    max_duration = round(rng.uniform(75.0, 95.0), 1)

    # 4. Canvas resolution preset (defaults to 1920x1080 Full HD)
    w, h = width, height
    if w == 1920 and h == 1080:
        aspect_choice = "landscape_1080p"
    elif w == 1280 and h == 720:
        aspect_choice = "landscape_720p"
    elif w == 720 and h == 720:
        aspect_choice = "square_720p"
    elif w == 720 and h == 1280:
        aspect_choice = "vertical_720p"
    else:
        aspect_choice = f"{w}x{h}"

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


DEFAULT_COUNT: int = 20


def generate_batch(
    count: int = DEFAULT_COUNT,
    output_dir: str = "./collision-videos",
    workers: int = 2,
    min_balls: int = DEFAULT_MIN_BALLS,
    max_balls: int = DEFAULT_MAX_BALLS,
    width: int = 1920,
    height: int = 1080,
) -> None:
    """Generate count videos in parallel and produce manifest.json and README.md."""
    os.makedirs(output_dir, exist_ok=True)
    base_seed = secrets.randbits(32)

    print("=" * 65)
    print(f"BATCH VIDEO GENERATOR: {count} RANDOM VIDEOS")
    print(f"Output Directory: {output_dir}")
    print(f"Resolution:       {width}x{height}")
    print(f"Base Seed:        {base_seed}")
    print(f"Worker Processes: {workers}")
    print(f"Ball Count Range: {min_balls} to {max_balls} (upper limit: {MAX_BALLS})")
    print("=" * 65)

    specs = [
        build_random_video_spec(
            i + 1,
            base_seed,
            min_balls=min_balls,
            max_balls=max_balls,
            width=width,
            height=height,
        )
        for i in range(count)
    ]
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
                f"N={res['n_balls']:4d} balls | "
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
        "min_balls": min_balls,
        "max_balls": max_balls,
        "width": width,
        "height": height,
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

Collection of {len(results)} distinct, randomized 1920x1080 Full HD ball collision simulations with slow, analytical speeds and organic random inward deflection angles.

- **Generated at**: `{generated_at}`
- **Total Videos**: {len(results)}
- **Resolution**: {width}×{height} Full HD
- **Total Storage**: {total_size_mb:.2f} MB
- **Base Entropy Seed**: `{base_seed}`

Each simulation varies randomly across:
1. **Target Balls ($N$)**: Varied between {min_balls} and {max_balls} balls (upper limit: {MAX_BALLS}).
2. **Initial Launch Angle**: Unique heading in [10°, 350°].
3. **Random Inward Deflections**: Every border collision spawns a new ball at a fresh random inward angle into the arena.
4. **Analytical Slow Speed**: Paced at $160 - 260$ px/s so viewers can clearly follow each bounce and spawn trajectory.
5. **30-Second Post-Max Floating**: Runs for ~30 seconds after target balls are reached to showcase the full floating ensemble.
6. **Spatial Audio & Color**: Multi-octave pentatonic stereo audio with golden-angle rainbow palettes.
7. **Resolution**: High-definition ({width}×{height}) canvas across all videos.

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
        description="Batch generator for randomized ball collision videos."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_COUNT,
        help=f"Number of videos to generate (default: {DEFAULT_COUNT})",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Canvas width in pixels (default: 1920)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Canvas height in pixels (default: 1080)",
    )
    parser.add_argument(
        "--min-balls",
        type=int,
        default=DEFAULT_MIN_BALLS,
        help=f"Minimum target number of balls per video (default: {DEFAULT_MIN_BALLS})",
    )
    parser.add_argument(
        "--max-balls",
        type=int,
        default=DEFAULT_MAX_BALLS,
        help=f"Maximum target number of balls per video (default: {DEFAULT_MAX_BALLS}, upper limit: {MAX_BALLS})",
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

    if args.min_balls < 1:
        parser.error("The minimum number of balls must be at least 1.")
    if args.max_balls > MAX_BALLS:
        parser.error(f"The maximum number of balls cannot exceed the upper limit of {MAX_BALLS} (got {args.max_balls}).")
    if args.min_balls > args.max_balls:
        parser.error(f"--min-balls ({args.min_balls}) cannot be greater than --max-balls ({args.max_balls}).")

    generate_batch(
        count=args.count,
        output_dir=args.output_dir,
        workers=args.workers,
        min_balls=args.min_balls,
        max_balls=args.max_balls,
        width=args.width,
        height=args.height,
    )


if __name__ == "__main__":
    main()
