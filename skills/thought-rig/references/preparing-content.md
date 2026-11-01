# Preparing content

The goal is to provide meaningful things to manipulate, not to reproduce every
pixel or DOM node. Start with the question: a headline, action pair, card row,
scene, or linked cluster may be a better object than its implementation elements.

## Capture and source evidence

Use the available browser/computer tools or existing project capture pipeline.
Prefer a frozen copy when the underlying app is changing. Record the capture's
dimensions, source identity, and whether it is a live observation, saved fixture,
or synthetic illustration. Preserve the original capture independently of the
editable composition.

Capture tooling is intentionally adaptable. An agent may write a task-local
collector, hide appropriate layers in an isolated preview, extract DOM geometry,
or use a different importer within the authorized task. Avoid changing the user's
active application or working files merely to obtain a capture.

## Rectangular cutter

Create a JSON manifest next to the capture:

```json
{
  "image": "capture.png",
  "width": 1000,
  "height": 600,
  "label": "Composition study",
  "source": {"identity": "isolated-preview-1", "evidence": "Captured from an isolated preview"},
  "regions": [
    {"id": "headline", "label": "Headline", "x": 200, "y": 80, "w": 600, "h": 70},
    {"id": "action", "label": "Main action", "x": 400, "y": 480, "w": 200, "h": 60}
  ]
}
```

Run the task-local tool:

```text
node WORKSPACE/toolkit/cli.mjs cut WORKSPACE regions.json
```

Coordinates use source-image pixels. The cutter copies the capture with a content
hash, produces independently movable image crops, and retains background tiles
around them. It keeps source rectangles and extraction provenance. Moving a
cutout exposes an unfilled region; it does not reconstruct the underlying scene.
Existing identities must not be overwritten by another extraction.
Use `source.evidence` to label synthetic, generated, or reconstructed inputs;
optional source metadata supplements the computed asset path, hash, and rectangles.

## Adapt extraction when necessary

Modify the workspace's cutter or create an ordinary script when rectangles are
the wrong unit. Useful adaptations include batch extraction, semantic labels,
masked objects, grouped crops, alternate captures, or input from another tool.
Preparation scripts need not implement the browser plugin API; they should emit
valid document objects and retain source metadata.

Distinguish captured pixels from generated or reconstructed pixels. Preserve
immutable inputs and record the extraction method. Do not silently reuse an old
object ID for a different region: existing notes and user transforms would become
misleading. If re-extraction maps cleanly, update the relevant asset while keeping
identity and edits; otherwise retain the old object and introduce a new candidate.

Inspect the resulting canvas. Check a representative crop's bounds and scale,
move it, attach a note, and verify the saved object's identity and source rectangle.
Asset preparation is successful when it makes the intended feedback easier to
express and recover—not merely when a script emits valid JSON.
