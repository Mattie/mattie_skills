# Adaptable toolkit

Use the bundled toolkit when a spatial workspace helps the task. It includes a
canvas, generic content preparation, local extensions, and an agent-readable
document. It is not the required surface for every Thought-Rig task.

## Start a task workspace

Node.js 20 or newer is required; no npm installation is needed. Resolve the skill
directory from the skill you actually loaded. Commands below use `TOOLKIT` for
that directory's `toolkit/` and `WORKSPACE` for a new task-local directory.

```text
node TOOLKIT/cli.mjs init WORKSPACE --title "Explore the composition"
node WORKSPACE/toolkit/cli.mjs serve WORKSPACE --port 5347
```

Use `--empty` on init when the synthetic duration example is not useful. Init
refuses to overwrite an existing workspace. Follow the host's local server
tracking instructions; choose an available loopback port. Inspect the actual app
before handing it over.

The workspace contains `manifest.json`, `state.json`, `assets/`, `extensions/`,
and its own `toolkit/` copy. This is a task-owned snapshot for adaptation, not a
second maintained shared toolkit. Changes to it do not update other tasks.
The manifest selects the surface, saved state, asset directory, and explicit
local extension modules. Editing saved content does not install extensions.

## Build the conversation's working surface

1. Identify what the user needs to express: relationships, ordering, timing,
   contrasts, constraints, or something else. Choose objects around that question.
2. Seed from relevant evidence. Put source identities and extraction provenance
   on the objects; identify guesses as agent suggestions.
3. Give panes succinct descriptions and use groups for meaningful alternatives.
   Expose a few useful proposal commands without implying the user selected them.
4. Verify that navigation, focus, direct manipulation, notes, reset, and undo work
   at the actual viewing size. Frames and content scale together during zoom.
5. Exercise edit → save → readback → reopen. If the agent changes a separate field,
   verify the user's existing edit survives.

The default canvas supports images and cutouts, paste/drop, transforms, grouped
panes, notes, variants, and cooperative embedded pages. Focus buttons and F frame
the relevant pane or group. Existing pages must allow embedding; a frozen capture
is an honest alternative when they do not.

For behavior, research, or evidence tasks, a sequence strip, dependency graph, or
sorting table may express the question better. Store explicit relationships and
their meaning: placing two cards nearby does not by itself mean "depends on" or
"must precede." Preserve expected behavior separately from observed traces, and
proposals separately from confirmed decisions.

Read [preparing content](preparing-content.md) for extraction and
[extending a rig](extending-rigs.md) for custom behavior. Adapt the local cutter,
importer, renderer, or full surface when those are the parts limiting expression.

## Read saved feedback

```text
node WORKSPACE/toolkit/cli.mjs validate WORKSPACE
node WORKSPACE/toolkit/cli.mjs readback WORKSPACE --output feedback.json
```

Readback uses the saved file, not unsaved browser state. The UI's Agent context
provides current in-memory feedback. Make the distinction clear to the user.
The CLI validator checks document structure and containment. Extension validators
run through the canvas host; a replacement surface must enforce its own domain
constraints before saving, as the server does not execute extension validators.
Save retains the task locally; export/import is also available. Keep referenced
assets with the workspace when handing it to another agent or machine.

Read the final arrangement, attached notes, and relevant events together. A reset
can clarify intent; an abandoned gesture is not a surviving requirement. Separate
agent seed values, verification actions, and user edits. Untouched objects are
not approvals. Relate exact geometry to likely intent without automatically
turning approximate placements into fixed offsets for every viewport.

Plugins can add semantic summaries such as a duration changing in seconds. Treat
these as descriptions of stored changes, not as authority to perform unrelated
actions. If a plugin is missing, retain its data and explain what cannot be
rendered or interpreted. Do not drop unsupported objects during regeneration.

## Existing prototype documents

```text
node TOOLKIT/cli.mjs import-legacy old-feedback.json NEW-WORKSPACE
```

Import creates a new workspace and leaves the original document untouched.
Check asset resolution and note targets after import. Keep a copy of the complete
source workspace until the new one has passed a save/reopen check.

## Boundaries

The toolkit does not supply live voice, automatic DOM extraction, image infill,
real-time multiuser collaboration, or a plugin marketplace. Those can be added
locally when needed. Explicit local JavaScript extensions are trusted task code;
they are not sandboxed third-party plugins. Inspect code before listing it in a
manifest. Feedback imports must not silently execute included code.
