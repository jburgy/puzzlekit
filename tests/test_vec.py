from __future__ import annotations

import math
import random

from puzzlekit import DOWN, LEFT, RIGHT, UP, Vec


def test_addition_is_vector_addition_not_tuple_concatenation() -> None:
    assert Vec(1, 2) + Vec(3, 4) == Vec(4, 6)
    assert Vec(1, 2) - Vec(3, 4) == Vec(-2, -2)
    assert Vec(1, 2) * 3 == Vec(3, 6)
    assert -Vec(1, 2) == Vec(-1, -2)


def test_rot_is_clockwise_on_screen() -> None:
    assert UP.rot() == RIGHT
    assert RIGHT.rot() == DOWN
    assert DOWN.rot() == LEFT
    assert LEFT.rot() == UP


def test_rot_cycles() -> None:
    v = Vec(3, -7)
    assert v.rot(4) == v
    assert v.rot(-1) == v.rot(3)


def test_norm2_is_exact_where_float_magnitude_is_not() -> None:
    """foo/bar/guard_fight.py compared ``abs(complex)`` floats to decide a tie-break."""
    rng = random.Random(0)
    vectors = [Vec(rng.randrange(10**9), rng.randrange(10**9)) for _ in range(200)]
    assert all(isinstance(v.norm2(), int) for v in vectors)
    assert all(v.norm2() == v.row**2 + v.col**2 for v in vectors)
    assert any(round(math.hypot(*v) ** 2) != v.norm2() for v in vectors)


def test_manhattan() -> None:
    assert Vec(3, 4).manhattan() == 7
    assert Vec(3, 4).manhattan(Vec(1, 1)) == 5


def test_hashable_as_a_dict_key() -> None:
    seen = {Vec(0, 0): "a"}
    seen[Vec(0, 0)] = "b"
    assert len(seen) == 1
