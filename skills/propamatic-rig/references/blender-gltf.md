# Bake Blender 4.5 Actions to glTF

For a single-layer, single-strip Action created by inserting keys on the target object, use its assigned slot to get the curves. Retain that slot when moving the Action onto an NLA strip. Blender 4.5 stores the curves in the slot's channel bag.

```python
slot = animation.action_slot
curves = action.layers[0].strips[0].channelbag(slot).fcurves
for curve in curves:
    for key in curve.keyframe_points:
        key.interpolation = "LINEAR"  # When the control requires linear keys.
animation.action = None
track = animation.nla_tracks.new()
track.name = clip_name
strip = track.strips.new(action.name, start_frame, action)
strip.action_slot = slot
```

Use identical custom NLA track names on the objects that belong in one clip. In NLA Tracks export mode Blender groups those tracks under the shared name. Give independent clips distinct names and check the exported clips, channels, and timestamps. For the authoring preview, clear the active Action (`animation.action = None`) and unmute the intended tracks. Exclude unwanted tracks explicitly, since Blender 4.5.16 can export muted tracks in this mode.

```python
result = bpy.ops.export_scene.gltf(
    filepath=output_glb, export_format="GLB", export_animations=True,
    export_animation_mode="NLA_TRACKS", export_force_sampling=True,
    export_anim_slide_to_zero=True,
)
if result != {"FINISHED"}:
    raise RuntimeError(f"glTF export failed: {result}")
```

Use `export_anim_slide_to_zero` when the contract calls for clips starting at zero. Rotation tracks interpolate between quaternions along the shortest arc. A full turn has identical endpoint orientations, and a segment longer than 180° can take the opposite arc. Bake intermediate poses no more than 90° apart as a conservative sampling rule. Check direction and accumulated travel in the consumer at interior times, since endpoint equality cannot prove a winding motion played.
