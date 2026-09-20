from __future__ import annotations

import random

import pytest

from puzzlekit import bits, ints, lines, sections, text


def test_ints_ignores_whatever_surrounds_the_numbers() -> None:
    """One helper replaces fixed-width slicing, three bracket strips and five regexes."""
    assert ints("Button A: X+94, Y+34") == [94, 34]
    assert ints("[#..#] 1,3,4 [12]") == [1, 3, 4, 12]
    assert ints("p=0,4 v=3,-3") == [0, 4, 3, -3]
    assert ints("no digits here") == []


def test_sections_splits_on_blank_lines() -> None:
    blob = "47|53\n97|13\n\n75,47,61\n97,61,53\n"
    assert sections(blob) == [["47|53", "97|13"], ["75,47,61", "97,61,53"]]


def test_sections_handles_crlf_and_trailing_blanks() -> None:
    assert sections("a\r\n\r\nb\n\n\n") == [["a"], ["b"]]


def test_text_and_lines_resolve_against_the_caller(tmp_path) -> None:
    sibling = tmp_path / "caller.py"
    sibling.write_text("")
    (tmp_path / "input.txt").write_text("one\ntwo\n")
    assert text("input.txt", relative_to=sibling) == "one\ntwo\n"
    assert lines("input.txt", relative_to=sibling) == ["one", "two"]


def test_bits_is_least_significant_first() -> None:
    assert list(bits(0b1011)) == [0, 1, 3]
    assert list(bits(0)) == []


def test_bits_agrees_with_bit_count() -> None:
    rng = random.Random(0)
    for _ in range(200):
        word = rng.randrange(1 << 64)
        assert len(list(bits(word))) == word.bit_count()
        assert sum(1 << i for i in bits(word)) == word


def test_bits_rejects_negatives() -> None:
    with pytest.raises(ValueError, match="two's complement"):
        list(bits(-1))
