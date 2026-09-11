#!/usr/bin/env python3
"""
GitHub Pages Static Site Generator for Artifacts
================================================
Reads all generated media assets and manifests from the artifacts branch
and builds a responsive, clean, and interactive single-page media explorer.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import re
import shutil
import sys
from typing import Any, Dict


def discover_artifacts(artifacts_dir: str) -> Dict[str, Any]:
    """Scan and parse all media directories and manifests from artifacts_dir."""
    data: Dict[str, Any] = {
        "collision": {"videos": [], "total": 0, "size_mb": 0.0, "generated_at": "", "base_seed": None},
        "gcd": {"grids": [], "total": 0, "generated_at": ""},
        "voronoi": {"diagrams": [], "total": 0, "seed": None, "generated_at": ""},
        "traversal": {"files": [], "videos": [], "graph": {}, "total": 0},
        "matrix": {"videos": [], "configuration": {}, "total": 0},
    }

    # 1. Collision Videos
    coll_dir = os.path.join(artifacts_dir, "collision-videos")
    coll_manifest = os.path.join(coll_dir, "manifest.json")
    if os.path.exists(coll_manifest):
        try:
            with open(coll_manifest, "r", encoding="utf-8") as f:
                c_data = json.load(f)
                data["collision"]["videos"] = c_data.get("videos", [])
                data["collision"]["total"] = c_data.get("total_videos", len(data["collision"]["videos"]))
                data["collision"]["size_mb"] = c_data.get("total_size_mb", 0.0)
                data["collision"]["generated_at"] = c_data.get("generated_at", "")
                data["collision"]["base_seed"] = c_data.get("base_seed")
                data["collision"]["release_tag"] = c_data.get("release_tag")
                data["collision"]["release_url"] = c_data.get("release_url")
                data["collision"]["release_archive_url"] = c_data.get("release_archive_url")
        except Exception as e:
            print(f"Warning loading collision manifest: {e}", file=sys.stderr)

    if not data["collision"]["videos"] and os.path.exists(coll_dir):
        mp4s = sorted([f for f in os.listdir(coll_dir) if f.endswith(".mp4")])
        data["collision"]["total"] = len(mp4s)
        for idx, f in enumerate(mp4s, 1):
            fpath = os.path.join(coll_dir, f)
            size_mb = round(os.path.getsize(fpath) / (1024 * 1024), 2)
            data["collision"]["videos"].append({
                "index": idx,
                "filename": f,
                "n_balls": 35,
                "initial_angle": 45.0,
                "speed": 240.0,
                "width": 1920,
                "height": 1080,
                "aspect_choice": "landscape_1080p",
                "file_size_mb": size_mb,
            })

    # 2. GCD Grids
    gcd_dir = os.path.join(artifacts_dir, "gcd-grids")
    gcd_manifest = os.path.join(gcd_dir, "manifest.json")
    if os.path.exists(gcd_manifest):
        try:
            with open(gcd_manifest, "r", encoding="utf-8") as f:
                g_data = json.load(f)
                data["gcd"]["grids"] = g_data.get("grids", [])
                data["gcd"]["total"] = g_data.get("total", len(data["gcd"]["grids"]))
                data["gcd"]["generated_at"] = g_data.get("generated_at", "")
                data["gcd"]["release_tag"] = g_data.get("release_tag")
                data["gcd"]["release_url"] = g_data.get("release_url")
                data["gcd"]["release_archive_url"] = g_data.get("release_archive_url")
        except Exception as e:
            print(f"Warning loading GCD manifest: {e}", file=sys.stderr)

    if not data["gcd"]["grids"] and os.path.exists(gcd_dir):
        svgs = sorted([f for f in os.listdir(gcd_dir) if f.endswith(".svg") and f.startswith("gcd-")])
        data["gcd"]["total"] = len(svgs)
        for s in svgs:
            parts = s.replace("gcd-", "").replace(".svg", "").split("-")
            w_val = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
            h_val = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            data["gcd"]["grids"].append({
                "file": s,
                "a": w_val,
                "b": h_val,
                "gcd": 1,
                "seed": 0,
                "steps": 1,
                "squares": 1,
            })

    # 3. Voronoi Diagrams
    vor_dir = os.path.join(artifacts_dir, "voronoi")
    vor_manifest = os.path.join(vor_dir, "manifest.json")
    if os.path.exists(vor_manifest):
        try:
            with open(vor_manifest, "r", encoding="utf-8") as f:
                v_data = json.load(f)
                data["voronoi"]["diagrams"] = v_data.get("files", [])
                data["voronoi"]["seed"] = v_data.get("seed")
                data["voronoi"]["generated_at"] = v_data.get("generated_at", "")
                data["voronoi"]["total"] = len(data["voronoi"]["diagrams"])
                data["voronoi"]["release_tag"] = v_data.get("release_tag")
                data["voronoi"]["release_url"] = v_data.get("release_url")
                data["voronoi"]["release_archive_url"] = v_data.get("release_archive_url")
        except Exception as e:
            print(f"Warning loading Voronoi manifest: {e}", file=sys.stderr)

    if not data["voronoi"]["diagrams"] and os.path.exists(vor_dir):
        v_svgs = sorted([f for f in os.listdir(vor_dir) if f.endswith(".svg") and "sites" in f])
        data["voronoi"]["total"] = len(v_svgs)
        for f in v_svgs:
            match = re.search(r"(\d+)", f)
            site_num = int(match.group(1)) if match else len(data["voronoi"]["diagrams"]) + 1
            data["voronoi"]["diagrams"].append({
                "sites": site_num,
                "file": f,
            })

    # 4. Traversal PDFs
    gen_dir = os.path.join(artifacts_dir, "generated")
    if os.path.exists(gen_dir):
        gen_manifest = os.path.join(gen_dir, "manifest.json")
        if os.path.exists(gen_manifest):
            try:
                with open(gen_manifest, "r", encoding="utf-8") as f:
                    t_data = json.load(f)
                    data["traversal"]["release_tag"] = t_data.get("release_tag")
                    data["traversal"]["release_url"] = t_data.get("release_url")
                    data["traversal"]["release_archive_url"] = t_data.get("release_archive_url")
            except Exception:
                pass

        graph_json = os.path.join(gen_dir, "graph.json")
        if os.path.exists(graph_json):
            try:
                with open(graph_json, "r", encoding="utf-8") as f:
                    data["traversal"]["graph"] = json.load(f)
            except Exception:
                pass

        pdf_items = []
        full_pdf = os.path.join(gen_dir, "bfs_dfs_complete_walkthrough.pdf")
        if os.path.exists(full_pdf):
            pdf_items.append({
                "title": "Complete BFS & DFS Walkthrough",
                "filename": "generated/bfs_dfs_complete_walkthrough.pdf",
                "description": "Full comparative walkthrough detailing Queue vs Stack exploration with state-colored nodes and discovery tree edges.",
                "size_kb": round(os.path.getsize(full_pdf) / 1024, 1),
            })

        spec_pdf = os.path.join(gen_dir, "specific-node", "specific_node_bfs_dfs_walkthrough.pdf")
        if os.path.exists(spec_pdf):
            pdf_items.append({
                "title": "Specific Node Search Walkthrough",
                "filename": "generated/specific-node/specific_node_bfs_dfs_walkthrough.pdf",
                "description": "Focused step-by-step exploration tracking discovery order from a designated start node.",
                "size_kb": round(os.path.getsize(spec_pdf) / 1024, 1),
            })

        # 4b. Traversal Videos
        video_items = []
        vids = [
            (
                "bfs_traversal.mp4",
                "Breadth-First Search (BFS) Animation",
                "Level-by-level wavefront exploration with FIFO Queue visualization and signal propagation.",
            ),
            (
                "dfs_traversal.mp4",
                "Depth-First Search (DFS) Animation",
                "Deep branch exploration and backtracking with LIFO Stack visualization.",
            ),
            (
                "bfs_dfs_comparison.mp4",
                "Comparative Traversal: BFS vs DFS",
                "Side-by-side synchronized comparison demonstrating Queue vs Stack on the identical graph topology.",
            ),
        ]
        for fname, v_title, v_desc in vids:
            vpath = os.path.join(gen_dir, fname)
            if os.path.exists(vpath):
                video_items.append({
                    "title": v_title,
                    "filename": f"generated/{fname}",
                    "description": v_desc,
                    "size_mb": round(os.path.getsize(vpath) / (1024 * 1024), 2),
                })

        data["traversal"]["files"] = pdf_items
        data["traversal"]["videos"] = video_items
        data["traversal"]["total"] = len(pdf_items) + len(video_items)

    # 5. Matrix Multiplication Animations
    mat_dir = os.path.join(artifacts_dir, "matrix-animations")
    if not os.path.exists(mat_dir):
        mat_dir = os.path.join(artifacts_dir, "2026-09-12", "matrix_multiplication_manim", "rendered_animations")

    if os.path.exists(mat_dir):
        mat_manifest = os.path.join(mat_dir, "animation_manifest.json")
        if os.path.exists(mat_manifest):
            try:
                with open(mat_manifest, "r", encoding="utf-8") as f:
                    m_data = json.load(f)
                    data["matrix"]["configuration"] = m_data.get("configuration", {})
                    data["matrix"]["generated_at"] = m_data.get("generated_at", "")
                    data["matrix"]["release_tag"] = m_data.get("release_tag")
                    data["matrix"]["release_url"] = m_data.get("release_url")
                    data["matrix"]["release_archive_url"] = m_data.get("release_archive_url")
            except Exception:
                pass

        descriptions = {
            "space_transformations.mp4": "Grid transformation under scaling, shearing, and general stretching.",
            "eigenvectors_invariant_directions.mp4": "Visualizing invariant eigen-lines and vectors that only scale (Av = lambda*v).",
            "matrix_multiplication_composition.mp4": "Sequential composition: A then B vs one-shot product matrix C = B @ A.",
            "master_matrix_multiplication_story.mp4": "Master cinematic story connecting basis vectors, eigenvectors, and matrix multiplication.",
        }

        mat_vids = []
        for f in sorted(os.listdir(mat_dir)):
            if f.endswith(".mp4"):
                fpath = os.path.join(mat_dir, f)
                pretty_title = f.replace(".mp4", "").replace("_", " ").title()
                mat_vids.append({
                    "filename": f"matrix-animations/{f}",
                    "title": pretty_title,
                    "description": descriptions.get(f, "Linear transformation animation generated with Manim."),
                    "size_mb": round(os.path.getsize(fpath) / (1024 * 1024), 2),
                })
        data["matrix"]["videos"] = mat_vids
        data["matrix"]["total"] = len(mat_vids)

    return data


def generate_html(data: Dict[str, Any], template_path: str) -> str:
    """Generate the complete self-contained HTML5 explorer from template."""
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    json_payload = json.dumps(data)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    total_media = (
        data["collision"]["total"]
        + data["gcd"]["total"]
        + data["voronoi"]["total"]
        + data["traversal"]["total"]
        + data["matrix"]["total"]
    )

    replacements = {
        "__DATA_JSON__": json_payload,
        "__NOW_STR__": now_str,
        "__TOTAL_MEDIA__": str(total_media),
        "__COLLISION_TOTAL__": str(data["collision"]["total"]),
        "__GCD_TOTAL__": str(data["gcd"]["total"]),
        "__VORONOI_TOTAL__": str(data["voronoi"]["total"]),
        "__TRAVERSAL_TOTAL__": str(data["traversal"]["total"]),
        "__MATRIX_TOTAL__": str(data["matrix"]["total"]),
    }

    for token, val in replacements.items():
        html = html.replace(token, val)

    return html


def build_site(artifacts_dir: str, output_dir: str):
    """Main build orchestrator: copy assets and generate index.html."""
    print("=" * 65)
    print("GITHUB PAGES ARTIFACTS WEBSITE BUILDER")
    print(f"Source Artifacts: {artifacts_dir}")
    print(f"Output Directory: {output_dir}")
    print("=" * 65)

    os.makedirs(output_dir, exist_ok=True)

    # 1. Discover manifests and media metadata
    data = discover_artifacts(artifacts_dir)
    print(f"Discovered:")
    print(f"  - Collision Videos: {data['collision']['total']} items ({data['collision']['size_mb']} MB)")
    print(f"  - GCD Grids:        {data['gcd']['total']} items")
    print(f"  - Voronoi Diagrams: {data['voronoi']['total']} items")
    print(f"  - Traversal PDFs:   {data['traversal']['total']} items")
    print(f"  - Matrix Videos:    {data['matrix']['total']} items")

    # 2. Copy media directories to output_dir
    subdirs = ["collision-videos", "gcd-grids", "voronoi", "generated", "matrix-animations"]
    for sub in subdirs:
        src_path = os.path.join(artifacts_dir, sub)
        dst_path = os.path.join(output_dir, sub)
        if os.path.exists(src_path):
            print(f"Copying {sub} -> {dst_path}...")
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)

    dst_mat = os.path.join(output_dir, "matrix-animations")
    if not os.path.exists(dst_mat):
        fallback_mat = os.path.join(artifacts_dir, "2026-09-12", "matrix_multiplication_manim", "rendered_animations")
        if os.path.exists(fallback_mat):
            print(f"Copying fallback matrix-animations -> {dst_mat}...")
            shutil.copytree(fallback_mat, dst_mat)

    # 3. Create .nojekyll to prevent GitHub Pages from ignoring files
    nojekyll_path = os.path.join(output_dir, ".nojekyll")
    with open(nojekyll_path, "w") as f:
        pass

    # 4. Generate index.html from template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "template.html")
    if not os.path.exists(template_path):
        # Fallback to local
        template_path = "template.html"

    html_content = generate_html(data, template_path)
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print()
    print(f"Website built successfully at: {index_path}")
    print(f"Total HTML Size: {len(html_content):,} bytes")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Build static GitHub Pages site from artifacts.")
    parser.add_argument(
        "--artifacts-dir",
        type=str,
        default=".",
        help="Path to directory containing artifacts branch files (default: .)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="_site",
        help="Destination directory for static site (default: _site)",
    )
    args = parser.parse_args()
    build_site(args.artifacts_dir, args.output_dir)


if __name__ == "__main__":
    main()
