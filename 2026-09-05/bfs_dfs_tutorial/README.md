# BFS / DFS Graphviz walkthrough

This small teaching demo turns an example graph traversal into numbered Graphviz DOT files and polished PDF slides. Orange means the node currently being processed, blue means discovered and waiting, green means complete, and purple edges show the discovery tree.

## Run

From this directory:

```bash
python3 bfs_dfs_visualizer.py --algorithm both
```

Generated files are placed in `output/bfs/` and `output/dfs/`. Each folder has one `step_XX.dot` source file and matching `step_XX.pdf` visual for every traversal state.

Run one algorithm or choose a different output location:

```bash
python3 bfs_dfs_visualizer.py --algorithm bfs --output demo_output
```

Graphviz must be installed and its `dot` command available on your PATH.

## Generate a random graph

The visualizer can make a connected random graph for a new demonstration. Pass a seed when you want the exact graph to be repeatable; the generated `graph.json` also records the graph and seed.

```bash
python3 bfs_dfs_visualizer.py --random-graph --nodes 10 --edge-probability 0.30 --seed 20260905
```

The repository workflow `.github/workflows/generate_pdf_for_traversel.yml` uses this mode and publishes the refreshed PDFs to the `artifacts` branch.

## Start from one specific node

`specific_node_traversal.py` is a dedicated entry point for demonstrating both traversals from one selected node (node `G` by default). It creates its own DOT files, individual PDFs, and graph metadata.

```bash
python3 specific_node_traversal.py --node G --algorithm both
```

Use `--random-graph --nodes 10 --seed 20260905` with it to reproduce the workflow's random graph. The workflow also creates a single `specific_node_bfs_dfs_walkthrough.pdf` for easier viewing.

## Customize the graph

Edit `GRAPH` and `START_NODE` near the top of `bfs_dfs_visualizer.py`. The neighbour ordering is preserved, so it controls the exact teaching sequence. `GRAPH` is currently undirected: include both directions for every connection.
