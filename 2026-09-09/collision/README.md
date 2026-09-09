# Random Angle Ball Collision Spawner Simulation

A high-performance, visually captivating 2D physics simulation and video generator built in Python.

A ball starts bouncing inside an expansive canvas with a gentle, slow speed designed for easy human tracking and trajectory analysis. Whenever any ball collides with an arena boundary, it reflects elastically and immediately spawns a new ball with the **exact same speed** and a **random inward angle** directed into the arena interior. Balls continue to multiply upon boundary impacts until a target count of $N$ balls is reached, creating organic, mesmerizing geometric webs and dynamic color-burst patterns.

---

## Visual & Acoustic Highlights

- **Slow, Analytical Pacing**: Default speed of $240$ px/s (batch range $160 - 260$ px/s) gives viewers ample time to visually follow and analyze every single bounce, wall flash, and spawn.
- **Organic Random Inward Spawning**: Rather than rigid 90-degree grids, each spawned ball launches at a random inward angle (sampled across a generous $150^\circ$ fan facing into the arena), yielding diverse, complex, and beautiful trajectory paths.
- **Expansive High-Resolution Canvas**: Default Full HD ($1920 \times 1080$), with built-in presets for $720p$, $1080p$ Square, $9:16$ Vertical Shorts/Reels/TikTok, and $4K$.
- **Strict Conservation of Speed**: Every spawned ball travels at the exact same scalar velocity as its parent ($\|\vec{v}_{spawn}\| = \|\vec{v}_{parent}\|$).
- **Sub-Step Continuous Physics**: Multiple physics substeps per frame prevent tunneling or clipping even near corners.
- **Neon Golden-Angle Color Wheel**: Each ball is assigned a distinct, vibrant color via golden-angle hue distribution ($H = (H_0 + i \cdot 0.6180339887) \pmod 1$).
- **Visual FX**:
  - 3D sphere specular highlights and outer glow.
  - Smooth fading motion trails.
  - Expanding collision shockwave ripples.
  - Dynamic border illumination flashes upon impact.
- **Live Glassmorphism HUD**: Real-time ball counter, animated progress bar, timestamp, resolution, speed, and angle mode.
- **Spatial Pentatonic Audio**: Synthesized multi-octave pentatonic chimes with continuous stereo panning based on horizontal collision coordinates ($x / W$).

---

## Mathematical Physics Model

### 1. Elastic Wall Reflection
Given an incident velocity $\vec{v}_{in} = (v_x, v_y)$ hitting a wall with inward-pointing unit normal $\hat{n}$:
$$\vec{v}_{refl} = \vec{v}_{in} - 2 (\vec{v}_{in} \cdot -\hat{n})(-\hat{n})$$

For vertical borders (left/right), $v_x \leftarrow -v_x$.  
For horizontal borders (top/bottom), $v_y \leftarrow -v_y$.

### 2. 90-Degree Inward Spawn Calculation
From base velocity $\vec{v}_{base} = (v_x, v_y)$ with speed $s = \|\vec{v}_{base}\|$, two orthogonal candidate vectors exist:
$$\vec{u}_1 = (-v_y, v_x), \quad \vec{u}_2 = (v_y, -v_x)$$

Both satisfy:
$$\vec{u}_1 \cdot \vec{v}_{base} = 0, \quad \|\vec{u}_1\| = \|\vec{u}_2\| = s$$

The vector chosen is the one directing the spawned ball into the arena:
$$\vec{v}_{spawn} = \arg\max_{\vec{u} \in \{\vec{u}_1, \vec{u}_2\}} (\vec{u} \cdot \hat{n})$$

---

## Installation & Requirements

Ensure Python 3.10+ and FFmpeg are available. Required Python packages:
```bash
pip install numpy opencv-python-headless
```

---

## Quick Start & CLI Usage

### Generate Default 1080p Video (50 Balls)
```bash
python3 ball_collision.py -n 50
```

### 1080p 60 FPS with Custom Output Name
```bash
python3 ball_collision.py -n 40 --preset 1080p --fps 60 -o collision_40.mp4
```

### Social Media Vertical Video (9:16 Shorts/TikTok)
```bash
python3 ball_collision.py -n 30 --preset vertical -o tiktok_collision.mp4
```

### Square Canvas (1:1 Instagram)
```bash
python3 ball_collision.py -n 35 --preset square -o instagram_collision.mp4
```

### Fast Simulation with Custom Speed & Post-Target Hold
```bash
python3 ball_collision.py -n 60 --speed 800 --duration-after 4.0 -o fast_sim.mp4
```

### Large Ensemble Simulation (Up to 1000 Balls)
```bash
python3 ball_collision.py -n 1000 --speed 360 -o massive_ensemble_1000.mp4
```

### Batch Video Generation (12 to 1000 Balls, 1920x1080 Full HD)
```bash
python3 generate_batch.py --count 20 --min-balls 12 --max-balls 1000 --width 1920 --height 1080 --output-dir ./collision-videos
```

---

## CLI Options

| Flag | Type | Default | Description |
|---|---|---|---|
| `-n`, `--balls` | `int` | `35` | Target number of balls to reach (1 to 1000, default: 35) |
| `--preset` | `str` | `1080p` | Resolution preset: `1080p`, `720p`, `square`, `vertical`, `4k` |
| `--width` | `int` | `None` | Custom canvas width in pixels (overrides preset) |
| `--height` | `int` | `None` | Custom canvas height in pixels (overrides preset) |
| `--margin` | `int` | `40` | Arena border margin in pixels |
| `--fps` | `int` | `60` | Output video frames per second |
| `--speed` | `float` | `240.0` | Ball speed in pixels per second (slow, analytical motion) |
| `--radius` | `float` | `14.0` | Ball radius in pixels |
| `--turn-angle` | `str` | `random` | Spawn deflection angle: `random` (default) or numeric degrees (e.g. `90.0`) |
| `--spawn-reference` | `str` | `incident` | Reference vector for deflection (`incident` or `reflected`) |
| `--duration-after` | `float` | `30.0` | Seconds to continue recording after reaching $N$ balls to observe floating effect |
| `--max-duration` | `float` | `90.0` | Maximum video duration cutoff in seconds |
| `--seed` | `int` | `42` | Random seed for deterministic trajectories |
| `-o`, `--output` | `str` | `None` | Output video path (defaults to `ball_collision_n{N}.mp4`) |
| `--no-audio` | `flag` | `False` | Disable spatial audio synthesis |
| `--no-trails` | `flag` | `False` | Disable visual motion trails |
| `--no-hud` | `flag` | `False` | Disable HUD metrics overlay |
| `--ball-collisions` | `flag` | `False` | Enable elastic pairwise ball-ball collisions |

---

## Running Unit Tests

A comprehensive unit test suite validates speed conservation, orthogonality, inward normal projection, termination criteria, and renderer output:

```bash
python3 -m unittest test_ball_collision.py
```
