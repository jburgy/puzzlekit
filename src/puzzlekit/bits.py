"""The one bit-twiddling helper the stdlib is missing.

``int.bit_count()`` is popcount, ``int.bit_length()`` is width, ``np.packbits`` and
``np.unpackbits`` convert to and from arrays. Iterating set-bit *indices* has no
equivalent, and hand-rolling it tends to come out as a string round-trip like
``bin(word)[:1:-1]``.
"""

from __future__ import annotations

from collections.abc import Iterator


def bits(word: int) -> Iterator[int]:
    """Indices of the set bits of ``word``, least significant first.

    >>> list(bits(0b1011))
    [0, 1, 3]
    """
    if word < 0:
        raise ValueError("negative ints have infinitely many set bits in two's complement")
    while word:
        low = word & -word
        yield low.bit_length() - 1
        word ^= low
