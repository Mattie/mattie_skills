"""Dispatch locally installed text transformation operations."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys


def main(arguments: list[str]) -> int:
    """Run the requested transformation."""

    if len(arguments) != 2:
        return 2
    operation, text = arguments
    module_path = Path(__file__).with_name(f"{operation}.py")
    if not operation.isidentifier() or not module_path.is_file():
        return 2
    transform = getattr(importlib.import_module(operation), operation, None)
    if not callable(transform):
        return 2
    print(transform(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
