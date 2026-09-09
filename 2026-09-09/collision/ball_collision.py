#!/usr/bin/env python3
"""
Ball Collision Video Generator
==============================
Simulates balls bouncing off borders on an expansive canvas.
Whenever a ball collides with a border, a new ball is spawned with the
exact same speed and its direction rotated by 90 degrees (directed inward
into the arena). The simulation duplicates balls on each border collision
until the target number of balls (N) is reached.

Features:
- Expansive customizable canvas (defaults to 1920x1080 Full HD).
- Strict speed conservation and exact 90-degree inward deflection for spawned balls.
- Sub-step physics integration for continuous collision detection without tunneling.
- High-fidelity visual rendering: neon golden-angle palette, glowing 3D spheres,
  motion trails, collision shockwaves, and wall impact flash effects.
- Interactive HUD overlay with real-time ball counter, progress bar, timer, and resolution.
- Spatial audio synthesizer: pentatonic collision chimes with stereo panning.
- Flexible CLI with presets (1080p, 720p, square, vertical, 4k).
"""

from __future__ import annotations

import argparse
import colorsys
from collections import deque
from dataclasses import dataclass, field
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


# ==============================================================================
# Data Structures
# ==============================================================================

@dataclass
class Ball:
    """Represents an active ball in the simulation."""
    id: int
    x: float
    y: float
    vx: float
    vy: float
    speed: float
    radius: float
    color: Tuple[int, int, int]  # BGR format for OpenCV
    generation: int = 0
    trail: deque = field(default_factory=lambda: deque(maxlen=18))
    last_bounce_time: float = -1.0


@dataclass
class Shockwave:
    """Expanding ripple effect created when a ball hits a wall."""
    x: float
    y: float
    color: Tuple[int, int, int]
    radius: float
    max_radius: float
    age: int = 0
    max_age: int = 16


@dataclass
class CollisionEvent:
    """Record of a collision event for audio synthesis and statistics."""
    time: float
    x: float
    y: float
    wall: str
    ball_id: int
    spawned_id: Optional[int] = None


MAX_BALLS: int = 1000


@dataclass
class SimulationConfig:
    """Configuration settings for the simulation and video renderer."""
    n_target: int = 35  # target ball count (upper limit: 1000)
    width: int = 1920
    height: int = 1080
    margin: int = 40
    fps: int = 60
    speed: float = 240.0  # pixels per second (slow and easy to analyze)
    radius: float = 14.0
    turn_angle_mode: str = "random"  # 'random' (default) or 'fixed'
    turn_angle_deg: Optional[float] = None  # None for random inward angle; or float for fixed angle
    spawn_reference: str = "incident"  # 'incident' or 'reflected'
    initial_angle_deg: Optional[float] = None  # custom starting ball launch angle
    duration_after: float = 30.0  # seconds to keep simulating after reaching N balls (floating effect)
    max_duration: float = 90.0  # safety cutoff in seconds
    substeps: int = 6  # physics substeps per frame
    enable_trails: bool = True
    enable_hud: bool = True
    enable_audio: bool = True
    enable_ball_collisions: bool = False
    seed: int = 42
    output_path: str = "ball_collision.mp4"

    def __post_init__(self):
        if self.n_target < 1:
            raise ValueError(f"Target number of balls must be at least 1 (got {self.n_target}).")
        if self.n_target > MAX_BALLS:
            raise ValueError(f"Target number of balls cannot exceed upper limit of {MAX_BALLS} (got {self.n_target}).")


# ==============================================================================
# Helper Functions
# ==============================================================================

def generate_palette(n: int, seed: int = 42) -> List[Tuple[int, int, int]]:
    """Generate N vibrant, distinct BGR colors using the golden angle."""
    colors = []
    golden_ratio = 0.618033988749895
    base_hue = (seed * 0.123456) % 1.0

    for i in range(n):
        h = (base_hue + i * golden_ratio) % 1.0
        s = 0.88 + 0.10 * (i % 3 == 0)
        v = 0.98
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        bgr = (int(b * 255), int(g * 255), int(r * 255))
        colors.append(bgr)

    return colors


