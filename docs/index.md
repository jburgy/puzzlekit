# puzzlekit

Small helpers for puzzle code — implicit-graph search, integer grids, input plumbing.

Extracted from a review of ~44 Advent of Code and Google Foobar solutions written under
time pressure. Every function here exists because the same shape was rewritten, slightly
differently, in file after file — and because at least one of those rewrites was wrong.

Python 3.13+, no runtime dependencies.

```bash
uv add puzzlekit
```

Every code block in these docs is live: edit it, press **Run**, and it executes in your
browser via [PyScript](https://pyscript.net/). The first run downloads a Python
interpreter, so give it a few seconds.

```{py-editor}
from puzzlekit import Grid, Vec, explore

grid = Grid.parse("""\
#########
#S..#..E#
#.#.#.#.#
#.......#
#########""")

start, end = grid.find("S"), grid.find("E")

def open_neighbours(pos):
    return [(q, 1) for _, q, v in grid.neighbors(pos) if v != "#"]

for pos, cost in explore([start], open_neighbours, order="fifo"):
    if pos == end:
        print("shortest path:", cost, "steps")
        break
```

Change `order="fifo"` to `order="lifo"` and run it again. The answer gets worse and
nothing complains — which is the entire reason that parameter has no default.

## Contents

```{toctree}
:maxdepth: 2

searching
grid
parsing
design
api
```

## What's deliberately *not* here

| Want | Use |
|---|---|
| union-find | {class}`scipy.cluster.hierarchy.DisjointSet` — `merge()` returns a bool, `n_subsets` is maintained |
| integer infinity | {data}`sys.maxsize` |
| popcount, bit width | {meth}`int.bit_count`, {meth}`int.bit_length` |
| flood fill, neighbour counts | `scipy.ndimage.label`, `scipy.ndimage.convolve` |
| sentinel border | `numpy.pad` |
| fixed-window scans | `numpy.lib.stride_tricks.sliding_window_view` |
| Dijkstra on an explicit graph | `scipy.sparse.csgraph`, `networkx` |
| topological order | {class}`graphlib.TopologicalSorter` |
| memoization | {func}`functools.cache` |
| puzzle input fetch + answer checking | [`aocd`](https://pypi.org/project/advent-of-code-data/) |

Three of the seven modules originally sketched for this package already existed. The one
that matched most exactly — union-find — was in a package the reviewed repo already
imported.
