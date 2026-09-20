"""Small helpers for puzzle code, extracted from a review of ~44 solution files.

Deliberately absent, because something better already exists:

===========================  =================================================
union-find                   ``scipy.cluster.hierarchy.DisjointSet``
integer infinity             ``sys.maxsize``
popcount / bit width         ``int.bit_count()`` / ``int.bit_length()``
flood fill, neighbour count  ``scipy.ndimage.label`` / ``.convolve``
sentinel border              ``np.pad``
Dijkstra on explicit graphs  ``scipy.sparse.csgraph`` / ``networkx``
topological order            ``graphlib.TopologicalSorter``
memoization                  ``functools.cache``
input fetch + answer check   ``aocd``
===========================  =================================================
"""

from .bits import bits
from .grid import Grid
from .io import ints, lines, sections, text
from .search import backtrack, dijkstra, explore
from .vec import ALL8, DIAGONAL, DOWN, LEFT, ORTHOGONAL, RIGHT, UP, Vec

__all__ = [
    "ALL8",
    "DIAGONAL",
    "DOWN",
    "LEFT",
    "ORTHOGONAL",
    "RIGHT",
    "UP",
    "Grid",
    "Vec",
    "backtrack",
    "bits",
    "dijkstra",
    "explore",
    "ints",
    "lines",
    "sections",
    "text",
]
