# State and handoff

Read this when connecting a rig to saved state, agent access, export/import, or
regeneration. Keep the implementation proportional to the task. The essential
promise is that a user's changes can be read accurately and carried forward.

## Agree on where intent lives

Use a domain document that both the UI and agent can understand. Prefer the
project's existing format when it can express the relevant decisions. The
rendered UI is a view of that document; browser memory or a screenshot should
not be the only record of editable intent.

Choose a return path the current environment actually supports:

- A project editor or local application can read and write the same domain files
  through its supported interfaces. Use an existing API or a small local bridge
  when needed, with current server/session guidance.
- A standalone browser tool can export a bundle for the agent to read and import
  an updated bundle. If it needs user attachment or an explicit submission to
  return edits, make that step clear.
- An inline fallback with documented submission and state access can use that
  mechanism when a suitable app is unavailable. Verify what is delivered;
  displayed controls alone do not establish that edits reach the agent.

An explicit export is a good return path. Don't simulate automatic feedback when
the host cannot deliver it. Local storage can aid recovery on the same device,
but should be supplemented by a portable export when it is the only persistence.

Let text, images, and structured data travel together as needed. A concise brief
can summarize a bundle, while exact timings, geometry, annotations, comparisons,
and settings remain in their domain representation. Include the references
needed to interpret them. Images can show appearance; structured data should
carry decisions that would be unreliable to recover from pixels.

## Give changes a context

Keep stable identities for editable objects and alternatives. Express units,
coordinate systems, and time bases explicitly. A note belongs to an object,
region, interval, or comparison; a bare "make this softer" loses its meaning
once the view changes.

Retain the seed or last reviewed version so changes have a baseline. A revision
identifier becomes useful when the agent and UI may edit concurrently. Keep
explicit user decisions distinguishable from seeded guesses and values computed
from other settings. This need not mean recording every slider movement.

For example, a timing editor might export this much context:

```json
{
  "schemaVersion": 1,
  "revision": 7,
  "basedOnRevision": 6,
  "timeUnit": "seconds",
  "layers": [
    {
      "id": "title-entrance",
      "start": 1.4,
      "duration": 0.6,
      "easing": "ease-out",
      "userEditedFields": ["start", "duration"]
    }
  ],
  "notes": [
    {
      "targetId": "title-entrance",
      "interval": [1.4, 2.0],
      "text": "Arrive just before the spoken phrase."
    }
  ]
}
```

This is an illustration, not a required universal schema. Preserve any asset
references, track relationships, constraints, or source identity the task needs.
Do not infer that the user selected `easing` merely because it appears in the
export; it may still be an unchanged seed value.

Make the return path visible in the tool itself. Identify which controls edit
intent, what their target is, and what Save or Export carries forward. For a
research map, that might mean current branch choices, branch notes, event
annotations, proposed missing avenues, and an edited layout. Keep a historical
outcome separate from a current choice to revisit its branch. A user-authored
proposal needs a stable identity and should remain visibly proposed until later
work establishes it. State whether the agent must read a saved file, receive an
export, or use a supported submission before continuing.

## Regenerate without losing decisions

Read the latest state before modifying it. Base agent changes on the revision
actually inspected, and make them recoverable. If the user has edited meanwhile,
merge independent changes or leave the conflict visible rather than writing an
older whole document over the newer one. A manual snapshot workflow is enough
for a small disposable tool; a multiuser collaboration engine usually is not.

Keep content changes and interface changes separate enough that adding a control
does not reset the content. Preserve edits to individual variants when switching
between them. If a schema or identity change affects existing annotations, map
them explicitly where the relationship is known and retain the original when
it is not. Derived previews can be rebuilt from saved intent.

## Make a return bundle usable

A useful export generally contains:

- The latest domain state and the baseline or revision needed to interpret edits.
- Notes and decisions attached to stable targets.
- Relevant assets or resolvable references, with selected alternative identities.
- A short summary of meaningful changes, assumptions, and open questions.
- A screenshot, render, or audio excerpt when appearance or sound matters and the
  available tools support creating and inspecting it.

Use only what the task needs. Export into the agreed task workspace or supported
submission channel. Collect the selected working state and relevant context,
without quietly copying unrelated conversations or private project data into a
reusable toolbox.

Before using feedback, exercise the path once: seed a proposal, make a
representative edit, save or submit it, read it as the agent would, and reopen or
reimport it. Check the value, units, target, and any attached note. When agent
write-back is supported, also change a different field and verify that the user
edit survives. In a manual workflow, make the next import explicit.

When read-back is unavailable, offer a smaller supported rig or explain the
specific handoff step needed. Do not tell the user that a UI choice has changed
the work until the relevant state has actually been read and applied.
