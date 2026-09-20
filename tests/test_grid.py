from __future__ import annotations

import pytest

from puzzlekit import ALL8, Grid, Vec
from puzzlekit.vec import RIGHT, UP

MAZE = """\
^..#
.#..
...E\
"""


@pytest.fixture
def grid() -> Grid[str]:
    return Grid.parse(MAZE)


def test_negative_indices_raise_instead_of_wrapping(grid: Grid[str]) -> None:
    """The shared root of three separate wrong-answer bugs in the survey."""
    with pytest.raises(IndexError):
        grid[Vec(0, -1)]
    with pytest.raises(IndexError):
        grid[Vec(-1, 0)]
    with pytest.raises(IndexError):
        grid[Vec(0, 4)]


def test_membership_is_positional(grid: Grid[str]) -> None:
    assert Vec(0, 0) in grid
    assert Vec(3, 0) not in grid


def test_get_default_replaces_the_sentinel_border(grid: Grid[str]) -> None:
    assert grid.get(Vec(9, 9), "#") == "#"
    assert grid.get(Vec(0, 0)) == "^"


def test_ragged_input_is_rejected() -> None:
    """Two files in the survey took ``max(map(len, rows))``, two took ``min``; neither said why."""
    with pytest.raises(ValueError, match="ragged"):
        Grid(["abc", "ab"])


def test_find_works_at_column_zero(grid: Grid[str]) -> None:
    """``line.find("^") > 0`` treated column 0 as 'not found'."""
    assert grid.find("^") == Vec(0, 0)


def test_find_raises_when_absent(grid: Grid[str]) -> None:
    with pytest.raises(ValueError, match="not in grid"):
        grid.find("Z")


def test_neighbors_yields_the_delta(grid: Grid[str]) -> None:
    """Carrying the delta is what lets a caller label the side it came from."""
    assert dict((d, v) for d, _, v in grid.neighbors(Vec(0, 0))) == {RIGHT: ".", Vec(1, 0): "."}


def test_neighbors_filters_out_of_bounds(grid: Grid[str]) -> None:
    assert all(p in grid for _, p, _ in grid.neighbors(Vec(0, 0), ALL8))
    assert len(list(grid.neighbors(Vec(0, 0), ALL8))) == 3


def test_ray_walks_until_it_leaves(grid: Grid[str]) -> None:
    assert "".join(v for _, v in grid.ray(Vec(2, 0), UP, include_start=True)) == "..^"
    assert list(grid.ray(Vec(0, 0), UP)) == []


def test_cells_is_reading_order(grid: Grid[str]) -> None:
    assert [p for p, _ in grid.cells()][:5] == [
        Vec(0, 0),
        Vec(0, 1),
        Vec(0, 2),
        Vec(0, 3),
        Vec(1, 0),
    ]


def test_findall(grid: Grid[str]) -> None:
    assert list(grid.findall("#")) == [Vec(0, 3), Vec(1, 1)]


def test_copy_is_independent(grid: Grid[str]) -> None:
    other = grid.copy()
    other[Vec(0, 0)] = "X"
    assert grid[Vec(0, 0)] == "^"


def test_str_roundtrips(grid: Grid[str]) -> None:
    assert str(grid) == MAZE
