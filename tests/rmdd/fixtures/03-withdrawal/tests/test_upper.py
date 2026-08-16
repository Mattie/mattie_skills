"""Tests for the uppercase transformation."""

from pathlib import Path
import subprocess
import sys
import unittest

from upper import upper


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class UpperTests(unittest.TestCase):
    def test_upper(self) -> None:
        self.assertEqual(upper("Hello"), "HELLO")

    def test_upper_command(self) -> None:
        result = subprocess.run(
            [sys.executable, "app.py", "upper", "hello"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.stdout, "HELLO\n")

    def test_removed_lower_command_is_unavailable(self) -> None:
        result = subprocess.run(
            [sys.executable, "app.py", "lower", "HELLO"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
