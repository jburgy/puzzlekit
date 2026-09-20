"""AoC 2024 day 18 - stop linear-scanning a monotone predicate.

"Is the exit still reachable after k bytes have fallen?" is False-then-True and never
flips back. The original re-ran BFS for every k, about 2000 times, for 29 seconds.
``bisect`` with a ``key`` asks the same question ~11 times.

The habit worth stealing: whenever a loop reads "increase a parameter until a boolean
flips", reach for ``bisect`` before writing the ``for``.
"""

from bisect import bisect_left

from puzzlekit import Grid, Vec, explore, ints

SAMPLE = """\
5,4
4,2
4,5
3,0
2,1
6,3
2,4
1,5
0,6
3,3
2,6
5,1
1,2
5,5
2,5
6,5
1,4
0,4
6,4
1,1
6,1
1,0
0,5
1,6
2,0\
"""

SIZE = 7
PREFIX = 12
EXPECTED = (22, "6,1")


def steps_to_exit(fallen: list[Vec], size: int) -> int | None:
    blocked = set(fallen)
    exit_ = Vec(size - 1, size - 1)
    grid = Grid([["."] * size for _ in range(size)])

    def open_neighbours(pos: Vec) -> list[tuple[Vec, int]]:
        return [(q, 1) for _, q, _ in grid.neighbors(pos) if q not in blocked]

    if Vec(0, 0) in blocked:
        return None
    for pos, cost in explore([Vec(0, 0)], open_neighbours, order="fifo"):
        if pos == exit_:
            return cost
    return None


def solve(text: str, size: int = SIZE, prefix: int = PREFIX) -> tuple[int, str]:
    coords = [Vec(row, col) for col, row in (ints(line) for line in text.splitlines())]

    part1 = steps_to_exit(coords[:prefix], size)
    assert part1 is not None

    counts = range(1, len(coords) + 1)
    first_blocking = bisect_left(
        counts, True, key=lambda k: steps_to_exit(coords[:k], size) is None
    )
    culprit = coords[counts[first_blocking] - 1]
    return part1, f"{culprit.col},{culprit.row}"


def main() -> tuple[int, str]:
    return solve(SAMPLE)


if __name__ == "__main__":
    print(*main(), sep="\n")
