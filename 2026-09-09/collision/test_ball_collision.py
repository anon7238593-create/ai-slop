#!/usr/bin/env python3
"""
Unit tests for Ball Collision Simulation
"""

import math
import os
import sys
import unittest
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ball_collision import (
    Ball,
    BallSimulation,
    SimulationConfig,
    calculate_spawn_velocity,
    calculate_90_degree_spawn_velocity,
    generate_palette,
    synthesize_audio_track,
    CollisionEvent,
)


class TestBallCollision(unittest.TestCase):
    def test_calculate_spawn_velocity_random_speed_preserved(self):
        """Verify speed is strictly preserved across random spawn velocity generation."""
        speed = 240.0
        wall_normal = (-1.0, 0.0)  # right wall
        rng = np.random.default_rng(42)

        for _ in range(30):
            vx, vy = calculate_spawn_velocity(
                vx_base=-200.0,
                vy_base=132.0,
                wall_normal=wall_normal,
                speed=speed,
                angle_mode="random",
                rng=rng,
            )
            calc_speed = math.hypot(vx, vy)
            self.assertAlmostEqual(calc_speed, speed, places=4)

    def test_calculate_spawn_velocity_random_points_inward(self):
        """Verify that randomly spawned velocities always point inward into the arena."""
        speed = 220.0
        walls = [
            ((-1.0, 0.0), (-200.0, 91.0)),   # right wall (inward is -x)
            ((1.0, 0.0), (200.0, 91.0)),     # left wall (inward is +x)
            ((0.0, 1.0), (91.0, 200.0)),     # top wall (inward is +y)
            ((0.0, -1.0), (91.0, -200.0)),   # bottom wall (inward is -y)
        ]
        rng = np.random.default_rng(123)

        for normal, (vx_base, vy_base) in walls:
            for _ in range(25):
                vx, vy = calculate_spawn_velocity(
                    vx_base=vx_base,
                    vy_base=vy_base,
                    wall_normal=normal,
                    speed=speed,
                    angle_mode="random",
                    rng=rng,
                )
                inward_dot = vx * normal[0] + vy * normal[1]
                self.assertGreater(inward_dot, 0.0, "Spawned velocity must point inward")

    def test_calculate_spawn_velocity_random_angle_diversity(self):
        """Verify that random spawn velocities cover diverse angles."""
        speed = 200.0
        wall_normal = (1.0, 0.0)  # left wall, inward normal is +x (angle 0)
        rng = np.random.default_rng(999)
        angles = set()

        for _ in range(40):
            vx, vy = calculate_spawn_velocity(
                vx_base=180.0,
                vy_base=87.0,
                wall_normal=wall_normal,
                speed=speed,
                angle_mode="random",
                rng=rng,
            )
            angle_deg = round(math.degrees(math.atan2(vy, vx)), 1)
            angles.add(angle_deg)

        # Diverse angles within inward arc
        self.assertGreater(len(angles), 25)

    def test_calculate_90_degree_spawn_velocity_speed_preserved(self):
        """Verify speed is strictly preserved across 90-degree deflection."""
        speed = 500.0
        # Right wall bounce: vx_refl is negative, vy_refl is positive
        vx_refl = -400.0
        vy_refl = 300.0
        wall_normal = (-1.0, 0.0)

        spawn_vx, spawn_vy = calculate_90_degree_spawn_velocity(
            vx_refl=vx_refl,
            vy_refl=vy_refl,
            wall_normal=wall_normal,
            speed=speed,
            turn_angle_deg=90.0,
        )

        spawn_speed = math.hypot(spawn_vx, spawn_vy)
        self.assertAlmostEqual(spawn_speed, speed, places=4)

    def test_calculate_90_degree_spawn_velocity_orthogonal(self):
        """Verify the spawned velocity dot product with reflected velocity is 0 (orthogonal)."""
        speed = 650.0
        angle_rad = math.radians(35.0)
        # Bouncing off bottom wall: vy_refl is negative
        vx_refl = speed * math.cos(angle_rad)
        vy_refl = -speed * math.sin(angle_rad)
        wall_normal = (0.0, -1.0)  # inward normal for bottom wall

        spawn_vx, spawn_vy = calculate_90_degree_spawn_velocity(
            vx_refl=vx_refl,
            vy_refl=vy_refl,
            wall_normal=wall_normal,
            speed=speed,
            turn_angle_deg=90.0,
        )

        # Dot product between reflected and spawned velocity
        dot = (vx_refl * spawn_vx + vy_refl * spawn_vy) / (speed * speed)
        self.assertAlmostEqual(dot, 0.0, places=4)

    def test_calculate_90_degree_spawn_velocity_points_inward(self):
        """Verify the spawned ball is directed into the arena."""
        speed = 600.0
        walls = [
            ((-1.0, 0.0), (-450.0, 396.86)),   # right wall
            ((1.0, 0.0), (450.0, 396.86)),     # left wall
            ((0.0, 1.0), (396.86, 450.0)),     # top wall
            ((0.0, -1.0), (396.86, -450.0)),   # bottom wall
        ]

        for normal, (vx_refl, vy_refl) in walls:
            spawn_vx, spawn_vy = calculate_90_degree_spawn_velocity(
                vx_refl=vx_refl,
                vy_refl=vy_refl,
                wall_normal=normal,
                speed=speed,
                turn_angle_deg=90.0,
            )
            # Dot product with inward normal must be non-negative
            inward_dot = spawn_vx * normal[0] + spawn_vy * normal[1]
            self.assertGreaterEqual(inward_dot, 0.0)

    def test_simulation_spawns_up_to_n(self):
        """Verify simulation stops spawning new balls once N is reached."""
        n_target = 8
        cfg = SimulationConfig(
            n_target=n_target,
            width=640,
            height=480,
            speed=800.0,
            radius=10.0,
            fps=30,
            duration_after=0.5,
            max_duration=10.0,
        )
        sim = BallSimulation(cfg)
        self.assertEqual(len(sim.balls), 1)

        # Run until finished
        dt = 1.0 / cfg.fps
        max_steps = int(cfg.max_duration * cfg.fps)
        for _ in range(max_steps):
            if sim.is_finished():
                break
            sim.step(dt)

        self.assertEqual(len(sim.balls), n_target)
        self.assertTrue(sim.is_finished())

    def test_palette_generation(self):
        """Check palette generates valid unique BGR tuples."""
        palette = generate_palette(20, seed=123)
        self.assertEqual(len(palette), 20)
        for bgr in palette:
            self.assertEqual(len(bgr), 3)
            for c in bgr:
                self.assertGreaterEqual(c, 0)
                self.assertLessEqual(c, 255)

    def test_audio_synthesis(self):
        """Verify audio synthesizer generates valid 16-bit PCM audio."""
        events = [
            CollisionEvent(time=0.1, x=200.0, y=100.0, wall='left', ball_id=1, spawned_id=2),
            CollisionEvent(time=0.3, x=800.0, y=500.0, wall='right', ball_id=2, spawned_id=3),
        ]
        audio = synthesize_audio_track(events, total_duration=0.6, sample_rate=44100, width=1000)
        self.assertIsNotNone(audio)
        self.assertEqual(audio.dtype, np.int16)
        self.assertEqual(audio.shape[1], 2)  # stereo
        self.assertGreater(len(audio), int(0.6 * 44100))

    def test_renderer_frame_shape_and_type(self):
        """Verify frame renderer generates valid numpy image."""
        from ball_collision import SimulationRenderer
        cfg = SimulationConfig(width=640, height=360, n_target=5)
        sim = BallSimulation(cfg)
        renderer = SimulationRenderer(cfg)
        frame = renderer.render_frame(sim)
        self.assertEqual(frame.shape, (360, 640, 3))
        self.assertEqual(frame.dtype, np.uint8)

    def test_batch_random_spec_generation(self):
        """Verify batch spec generator produces varied, valid randomized specs."""
        from generate_batch import build_random_video_spec, get_random_valid_angle
        import random
        rng = random.Random(999)
        for _ in range(50):
            angle = get_random_valid_angle(rng)
            self.assertGreaterEqual(angle, 10.0)
            self.assertLessEqual(angle, 350.0)
            self.assertGreaterEqual(angle % 90.0, 8.0)
            self.assertLessEqual(angle % 90.0, 82.0)

        specs = [build_random_video_spec(i, base_seed=12345) for i in range(1, 21)]
        ball_counts = {s["n_balls"] for s in specs}
        angles = {s["initial_angle"] for s in specs}
        self.assertGreater(len(ball_counts), 5)
        self.assertGreater(len(angles), 15)
        self.assertTrue(all(160.0 <= s["speed"] <= 260.0 for s in specs))
        self.assertTrue(all(12 <= s["n_balls"] <= 1000 for s in specs))
        self.assertTrue(all(28.0 <= s["duration_after"] <= 32.0 for s in specs))
        self.assertTrue(all(s["width"] == 1920 and s["height"] == 1080 for s in specs))
        self.assertTrue(all(s["aspect_choice"] == "landscape_1080p" for s in specs))

    def test_post_max_floating_duration(self):
        """Verify simulation continues running for duration_after seconds after reaching target balls."""
        n_target = 3
        duration_after = 1.0
        cfg = SimulationConfig(
            n_target=n_target,
            width=500,
            height=400,
            speed=500.0,
            radius=8.0,
            fps=30,
            duration_after=duration_after,
            max_duration=10.0,
        )
        sim = BallSimulation(cfg)
        dt = 1.0 / cfg.fps

        while not sim.is_finished():
            sim.step(dt)

        self.assertIsNotNone(sim.target_reached_time)
        self.assertGreaterEqual(len(sim.balls), n_target)
        floating_elapsed = sim.time - sim.target_reached_time
        self.assertGreaterEqual(floating_elapsed, duration_after)

    def test_ball_limit_validation(self):
        """Verify upper limit of 1000 balls is enforced and valid configurations succeed."""
        # 1000 balls configuration must be valid
        cfg_1000 = SimulationConfig(n_target=1000)
        self.assertEqual(cfg_1000.n_target, 1000)

        # Exceeding 1000 balls must raise ValueError
        with self.assertRaises(ValueError):
            SimulationConfig(n_target=1001)

        # Below 1 ball must raise ValueError
        with self.assertRaises(ValueError):
            SimulationConfig(n_target=0)

    def test_simulation_with_1000_balls(self):
        """Verify simulation correctly initializes and steps with upper limit of 1000 balls."""
        cfg = SimulationConfig(
            n_target=1000,
            width=640,
            height=360,
            speed=240.0,
            fps=30,
            duration_after=1.0,
            max_duration=5.0,
        )
        sim = BallSimulation(cfg)
        self.assertEqual(len(sim.colors), 1050)
        for _ in range(60):
            sim.step(1.0 / 30.0)
        self.assertGreater(len(sim.balls), 1)
        self.assertLessEqual(len(sim.balls), 1000)


if __name__ == '__main__':
    unittest.main()
