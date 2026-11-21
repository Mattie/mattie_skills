---
name: propamatic-verify
description: Verify generated Blender and glTF assets against references, articulation limits, and target-engine behavior using measured checks and fresh re-imports. Use before accepting a procedural asset or rig as finished.
---

# Verify the asset people will use

Compare the final export with the intended object and its actual runtime behavior. A clean log, an attractive render or matching object counts alone is insufficient.

## Choose an independent answer key

Use approved references, measured dimensions, the parts/control plan and runtime requirements as expected behavior. Do not derive every expected result from the same builder constants being checked. Record justified tolerances before evaluating outcomes; do not move them merely to make a failing asset pass.

Select checks according to the asset. Static props do not need gait tests. Prioritize silhouette, scale and attachment errors over surface polish.

## Keep verification from executing the asset

Run only reviewed verifier code. Treat supplied scripts, embedded text, expressions, drivers, external file links and add-on requests as untrusted. Never rebake by executing text embedded in a `.blend`, and never use metadata as Python. Disable automatic script execution; use actual process isolation for outside binaries and untrusted outputs. A fresh scene is a correctness boundary, not a security sandbox.

Use local staged inputs with no network or generation credentials. Do not follow model URIs outside the staged asset root or fetch remote textures automatically. Validate paths and symlinks; flag missing dependencies rather than resolving them through arbitrary downloads. Bound file sizes, scene complexity, frame/sample counts, runtime and memory before processing.

## Compare geometry and motion

- Check units, dimensions, axes, pivots, required assemblies and material assignments.
- Compare renders from reference-matched cameras. List visible disagreements instead of relying solely on counts or image similarity scores.
- Sweep control endpoints and interior samples; include dependency boundaries, interacting pairs and representative multi-control states. Report sampled coverage rather than claiming every continuous state was proven safe.
- Measure clearances and overlaps with a documented tolerance. Check the moving part's swept envelope against surrounding fixed geometry, including hidden end caps and flanges. Separate intentional contact from unintended clashes. Assert that each required slice or region includes geometry from the parts it is meant to test. Prefer intersecting triangles or edges with the slice over selecting vertices inside it. A face can cross the region even when every vertex lies outside it.
- For locomotion, measure foot slip during stance, root displacement per cycle and loop continuity. For secondary motion, check finite values, stability and a fixed time horizon.

## Verify the exported artifact

Identify the exact candidate by hash and run ID. Re-import it into a fresh process or scene and compare evaluated poses, transforms, morphs, animation durations and visual appearance with the source at corresponding times. Check conversion of axes and units explicitly. Compare Blender poses relative to each strip's start and check GLB timestamps separately. Blender may place the imported strip at a different scene frame even when the GLB correctly starts at zero.

Establish the declared rest pose before sampling each clip. Muting a track can leave transforms evaluated from a previous clip, especially when the current clip animates different objects. Reset those transforms or explicitly sample disjoint tracks at rest. Test intended clip combinations separately.

Exercise at least the target runtime behavior that can differ from Blender: parameter seeking, clip mixing for coupled controls, root motion, material support, texture loading and loop interpolation. If the target runtime is unavailable, label that behavior unverified. Do not silently replace this check with another Blender render.

For compatible self-contained GLBs targeting Three.js, use the [Node playback check](references/node-gltf.md) to test poses and looping without WebGL. Check rendered materials and shaders in the target renderer.

Inspect export metadata for private paths, prompts, credentials and executable content. A format validator can check structure, but cannot certify an asset harmless or visually correct.

## Demonstrate the result

For a finished new or substantially revised 3D asset, include a short MP4 turntable when presenting the result. Use a full orbit with a gentle change in elevation, stable lighting, and enough margin to see the whole model. When the asset is articulated, play its representative motion during the orbit by default. Add a separate close-up if that helps show small movements. Read [turntable.md](references/turntable.md) for camera, rendering, and delivery checks.

Prefer the verified export as the subject. Record the source and run used for the video. Keep the turntable with the visual comparisons and report its observations alongside measured checks.

## Report honestly

For a completed review, read [result-record.md](references/result-record.md). Keep build failure, verification failure and unavailable checks distinct. Failures stop artifact promotion; preserve evidence for diagnosis. Do not mask exit codes or report a previous run's output as the current result.

State what was checked, which exact artifacts it covers, what failed and what remains unverified. Separate observed results from assumptions. Publish or deploy only within the user's existing authorization.
