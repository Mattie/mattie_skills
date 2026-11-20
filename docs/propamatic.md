# Prop-a-Matic

Prop-a-Matic is a skill suite for building Blender props, from reference art to an export you can inspect in motion. Each skill also works on its own. With a model you already have, start at the stage you need. Static props can skip rigging.

| Skill | Use it to |
| --- | --- |
| [`propamatic-plan`](../skills/propamatic-plan/) | Turn references into a measured parts plan with pivots, travel, and clearance. |
| [`propamatic-build`](../skills/propamatic-build/) | Build reproducible geometry and materials from reviewed local scripts. |
| [`propamatic-rig`](../skills/propamatic-rig/) | Add bounded controls and bake them into animation the target runtime can play. |
| [`propamatic-verify`](../skills/propamatic-verify/) | Check the exact export against the plan, exercise it in the target runtime, and render an MP4 turntable. |

## Example

Ask `$propamatic-plan` to lay out a steampunk jackhammer with a visible 60 mm chisel stroke. Build the housing and guide with `$propamatic-build`, then use `$propamatic-rig` to give the chisel a one-second control clip and a separate hammering loop. Have `$propamatic-verify` measure the exported stroke, check the full travel path through the guide and housing, and render an orbit while the chisel cycles.

Check the swept clearance and try a low-detail export before committing to finish work. The jackhammer pilot used those checks to catch a hidden flange intersecting the shaft and a one-frame offset that kept a normalized seek from reaching full extension.

## Execution and installation

Install the four skill directories in your agent's skill root, or install only the stage you need. Each directory carries its own references. Blender, the exporter, and any rendering tools come from the project environment.

The suite treats control metadata as data and keeps local builds separate from credentialed reference generation. Use a disposable worker to process outside models or scripts, and use the project’s verified export as the subject for the finished demonstration.

The planning and articulation stages draw on AnyMachine’s reference-first workflow. The Prop-a-Matic instructions and examples were written for this suite.
