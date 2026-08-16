# Tiny Slug

Tiny Slug adds a small ASCII slug somewhere inside a text string. It keeps the
original text in order and gives the slug and its decorations room on their
own lines.

Install the color support dependency, then give Tiny Slug a phrase:

```console
$ python3 -m pip install colorama
```

```console
$ python3 app.py "The garden is quiet tonight."
The garden is
     _   _
    (.)_(.)
 __/       \__
/             \____
quiet tonight.
```

With no options, the drawing may appear at any suitable point in the supplied
text, so its exact position is intentionally unspecified.

## Dress up a slug

Tiny Slug has nine small ways to make each visit more playful:

1. Pick a face with `--mood happy`, `sleepy`, `shy`, or `grumpy`.
2. Add a shell pattern with `--shell plain`, `dots`, `stripes`, or `stars`.
3. Wear a `flower`, `bow`, or `party-hat` with `--accessory`.
4. Put a name below the drawing with `--name Moss`.
5. Give the slug a speech bubble with `--say "good evening"`.
6. Leave a `dots`, `hearts`, or `stars` trail with `--trail`.
7. Bring along a `butterfly`, `ladybug`, or `bee` with `--friend`.
8. Color the slug and its decorations with `--color auto`, `always`, or
   `never`. Automatic color is used only when output goes to a terminal.
9. Let `--surprise` choose a mood, shell, accessory, trail, and friend. Add
   `--seed INTEGER` when the same surprise should appear again.

Options combine, so a named sleepy slug can wear a flower while leaving a
trail:

```console
$ python3 app.py --mood sleepy --accessory flower --name Moss --say "shh" --trail hearts "The garden is quiet tonight."
```

Pass exactly one text string. When the text is missing, more than one
positional value is supplied, or an option value is unknown, the command exits
with status 2 and prints argparse's usage and error output.

## Changelog

### Unreleased

- Added moods, patterned shells, accessories, names, speech bubbles, trails,
  garden friends, terminal colors, and repeatable surprises.
- Added `colorama` so colored slugs render consistently on Windows terminals
  as well as macOS and Linux.
