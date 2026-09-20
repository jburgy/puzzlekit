"""AoC 2024 day 10 - both parts from a single traversal.

The point: part 1 counts distinct summits reachable from a trailhead, part 2 counts
distinct *paths* to them. One traversal answers both, but only if deduplication can be
switched off - hence ``key=None``. A search helper that hardcodes a ``seen`` set cannot
express part 2 at all.
"""

from puzzlekit import Grid, Vec, explore

SAMPLE = """\
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732\
"""

EXPECTED = (36, 81)


def solve(text: str) -> tuple[int, int]:
    grid = Grid.parse(text)

    def uphill(pos: Vec) -> list[tuple[Vec, int]]:
        height = int(grid[pos])
        return [(q, 1) for _, q, v in grid.neighbors(pos) if v.isdigit() and int(v) == height + 1]

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
    return score, rating


def main() -> tuple[int, int]:
    return solve(SAMPLE)


if __name__ == "__main__":
    print(*main(), sep="\n")
