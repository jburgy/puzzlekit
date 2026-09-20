"""Frontier search over an **implicit** state space.

``scipy.sparse.csgraph``, ``networkx`` and ``rustworkx`` all want a materialised graph.
When states are generated on the fly — ``(position, heading)``, a grid with a budget,
a packed bitmask — building the matrix first is more code than the loop. That gap is
what this module fills.

Two parameters carry the whole design:

``order``
    Has **no default**. ``"lifo"`` where ``"fifo"`` was meant is a shortest-path
    function that silently returns non-minimal distances, and a default would make
    that the easy mistake to keep making.

``key``
    Maps a state to its dedup identity. ``key=None`` disables deduplication entirely,
    which is required when counting distinct paths; ``key=lambda s: s.pos`` dedups on
    part of the state while the rest rides along.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Hashable, Iterable, Iterator, Mapping
from heapq import heappop, heappush
from itertools import count
from typing import Literal

type Order = Literal["fifo", "lifo", "priority"]
type Successors[S] = Callable[[S], Iterable[tuple[S, int]]]

_ORDERS = ("fifo", "lifo", "priority")


def _identity[S](state: S) -> S:
    return state


def explore[S](
    starts: Iterable[S],
    succ: Successors[S],
    *,
    order: Order,
    key: Callable[[S], Hashable] | None = _identity,
) -> Iterator[tuple[S, int]]:
    """Yield ``(state, cost)`` in visit order.

    ``starts`` is an *iterable* of states, never a bare state — a state is very often
    itself a tuple, and guessing would be a coin flip.

    ``succ`` yields ``(next_state, step_cost)`` and owns every domain rule: bounds
    checks, walls, turn costs. Filtering at push time is the point; it is what keeps
    illegal states out of the frontier instead of rejecting them after popping.

    A generator, not a callback, so callers keep plain local accumulators — some need
    to record a set *and* bump a counter on the same visit.
    """
    if order not in _ORDERS:
        raise ValueError(f"order must be one of {_ORDERS}, not {order!r}")
    if order == "priority":
        if key is None:
            raise ValueError(
                "order='priority' needs a key: without dedup a cyclic graph never settles"
            )
        return _priority(starts, succ, key)
    return _flat(starts, succ, order, key)


def _flat[S](
    starts: Iterable[S],
    succ: Successors[S],
    order: Order,
    key: Callable[[S], Hashable] | None,
) -> Iterator[tuple[S, int]]:
    frontier: deque[tuple[S, int]] = deque()
    seen: set[Hashable] | None = None if key is None else set()

    def push(state: S, cost: int) -> None:
        if seen is not None:
            k = key(state)  # type: ignore[misc]
            if k in seen:
                return
            seen.add(k)
        frontier.append((state, cost))

    for state in starts:
        push(state, 0)
    pop = frontier.popleft if order == "fifo" else frontier.pop
    while frontier:
        state, cost = pop()
        yield state, cost
        for nxt, step in succ(state):
            push(nxt, cost + step)


def _priority[S](
    starts: Iterable[S], succ: Successors[S], key: Callable[[S], Hashable]
) -> Iterator[tuple[S, int]]:
    tie = count()  # states need not be orderable
    heap: list[tuple[int, int, S]] = []
    best: dict[Hashable, int] = {}
    for state in starts:
        k = key(state)
        if k not in best:
            best[k] = 0
            heappush(heap, (0, next(tie), state))
    settled: set[Hashable] = set()
    while heap:
        cost, _, state = heappop(heap)
        k = key(state)
        if k in settled:
            continue
        settled.add(k)
        yield state, cost
        for nxt, step in succ(state):
            nk = key(nxt)
            if nk in settled:
                continue
            total = cost + step
            if nk not in best or total < best[nk]:
                best[nk] = total
                heappush(heap, (total, next(tie), nxt))


def dijkstra[S](
    starts: Iterable[S],
    succ: Successors[S],
    *,
    goal: Callable[[S], bool] | None = None,
) -> tuple[dict[S, int], dict[S, list[S]]]:
    """Return ``(dist, preds)``.

    ``preds[state]`` lists **every** optimal predecessor, so all shortest paths are
    recoverable with :func:`backtrack` instead of a second traversal.

    With ``goal``, the search stops once a goal state settles and ``dist`` is then
    only complete for states closer than that goal.
    """
    tie = count()
    heap: list[tuple[int, int, S]] = []
    dist: dict[S, int] = {}
    preds: dict[S, list[S]] = {}
    for state in starts:
        if state not in dist:
            dist[state] = 0
            preds[state] = []
            heappush(heap, (0, next(tie), state))
    settled: set[S] = set()
    while heap:
        cost, _, state = heappop(heap)
        if state in settled:
            continue
        settled.add(state)
        if goal is not None and goal(state):
            break
        for nxt, step in succ(state):
            total = cost + step
            known = dist.get(nxt)
            if known is None or total < known:
                dist[nxt] = total
                preds[nxt] = [state]
                heappush(heap, (total, next(tie), nxt))
            elif total == known and state not in preds[nxt]:
                preds[nxt].append(state)
    return dist, preds


def backtrack[S](preds: Mapping[S, Iterable[S]], targets: Iterable[S]) -> set[S]:
    """Every state lying on some optimal path into ``targets``."""
    seen: set[S] = set()
    stack = list(targets)
    while stack:
        state = stack.pop()
        if state in seen:
            continue
        seen.add(state)
        stack.extend(preds.get(state, ()))
    return seen
