"""Input plumbing.

``aocd`` (advent-of-code-data) supersedes :func:`text` and :func:`lines` if you are
willing to hand it a session token; it caches per day and ships a runner that verifies
answers. This module exists for inputs already sitting next to the solution file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_INT = re.compile(r"-?\d+")


def _caller_dir(depth: int = 2) -> Path:
    origin = sys._getframe(depth).f_globals.get("__file__")
    return Path(origin).resolve().parent if origin else Path.cwd()


def text(name: str, *, relative_to: str | Path | None = None) -> str:
    """Read ``name`` from the **calling module's** directory, not the cwd.

    Every solution file in the survey that motivated this package hardcoded a path
    relative to the repo root, so none of them ran from anywhere else.
    """
    base = Path(relative_to).resolve().parent if relative_to else _caller_dir()
    return (base / name).read_text()


def lines(name: str, *, relative_to: str | Path | None = None) -> list[str]:
    """``splitlines()``, so there is no rstrip-or-not decision left to make."""
    base = Path(relative_to).resolve().parent if relative_to else _caller_dir()
    return (base / name).read_text().splitlines()


def sections(blob: str) -> list[list[str]]:
    """Split on blank lines.

    Replaces the ``if/elif`` parser state machines and the ``mode = None`` flags that
    show up whenever an input has two shapes stacked in one file.
    """
    chunks = blob.replace("\r\n", "\n").split("\n\n")
    return [chunk.splitlines() for chunk in chunks if chunk.strip()]


def ints(blob: str) -> list[int]:
    """Every integer in the string, sign included.

    Brackets, commas, labels and fixed-width columns all stop mattering.
    """
    return [int(m.group()) for m in _INT.finditer(blob)]
