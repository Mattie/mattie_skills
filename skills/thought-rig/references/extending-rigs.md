# Extending or replacing a rig

Use configuration for new content, plugins for new capabilities, and task-local
code changes for a different interaction model. These are alternatives, not a
mandatory progression. The canvas and preparation tools are both adaptable.

## Local extension module

Start from the workspace's `extensions/duration.mjs`. A manifest explicitly lists
trusted local modules:

```json
{"extensions": [{"id": "duration", "module": "extensions/duration.mjs"}]}
```

Modules export `register(host)` for browser features and optionally
`summarizeChanges({before, after})` for semantic readback. Keep module import and
the summary function independent of browser globals so the CLI can read saved
feedback too. Access DOM only inside browser callbacks.

Use namespaced object types, such as `example:cue`. Their geometry is optional;
domain values live in `data`. Objects have stable IDs and optional `parentId`
containment. A cue's duration is not its displayed rectangle width unless the
tool explicitly models that relationship.

## Extension points

The host supports:

- `registerType(type, definition)`: defaults, validation, rendering, optional
  hit-testing, and declarative inspector fields.
- `registerCommand(definition)`: toolbar or context-menu actions, with a predicate
  for when they apply.
- `registerTool(definition)`: pointer-down/move/up behavior in canvas coordinates.
- `registerPanel(definition)`: a custom DOM view with a mount callback.

For a type, use `defaults: {geometry, data}`, `validate(object)`,
`render({ctx, object, selected})`, optional `hitTest({point, object})`, and
`inspector: [{key, label, input, min, step}]`. Inspector fields address `data`.
Use the executable duration example as the exact working reference.

Commands receive the host, selection, and actor. Pointer callbacks receive the
point, event, and host. Panel mount receives its element and host. Subscribe to
state or selection changes instead of retaining stale copies of the document.
Keep names, units, and action labels understandable to the user of the rig.

## Mutations and readback

`getDocument()` and `getSelection()` provide state snapshots.
`subscribeState(callback)` and `subscribeSelection(callback)` support reactive
views. `transaction(label, mutateDraft, {actor})` changes the canonical document
through history and persistence; `createObject`, `addNote`, and `focus` provide
common operations.

Use actor `user` for user-triggered commands, `agent` for proposals/seeds, and
`verification` for test actions. The transaction default is `agent`; the canvas
sets `user` for its UI controls. Do not mutate a returned snapshot and expect it
to persist, or write around the transaction path from a custom inspector.

Semantic summaries should describe what changed in domain terms, include units,
and preserve target identity. They supplement structural differences and notes;
they must not infer approval from unchanged defaults. Unknown plugin data remains
intact even when its renderer or summary is unavailable.

## Adapt beyond the API

Edit the task-local renderer, navigation, cutters, importers, or exporters when
the extension points are awkward. Build a timeline, comparison bench, simulation,
or another surface when that better expresses the question. Do not require every
domain to imitate spatial screenshot pieces.

The durable obligations are the intent document and return path: preserve user
edits, baselines, asset references, note targets, units, and relevant provenance.
Keep UI changes separate from content regeneration. Retain recoverable old state
when changing schemas or identities; surface unresolved mappings rather than
guessing. Shared toolkit promotion is a separate task.

## Verify an extension

Create a synthetic object, change its custom property through the real UI, undo
and redo, attach a note, save, reopen, and run CLI readback. Check the property,
unit, actor, and note target. Change local extension code and verify content
survives. Temporarily omit the extension in an isolated copy and verify unknown
objects still survive export/import. Confirm pointer tools and shortcuts do not
interfere with text input or normal canvas navigation.
