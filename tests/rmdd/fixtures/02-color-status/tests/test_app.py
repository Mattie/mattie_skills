"""Behavioral tests for Color Status."""

from pathlib import Path
import subprocess
import sys
import unittest

import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ColorStatusTests(unittest.TestCase):
    def test_current_color(self) -> None:
        self.assertEqual(app.status(), "blue")

    def test_command_output(self) -> None:
        result = subprocess.run(
            [sys.executable, "app.py"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.stdout, "blue\n")


if __name__ == "__main__":
    unittest.main()
