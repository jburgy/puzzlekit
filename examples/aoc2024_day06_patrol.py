"""AoC 2024 day 6 - deliberately *not* using ``explore``.

A guard patrol is a single walker, not a frontier, and forcing it into a search API
would be worse than the ``while`` loop. What the package does contribute is
``Grid.find`` (the original's ``line.find("^") > 0`` treated column 0 as "not found")
and ``Vec.rot`` (clearer than modular arithmetic over a direction table).

The performance lesson is the interesting part. The original tried an obstruction on
every one of ~16000 free cells and took over ten minutes. Only cells the guard actually
visits can matter - and part 1 already computed that set, then threw it away.
"""

from puzzlekit import UP, Grid, Vec

SAMPLE = """\
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...\
"""

EXPECTED = (41, 6)


def patrol(grid: Grid[str], start: Vec) -> tuple[set[Vec], bool]:
    """Return the visited cells and whether the guard got stuck in a loop.

    Two return values rather than one overloaded one: the original returned
    ``list | None`` and every caller had to disambiguate it.
    """
    pos, heading = start, UP
    seen: set[tuple[Vec, Vec]] = set()
    while (pos, heading) not in seen:
        seen.add((pos, heading))
        ahead = pos + heading
        cell = grid.get(ahead)
        if cell is None:
            return {p for p, _ in seen}, False
        if cell == "#":
            heading = heading.rot()
        else:
            pos = ahead
    return {p for p, _ in seen}, True


def solve(text: str) -> tuple[int, int]:
    grid = Grid.parse(text)
    start = grid.find("^")
    grid[start] = "."

    path, _ = patrol(grid, start)

    loops = 0
    for candidate in path - {start}:  # not every free cell: only the ones on the path
        grid[candidate] = "#"
        _, looped = patrol(grid, start)
        grid[candidate] = "."
        loops += looped
    return len(path), loops


def main() -> tuple[int, int]:
    return solve(SAMPLE)


if __name__ == "__main__":
    print(*main(), sep="\n")
