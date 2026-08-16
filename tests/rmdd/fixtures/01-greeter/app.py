"""Run the Pocket Greeter command."""

from __future__ import annotations

import sys


def greeting(name: str | None = None) -> str:
    """Return the documented greeting for a name or the world."""

    return f"Hello, {name or 'world'}!"


if __name__ == "__main__":
    supplied_name = sys.argv[1] if len(sys.argv) > 1 else None
    print(greeting(supplied_name))
