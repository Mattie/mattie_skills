"""Command-line entry point for the Tiny Slug utility."""

from __future__ import annotations

import argparse
import random
import re
import sys
from typing import TextIO

from colorama import Fore, Style, just_fix_windows_console


MOODS = ("happy", "sleepy", "shy", "grumpy")
SHELLS = ("plain", "dots", "stripes", "stars")
ACCESSORIES = ("flower", "bow", "party-hat")
TRAILS = ("dots", "hearts", "stars")
FRIENDS = ("butterfly", "ladybug", "bee")

MOOD_FACES = {
    "happy": "    (^)_(^)",
    "sleepy": "    (-)_(-)",
    "shy": "    (o)_(o)",
    "grumpy": "    (>)_(<)",
}
SHELL_PATTERNS = {
    "plain": "             ",
    "dots": ". . . . . . .",
    "stripes": "|/|/|/|/|/|/|",
    "stars": "* * * * * * *",
}
ACCESSORY_ART = {
    "flower": ("      {@}",),
    "bow": ("     {<=>}",),
    "party-hat": ("       /\\", "      /__\\"),
}
TRAIL_ART = {
    "dots": ". . .",
    "hearts": "<3 <3 <3",
    "stars": "* * *",
}
FRIEND_ART = {
    "butterfly": "}i{",
    "ladybug": "(o)",
    "bee": "<B>",
}

SLUG_DRAWING = """     _   _
    (.)_(.)
 __/       \\__
/             \\____"""


def _split_text(text: str) -> tuple[str, str]:
    """Split text at a readable point near its middle.

    An internal whitespace run becomes the line break around the drawing. If
    there is no such run, the text is split between characters instead.
    """

    midpoint = len(text) / 2
    internal_gaps = [
        match
        for match in re.finditer(r"\s+", text)
        if match.start() > 0 and match.end() < len(text)
    ]
    if internal_gaps:
        gap = min(
            internal_gaps,
            key=lambda match: abs(((match.start() + match.end()) / 2) - midpoint),
        )
        return text[: gap.start()], text[gap.end() :]

    split_at = (len(text) + 1) // 2
    return text[:split_at], text[split_at:]


def _render_slug(
    *,
    mood: str | None,
    shell: str,
    accessory: str | None,
    name: str | None,
    saying: str | None,
    trail: str | None,
    friend: str | None,
) -> list[str]:
    """Build one slug and its decorations as a list of output lines."""

    lines: list[str] = []
    if saying is not None:
        lines.extend((f"< {saying} >", "       \\"))
    if accessory:
        lines.extend(ACCESSORY_ART[accessory])

    lines.extend(
        (
            "     _   _",
            MOOD_FACES[mood] if mood else "    (.)_(.)",
            " __/       \\__",
            f"/{SHELL_PATTERNS[shell]}\\____",
        )
    )
    if name is not None:
        lines.append(f"      {name}")
    if trail:
        lines.append(f"      {TRAIL_ART[trail]}")
    if friend:
        lines.append(f"      {FRIEND_ART[friend]}")
    return lines


def _use_color(mode: str, stream: TextIO | None) -> bool:
    """Resolve a color mode against the destination stream."""

    if mode == "always":
        return True
    if mode == "never":
        return False
    if mode != "auto":
        raise ValueError(f"unknown color mode: {mode}")
    return bool(stream and stream.isatty())


def insert_slug(
    text: str,
    *,
    mood: str | None = None,
    shell: str | None = None,
    accessory: str | None = None,
    name: str | None = None,
    say: str | None = None,
    trail: str | None = None,
    friend: str | None = None,
    color: str = "never",
    surprise: bool = False,
    seed: int | None = None,
    stream: TextIO | None = None,
) -> str:
    """Insert a decorated slug inside ``text``.

    Surprise values fill options that the caller did not choose explicitly.
    A seed makes all surprise selections repeatable.
    """

    if surprise:
        generator = random.Random(seed)
        mood = mood or generator.choice(MOODS)
        shell = shell or generator.choice(SHELLS)
        accessory = accessory or generator.choice(ACCESSORIES)
        trail = trail or generator.choice(TRAILS)
        friend = friend or generator.choice(FRIENDS)

    drawing = "\n".join(
        _render_slug(
            mood=mood,
            shell=shell or "plain",
            accessory=accessory,
            name=name,
            saying=say,
            trail=trail,
            friend=friend,
        )
    )
    if _use_color(color, stream):
        drawing = f"{Fore.GREEN}{drawing}{Style.RESET_ALL}"

    before, after = _split_text(text)
    parts = [part for part in (before, drawing, after) if part]
    return "\n".join(parts)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description="Add an ASCII slug to some text.")
    parser.add_argument("--mood", choices=MOODS)
    parser.add_argument("--shell", choices=SHELLS)
    parser.add_argument("--accessory", choices=ACCESSORIES)
    parser.add_argument("--name")
    parser.add_argument("--say")
    parser.add_argument("--trail", choices=TRAILS)
    parser.add_argument("--friend", choices=FRIENDS)
    parser.add_argument("--color", choices=("auto", "always", "never"), default="auto")
    parser.add_argument("--surprise", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("text", help="text to decorate")
    return parser


def main() -> None:
    """Parse command-line arguments and print the decorated text."""

    args = build_parser().parse_args()
    just_fix_windows_console()
    print(
        insert_slug(
            args.text,
            mood=args.mood,
            shell=args.shell,
            accessory=args.accessory,
            name=args.name,
            say=args.say,
            trail=args.trail,
            friend=args.friend,
            color=args.color,
            surprise=args.surprise,
            seed=args.seed,
            stream=sys.stdout,
        )
    )


if __name__ == "__main__":
    main()
