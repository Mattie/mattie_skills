# Adaptable toolkit acceptance

Run from the repository root:

```text
node --test tests/thought-rig/*.test.mjs
node skills/thought-rig/toolkit/canvas/check-extensions.mjs
node skills/thought-rig/toolkit/canvas/check-reset.mjs
```

These check document projection, provenance, collision protection, legacy import,
unknown objects, semantic readback, revision conflicts, alternate surfaces,
extension contracts, reset history, distribution privacy, and packaged links.

## Fresh-agent exercise

Give an agent only the packaged skill location, a new task workspace, and this
task. Do not pass implementation discussion or source-project experiments:

> Build a rig for three illustrated story moments so a person can move the
> moments, edit durations, and attach notes about pacing. Create a synthetic
> contact sheet. Adapt the task-local cutter or importer to an input format other
> than the stock regions JSON. Add one useful custom control or object beyond the
> starter. Preserve original assets and identities. Exercise edit/save/readback,
> repeated extraction, and an independent agent edit without losing existing
> decisions. Label synthetic verification actions. Do not modify shared tooling.

Reserve browser verification for the parent if tool sessions cannot be shared.
Then open the result, exercise the custom control, undo/redo, save/reopen, and
check its CLI semantic readback against the actual edits. Retain task-local input,
output, handoff, and verification files. The acceptance target is recovered
meaning, not a polished second application.

## Recorded result: 2026-11-01

Passed the fresh-agent exercise with a separate timeline surface. The agent
extracted three labeled nested SVG panels, preserved source hashes and rectangles,
and introduced a pause-after property plus an arrangement command. Re-extraction
preserved IDs, edits, and notes. Its file-based exercise also checked unknown
nonspatial data and independent agent writeback.

Parent browser verification changed pause-after from 0.5s to 1.5s. Arrangement
moved the next two starts from 3s/7s to 4s/8s. Undo/redo, note attachment, save,
reopen, and CLI readback retained those exact values. Browser-driven events use
the normal UI user path; these isolated test actions are verification evidence,
not actual user decisions.

The exercise found and resolved an alternate-surface server import restriction:
the workspace toolkit runtime must remain available when the manifest selects a
different surface. A regression test covers this. Instructions also clarify
Node 20+ and that replacement surfaces enforce their own domain validation.

The packaged canvas separately passed browser checks for duration 3s → 5s,
undo/redo, save/reopen, targeted notes, custom All reset, rectangular crop import,
drag/resize/rotation, group creation, focus, consistent group/pane zoom geometry,
clipboard image paste, and Original/Custom proposal switching. CLI feedback
retained the crop identity, source rectangle, geometry changes, and note target.
The source was explicitly labeled synthetic. No private project captures were
used in the distributed toolkit.

Automated result: 13 Node tests plus extension and reset contract checks passed;
skill metadata validation passed. This proves a bounded local extension exercise.
It does not prove usability across all long-horizon tasks, simultaneous editing,
voice interaction, or every possible custom renderer.
