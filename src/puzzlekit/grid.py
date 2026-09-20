"""A rectangular grid addressed by :class:`~puzzlekit.vec.Vec`.

Scoped deliberately to the *per-cell walk* — guard patrols, ray casting, flood fill.
If the whole grid can be processed at once, numpy/scipy already win: ``np.pad`` for a
sentinel border, ``scipy.ndimage.label`` for regions, ``scipy.ndimage.convolve`` with a
3x3 kernel for neighbour counts, ``sliding_window_view`` for fixed-window scans.

Two decisions worth stating:

* ``grid[p]`` **raises** off-grid. Python's negative-index wraparound is silent and
  produces plausible wrong answers rather than tracebacks.
* There is no ``pad=`` sentinel border, because it would shift every coordinate by one.
  ``grid.get(p, "#")`` buys the same "out of bounds is a wall" behaviour with no shift.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence

from .vec import ORTHOGONAL, Vec


class Grid[T]:
    __slots__ = ("height", "rows", "width")

    def __init__(self, rows: Iterable[Sequence[T]]) -> None:
        self.rows: list[list[T]] = [list(row) for row in rows]
        if not self.rows:
            raise ValueError("empty grid")
        widths = {len(row) for row in self.rows}
        if len(widths) != 1:
            raise ValueError(f"ragged grid, row widths {sorted(widths)}")
        self.height = len(self.rows)
        self.width = widths.pop()

    @classmethod
    def parse(cls, text: str) -> Grid[str]:
        return Grid(text.splitlines())

    def __contains__(self, p: tuple[int, int]) -> bool:
        """Membership is **positional**, not by value."""
        row, col = p
        return 0 <= row < self.height and 0 <= col < self.width

    def __getitem__(self, p: tuple[int, int]) -> T:
        if p not in self:
            raise IndexError(f"{tuple(p)} outside {self.height}x{self.width} grid")
        return self.rows[p[0]][p[1]]

    def __setitem__(self, p: tuple[int, int], value: T) -> None:
        if p not in self:
            raise IndexError(f"{tuple(p)} outside {self.height}x{self.width} grid")
        self.rows[p[0]][p[1]] = value

    def get(self, p: tuple[int, int], default: T | None = None) -> T | None:
        """Bounds check and fetch in one, which is what callers actually want."""
        return self[p] if p in self else default  # noqa: SIM401 - self.get would recurse

    def cells(self) -> Iterator[tuple[Vec, T]]:
        for row, values in enumerate(self.rows):
            for col, value in enumerate(values):
                yield Vec(row, col), value

    def findall(self, value: T) -> Iterator[Vec]:
        return (p for p, v in self.cells() if v == value)

    def find(self, value: T) -> Vec:
        """First position holding ``value``, in reading order.

        Raises rather than returning a sentinel, so ``grid.find("^")`` at column 0
        cannot be mistaken for "not found".
        """
        for p in self.findall(value):
            return p
        raise ValueError(f"{value!r} not in grid")

    def neighbors(
        self, p: tuple[int, int], deltas: Iterable[Vec] = ORTHOGONAL
    ) -> Iterator[tuple[Vec, Vec, T]]:
        """Yield ``(delta, position, value)`` for in-bounds neighbours.

        The delta comes back too: that is what lets a caller attach a label or a side
        to the direction it arrived from without a second lookup.
        """
        here = Vec(*p)
        for delta in deltas:
            q = here + delta
            if q in self:
                yield delta, q, self[q]

    def ray(
        self, start: tuple[int, int], delta: tuple[int, int], *, include_start: bool = False
    ) -> Iterator[tuple[Vec, T]]:
        """Walk from ``start`` along ``delta`` until leaving the grid."""
        p = Vec(*start)
        if not include_start:
            p = p + delta
        while p in self:
            yield p, self[p]
            p = p + delta

    def copy(self) -> Grid[T]:
        return Grid(self.rows)

    def __iter__(self) -> Iterator[list[T]]:
        return iter(self.rows)

    def __str__(self) -> str:
        return "\n".join("".join(str(v) for v in row) for row in self.rows)

    def __repr__(self) -> str:
        return f"<Grid {self.height}x{self.width}>"
