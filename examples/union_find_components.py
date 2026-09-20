"""Union-find - the module puzzlekit deliberately does *not* ship.

``scipy.cluster.hierarchy.DisjointSet`` already has the two properties a hand-rolled
version in the survey was missing, and whose absence was its worst performance bug:

* ``merge(a, b)`` returns whether a merge actually happened, so you can count merges
  without a separate find-and-compare.
* ``n_subsets`` is **maintained**, not recomputed. The original asked
  ``sum(circuit != set() for circuit in circuits) == 1`` after every union - a
  thousand-element scan that also allocated a thousand empty sets, ~999000 operations
  to learn a number that a decrement already knew.

Union by size and path halving come free, which also removes the O(n^2) worst case of
merging into the lower-numbered index.
"""

from scipy.cluster.hierarchy import DisjointSet

NODES = 10
#: Deliberately ordered so the graph connects on the last edge, not the first spanning one.
EDGES = [
    (0, 1),
    (2, 3),
    (4, 5),
    (6, 7),
    (8, 9),
    (0, 2),
    (4, 6),
    (1, 3),
    (5, 7),
    (0, 4),
    (8, 0),
]

EXPECTED = (16, (8, 0))


def solve(nodes: int, edges: list[tuple[int, int]], prefix: int = 6) -> tuple[int, tuple[int, int]]:
    """Product of the three largest components after ``prefix`` edges, and the edge
    that first connects the whole graph."""
    partial = DisjointSet(range(nodes))
    for a, b in edges[:prefix]:
        partial.merge(a, b)
    sizes = sorted((len(s) for s in partial.subsets()), reverse=True)
    product = sizes[0] * sizes[1] * sizes[2]

    live = DisjointSet(range(nodes))
    connector = None
    for edge in edges:
        live.merge(*edge)
        if live.n_subsets == 1:  # O(1), and correct by construction
            connector = edge
            break
    assert connector is not None
    return product, connector


def main() -> tuple[int, tuple[int, int]]:
    return solve(NODES, EDGES)


if __name__ == "__main__":
    print(*main(), sep="\n")
