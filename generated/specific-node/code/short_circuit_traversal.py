#!/usr/bin/env python3
"""Generate BFS and DFS animation videos and PDF walkthroughs with eager short-circuit on discovery.

Unlike standard graph search (which enqueues discovered neighbors into active memory
and only verifies destination target nodes when later popped/dequeued), eager
short-circuit detection halts the traversal immediately the moment an edge (u -> v)
discovers v == target_node.

Highlights:
- Eager early-exit: Halts immediately upon target discovery on edge inspection.
- Non-adjacent guarantee: Enforces shortest-path hop distance >= min_distance (default: 2).
- Pedagogical pacing: Relaxed 1.8s/step transitions for clear conceptual clarity.
- Multi-format output: Standalone BFS, DFS, side-by-side comparative MP4s, and Graphviz PDFs.

Example:
    python3 short_circuit_traversal.py --start-node A --target-node K --algorithm all
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Optional

import bfs_dfs_visualizer as visualizer
from specific_node_traversal import pick_target_node
from traversal_animator import (
    DEFAULT_GRAPH,
    find_ffmpeg,
    layout_graph,
    random_connected_graph,
    render_comparative_video,
    render_standalone_video,
)


def generate_short_circuit_traversal(
    graph: dict[str, list[str]],
    start_node: str = "A",
    target_node: Optional[str] = "K",
    output_dir: Path | str = Path("short_circuit_output"),
    algorithm: str = "all",
    fps: int = 30,
    step_duration: float = 1.8,
    preset: str = "1080p",
    width: Optional[int] = None,
    height: Optional[int] = None,
    render_video: bool = True,
    render_pdf: bool = True,
    save_frames: bool = True,
    ffmpeg_bin: Optional[str] = None,
    seed: Optional[int] = None,
    edge_probability: Optional[float] = None,
    min_distance: int = 2,
) -> dict:
    """Generate traversal animation videos and PDF walkthroughs with eager short-circuiting on edge discovery."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if start_node not in graph:
        start_node = next(iter(graph))

    target_node, target_dist = pick_target_node(
        graph=graph,
        start_node=start_node,
        preferred_target=target_node,
        min_distance=min_distance,
    )
    print(
        f"[INFO] Short-Circuit Traversal: origin '{start_node}', destination '{target_node}' "
        f"({target_dist} hops away, min_distance={min_distance})"
    )

    # Resolution calculation
    RESOLUTION_PRESETS = {
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "1440p": (2560, 1440),
        "2k": (2560, 1440),
        "4k": (3840, 2160),
    }
    preset_w, preset_h = RESOLUTION_PRESETS.get(preset, (1920, 1080))
    video_width = width if width is not None else preset_w
    video_height = height if height is not None else preset_h

    # 1. Write Graph Metadata
    metadata = {
        "graph": graph,
        "start_node": start_node,
        "target_node": target_node,
        "target_hop_distance": target_dist,
        "min_distance": min_distance,
        "short_circuit": True,
        "random_seed": seed,
        "edge_probability": edge_probability,
        "nodes": len(graph),
        "edges": sum(len(v) for v in graph.values()) // 2,
        "step_duration_seconds": step_duration,
        "scope": f"short_circuit_target_{target_node}",
    }
    (output_path / "short_circuit_graph.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    manifest = {
        "graph": graph,
        "start_node": start_node,
        "target_node": target_node,
        "target_hop_distance": target_dist,
        "min_distance": min_distance,
        "short_circuit": True,
        "seed": seed,
        "nodes": len(graph),
        "edges": sum(len(v) for v in graph.values()) // 2,
        "resolution": f"{video_width}x{video_height}",
        "fps": fps,
        "step_duration_seconds": step_duration,
        "preset": preset,
        "scope": f"short_circuit_target_{target_node}",
        "generated_videos": [],
    }

    # 2. Render Videos
    if render_video:
        resolved_ffmpeg = find_ffmpeg(ffmpeg_bin)
        if not resolved_ffmpeg:
            print("Notice: FFmpeg executable not found. Skipping video animation rendering.")
        else:
            scale = max(0.2, min(video_width / 1920.0, video_height / 1080.0))
            margin = 35.0 * scale
            gap = 25.0 * scale
            graph_w = (video_width - 2.0 * margin - gap) * 0.675
            graph_h = video_height - 2.0 * margin

            box_x = margin + 20.0 * scale
            box_y = margin + 55.0 * scale
            box_w = graph_w - 40.0 * scale
            box_h = graph_h - 75.0 * scale

            layout = layout_graph(
                graph,
                box_x=box_x,
                box_y=box_y,
                box_w=box_w,
                box_h=box_h,
                margin=75.0 * scale,
                seed=seed if seed is not None else 42,
            )

            alg_choice = algorithm

            if alg_choice in ("bfs", "both", "all"):
                out_bfs = output_path / "bfs_traversal.mp4"
                prev_bfs = (output_path / "bfs_traversal_preview.png") if save_frames else None
                render_standalone_video(
                    graph,
                    layout,
                    "bfs",
                    out_bfs,
                    start_node=start_node,
                    target_node=target_node,
                    short_circuit=True,
                    fps=fps,
                    width=video_width,
                    height=video_height,
                    ffmpeg_bin=resolved_ffmpeg,
                    save_preview_frame=prev_bfs,
                    step_duration=step_duration,
                )
                # Also create named alias bfs_short_circuit.mp4
                shutil.copyfile(out_bfs, output_path / "bfs_short_circuit.mp4")

                manifest["generated_videos"].append({
                    "algorithm": "bfs",
                    "filename": out_bfs.name,
                    "alias": "bfs_short_circuit.mp4",
                    "title": f"Short-Circuit Target Search (Finding Node {target_node}): BFS Animation",
                    "description": f"Breadth-first search from Node {start_node} seeking Node {target_node} ({target_dist} hops away). Halts immediately upon discovery edge (u -> {target_node}) without waiting in FIFO Queue.",
                    "data_structure": "FIFO Queue (Short-Circuited)",
                    "start_node": start_node,
                    "target_node": target_node,
                    "target_hop_distance": target_dist,
                    "short_circuit": True,
                    "scope": f"short_circuit_target_{target_node}",
                    "resolution": f"{video_width}x{video_height}",
                    "step_duration": step_duration,
                })

            if alg_choice in ("dfs", "both", "all"):
                out_dfs = output_path / "dfs_traversal.mp4"
                prev_dfs = (output_path / "dfs_traversal_preview.png") if save_frames else None
                render_standalone_video(
                    graph,
                    layout,
                    "dfs",
                    out_dfs,
                    start_node=start_node,
                    target_node=target_node,
                    short_circuit=True,
                    fps=fps,
                    width=video_width,
                    height=video_height,
                    ffmpeg_bin=resolved_ffmpeg,
                    save_preview_frame=prev_dfs,
                    step_duration=step_duration,
                )
                # Also create named alias dfs_short_circuit.mp4
                shutil.copyfile(out_dfs, output_path / "dfs_short_circuit.mp4")

                manifest["generated_videos"].append({
                    "algorithm": "dfs",
                    "filename": out_dfs.name,
                    "alias": "dfs_short_circuit.mp4",
                    "title": f"Short-Circuit Target Search (Finding Node {target_node}): DFS Animation",
                    "description": f"Depth-first search from Node {start_node} seeking Node {target_node} ({target_dist} hops away). Halts eagerly on finding {target_node} along active branch without waiting in LIFO Stack.",
                    "data_structure": "LIFO Stack (Short-Circuited)",
                    "start_node": start_node,
                    "target_node": target_node,
                    "target_hop_distance": target_dist,
                    "short_circuit": True,
                    "scope": f"short_circuit_target_{target_node}",
                    "resolution": f"{video_width}x{video_height}",
                    "step_duration": step_duration,
                })

            if alg_choice in ("comparison", "all"):
                out_comp = output_path / "bfs_dfs_comparison.mp4"
                prev_comp = (output_path / "bfs_dfs_comparison_preview.png") if save_frames else None
                render_comparative_video(
                    graph,
                    layout,
                    out_comp,
                    start_node=start_node,
                    target_node=target_node,
                    short_circuit=True,
                    fps=fps,
                    width=video_width,
                    height=video_height,
                    ffmpeg_bin=resolved_ffmpeg,
                    save_preview_frame=prev_comp,
                    step_duration=step_duration,
                )
                # Also create named alias bfs_dfs_short_circuit_comparison.mp4
                shutil.copyfile(out_comp, output_path / "bfs_dfs_short_circuit_comparison.mp4")

                manifest["generated_videos"].append({
                    "algorithm": "comparison",
                    "filename": out_comp.name,
                    "alias": "bfs_dfs_short_circuit_comparison.mp4",
                    "title": f"Short-Circuit Target Search (Finding Node {target_node}): Comparative Traversal (BFS vs DFS)",
                    "description": f"Synchronized eager search from Node {start_node} seeking Node {target_node} ({target_dist} hops away). Contrasts BFS eager level-by-level discovery vs DFS eager branch discovery.",
                    "data_structure": "Queue vs Stack (Short-Circuited)",
                    "start_node": start_node,
                    "target_node": target_node,
                    "target_hop_distance": target_dist,
                    "short_circuit": True,
                    "scope": f"short_circuit_target_{target_node}",
                    "resolution": f"{video_width}x{video_height}",
                    "step_duration": step_duration,
                })

            (output_path / "video_manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
            print(
                f"[SUCCESS] Eager short-circuit animations for target search ({start_node} -> {target_node}) "
                f"generated in {output_path}"
            )

    # 3. Generate Graphviz DOT & PDF Walkthroughs
    if render_pdf:
        if shutil.which("dot"):
            visualizer.GRAPH = graph
            visualizer.START_NODE = start_node
            visualizer.TARGET_NODE = target_node
            visualizer.SHORT_CIRCUIT = True
            for alg in (("bfs", "dfs") if algorithm in ("both", "all", "comparison") else (algorithm,)):
                visualizer.render(alg, output_path, short_circuit=True)
        else:
            print("Notice: Graphviz 'dot' command not found. Skipping DOT and step PDF rendering.")

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create BFS/DFS animation videos and PDF walkthroughs that eager short-circuit upon target node discovery."
    )
    parser.add_argument("--start-node", default="A", help="node at which to begin traversal (default: A)")
    parser.add_argument(
        "--target-node",
        "--target",
        "--node",
        dest="target_node",
        default="K",
        help="destination ending node to search for and short-circuit upon discovering (default: K)",
    )
    parser.add_argument(
        "--algorithm",
        choices=("bfs", "dfs", "both", "comparison", "all"),
        default="all",
        help="algorithm to visualize: bfs, dfs, both, comparison, or all (default: all)",
    )
    parser.add_argument("--output", type=Path, default=Path("short_circuit_output"), help="output directory")
    parser.add_argument("--graph-json", type=Path, help="path to existing graph.json metadata file to reuse")
    parser.add_argument("--random-graph", action="store_true", help="generate a random connected graph")
    parser.add_argument("--nodes", type=int, default=15, help="number of nodes (3-26) for random graph (default: 15)")
    parser.add_argument(
        "--edge-probability",
        type=float,
        default=0.18,
        help="edge probability for random graph (default: 0.18)",
    )
    parser.add_argument("--seed", type=int, help="random seed for graph generator or layout")
    parser.add_argument(
        "--preset",
        choices=("720p", "1080p", "1440p", "2k", "4k"),
        default="1080p",
        help="video resolution preset (default: 1080p)",
    )
    parser.add_argument("--width", type=int, help="custom video width in pixels")
    parser.add_argument("--height", type=int, help="custom video height in pixels")
    parser.add_argument("--fps", type=int, default=30, help="frames per second (default: 30)")
    parser.add_argument(
        "--no-video",
        action="store_false",
        dest="render_video",
        help="disable video animation rendering (only generate PDF and dot)",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_false",
        dest="render_pdf",
        help="disable PDF step rendering (only generate video animations)",
    )
    parser.add_argument(
        "--speed",
        choices=("slow", "normal", "fast"),
        default="normal",
        help="pacing preset: slow (2.5s/step), normal (1.8s/step, default), fast (1.0s/step)",
    )
    parser.add_argument("--step-duration", type=float, help="duration in seconds for each traversal step")
    parser.add_argument(
        "--min-distance",
        type=int,
        default=2,
        help="minimum shortest-path hop distance between start and ending target node (default: 2)",
    )
    parser.add_argument("--ffmpeg-bin", help="path to ffmpeg binary executable")
    parser.add_argument("--save-frames", action="store_true", help="export sample preview PNG frames")

    args = parser.parse_args()

    SPEED_PRESETS = {
        "slow": 2.5,
        "normal": 1.8,
        "fast": 1.0,
    }
    step_duration = args.step_duration if args.step_duration is not None else SPEED_PRESETS.get(args.speed, 1.8)

    # Avoid direct edge between start and target if generating random graph
    start_req = args.start_node or "A"
    target_req = args.target_node
    avoid = {frozenset((start_req, target_req))} if target_req else None

    # Resolve Graph
    seed = args.seed
    if args.graph_json and args.graph_json.exists():
        with open(args.graph_json, "r", encoding="utf-8") as f:
            meta = json.load(f)
            graph = meta.get("graph", DEFAULT_GRAPH)
            seed = meta.get("random_seed", args.seed)
    elif args.random_graph:
        graph = random_connected_graph(args.nodes, args.edge_probability, args.seed, avoid_edges=avoid)
    else:
        graph = DEFAULT_GRAPH

    start_node = args.start_node
    if start_node not in graph:
        start_node = next(iter(graph))

    generate_short_circuit_traversal(
        graph=graph,
        start_node=start_node,
        target_node=args.target_node,
        output_dir=args.output,
        algorithm=args.algorithm,
        fps=args.fps,
        step_duration=step_duration,
        preset=args.preset,
        width=args.width,
        height=args.height,
        render_video=args.render_video,
        render_pdf=args.render_pdf,
        save_frames=args.save_frames,
        ffmpeg_bin=args.ffmpeg_bin,
        seed=seed,
        edge_probability=args.edge_probability if args.random_graph else None,
        min_distance=args.min_distance,
    )


if __name__ == "__main__":
    main()