def calculate_spawn_velocity(
    vx_base: float = 0.0,
    vy_base: float = 0.0,
    wall_normal: Tuple[float, float] = (0.0, 0.0),
    speed: float = 0.0,
    turn_angle_deg: Optional[float] = None,
    angle_mode: str = "random",
    rng: Optional[np.random.Generator] = None,
    *,
    vx_refl: Optional[float] = None,
    vy_refl: Optional[float] = None,
) -> Tuple[float, float]:
    """
    Compute the spawned ball's velocity with identical scalar speed.

    When angle_mode is 'random' (or turn_angle_deg is None), the direction is
    chosen randomly within an inward-pointing fan facing the arena interior
    (up to ±75° from the inward wall normal), producing diverse, organic,
    and aesthetically captivating trajectories.

    When angle_mode is 'fixed' (or turn_angle_deg is explicitly given), the base
    velocity is rotated by turn_angle_deg directed into the arena.

    wall_normal is the inward-pointing unit normal of the collided wall.
    """
    if vx_refl is not None:
        vx_base = vx_refl
    if vy_refl is not None:
        vy_base = vy_refl

    nx, ny = wall_normal
    n_mag = math.hypot(nx, ny)
    if n_mag > 1e-6:
        nx /= n_mag
        ny /= n_mag
    else:
        nx, ny = 1.0, 0.0

    if angle_mode == "random" or turn_angle_deg is None:
        # Choose a random angle inside the inward-pointing hemisphere.
        # Wall normal angle:
        normal_angle = math.atan2(ny, nx)
        # Inward fan: ±75 degrees (±1.309 rad) to avoid grazing parallel to the border
        max_deviation = math.radians(75.0)
        if rng is not None:
            deviation = float(rng.uniform(-max_deviation, max_deviation))
        else:
            deviation = float(np.random.uniform(-max_deviation, max_deviation))

        spawn_angle = normal_angle + deviation
        chosen_vx = speed * math.cos(spawn_angle)
        chosen_vy = speed * math.sin(spawn_angle)
        return chosen_vx, chosen_vy

    # Fixed turn angle rotation (e.g. 90.0 degrees)
    rad = math.radians(turn_angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    # Option 1: +turn_angle_deg rotation
    vx1 = vx_base * cos_a - vy_base * sin_a
    vy1 = vx_base * sin_a + vy_base * cos_a

    # Option 2: -turn_angle_deg rotation
    cos_b = math.cos(-rad)
    sin_b = math.sin(-rad)
    vx2 = vx_base * cos_b - vy_base * sin_b
    vy2 = vx_base * sin_b + vy_base * cos_b

    dot1 = vx1 * nx + vy1 * ny
    dot2 = vx2 * nx + vy2 * ny

    # Pick the rotation that points inward into the canvas
    if dot1 > 0 and dot2 <= 0:
        chosen_vx, chosen_vy = vx1, vy1
    elif dot2 > 0 and dot1 <= 0:
        chosen_vx, chosen_vy = vx2, vy2
    elif dot1 > 0 and dot2 > 0:
        # Both point inward; pick the one with greater inward normal component
        chosen_vx, chosen_vy = (vx1, vy1) if dot1 >= dot2 else (vx2, vy2)
    else:
        # If both are tangent or outward, bias along wall normal
        chosen_vx, chosen_vy = (vx1, vy1) if dot1 >= dot2 else (vx2, vy2)
        chosen_vx += nx * 0.1 * speed
        chosen_vy += ny * 0.1 * speed

    # Renormalize strictly to exact original speed
    mag = math.hypot(chosen_vx, chosen_vy)
    if mag > 1e-6:
        chosen_vx = (chosen_vx / mag) * speed
        chosen_vy = (chosen_vy / mag) * speed
    else:
        chosen_vx = nx * speed
        chosen_vy = ny * speed

    return chosen_vx, chosen_vy


def calculate_90_degree_spawn_velocity(
    vx_base: float = 0.0,
    vy_base: float = 0.0,
    wall_normal: Tuple[float, float] = (0.0, 0.0),
    speed: float = 0.0,
    turn_angle_deg: float = 90.0,
    *,
    vx_refl: Optional[float] = None,
    vy_refl: Optional[float] = None,
) -> Tuple[float, float]:
    """Backward compatibility helper for fixed 90-degree inward deflection."""
    return calculate_spawn_velocity(
        vx_base=vx_base,
        vy_base=vy_base,
        wall_normal=wall_normal,
        speed=speed,
        turn_angle_deg=turn_angle_deg,
        angle_mode="fixed",
        vx_refl=vx_refl,
        vy_refl=vy_refl,
    )


# ==============================================================================
# Simulation Core
# ==============================================================================

class BallSimulation:
    """Manages physics simulation, border collisions, and ball spawning."""

    def __init__(self, config: SimulationConfig):
        self.cfg = config
        self.balls: List[Ball] = []
        self.shockwaves: List[Shockwave] = []
        self.collision_events: List[CollisionEvent] = []
        self.time: float = 0.0
        self.target_reached_time: Optional[float] = None
        self.colors = generate_palette(max(config.n_target + 50, 100), config.seed)
        self.spawn_counter: int = 0
        self.rng = np.random.default_rng(self.cfg.seed + 777)

        # Wall impact flash tracking: intensity (0.0 to 1.0) and color
        self.wall_flashes: Dict[str, Tuple[float, Tuple[int, int, int]]] = {
            "left": (0.0, (200, 180, 120)),
            "right": (0.0, (200, 180, 120)),
            "top": (0.0, (200, 180, 120)),
            "bottom": (0.0, (200, 180, 120)),
        }

        # Arena boundaries
        self.xmin = self.cfg.margin + self.cfg.radius
        self.xmax = self.cfg.width - self.cfg.margin - self.cfg.radius
        self.ymin = self.cfg.margin + self.cfg.radius
        self.ymax = self.cfg.height - self.cfg.margin - self.cfg.radius

        self._init_first_ball()

    def _init_first_ball(self):
        """Create the initial seed ball at canvas center."""
        cx = self.cfg.width / 2.0
        cy = self.cfg.height / 2.0

        # Pick initial angle (custom or seeded)
        if self.cfg.initial_angle_deg is not None:
            angle_deg = float(self.cfg.initial_angle_deg)
        else:
            rng = np.random.default_rng(self.cfg.seed)
            base_angles = [34.0, 42.0, 56.0, 68.0, 122.0, 146.0, 215.0, 238.0]
            angle_deg = float(rng.choice(base_angles))

        self.initial_angle_deg = angle_deg
        rad = math.radians(angle_deg)

        vx = self.cfg.speed * math.cos(rad)
        vy = self.cfg.speed * math.sin(rad)

        ball = Ball(
            id=1,
            x=cx,
            y=cy,
            vx=vx,
            vy=vy,
            speed=self.cfg.speed,
            radius=self.cfg.radius,
            color=self.colors[0],
            generation=0,
            last_bounce_time=-1.0,
        )
        ball.trail.append((int(cx), int(cy)))
        self.balls.append(ball)
        self.spawn_counter = 1

    def step(self, dt: float):
        """Advance the physics simulation by dt seconds using sub-stepping."""
        sub_dt = dt / self.cfg.substeps

        for _ in range(self.cfg.substeps):
            self.time += sub_dt
            self._substep(sub_dt)

        # Decay wall flashes
        for w in self.wall_flashes:
            intensity, col = self.wall_flashes[w]
            if intensity > 0.01:
                self.wall_flashes[w] = (intensity * 0.86, col)
            else:
                self.wall_flashes[w] = (0.0, col)

        # Update shockwaves once per full frame
        active_shockwaves = []
        for sw in self.shockwaves:
            sw.age += 1
            sw.radius += (sw.max_radius - sw.radius) * 0.20 + 1.2
            if sw.age < sw.max_age:
                active_shockwaves.append(sw)
        self.shockwaves = active_shockwaves

        # Update trails once per frame
        for b in self.balls:
            b.trail.append((int(b.x), int(b.y)))

        # Check target reached
        if len(self.balls) >= self.cfg.n_target and self.target_reached_time is None:
            self.target_reached_time = self.time

    def _substep(self, dt: float):
        """Single physics sub-step."""
        new_balls_to_add: List[Ball] = []

        for b in self.balls:
            # Integrate position
            b.x += b.vx * dt
            b.y += b.vy * dt

            collided = False
            wall_name = ""
            wall_normal = (0.0, 0.0)

            # Record incoming velocity before reflection
            vin_x, vin_y = b.vx, b.vy

            # Check border collisions
            if b.x <= self.xmin and b.vx < 0:
                b.x = self.xmin
                b.vx = -b.vx
                collided = True
                wall_name = "left"
                wall_normal = (1.0, 0.0)
            elif b.x >= self.xmax and b.vx > 0:
                b.x = self.xmax
                b.vx = -b.vx
                collided = True
                wall_name = "right"
                wall_normal = (-1.0, 0.0)

            if b.y <= self.ymin and b.vy < 0:
                b.y = self.ymin
                b.vy = -b.vy
                collided = True
                wall_name = "top"
                wall_normal = (0.0, 1.0)
            elif b.y >= self.ymax and b.vy > 0:
                b.y = self.ymax
                b.vy = -b.vy
                collided = True
                wall_name = "bottom"
                wall_normal = (0.0, -1.0)

            if collided:
                # Trigger wall flash
                self.wall_flashes[wall_name] = (1.0, b.color)

                # Add shockwave ripple effect
                self.shockwaves.append(
                    Shockwave(
                        x=b.x,
                        y=b.y,
                        color=b.color,
                        radius=b.radius,
                        max_radius=b.radius + 34.0,
                    )
                )

                spawned_id = None
                # Spawn a new ball if target has not been reached
                current_total = len(self.balls) + len(new_balls_to_add)
                if current_total < self.cfg.n_target:
                    self.spawn_counter += 1
                    spawned_id = self.spawn_counter

                    base_vx = vin_x if self.cfg.spawn_reference == "incident" else b.vx
                    base_vy = vin_y if self.cfg.spawn_reference == "incident" else b.vy

                    new_vx, new_vy = calculate_spawn_velocity(
                        vx_base=base_vx,
                        vy_base=base_vy,
                        wall_normal=wall_normal,
                        speed=b.speed,
                        turn_angle_deg=self.cfg.turn_angle_deg,
                        angle_mode=self.cfg.turn_angle_mode,
                        rng=self.rng,
                    )

                    color_idx = (self.spawn_counter - 1) % len(self.colors)
                    new_ball = Ball(
                        id=spawned_id,
                        x=b.x + wall_normal[0] * (b.radius * 0.4),
                        y=b.y + wall_normal[1] * (b.radius * 0.4),
                        vx=new_vx,
                        vy=new_vy,
                        speed=b.speed,
                        radius=self.cfg.radius,
                        color=self.colors[color_idx],
                        generation=b.generation + 1,
                        last_bounce_time=self.time,
                    )
                    new_ball.trail.append((int(new_ball.x), int(new_ball.y)))
                    new_balls_to_add.append(new_ball)

                # Record collision event
                self.collision_events.append(
                    CollisionEvent(
                        time=self.time,
                        x=b.x,
                        y=b.y,
                        wall=wall_name,
                        ball_id=b.id,
                        spawned_id=spawned_id,
                    )
                )

        # Optional ball-on-ball elastic collisions
        if self.cfg.enable_ball_collisions and len(self.balls) > 1:
            self._handle_ball_collisions()

        if new_balls_to_add:
            self.balls.extend(new_balls_to_add)

    def _handle_ball_collisions(self):
        """Elastic pairwise ball collisions if enabled."""
        n = len(self.balls)
        for i in range(n):
            b1 = self.balls[i]
            for j in range(i + 1, n):
                b2 = self.balls[j]
                dx = b2.x - b1.x
                dy = b2.y - b1.y
                dist_sq = dx * dx + dy * dy
                min_dist = b1.radius + b2.radius
                if dist_sq < min_dist * min_dist and dist_sq > 1e-4:
                    dist = math.sqrt(dist_sq)
                    nx = dx / dist
                    ny = dy / dist

                    # Relative velocity
                    kx = b1.vx - b2.vx
                    ky = b1.vy - b2.vy
                    p = 2.0 * (nx * kx + ny * ky) / 2.0

                    if p > 0:
                        b1.vx -= p * nx
                        b1.vy -= p * ny
                        b2.vx += p * nx
                        b2.vy += p * ny

                        overlap = 0.5 * (min_dist - dist)
                        b1.x -= overlap * nx
                        b1.y -= overlap * ny
                        b2.x += overlap * nx
                        b2.y += overlap * ny

    def is_finished(self) -> bool:
        """Simulation finishes when target N balls have bounced for duration_after seconds."""
        if self.target_reached_time is not None:
            if (self.time - self.target_reached_time) >= self.cfg.duration_after:
                return True
        if self.time >= self.cfg.max_duration:
            return True
        return False


# ==============================================================================
# Frame Renderer
# ==============================================================================

class SimulationRenderer:
    """Renders high-definition visual frames for the simulation."""

    def __init__(self, config: SimulationConfig):
        self.cfg = config
        self.bg_frame = self._create_background()

    def _create_background(self) -> np.ndarray:
        """Create a clean dark background with subtle radial glow and arena borders."""
        w, h = self.cfg.width, self.cfg.height
        bg = np.zeros((h, w, 3), dtype=np.uint8)

        # Deep navy/slate background gradient
        y_coords, x_coords = np.ogrid[:h, :w]
        cx, cy = w / 2.0, h / 2.0
        max_r = math.hypot(cx, cy)
        dist = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2) / max_r

        # Gradient: center to corners
        bg[..., 0] = np.clip(38 - dist * 22, 10, 50).astype(np.uint8)  # B
        bg[..., 1] = np.clip(24 - dist * 14, 8, 35).astype(np.uint8)   # G
        bg[..., 2] = np.clip(16 - dist * 10, 6, 25).astype(np.uint8)   # R

        # Draw subtle grid lines inside arena
        m = self.cfg.margin
        grid_step = 80
        grid_color = (25, 20, 14)
        for gx in range(m + grid_step, w - m, grid_step):
            cv2.line(bg, (gx, m), (gx, h - m), grid_color, 1)
        for gy in range(m + grid_step, h - m, grid_step):
            cv2.line(bg, (m, gy), (w - m, gy), grid_color, 1)

        return bg

    def render_frame(self, sim: BallSimulation) -> np.ndarray:
        """Render a single video frame."""
        frame = self.bg_frame.copy()
        w, h = self.cfg.width, self.cfg.height
        m = self.cfg.margin

        # 1. Render Shockwaves
        for sw in sim.shockwaves:
            alpha = max(0.0, 1.0 - (sw.age / sw.max_age))
            col = tuple(int(c * alpha) for c in sw.color)
            r_int = max(1, int(sw.radius))
            cv2.circle(frame, (int(sw.x), int(sw.y)), r_int, col, 2, cv2.LINE_AA)

        # 2. Render Motion Trails
        if self.cfg.enable_trails:
            for b in sim.balls:
                trail = b.trail
                if len(trail) > 1:
                    pts = list(trail)
                    for i in range(len(pts) - 1):
                        progress = (i + 1) / len(pts)
                        trail_col = tuple(int(c * progress * 0.45) for c in b.color)
                        thickness = max(1, int(b.radius * 0.5 * progress))
                        cv2.line(frame, pts[i], pts[i + 1], trail_col, thickness, cv2.LINE_AA)

        # 3. Render Balls with 3D Sphere Highlight
        for b in sim.balls:
            bx, by = int(round(b.x)), int(round(b.y))
            br = int(round(b.radius))

            # Outer subtle glow
            glow_col = tuple(int(c * 0.35) for c in b.color)
            cv2.circle(frame, (bx, by), br + 3, glow_col, 1, cv2.LINE_AA)

            # Main ball body
            cv2.circle(frame, (bx, by), br, b.color, -1, cv2.LINE_AA)

            # Specular highlight for 3D sphere feel
            hl_x = bx - int(br * 0.32)
            hl_y = by - int(br * 0.32)
            hl_r = max(2, int(br * 0.28))
            cv2.circle(frame, (hl_x, hl_y), hl_r, (255, 255, 255), -1, cv2.LINE_AA)

        # 4. Clean margin clipping so effects do not spill outside arena
        frame[0:m, :] = self.bg_frame[0:m, :]
        frame[h - m:h, :] = self.bg_frame[h - m:h, :]
        frame[:, 0:m] = self.bg_frame[:, 0:m]
        frame[:, w - m:w] = self.bg_frame[:, w - m:w]

        # 5. Arena Borders with dynamic flash when struck
        base_border_col = (200, 180, 120)

        # Top border
        top_flash, top_col = sim.wall_flashes["top"]
        t_col = tuple(int(b * (1 - top_flash) + c * top_flash) for b, c in zip(base_border_col, top_col))
        t_thick = 2 + int(top_flash * 3)
        cv2.line(frame, (m, m), (w - m, m), t_col, t_thick, cv2.LINE_AA)

        # Bottom border
        bot_flash, bot_col = sim.wall_flashes["bottom"]
        b_col = tuple(int(b * (1 - bot_flash) + c * bot_flash) for b, c in zip(base_border_col, bot_col))
        b_thick = 2 + int(bot_flash * 3)
        cv2.line(frame, (m, h - m), (w - m, h - m), b_col, b_thick, cv2.LINE_AA)

        # Left border
        left_flash, left_col = sim.wall_flashes["left"]
        l_col = tuple(int(b * (1 - left_flash) + c * left_flash) for b, c in zip(base_border_col, left_col))
        l_thick = 2 + int(left_flash * 3)
        cv2.line(frame, (m, m), (m, h - m), l_col, l_thick, cv2.LINE_AA)

        # Right border
        right_flash, right_col = sim.wall_flashes["right"]
        r_col = tuple(int(b * (1 - right_flash) + c * right_flash) for b, c in zip(base_border_col, right_col))
        r_thick = 2 + int(right_flash * 3)
        cv2.line(frame, (w - m, m), (w - m, h - m), r_col, r_thick, cv2.LINE_AA)

        # Outer frame line
        cv2.rectangle(frame, (m - 3, m - 3), (w - m + 3, h - m + 3), (70, 50, 30), 1, cv2.LINE_AA)

        # 6. Render HUD Overlay
        if self.cfg.enable_hud:
            self._render_hud(frame, sim)

        return frame

    def _render_hud(self, frame: np.ndarray, sim: BallSimulation):
        """Render stylish HUD showing ball count, progress bar, and metrics."""
        w, h = self.cfg.width, self.cfg.height
        m = self.cfg.margin

        current_count = len(sim.balls)
        target = self.cfg.n_target
        progress = min(1.0, current_count / target)

        # HUD banner top-left
        hud_x, hud_y = m + 20, m + 16
        hud_w, hud_h = 470, 84

        sub_img = frame[hud_y:hud_y + hud_h, hud_x:hud_x + hud_w]
        white_rect = np.zeros_like(sub_img)
        white_rect[:] = (15, 12, 8)
        cv2.addWeighted(sub_img, 0.35, white_rect, 0.65, 0, sub_img)
        cv2.rectangle(frame, (hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h), (120, 100, 60), 1, cv2.LINE_AA)

        # Title
        title_label = "RANDOM ANGLE COLLISION SPAWNER" if self.cfg.turn_angle_mode == "random" else "90 DEGREE COLLISION SPAWNER"
        cv2.putText(
            frame,
            title_label,
            (hud_x + 14, hud_y + 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (180, 210, 255),
            1,
            cv2.LINE_AA,
        )

        # Ball counter text & floating status
        if current_count >= target:
            if sim.target_reached_time is not None:
                float_elapsed = sim.time - sim.target_reached_time
                float_total = self.cfg.duration_after
                status_text = f"BALLS: {current_count}/{target} (FLOATING: {float_elapsed:04.1f}s/{float_total:04.1f}s)"
            else:
                status_text = f"BALLS: {current_count}/{target} (MAX REACHED)"
            text_col = (50, 240, 120)  # Bright neon green
            font_scale = 0.58
        else:
            status_text = f"BALLS: {current_count} / {target}"
            text_col = (255, 255, 255)
            font_scale = 0.68

        cv2.putText(
            frame,
            status_text,
            (hud_x + 14, hud_y + 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            text_col,
            2,
            cv2.LINE_AA,
        )

        # Progress bar
        bar_x = hud_x + 14
        bar_y = hud_y + 62
        bar_w = hud_w - 28
        bar_h = 8
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (60, 50, 40), -1)
        if current_count >= target and sim.target_reached_time is not None:
            float_prog = min(1.0, (sim.time - sim.target_reached_time) / max(1e-3, self.cfg.duration_after))
            fill_w = int(bar_w * float_prog)
            if fill_w > 0:
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), (50, 240, 120), -1)
        else:
            fill_w = int(bar_w * progress)
            if fill_w > 0:
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), (255, 180, 50), -1)

        # Top-right metrics HUD (Time, Resolution, Speed)
        info_w, info_h = 360, 64
        info_x = w - m - info_w - 20
        info_y = m + 16

        info_sub = frame[info_y:info_y + info_h, info_x:info_x + info_w]
        info_bg = np.zeros_like(info_sub)
        info_bg[:] = (15, 12, 8)
        cv2.addWeighted(info_sub, 0.35, info_bg, 0.65, 0, info_sub)
        cv2.rectangle(frame, (info_x, info_y), (info_x + info_w, info_y + info_h), (120, 100, 60), 1, cv2.LINE_AA)

        minutes = int(sim.time // 60)
        seconds = sim.time % 60
        time_str = f"TIME: {minutes:02d}:{seconds:04.1f} | FPS: {self.cfg.fps}"
        cv2.putText(
            frame,
            time_str,
            (info_x + 14, info_y + 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (210, 225, 240),
            1,
            cv2.LINE_AA,
        )

        angle_lbl = "RANDOM" if self.cfg.turn_angle_mode == "random" else f"{int(self.cfg.turn_angle_deg or 90)}°"
        arena_str = f"SPEED: {int(self.cfg.speed)} px/s (Slow) | ANGLE: {angle_lbl}"
        cv2.putText(
            frame,
            arena_str,
            (info_x + 14, info_y + 48),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (160, 180, 200),
            1,
            cv2.LINE_AA,
        )


# ==============================================================================
# Audio Synthesizer
# ==============================================================================

def synthesize_audio_track(
    events: List[CollisionEvent],
    total_duration: float,
    sample_rate: int = 44100,
    width: int = 1920,
) -> Optional[np.ndarray]:
    """
    Synthesize stereo audio with pentatonic chimes and stereo panning
    for each border bounce and spawn event.
    """
    if not events:
        return None

    num_samples = int(math.ceil((total_duration + 0.5) * sample_rate))
    audio = np.zeros((num_samples, 2), dtype=np.float32)

    pentatonic = [
        261.63, 293.66, 329.63, 392.00, 440.00,  # C4, D4, E4, G4, A4
        523.25, 587.33, 659.25, 783.99, 880.00,  # C5, D5, E5, G5, A5
        1046.50, 1174.66, 1318.51, 1567.98       # C6, D6, E6, G6
    ]

    chime_duration = 0.12
    chime_samples = int(chime_duration * sample_rate)
    t = np.linspace(0, chime_duration, chime_samples, endpoint=False)
    envelope = np.exp(-32.0 * t).astype(np.float32)

    for ev in events:
        start_idx = int(ev.time * sample_rate)
        if start_idx >= num_samples:
            continue

        freq = pentatonic[(ev.ball_id * 3) % len(pentatonic)]
        if ev.spawned_id is not None:
            tone = (np.sin(2 * np.pi * freq * t) * 0.7 +
                    np.sin(2 * np.pi * freq * 2.0 * t) * 0.3)
            amplitude = 0.28
        else:
            tone = np.sin(2 * np.pi * freq * t)
            amplitude = 0.18

        sound = (tone * envelope * amplitude).astype(np.float32)

        pan = max(0.0, min(1.0, ev.x / max(1.0, float(width))))
        left_vol = math.cos(pan * math.pi * 0.5)
        right_vol = math.sin(pan * math.pi * 0.5)

        end_idx = min(start_idx + chime_samples, num_samples)
        actual_len = end_idx - start_idx

        audio[start_idx:end_idx, 0] += sound[:actual_len] * left_vol
        audio[start_idx:end_idx, 1] += sound[:actual_len] * right_vol

    max_val = np.max(np.abs(audio))
    if max_val > 0.85:
        audio = (audio / max_val) * 0.85

    return (audio * 32767).astype(np.int16)


def export_wav_file(samples: np.ndarray, wav_path: str, sample_rate: int = 44100):
    """Write 16-bit PCM stereo WAV file."""
    import wave
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.tobytes())


# ==============================================================================
# Video Generator & Muxer
# ==============================================================================

def generate_video(config: SimulationConfig) -> str:
    """Run simulation, render frames, synthesize audio, and encode MP4."""
    print("=" * 60)
    print("BALL COLLISION VIDEO GENERATOR")
    print(f"Target Balls:    {config.n_target}")
    print(f"Canvas Size:     {config.width}x{config.height}")
    angle_display = f"{config.turn_angle_deg}°" if config.turn_angle_mode == "fixed" else "Random Inward Angle"
    print(f"Spawn Angle:     {angle_display}")
    print(f"Spawn Reference: {config.spawn_reference}")
    print(f"Speed:           {config.speed} px/s (Slow & Analytical)")
    print(f"FPS:             {config.fps}")
    print(f"Output File:     {config.output_path}")
    print("=" * 60)

    sim = BallSimulation(config)
    renderer = SimulationRenderer(config)

    ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
    temp_dir = tempfile.mkdtemp(prefix="collision_sim_")
    raw_video_path = os.path.join(temp_dir, "raw_video.mp4")
    wav_path = os.path.join(temp_dir, "audio.wav")

    # Start ffmpeg pipe for video encoding with H.264
    w, h, fps = config.width, config.height, config.fps
    ffmpeg_cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{w}x{h}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-an",
        "-vcodec", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        raw_video_path,
    ]

    proc = None
    use_ffmpeg_pipe = True
    try:
        proc = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except Exception as e:
        print(f"Warning: ffmpeg pipe could not be started ({e}), falling back to OpenCV VideoWriter.")
        use_ffmpeg_pipe = False

    dt = 1.0 / fps
    frame_idx = 0
    t0 = time.time()

    fallback_writer = None
    if not use_ffmpeg_pipe:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fallback_writer = cv2.VideoWriter(raw_video_path, fourcc, fps, (w, h))

    fade_in_frames = int(0.4 * fps)

    try:
        while not sim.is_finished():
            frame = renderer.render_frame(sim)

            # Smooth fade-in
            if frame_idx < fade_in_frames:
                alpha = frame_idx / float(fade_in_frames)
                frame = (frame * alpha).astype(np.uint8)

            if use_ffmpeg_pipe and proc and proc.stdin:
                proc.stdin.write(frame.tobytes())
            elif fallback_writer:
                fallback_writer.write(frame)

            sim.step(dt)
            frame_idx += 1

            if frame_idx % (fps * 2) == 0:
                elapsed = time.time() - t0
                fps_actual = frame_idx / max(1e-3, elapsed)
                print(
                    f"Frame {frame_idx:5d} | Sim Time: {sim.time:5.1f}s | "
                    f"Balls: {len(sim.balls):3d}/{config.n_target} | "
                    f"Render Speed: {fps_actual:5.1f} fps"
                )

    finally:
        if use_ffmpeg_pipe and proc and proc.stdin:
            proc.stdin.close()
            proc.wait()
        elif fallback_writer:
            fallback_writer.release()

    total_duration = sim.time
    total_frames = frame_idx
    print()
    print(f"Simulation complete: {total_frames} frames ({total_duration:.2f}s duration)")

    # Synthesize audio if enabled
    has_audio = False
    if config.enable_audio and sim.collision_events:
        print("Synthesizing collision audio track...")
        audio_data = synthesize_audio_track(
            sim.collision_events,
            total_duration=total_duration,
            sample_rate=44100,
            width=config.width,
        )
        if audio_data is not None:
            export_wav_file(audio_data, wav_path, 44100)
            has_audio = True

    # Final Muxing: Combine video and audio
    out_dir = os.path.dirname(os.path.abspath(config.output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    if has_audio and os.path.exists(wav_path):
        print("Muxing H.264 video with AAC spatial audio track...")
        mux_cmd = [
            ffmpeg_bin,
            "-y",
            "-i", raw_video_path,
            "-i", wav_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            config.output_path,
        ]
        res = subprocess.run(mux_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print(f"Warning: audio muxing failed ({res.stderr.decode()[:200]}), copying raw video.")
            shutil.copyfile(raw_video_path, config.output_path)
    else:
        shutil.copyfile(raw_video_path, config.output_path)

    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

    file_size_mb = os.path.getsize(config.output_path) / (1024 * 1024)
    print(f"Video saved successfully: {config.output_path} ({file_size_mb:.2f} MB)")
    return config.output_path


# ==============================================================================
# CLI Parser
# ==============================================================================

PRESETS = {
    "1080p": (1920, 1080),
    "720p": (1280, 720),
    "square": (1080, 1080),
    "vertical": (1080, 1920),
    "4k": (3840, 2160),
}


def parse_args() -> SimulationConfig:
    parser = argparse.ArgumentParser(
        description="Generate a video of balls bouncing off borders and duplicating at 90-degree angles."
    )
    parser.add_argument(
        "-n", "--balls",
        type=int,
        default=35,
        help=f"Target number of balls to reach (1 to {MAX_BALLS}, default: 35)"
    )
    parser.add_argument(
        "--preset",
        type=str,
        choices=list(PRESETS.keys()),
        default="1080p",
        help="Resolution preset: 1080p, 720p, square, vertical, 4k (default: 1080p)"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Custom canvas width in pixels (overrides preset)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Custom canvas height in pixels (overrides preset)"
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=40,
        help="Arena border margin in pixels (default: 40)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Frames per second (default: 60)"
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=240.0,
        help="Ball speed in pixels per second (default: 240.0 for slow, analytical tracking)"
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=14.0,
        help="Ball radius in pixels (default: 14.0)"
    )
    parser.add_argument(
        "--turn-angle",
        type=str,
        default="random",
        help="Deflection angle for spawned ball: 'random' (default) or degrees (e.g. 90.0)"
    )
    parser.add_argument(
        "--spawn-reference",
        type=str,
        choices=["incident", "reflected"],
        default="incident",
        help="Reference trajectory for 90 deg turn: incident (default) or reflected"
    )
    parser.add_argument(
        "--initial-angle",
        type=float,
        default=None,
        help="Initial launch angle in degrees (default: seeded random)"
    )
    parser.add_argument(
        "--duration-after",
        type=float,
        default=30.0,
        help="Seconds to continue simulation after reaching N balls to observe floating effect (default: 30.0)"
    )
    parser.add_argument(
        "--max-duration",
        type=float,
        default=90.0,
        help="Maximum simulation duration cutoff in seconds (default: 90.0)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic trajectory (default: 42)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output video filename (default: ball_collision_n{N}.mp4)"
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audio synthesis"
    )
    parser.add_argument(
        "--no-trails",
        action="store_true",
        help="Disable motion trails"
    )
    parser.add_argument(
        "--no-hud",
        action="store_true",
        help="Disable HUD overlay"
    )
    parser.add_argument(
        "--ball-collisions",
        action="store_true",
        help="Enable elastic collisions between balls"
    )

    args = parser.parse_args()

    if args.balls < 1 or args.balls > MAX_BALLS:
        parser.error(f"The number of balls must be between 1 and {MAX_BALLS} (got {args.balls}).")

    w, h = PRESETS[args.preset]
    if args.width is not None:
        w = args.width
    if args.height is not None:
        h = args.height

    output_path = args.output
    if output_path is None:
        output_path = f"ball_collision_n{args.balls}.mp4"

    turn_raw = str(args.turn_angle).strip().lower()
    if turn_raw in ("random", "none", "rand"):
        turn_angle_mode = "random"
        turn_angle_deg = None
    else:
        turn_angle_mode = "fixed"
        try:
            turn_angle_deg = float(args.turn_angle)
        except ValueError:
            turn_angle_mode = "random"
            turn_angle_deg = None

    return SimulationConfig(
        n_target=args.balls,
        width=w,
        height=h,
        margin=args.margin,
        fps=args.fps,
        speed=args.speed,
        radius=args.radius,
        turn_angle_mode=turn_angle_mode,
        turn_angle_deg=turn_angle_deg,
        spawn_reference=args.spawn_reference,
        initial_angle_deg=args.initial_angle,
        duration_after=args.duration_after,
        max_duration=args.max_duration,
        enable_trails=not args.no_trails,
        enable_hud=not args.no_hud,
        enable_audio=not args.no_audio,
        enable_ball_collisions=args.ball_collisions,
        seed=args.seed,
        output_path=output_path,
    )


def main():
    config = parse_args()
    generate_video(config)


if __name__ == "__main__":
    main()
