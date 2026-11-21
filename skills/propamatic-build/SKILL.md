---
name: propamatic-build
description: Build reproducible Blender props or machine geometry from a parts plan using reviewed local Python, staged renders, and bounded output directories. Use for procedural asset construction and texture baking.
---

# Build procedural Blender assets

Turn the parts plan into geometry that is easy to rebuild and compare with its references. Prefer one understandable build entry point with small project-local helpers. Reuse the project's established geometry library before adding a new abstraction.

## Execute in the right boundary

Read [execution-boundary.md](references/execution-boundary.md) before running Blender, importing outside assets, or setting up workers. A Python build script is executable code. A fresh Blender startup and disabled auto-execution are useful settings, not process isolation.

Review code before running it, including imported helpers, add-ons, shell wrappers and remote-worker clients. Do not source an unrelated project's environment script or install whatever package an imported asset requests. Use the project's pinned environment; record Blender and exporter versions. Building and rendering local geometry should run without generation keys or network access.

## Build in useful passes

Start with scale, silhouette, assembly boundaries and pivots. Render a cheap clay view from the reference directions. Fix structural mismatches before adding fasteners and wear. Build repeated parts by instancing where practical; keep parts that move separately distinct.

In close-ups, compare the camera's near clipping distance with the closest surface across the motion. A 0.1 m near plane can slice a tabletop prop. Set `camera.data.clip_start` below that distance, for example `0.005` when one Blender unit represents a metre.

For a mechanical connection, model its relevant contact and clearance: coaxial hinge barrels, fork and tongue, sliding interfaces, or cylinder and rod on separate attachments. Do not hide an impossible mechanism under detail. For soft goods, distinguish visible deformation from a mechanical joint.

Before detail work, sweep the moving envelope against every fixed part along the travel path. Include hidden faces and attached pieces such as end caps, flanges and the adjoining housing. A guide may fit while another solid blocks the same shaft. A simple section view and a numerical clearance check are useful together.

Use geometry for silhouette and interaction. Small surface relief can be bake-only geometry. Keep final materials, UVs and texture sets aligned with the target runtime budget. Start baking with small textures and low samples to check layout; only then use the requested quality. Avoid expanding GPU or cloud usage beyond the authorized budget.

## Keep rebuilds and cleanup predictable

Write each attempt to a new generated run directory. Use validated identifiers for asset names, keep explicit input and output roots, and follow the run directory pattern in the [execution boundary](references/execution-boundary.md#reviewed-local-source-and-project-assets). Pass subprocess arguments as arrays so job values stay data. Preserve errors and timeouts.

Do not recursively delete a path assembled from an unchecked argument. Prefer leaving a failed run for inspection; cleanup should target a known run created by this workflow. If using a shell wrapper, quote paths, terminate option parsing where supported, and preserve child exit status through logging pipelines.

## Handoff

Deliver editable source, required local inputs, a reproducible build command, generated artifact paths, and a brief account of visual compromises. Hash the artifacts being handed off. Treat exports as candidate outputs until re-imported and compared in a fresh scene. Report a failed or unavailable check explicitly; do not reuse a stale artifact as a successful build.
