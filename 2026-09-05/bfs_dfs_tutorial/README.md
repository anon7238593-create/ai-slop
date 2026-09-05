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

## Customize the graph

Edit `GRAPH` and `START_NODE` near the top of `bfs_dfs_visualizer.py`. The neighbour ordering is preserved, so it controls the exact teaching sequence. `GRAPH` is currently undirected: include both directions for every connection.
