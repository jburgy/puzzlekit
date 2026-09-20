"""Every test here is a regression for a defect found while reviewing real solution files."""

from __future__ import annotations

import random

import pytest

from puzzlekit import Vec, backtrack, dijkstra, explore
from puzzlekit.vec import ORTHOGONAL

# --------------------------------------------------------------------------------------
# A small weighted DAG with two equally good routes A->D.
#
#      B
#    /   \
#   A     D --- E
#    \   /
#      C
GRAPH: dict[str, list[tuple[str, int]]] = {
    "A": [("B", 1), ("C", 1)],
    "B": [("D", 1)],
    "C": [("D", 1)],
    "D": [("E", 1)],
    "E": [],
}


def graph_succ(node: str) -> list[tuple[str, int]]:
    return GRAPH[node]


def test_order_has_no_default() -> None:
    """The whole point: you cannot get a frontier without saying which one."""
    with pytest.raises(TypeError):
        explore(["A"], graph_succ)  # type: ignore[call-arg]


def test_bad_order_raises_before_the_first_yield() -> None:
    """Eager validation - a generator would hide the mistake until iteration."""
    with pytest.raises(ValueError, match="order must be one of"):
        explore(["A"], graph_succ, order="bfs")  # type: ignore[arg-type]


def test_priority_rejects_key_none() -> None:
    with pytest.raises(ValueError, match="never settles"):
        explore(["A"], graph_succ, order="priority", key=None)


# --------------------------------------------------------------------------------------
# foo/bar/bunnies_escape.py: shortest path through a grid where you may delete one wall.
# The original used stack.pop() with a visited check - the *component labelling* variant -
# where the shortest-path variant was required, and was wrong on 14% of random grids.

State = tuple[Vec, int]


def escape(grid: list[list[int]], order: str) -> int:
    height, width = len(grid), len(grid[0])
    goal = Vec(height - 1, width - 1)

    def succ(state: State) -> list[tuple[State, int]]:
        pos, used = state
        out = []
        for delta in ORTHOGONAL:
            q = pos + delta
            if not (0 <= q.row < height and 0 <= q.col < width):
                continue
            spent = used + grid[q.row][q.col]
            if spent <= 1:
                out.append(((q, spent), 1))
        return out

    for (pos, _), cost in explore([(Vec(0, 0), 0)], succ, order=order):  # type: ignore[arg-type]
        if pos == goal:
            return cost + 1  # the puzzle counts cells, not steps
    return 0


def reference_escape(grid: list[list[int]]) -> int:
    """Nine lines of obviously-correct BFS. This is what caught the original bug."""
    from collections import deque

    height, width = len(grid), len(grid[0])
    start = (0, 0, 0)
    seen = {start}
    queue = deque([(start, 1)])
    while queue:
        (row, col, used), dist = queue.popleft()
        if (row, col) == (height - 1, width - 1):
            return dist
        for drow, dcol in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nrow, ncol = row + drow, col + dcol
            if not (0 <= nrow < height and 0 <= ncol < width):
                continue
            spent = used + grid[nrow][ncol]
            if spent > 1:
                continue
            state = (nrow, ncol, spent)
            if state not in seen:
                seen.add(state)
                queue.append((state, dist + 1))
    return 0


def random_grids(count: int, size: int, seed: int) -> list[list[list[int]]]:
    rng = random.Random(seed)
    return [
        [[int(rng.random() < 0.32) for _ in range(size)] for _ in range(size)] for _ in range(count)
    ]


def test_fifo_matches_an_independent_bfs() -> None:
    for grid in random_grids(200, 5, seed=0):
        assert escape(grid, "fifo") == reference_escape(grid)


def test_lifo_is_not_a_shortest_path_search() -> None:
    """Documents why ``order`` is mandatory rather than defaulted."""
    grids = random_grids(200, 5, seed=0)
    assert any(escape(g, "lifo") != reference_escape(g) for g in grids)


def test_the_three_by_three_case_the_original_got_wrong() -> None:
    grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    assert escape(grid, "fifo") == 5  # the original returned 3, below the Manhattan bound


# --------------------------------------------------------------------------------------
# aoc2024/day10.py: part 1 counts distinct endpoints, part 2 counts distinct paths.
# Path counting requires that deduplication be *off*.


def test_key_none_counts_paths_not_states() -> None:
    visits = [state for state, _ in explore(["A"], graph_succ, order="lifo", key=None)]
    assert visits.count("D") == 2  # once via B, once via C
    assert visits.count("E") == 2


def test_default_key_dedups() -> None:
    visits = [state for state, _ in explore(["A"], graph_succ, order="fifo")]
    assert sorted(visits) == ["A", "B", "C", "D", "E"]


def test_key_can_project_part_of_the_state() -> None:
    """aoc2024/day6: a guard revisiting a cell is fine, revisiting a *heading* is a loop."""
    seen_positions = set()

    def succ(state: tuple[int, int]) -> list[tuple[tuple[int, int], int]]:
        pos, heading = state
        return [(((pos + 1) % 3, heading), 1)]

    for (pos, _), _ in explore([(0, 0)], succ, order="fifo", key=lambda s: s[0]):
        seen_positions.add(pos)
    assert seen_positions == {0, 1, 2}  # terminates: dedup ignores the heading


# --------------------------------------------------------------------------------------
# aoc2024/day16.py: turning costs 1000, stepping costs 1.


def test_priority_respects_edge_weights() -> None:
    weighted = {"A": [("B", 10), ("C", 1)], "C": [("B", 1)], "B": []}
    costs = dict(explore(["A"], lambda n: weighted[n], order="priority"))
    assert costs["B"] == 2


def test_priority_yields_in_nondecreasing_cost_order() -> None:
    weighted = {"A": [("B", 5), ("C", 2)], "C": [("D", 1)], "B": [], "D": []}
    order = [cost for _, cost in explore(["A"], lambda n: weighted[n], order="priority")]
    assert order == sorted(order)


def test_dijkstra_records_every_optimal_predecessor() -> None:
    dist, preds = dijkstra(["A"], graph_succ)
    assert dist["E"] == 3
    assert sorted(preds["D"]) == ["B", "C"]


def test_backtrack_recovers_all_optimal_paths() -> None:
    """aoc2024/day16 part 2 was a whole second traversal; it is a backward walk."""
    _, preds = dijkstra(["A"], graph_succ)
    assert backtrack(preds, ["E"]) == {"A", "B", "C", "D", "E"}


def test_multi_source() -> None:
    dist, _ = dijkstra(["B", "C"], graph_succ)
    assert dist["D"] == 1
    assert "A" not in dist


def test_goal_stops_early() -> None:
    dist, _ = dijkstra(["A"], graph_succ, goal=lambda n: n == "D")
    assert "E" not in dist
