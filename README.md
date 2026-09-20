# puzzlekit

Small helpers for puzzle code — implicit-graph search, integer grids, input plumbing.

Extracted from a review of ~44 Advent of Code and Google Foobar solutions written under
time pressure. Every function here exists because the same shape was rewritten, slightly
differently, in file after file — and because at least one of those rewrites was wrong.

Python 3.13+, no runtime dependencies.

**Docs: <https://bur.gy/puzzlekit/>** — every example there is editable and runs in the
browser via PyScript.

```bash
uv add puzzlekit          # or: uv sync  (development)
uv run pytest
```

## What's in it

```python
from puzzlekit import Grid, Vec, backtrack, dijkstra, explore, ints, sections
```

### `explore` / `dijkstra` — search over states you generate, not a graph you build

`scipy.sparse.csgraph`, `networkx` and `rustworkx` all want a materialised graph. When
the state is `(position, heading)` or a grid plus a budget, building the matrix first is
more code than the loop. Two parameters carry the design:

```python
explore(starts, succ, *, order, key=identity)
```

**`order` has no default.** `"lifo"` where `"fifo"` was meant is a shortest-path
function that silently returns non-minimal distances. That exact substitution produced
wrong answers on 14% of random grids in one of the reviewed files, and its two
hand-written test cases both passed.

**`key=None` turns deduplication off**, which is required when counting distinct paths
rather than distinct states. `key=lambda s: s.pos` dedups on part of the state while the
rest rides along — a guard may revisit a cell, but revisiting a *heading* is a loop.

`succ(state)` yields `(next_state, step_cost)` and owns every domain rule: bounds,
walls, turn costs. Filtering at push time keeps illegal states out of the frontier
instead of rejecting them after popping.

`dijkstra` returns `(dist, preds)` where `preds[state]` lists **every** optimal
predecessor, so `backtrack(preds, targets)` recovers all shortest paths. The reviewed
solution answered that question with a second full traversal.

### `Grid` / `Vec` — for the per-cell walk

`grid[p]` **raises** off-grid. Python's negative-index wraparound is silent and yields
plausible wrong answers rather than tracebacks; it was the shared root of three separate
bugs in the survey. `grid.get(p, "#")` gives "out of bounds is a wall" without the
coordinate shift a padded border would force.

`Vec` is `(row, col)` with row increasing downwards, so `rot(1)` is clockwise on screen.
`norm2()` returns an `int` — compare those instead of `abs()`, which in one file was a
float square root taken purely to be compared, and was also 1.5× slower than the exact
version.

`neighbors()` yields `(delta, position, value)`. The delta comes back so a caller can
label the side it arrived from without a second lookup.

### `ints` / `sections` — stop writing parsers

`ints("p=0,4 v=3,-3") == [0, 4, 3, -3]`. Brackets, commas, labels and fixed-width
columns all stop mattering. `sections` splits on blank lines, which replaces the
`if/elif` parser state machines and `mode = None` flags.

## What's deliberately *not* in it

| Want | Use |
|---|---|
| union-find | `scipy.cluster.hierarchy.DisjointSet` — `merge()` returns a bool, `n_subsets` is maintained |
| integer infinity | `sys.maxsize` |
| popcount, bit width | `int.bit_count()`, `int.bit_length()` |
| flood fill, neighbour counts | `scipy.ndimage.label`, `scipy.ndimage.convolve` |
| sentinel border | `np.pad` |
| fixed-window scans | `np.lib.stride_tricks.sliding_window_view` |
| Dijkstra on an explicit graph | `scipy.sparse.csgraph`, `networkx` |
| topological order | `graphlib.TopologicalSorter` |
| memoization | `functools.cache` |
| input fetch + answer checking | `aocd` |

Three of the seven modules originally sketched for this package already existed. The
one that matched most exactly — union-find — is in a package the reviewed repo already
imported.

## Examples

Runnable, and each asserts its own answer (`uv run pytest` covers them):

| file | shows |
|---|---|
| [`aoc2024_day10_trailheads.py`](examples/aoc2024_day10_trailheads.py) | `key=None` — both parts from one traversal |
| [`aoc2024_day16_reindeer.py`](examples/aoc2024_day16_reindeer.py) | weighted implicit states, `backtrack` for all optimal paths |
| [`aoc2024_day12_regions.py`](examples/aoc2024_day12_regions.py) | flood fill, and the same answer via `scipy.ndimage.label` |
| [`aoc2024_day18_bisect.py`](examples/aoc2024_day18_bisect.py) | `bisect` over a monotone predicate instead of ~2000 re-runs |
| [`aoc2024_day06_patrol.py`](examples/aoc2024_day06_patrol.py) | when *not* to use the search helper |
| [`union_find_components.py`](examples/union_find_components.py) | the module this package doesn't ship |

## License

Apache-2.0
