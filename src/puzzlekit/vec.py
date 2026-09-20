"""Integer 2-D points.

One convention, fixed here and used everywhere else in the package: ``Vec(row, col)``
with ``row`` increasing **downwards**, so ``rot(1)`` is a clockwise quarter turn on screen.

``complex`` is the stdlib alternative and the reason this module exists: it makes every
grid access an ``int(z.real)`` and turns exact integer comparisons into float ones.
"""

from __future__ import annotations

from typing import NamedTuple


class Vec(NamedTuple):
    row: int
    col: int

    def __add__(self, other: tuple[int, int]) -> Vec:  # type: ignore[override]
        return Vec(self.row + other[0], self.col + other[1])

    def __sub__(self, other: tuple[int, int]) -> Vec:
        return Vec(self.row - other[0], self.col - other[1])

    def __mul__(self, k: int) -> Vec:  # type: ignore[override]
        return Vec(self.row * k, self.col * k)

    __rmul__ = __mul__

    def __neg__(self) -> Vec:
        return Vec(-self.row, -self.col)

    def rot(self, quarter_turns: int = 1) -> Vec:
        """Rotate clockwise. Exact: no floats, no ``1j``."""
        row, col = self
        for _ in range(quarter_turns % 4):
            row, col = col, -row
        return Vec(row, col)

    def norm2(self) -> int:
        """Squared length, as an ``int``.

        Compare these instead of ``abs()``: exact, and faster than a square root you
        were only ever going to compare.
        """
        return self.row * self.row + self.col * self.col

    def manhattan(self, other: tuple[int, int] = (0, 0)) -> int:
        return abs(self.row - other[0]) + abs(self.col - other[1])


UP = Vec(-1, 0)
RIGHT = Vec(0, 1)
DOWN = Vec(1, 0)
LEFT = Vec(0, -1)

#: Clockwise from up. The order is stable and may be relied on.
ORTHOGONAL = (UP, RIGHT, DOWN, LEFT)
DIAGONAL = (Vec(-1, 1), Vec(1, 1), Vec(1, -1), Vec(-1, -1))
ALL8 = ORTHOGONAL + DIAGONAL
