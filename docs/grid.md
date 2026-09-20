# Grids and vectors

{class}`~puzzlekit.grid.Grid` is scoped to the **per-cell walk** — guard patrols, ray
casting, flood fill. If the whole grid can be processed at once, numpy and scipy already
win; see [below](#when-to-stop-looping).

## `grid[p]` raises off-grid

Python's negative indices wrap silently. On a grid that turns "one step left from column
zero" into "the far end of the previous row", which produces a plausible wrong answer
rather than a traceback. It was the shared root of three separate bugs in the reviewed
code.

```{py-editor}
from puzzlekit import Grid, Vec

grid = Grid.parse("""\
^..#
.#..
...E""")

rows = grid.rows
print("raw list-of-lists wraps: ", rows[0][-1])

try:
    grid[Vec(0, -1)]
except IndexError as err:
    print("Grid refuses:", err)

# The common case is check-then-fetch, so get() does both:
print("out of bounds ->", grid.get(Vec(9, 9), "#"))
```

`grid.get(p, "#")` gives you "out of bounds is a wall" without the coordinate shift a
padded sentinel border would force on every other line of the solution.

Construction also rejects ragged input. Two reviewed files took `max(map(len, rows))` and
two took `min`; neither said which assumption it was making.

## `neighbors` yields the delta

```{py-editor}
from puzzlekit import ALL8, Grid, Vec

grid = Grid.parse("""\
.#.
#@#
.#.""")

for delta, pos, value in grid.neighbors(Vec(1, 1)):
    print(f"{delta} -> {pos} = {value!r}")

walls = sum(v == "#" for _, _, v in grid.neighbors(Vec(1, 1), ALL8))
print("8-way count:", walls)
```

The delta comes back with the position so a caller can attach a label to the direction it
arrived from — a side, a wall, a turn — without a second lookup. One reviewed file spelled
that as four near-identical `if` blocks.

`ray` walks a direction to the edge, which replaces the `while True: ... else: break`
idiom and the assorted slice/`itemgetter`/manual-loop spellings of "read four cells in a
line".

```{py-editor}
from puzzlekit import Grid, Vec
from puzzlekit.vec import DIAGONAL

grid = Grid.parse("""\
MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX""")

found = 0
for pos, value in grid.cells():
    if value != "X":
        continue
    for delta in DIAGONAL:
        word = "".join(v for _, v in grid.ray(pos, delta, include_start=True))
        found += word.startswith("XMAS")
print("diagonal XMAS:", found)
```

## `Vec` is exact

`(row, col)`, row increasing downwards, so `rot(1)` is a clockwise quarter turn on
screen. `complex` is the stdlib alternative and the reason this exists: it makes every
grid access an `int(z.real)` and turns integer comparisons into float ones.

```{py-editor}
import math
from puzzlekit import DOWN, LEFT, RIGHT, UP, Vec

print(UP.rot(), RIGHT.rot(), DOWN.rot(), LEFT.rot())
print("addition is vector addition:", Vec(1, 2) + Vec(3, 4))
print("tuple concat would give:   ", tuple(Vec(1, 2)) + tuple(Vec(3, 4)))

v = Vec(999_999_999, 999_999_998)
print("norm2 (exact int):", v.norm2())
print("via hypot:        ", round(math.hypot(*v) ** 2))
```

A reviewed file compared `abs(complex)` floats to decide which target to shoot. The exact
integer version was not only correct, it was 1.5× faster — the square root existed purely
to be compared away.

(when-to-stop-looping)=
## When to stop looping

If the grid fits in an array, the frontier loop is usually the wrong tool entirely:

| Task | Call |
|---|---|
| connected components | `scipy.ndimage.label` |
| neighbour counts | `scipy.ndimage.convolve` with a 3×3 kernel |
| sentinel border | `numpy.pad` |
| fixed-window scan | `numpy.lib.stride_tricks.sliding_window_view` |
| find a character | `numpy.argwhere(grid == ch)` |
| iterate cells | `numpy.ndenumerate` |

`puzzlekit` does not wrap any of these. The
[`aoc2024_day12_regions.py`](https://github.com/jburgy/puzzlekit/blob/main/examples/aoc2024_day12_regions.py)
example computes the same answer both ways so the boundary is visible.
