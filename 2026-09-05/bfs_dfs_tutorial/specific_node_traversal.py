#!/usr/bin/env python3
"""Generate BFS and DFS walkthrough PDFs and animation videos for a particular start node.

Supports:
- Particular starting node (default: Node E)
- Optional target node search (halts and highlights path when destination is reached)
- Slower, clearly visible pedagogical pacing (default: 1.8s/step)
- 15-node demonstrative graph topology
- Standalone BFS, DFS, and side-by-side comparative MP4 videos
- Graphviz DOT and PDF walkthroughs

Example:
    python3 specific_node_traversal.py --node E --algorithm all
    python3 specific_node_traversal.py --node E --target-node O --algorithm comparison
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Optional

import bfs_dfs_visualizer as visualizer
from traversal_animator import (
    DEFAULT_GRAPH,
    find_ffmpeg,
    layout_graph,
    random_connected_graph,
    render_comparative_video,
    render_standalone_video,
)


def generate_specific_node_traversal(
    graph: dict[str, list[str]],
    start_node: str = "E",
    target_node: Optional[str] = None,
    output_dir: Path | str = Path("specific_node_output"),
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
) -> dict:
    """Generate traversal animation videos and PDF walkthroughs for a specific start node."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if start_node not in graph:
        raise ValueError(f"Unknown start node {start_node!r}. Choose one of: {', '.join(graph)}")

    if target_node and target_node not in graph:
        print(f"Warning: target node {target_node!r} not in graph. Ignoring target node.")
        target_node = None

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
        "random_seed": seed,
        "edge_probability": edge_probability,
        "nodes": len(graph),
        "edges": sum(len(v) for v in graph.values()) // 2,
        "step_duration_seconds": step_duration,
        "scope": "particular_node",
    }
    (output_path / "specific_node_graph.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    manifest = {
        "graph": graph,
        "start_node": start_node,
        "target_node": target_node,
        "seed": seed,
        "nodes": len(graph),
        "edges": sum(len(v) for v in graph.values()) // 2,
        "resolution": f"{video_width}x{video_height}",
        "fps": fps,
        "step_duration_seconds": step_duration,
        "preset": preset,
        "scope": "particular_node",
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
                    fps=fps,
                    width=video_width,
                    height=video_height,
                    ffmpeg_bin=resolved_ffmpeg,
                    save_preview_frame=prev_bfs,
                    step_duration=step_duration,
                )
                manifest["generated_videos"].append({
                    "algorithm": "bfs",
                    "filename": out_bfs.name,
                    "title": f"Particular Node ({start_node}): BFS Animation",
                    "data_structure": "FIFO Queue",
                    "start_node": start_node,
                    "target_node": target_node,
                    "scope": "particular_node",
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
                    fps=fps,
                    width=video_width,
                    height=video_height,
                    ffmpeg_bin=resolved_ffmpeg,
                    save_preview_frame=prev_dfs,
                    step_duration=step_duration,
                )
                manifest["generated_videos"].append({
                    "algorithm": "dfs",
                    "filename": out_dfs.name,
                    "title": f"Particular Node ({start_node}): DFS Animation",
                    "data_structure": "LIFO Stack",
                    "start_node": start_node,
                    "target_node": target_node,
                    "scope": "particular_node",
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
                    fps=fps,
                    width=video_width,
                    height=video_height,
                    ffmpeg_bin=resolved_ffmpeg,
                    save_preview_frame=prev_comp,
                    step_duration=step_duration,
                )
                manifest["generated_videos"].append({
                    "algorithm": "comparison",
                    "filename": out_comp.name,
                    "title": f"Particular Node ({start_node}): Comparative Traversal (BFS vs DFS)",
                    "data_structure": "Queue vs Stack",
                    "start_node": start_node,
                    "target_node": target_node,
                    "scope": "particular_node",
                    "resolution": f"{video_width}x{video_height}",
                    "step_duration": step_duration,
                })

            (output_path / "video_manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
            print(f"[SUCCESS] All requested animations for Node {start_node} generated in {output_path}")

    # 3. Generate Graphviz DOT & PDF Walkthroughs (if dot is installed and render_pdf is True)
    if render_pdf:
        if shutil.which("dot"):
            visualizer.GRAPH = graph
            visualizer.START_NODE = start_node
            for alg in (("bfs", "dfs") if algorithm in ("both", "all", "comparison") else (algorithm,)):
                visualizer.render(alg, output_path)
        else:
            print("Notice: Graphviz 'dot' command not found. Skipping DOT and step PDF rendering.")

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create BFS/DFS video animations and PDF walkthroughs for a particular node."
    )
    parser.add_argument("--node", default="E", help="node at which to begin traversal (default: E)")
    parser.add_argument(
        "--target-node",
        help="optional destination node to search for (stops and highlights path when reached)",
    )
    parser.add_argument(
        "--algorithm",
        choices=("bfs", "dfs", "both", "comparison", "all"),
        default="all",
        help="algorithm to visualize: bfs, dfs, both, comparison, or all (default: all)",
    )
    parser.add_argument("--output", type=Path, default=Path("specific_node_output"), help="output directory")
    parser.add_argument("--graph-json", type=Path, help="path to existing graph.json metadata file to reuse")
    parser.add_argument("--random-graph", action="store_true", help="generate a random connected graph")
    parser.add_argument("--nodes", type=int, default=15, help="number of nodes (3-26) for random graph (default 15)")
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
    parser.add_argument("--ffmpeg-bin", help="path to ffmpeg binary executable")
    parser.add_argument("--save-frames", action="store_true", help="export sample preview PNG frames")

    args = parser.parse_args()

    SPEED_PRESETS = {
        "slow": 2.5,
        "normal": 1.8,
        "fast": 1.0,
    }
    step_duration = args.step_duration if args.step_duration is not None else SPEED_PRESETS.get(args.speed, 1.8)

    # Resolve Graph
    seed = args.seed
    if args.graph_json and args.graph_json.exists():
        with open(args.graph_json, "r", encoding="utf-8") as f:
            meta = json.load(f)
            graph = meta.get("graph", DEFAULT_GRAPH)
            seed = meta.get("random_seed", args.seed)
    elif args.random_graph:
        graph = random_connected_graph(args.nodes, args.edge_probability, args.seed)
    else:
        graph = DEFAULT_GRAPH

    generate_specific_node_traversal(
        graph=graph,
        start_node=args.node,
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
    )


if __name__ == "__main__":
    main()
