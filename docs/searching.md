# Search

`scipy.sparse.csgraph`, `networkx` and `rustworkx` all want a graph you have already
built. When the state is `(position, heading)`, or a grid plus a budget, or a packed
bitmask, materialising that graph first is more code than the loop it replaces.
{func}`~puzzlekit.search.explore` and {func}`~puzzlekit.search.dijkstra` take a
successor *function* instead.

```python
explore(starts, succ, *, order, key=identity)
```

`starts` is an *iterable* of states, never a bare state — a state is very often itself a
tuple, and guessing would be a coin flip.

`succ(state)` yields `(next_state, step_cost)` pairs and owns every domain rule: bounds
checks, walls, turn costs. Filtering at push time is the point; it keeps illegal states
out of the frontier rather than rejecting them after popping.

## `order` has no default

`"lifo"` with a visited set is the *component-labelling* variant of a frontier loop.
`"fifo"` is the shortest-path variant. They look identical on the page and differ only
in which method pops.

A reviewed solution used the first where it needed the second and was wrong on 14% of
random grids — while both of its hand-written test cases passed. A default would have
made that the easy mistake to keep making.

```{py-editor}
from puzzlekit import Vec, explore
from puzzlekit.vec import ORTHOGONAL

GRID = [
    [0, 0, 0],
    [0, 1, 0],
    [0, 0, 0],
]

def escape(order):
    """Shortest path to the far corner, allowed to delete at most one wall."""
    goal = Vec(2, 2)

    def succ(state):
        pos, used = state
        out = []
        for delta in ORTHOGONAL:
            q = pos + delta
            if 0 <= q.row < 3 and 0 <= q.col < 3:
                spent = used + GRID[q.row][q.col]
                if spent <= 1:
                    out.append(((q, spent), 1))
        return out

    for (pos, _), cost in explore([(Vec(0, 0), 0)], succ, order=order):
        if pos == goal:
            return cost + 1  # the puzzle counts cells, not steps

print("fifo:", escape("fifo"), "<- correct")
print("lifo:", escape("lifo"), "<- plausible, and wrong")
```

The Manhattan distance alone puts the answer at 5. The original returned 3.

## `key` decides what counts as "already seen"

`key` maps a state to its dedup identity. Three settings, three different algorithms:

`key=identity` (the default)
: Visit each state once. Flood fill, plain BFS.

`key=None`
: No deduplication at all. Required when you are counting *paths* rather than states.

`key=lambda s: s.pos`
: Dedup on part of the state while the rest rides along. A guard may revisit a cell;
  revisiting a *heading* is a loop.

Advent of Code 2024 day 10 asks for both at once — distinct summits in part 1, distinct
routes to them in part 2. One traversal answers both, but only with dedup off:

```{py-editor}
from puzzlekit import Grid, explore

grid = Grid.parse("""\
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732""")

def uphill(pos):
    height = int(grid[pos])
    return [
        (q, 1)
        for _, q, v in grid.neighbors(pos)
        if v.isdigit() and int(v) == height + 1
    ]

score = rating = 0
for start, value in grid.cells():
    if value != "0":
        continue
    summits = set()
    for pos, _ in explore([start], uphill, order="lifo", key=None):
        if grid[pos] == "9":
            summits.add(pos)
            rating += 1
    score += len(summits)

print("part 1 (summits):", score)
print("part 2 (routes): ", rating)
```

Drop `key=None` and part 2 collapses to part 1. A helper that hardcodes a `seen` set
cannot express this at all.

`order="priority"` with `key=None` raises, because without deduplication a cyclic graph
never settles.

## Weights, and every optimal path

{func}`~puzzlekit.search.dijkstra` returns `(dist, preds)` where `preds[state]` lists
**every** optimal predecessor. {func}`~puzzlekit.search.backtrack` then walks that
backwards, so "which tiles lie on *some* best path" costs a graph walk instead of a
second search.

The reviewed solution answered it with a whole second traversal that materialised
complete paths as ever-growing tuples.

```{py-editor}
from puzzlekit import RIGHT, Grid, backtrack, dijkstra
from puzzlekit.vec import ORTHOGONAL

grid = Grid.parse("""\
###############
#.......#....E#
#.#.###.#.###.#
#.....#.#...#.#
#.###.#####.#.#
#.#.#.......#.#
#.#.#####.###.#
#...........#.#
###.#.#####.#.#
#...#.....#.#.#
#.#.#.###.#.#.#
#.....#...#.#.#
#.###.#.#.#.#.#
#S..#.....#...#
###############""")

start, end = grid.find("S"), grid.find("E")

def moves(state):
    pos, heading = state
    ahead = pos + heading
    out = [((pos, heading.rot(1)), 1000), ((pos, heading.rot(-1)), 1000)]
    if grid.get(ahead, "#") != "#":
        out.append(((ahead, heading), 1))
    return out

dist, preds = dijkstra([(start, RIGHT)], moves)

arrivals = [(end, h) for h in ORTHOGONAL if (end, h) in dist]
best = min(dist[a] for a in arrivals)
winners = [a for a in arrivals if dist[a] == best]
tiles = {pos for pos, _ in backtrack(preds, winners)}

print("best score:", best)
print("tiles on some best path:", len(tiles))
```

Note the state: `(position, heading)`. Turning costs 1000 and stepping costs 1, so this
graph has four nodes per cell and does not exist until `moves` invents it.

## Why a generator

`explore` yields rather than calling back. Callers routinely need to do two unrelated
things per visit — record a set *and* bump a counter, as in the day 10 example above, or
count an area *and* write a region label. A callback returning a single value cannot
express either without closure gymnastics; a `for` loop with plain local variables can.

## When not to use it

A guard patrol is a single walker, not a frontier. Forcing it through a search API is
worse than the `while` loop:

```{py-editor}
from puzzlekit import UP, Grid

grid = Grid.parse("""\
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...""")

start = grid.find("^")
grid[start] = "."

def patrol(pos, heading=UP):
    """Returns the visited cells and whether the guard got stuck in a loop."""
    seen = set()
    while (pos, heading) not in seen:
        seen.add((pos, heading))
        cell = grid.get(pos + heading)
        if cell is None:
            return {p for p, _ in seen}, False
        if cell == "#":
            heading = heading.rot()
        else:
            pos = pos + heading
    return {p for p, _ in seen}, True

path, _ = patrol(start)
print("cells visited:", len(path))

# Only cells on that path can ever matter - the original tried all 16000 free ones.
loops = 0
for candidate in path - {start}:
    grid[candidate] = "#"
    loops += patrol(start)[1]
    grid[candidate] = "."
print("obstructions that cause a loop:", loops)
```

What the package contributes here is `Grid.find` (the original's `line.find("^") > 0`
treated column 0 as "not found") and `Vec.rot`, not a frontier.
