"""Tests for the Tiny Slug command-line utility."""

from __future__ import annotations

import subprocess
import sys
import unittest
from io import StringIO
from pathlib import Path

from colorama import Fore, Style

from app import (
    ACCESSORY_ART,
    FRIEND_ART,
    MOOD_FACES,
    SHELL_PATTERNS,
    SLUG_DRAWING,
    TRAIL_ART,
    insert_slug,
)


ROOT = Path(__file__).resolve().parents[1]


class TerminalBuffer(StringIO):
    """String buffer that reports itself as an interactive terminal."""

    def isatty(self) -> bool:
        """Report terminal capability for automatic-color tests."""

        return True


class TinySlugTests(unittest.TestCase):
    """Exercise the Python API and command-line behavior."""

    def test_insert_slug_matches_the_readme_example(self) -> None:
        self.assertEqual(
            insert_slug("The garden is quiet tonight."),
            "The garden is\n"
            "     _   _\n"
            "    (.)_(.)\n"
            " __/       \\__\n"
            "/             \\____\n"
            "quiet tonight.",
        )

    def test_insert_slug_preserves_text_without_whitespace(self) -> None:
        self.assertEqual(
            insert_slug("garden"),
            f"gar\n{SLUG_DRAWING}\nden",
        )

    def test_cli_prints_text_with_the_slug_on_its_own_lines(self) -> None:
        result = subprocess.run(
            [sys.executable, "app.py", "The garden is quiet tonight."],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout,
            f"The garden is\n{SLUG_DRAWING}\nquiet tonight.\n",
        )

    def test_cli_requires_a_phrase(self) -> None:
        result = subprocess.run(
            [sys.executable, "app.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stderr)
        self.assertIn("error:", result.stderr)

    def test_cli_rejects_more_than_one_phrase(self) -> None:
        result = subprocess.run(
            [sys.executable, "app.py", "first phrase", "second phrase"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stderr)
        self.assertIn("error:", result.stderr)

    def test_mood_and_shell_choices_change_the_slug(self) -> None:
        for mood, face in MOOD_FACES.items():
            with self.subTest(mood=mood):
                self.assertIn(face, insert_slug("garden", mood=mood))

        for shell, pattern in SHELL_PATTERNS.items():
            with self.subTest(shell=shell):
                self.assertIn(f"/{pattern}\\____", insert_slug("garden", shell=shell))

    def test_accessories_names_speech_trails_and_friends_combine(self) -> None:
        decorated = insert_slug(
            "The garden is quiet tonight.",
            mood="sleepy",
            accessory="flower",
            name="Moss",
            say="shh",
            trail="hearts",
            friend="butterfly",
        )

        self.assertIn(MOOD_FACES["sleepy"], decorated)
        self.assertIn(ACCESSORY_ART["flower"][0], decorated)
        self.assertIn("      Moss", decorated)
        self.assertIn("< shh >", decorated)
        self.assertIn(TRAIL_ART["hearts"], decorated)
        self.assertIn(FRIEND_ART["butterfly"], decorated)

    def test_each_decoration_choice_has_distinct_art(self) -> None:
        for accessory, art in ACCESSORY_ART.items():
            with self.subTest(accessory=accessory):
                output = insert_slug("garden", accessory=accessory)
                self.assertTrue(all(line in output for line in art))
        for trail, art in TRAIL_ART.items():
            with self.subTest(trail=trail):
                self.assertIn(art, insert_slug("garden", trail=trail))
        for friend, art in FRIEND_ART.items():
            with self.subTest(friend=friend):
                self.assertIn(art, insert_slug("garden", friend=friend))

    def test_color_modes_respect_terminal_detection(self) -> None:
        always = insert_slug("garden", color="always")
        automatic_terminal = insert_slug(
            "garden", color="auto", stream=TerminalBuffer()
        )
        automatic_redirect = insert_slug("garden", color="auto", stream=StringIO())

        self.assertIn(Fore.GREEN, always)
        self.assertIn(Style.RESET_ALL, always)
        self.assertIn(Fore.GREEN, automatic_terminal)
        self.assertNotIn(Fore.GREEN, automatic_redirect)
        self.assertNotIn(Fore.GREEN, insert_slug("garden", color="never"))

    def test_seeded_surprises_repeat_and_fill_all_surprise_options(self) -> None:
        first = insert_slug("garden", surprise=True, seed=73)
        second = insert_slug("garden", surprise=True, seed=73)

        self.assertEqual(first, second)
        self.assertTrue(any(face in first for face in MOOD_FACES.values()))
        self.assertTrue(
            any(f"/{pattern}\\____" in first for pattern in SHELL_PATTERNS.values())
        )
        self.assertTrue(
            any(all(line in first for line in art) for art in ACCESSORY_ART.values())
        )
        self.assertTrue(any(art in first for art in TRAIL_ART.values()))
        self.assertTrue(any(art in first for art in FRIEND_ART.values()))

    def test_explicit_choice_wins_when_combined_with_surprise(self) -> None:
        output = insert_slug(
            "garden",
            mood="grumpy",
            shell="stars",
            friend="bee",
            surprise=True,
            seed=9,
        )

        self.assertIn(MOOD_FACES["grumpy"], output)
        self.assertIn(f"/{SHELL_PATTERNS['stars']}\\____", output)
        self.assertIn(FRIEND_ART["bee"], output)

    def test_cli_accepts_the_documented_combination(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "app.py",
                "--mood",
                "sleepy",
                "--accessory",
                "flower",
                "--name",
                "Moss",
                "--say",
                "shh",
                "--trail",
                "hearts",
                "--friend",
                "ladybug",
                "--color",
                "never",
                "The garden is quiet tonight.",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn(MOOD_FACES["sleepy"], result.stdout)
        self.assertIn("Moss", result.stdout)
        self.assertIn(FRIEND_ART["ladybug"], result.stdout)

    def test_cli_rejects_unknown_option_values(self) -> None:
        invalid_commands = (
            ["--mood", "mysterious", "garden"],
            ["--friend", "dragonfly", "garden"],
            ["--weather", "sun", "garden"],
            ["--parade", "2", "garden"],
        )
        for arguments in invalid_commands:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, "app.py", *arguments],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("usage:", result.stderr)
                self.assertIn("error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
