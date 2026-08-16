"""Behavior tests derived from the Pocket Greeter documentation."""

from pathlib import Path
import subprocess
import sys
import unittest

import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PocketGreeterTests(unittest.TestCase):
    def test_named_greeting(self) -> None:
        self.assertEqual(app.greeting("Ada"), "Hello, Ada!")

    def test_default_command_greeting(self) -> None:
        result = subprocess.run(
            [sys.executable, "app.py"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.stdout, "Hello, world!\n")


if __name__ == "__main__":
    unittest.main()
