"""Create one Graphviz PDF for every step of a BFS traversal.

Run from this directory:

    python3 bfs_visualize.py

The DOT files are temporary; the generated PDFs are kept in ``bfs_pdfs/``.
Graphviz's ``dot`` executable must be installed and available on PATH.
"""

from pathlib import Path
import subprocess
from typing import Hashable, Iterable, Mapping

from traversals import BFSStep, bfs_trace

Vertex = Hashable
Graph = Mapping[Vertex, Iterable[Vertex]]


def _quote(value: object) -> str:
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def bfs_step_dot(graph: Graph, snapshot: BFSStep) -> str:
    """Return a readable DOT document for one BFS snapshot."""
    vertices = set(graph)
    for neighbors in graph.values():
        vertices.update(neighbors)
    vertices.update(snapshot.discovered)
    order = sorted(vertices, key=str)
    identifiers = {vertex: f"v{index}" for index, vertex in enumerate(order)}
    lines = [
        "graph BFS {",
        '  graph [layout=dot, overlap=false, labelloc=t, '
        f'label={_quote(f"BFS step {snapshot.step}: processing {snapshot.current}\\\\nqueue: {list(snapshot.queue)}")}, '
        'fontsize=18];',
        '  node [shape=circle, style=filled, fontname="Helvetica"];',
        '  edge [fontname="Helvetica"];',
    ]
    for vertex in order:
        if vertex == snapshot.current:
            fill = "gold"
        elif vertex in snapshot.discovered:
            fill = "palegreen2"
        else:
            fill = "white"
        lines.append(
            f"  {identifiers[vertex]} [label={_quote(vertex)}, fillcolor={fill}];"
        )

    seen_edges: set[tuple[Vertex, Vertex]] = set()
    for source, neighbors in graph.items():
        for target in neighbors:
            edge = tuple(sorted((source, target), key=str))
            if edge in seen_edges:
                continue
            seen_edges.add(edge)
            if snapshot.parent.get(target) == source or snapshot.parent.get(source) == target:
                color = "forestgreen"
                width = 3
            else:
                color = "gray60"
                width = 1
            lines.append(
                f"  {identifiers[source]} -- {identifiers[target]} "
                f"[color={color}, penwidth={width}];"
            )
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_bfs_pdfs(
    graph: Graph,
    start: Vertex,
    output_dir: str | Path = "bfs_pdfs",
) -> list[Path]:
    """Render all BFS snapshots to numbered PDF files with Graphviz."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    steps, _, _, _ = bfs_trace(graph, start)
    pdfs: list[Path] = []
    for snapshot in steps:
        dot_path = output_path / f"bfs_step_{snapshot.step:02d}.dot"
        pdf_path = output_path / f"bfs_step_{snapshot.step:02d}.pdf"
        dot_path.write_text(bfs_step_dot(graph, snapshot), encoding="utf-8")
        subprocess.run(
            ["dot", "-Tpdf", str(dot_path), "-o", str(pdf_path)],
            check=True,
        )
        dot_path.unlink()
        pdfs.append(pdf_path)
    return pdfs


def main() -> None:
    graph = {
        "A": ["B", "C"],
        "B": ["A", "D", "E"],
        "C": ["A", "F"],
        "D": ["B"],
        "E": ["B", "F"],
        "F": ["C", "E"],
    }
    pdfs = render_bfs_pdfs(graph, "A")
    print(f"Generated {len(pdfs)} BFS step PDFs in {pdfs[0].parent}/")


if __name__ == "__main__":
    main()
