"""Every example is executable and asserts its own answer.

That is the missing regression test from the review: none of the 44 files surveyed
asserted a single known-correct value.
"""

from __future__ import annotations

import importlib

import pytest

EXAMPLES = [
    "aoc2024_day06_patrol",
    "aoc2024_day10_trailheads",
    "aoc2024_day12_regions",
    "aoc2024_day16_reindeer",
    "aoc2024_day18_bisect",
    "union_find_components",
]


@pytest.mark.parametrize("name", EXAMPLES)
def test_example_reproduces_its_expected_answer(name: str) -> None:
    module = importlib.import_module(name)
    assert module.main() == module.EXPECTED


def test_scipy_flood_fill_agrees_with_the_hand_rolled_one() -> None:
    module = importlib.import_module("aoc2024_day12_regions")
    assert module.with_scipy(module.SAMPLE) == module.EXPECTED
