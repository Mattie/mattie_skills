# Prop-a-Matic

Use [`$propamatic`](../skills/propamatic/) to build a Blender prop from an idea or reference through verification and an MP4 turntable. With a model you already have, tell it what needs work. Static props skip rigging. You can also invoke each stage on its own.

| Skill | Use it to |
| --- | --- |
| [`propamatic-plan`](../skills/propamatic-plan/) | Turn references into a measured parts plan with pivots, travel, and clearance. |
| [`propamatic-build`](../skills/propamatic-build/) | Build reproducible geometry and materials from reviewed local scripts. |
| [`propamatic-rig`](../skills/propamatic-rig/) | Add bounded controls and bake them into animation the target runtime can play. |
| [`propamatic-verify`](../skills/propamatic-verify/) | Check the exact export against the plan, exercise it in the target runtime, and render an MP4 turntable. |

## Example

> Use `$propamatic` to make a steampunk jackhammer with a visible 60 mm chisel stroke. Deliver the editable Blender file, the verified GLB, and an MP4 orbit with the chisel cycling.

The base skill loads the plan, build, rig, and verify skills as it reaches each stage. It carries the parts plan and acceptance criteria through the build and checks the exact model used for the demo.

Check the swept clearance and try a low-detail export before committing to finish work. The jackhammer pilot used those checks to catch a hidden flange intersecting the shaft and a one-frame offset that kept a normalized seek from reaching full extension.

## Execution and installation

Install `propamatic` and the four stage skill directories together in your agent's skill root for the full workflow. For focused work, install just the stage skill you need. Blender, the exporter, and rendering tools come from the project environment.

The suite treats control metadata as data and keeps local builds separate from credentialed reference generation. Use a disposable worker to process outside models or scripts, and use the project’s verified export as the subject for the finished demonstration.

The planning and articulation stages draw on AnyMachine’s reference-first workflow. The Prop-a-Matic instructions and examples were written for this suite.
