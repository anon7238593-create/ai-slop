---
name: simulation-physics-generator
description: >-
  Automatically use this skill whenever working with 2D physics simulations, ball collision engines, ball_collision.py, generate_batch.py, spatial stereo audio synthesis, FFmpeg piping, or rendering collision videos.
---

# Simulation & Physics Video Generator Skill

## Purpose
Develop, optimize, test, and render high-performance 2D physics simulations, procedural audio, and animated video assets in `2026-09-09/collision/`.

## Key Files
- `2026-09-09/collision/ball_collision.py`: Continuous collision detection engine, velocity spawner, neon rendering, spatial audio.
- `2026-09-09/collision/generate_batch.py`: Batch generator compiling `manifest.json`.
- `2026-09-09/collision/test_ball_collision.py`: Unit test suite.

## Procedures

### 1. Invariants to Uphold
- **Strict speed conservation**: $\|\vec{v}_{child}\| = \|\vec{v}_{parent}\|$.
- **Strict inward reflection**: Spawned velocities must point inward ($\vec{v}_{spawn} \cdot \hat{n}_{wall} > 0$).
- **Sub-stepping**: Prevent tunneling at high velocities by dividing time steps ($\Delta t_{sub} = \Delta t / k$).

### 2. Testing & Rendering
```bash
# Run unit tests
cd 2026-09-09/collision
python3 -m unittest test_ball_collision.py -v

# Render quick test video
python3 ball_collision.py -n 20 --duration 5 -o /tmp/test_collision.mp4
```

### 3. Audio & Video Pipelines
- Multiplex spatial stereo audio chimes (panned $x / W$) with H.264 video.
- Support resolution presets: Full HD (`1920x1080`), 4K (`3840x2160`), Vertical (`1080x1920`), Square (`1080x1080`).
