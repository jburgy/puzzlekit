"""AoC 2024 day 12 - flood fill, and when to stop hand-rolling one.

``explore(order="lifo")`` is a fine flood fill and ``Grid.neighbors`` yielding the
value means the region test and the perimeter count read the same way.

But note the alternative at the bottom: if the grid fits in a numpy array,
``scipy.ndimage.label`` does connected components in one call, in C. This example
exists as much to mark that boundary as to demonstrate the helper.
"""

from puzzlekit import Grid, Vec, explore

SAMPLE = """\
AAAA
BBCD
BBCC
EEEC\
"""

EXPECTED = 140


def solve(text: str) -> int:
    grid = Grid.parse(text)
    seen: set[Vec] = set()
    total = 0

    for start, crop in grid.cells():
        if start in seen:
            continue

        def same_crop(pos: Vec, crop: str = crop) -> list[tuple[Vec, int]]:
            return [(q, 1) for _, q, v in grid.neighbors(pos) if v == crop]

        region = {pos for pos, _ in explore([start], same_crop, order="lifo")}
        seen |= region
        perimeter = sum(4 - sum(1 for _ in same_crop(pos)) for pos in region)
        total += len(region) * perimeter
    return total


def with_scipy(text: str) -> int:
    """The same answer, without a frontier loop at all."""
    import numpy as np
    from scipy.ndimage import label

    plots = np.array([list(line) for line in text.splitlines()])
    total = 0
    for crop in np.unique(plots):
        regions, count = label(plots == crop)
        for index in range(1, count + 1):
            mask = np.pad(regions == index, 1)
            perimeter = sum(
                int((mask & ~np.roll(mask, shift, axis)).sum())
                for axis in (0, 1)
                for shift in (1, -1)
            )
            total += int(mask.sum()) * perimeter
    return total


def main() -> int:
    return solve(SAMPLE)


if __name__ == "__main__":
    print(main())
