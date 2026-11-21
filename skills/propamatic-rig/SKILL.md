---
name: propamatic-rig
description: Design and bake bounded controls for mechanical or soft-goods Blender rigs, including hinges, gait cycles, interacting controls, and glTF parameter actions. Use when a static asset needs working articulation.
---

# Give an asset working controls

Expose meaningful parameters and produce animation the target engine can actually consume. Keep joint semantics independent from Blender-specific driver machinery.

## Define controls before implementation

For each control, record its neutral/default state, normalized domain, affected parts, physical range and dependencies. Use a finite normalized input in [0, 1] for user-facing controls unless the project already has another convention. Define whether out-of-range finite values clamp or reject; reject NaN, infinity, invalid types and unknown controls. Check booleans separately where numeric types would otherwise admit them.

Measure hinge axes and pivots from the asset, then rebuild or separate geometry where topology prevents clean articulation. Give each rigid part one attachment where appropriate. For locomotion, define support groups, stride, duty factor, root motion and intended speed before tuning the animation.

## Keep rig data inert

Read [declarative-controls.md](references/declarative-controls.md) when defining a machine specification or accepting outside rig metadata. Store numbers, enums, identifiers, sampled curves and explicit dependencies. Never execute strings from a model, JSON file or prompt as Python. Do not use `eval`, `exec`, dynamic imports, shell commands or embedded Blender text to interpret metadata.

Bake externally supplied definitions using trusted code. For project-authored interactive drivers, keep any expressions fixed in reviewed source and restrict parameters to validated numbers; never substitute metadata into executable expressions. Do not enable automatic script execution to make an unfamiliar rig work. Importing or running an outside Blender file requires a separate isolated execution boundary.

## Solve the mechanism, then sample it

Check actual limits and clearance over each control range. Hinges rotate about their measured axis; sliders respect stroke; cylinder and rod remain attached and within travel. For gait cycles, measure planted-foot slip and support timing, and distinguish in-place animation from forward root motion.

For soft goods, identify which motion is a hinge, shape key, path deformation, fill effect, roll, clip, or jiggle. Controls can interact: clipping may pin a strap; filling may reduce lid travel. Encode dependencies explicitly and reject cycles or impossible states. Test combinations, not only one-at-a-time sweeps.

For secondary motion, use bounded timesteps and a finite simulation interval. Cap sampling counts and chain sizes before allocation. Record any approximate behavior that does not represent a physical simulation.

## Bake a portable result

Bake controls to explicit transforms or morph weights. To map a normalized control directly to clip time, export time zero and set a known duration, such as one second. Check the exported timestamps and seek the exact endpoints in a consumer. A Blender timeline starting at frame 1 may add a one-frame offset unless the glTF exporter slides the clip to zero. Keep demo animation separate from parameter actions.

For Blender 4.5 Actions and glTF export, read [Blender glTF baking](references/blender-gltf.md) for slot handling, clip grouping, and sampling full rotations.

Before finish renders or texture baking, export a low-detail candidate with the intended clip settings. Read the first and last key timestamps as well as the reported duration. In a consumer, seek both endpoints and one interior value, then compare the resulting poses with the control spec. A duration check alone can miss leading dead time. Recheck the finished export after any change to its animation or exporter settings.

Do not assume independent glTF clips reproduce coupled controls. Test the target engine's mixing behavior; if controls overwrite the same transforms or violate dependencies, use a documented runtime combiner or bake supported combinations instead. Never promise arbitrary combinations from isolated clips alone.

Deliver the editable rig, inert control specification, baked export, and measured limits. Verification should sweep endpoints, interior samples and interacting controls, then re-import the export and compare evaluated poses.
