# MP4 turntable demonstration

Use the verified export as the model when available. Before the final render, confirm a passing verification record for that candidate and match its SHA-256 to the input being rendered. A project's `runtime-verification.json` can supply the status and hash. Re-import into a fresh scene or reuse the lighting stage with the source meshes replaced. Use the same trust boundary as other imports. Identify the source if the demo uses the authoring scene instead. Keep staging props, cameras and lights out of the export.

Start in a readable three-quarter view and complete one steady 360° orbit over roughly 6–10 seconds. Aim the camera at the center of the evaluated bounds. Maintain a constant distance or orthographic scale. Vary the elevation smoothly and keep roll level. A swing of about 8–12° either side of a slightly raised view works for many props. Change the angle, backdrop or floor if it hides details the user needs to see.

Keep lighting fixed in the scene. Use broad fill for sides that turn away from the key light and keep the backdrop quiet. Frame the asset with breathing room across its orbit and range of motion. On an articulated asset, play the representative exported animation while the camera orbits so the viewer can see motion from several angles. For a looping clip, fit whole motion cycles into the orbit where practical so both return smoothly to their starting states. Show subtle motion in an optional close-up. Use a neutral pose for a static asset or when requested.

Before rendering the sequence, make four draft views a quarter turn apart. Sample distinct motion phases to check travel, silhouette, framing, and lighting. Time one representative frame at the intended resolution and settings, including denoising, to budget the full sequence. If CPU OpenImageDenoise dominates, benchmark WebGL or a render with per-frame denoising disabled. Compare a short draft for flicker if using a post-filter such as `hqdn3d`. Use the pinned renderer and a bounded frame count, resolution, render time and output directory.

Assert that the evaluated poses for the actual rendered frames reach the expected range or milestones in each intended cycle. Camera movement alone can hide a frozen rig. Use evenly spaced frames and leave out a duplicate final pose for smooth looping. For a 24 fps numbered sequence, encode and verify the MP4 with:

```sh
ffmpeg -nostdin -n -framerate 24 -i orbit-%04d.png \
  -c:v libx264 -crf 17 -pix_fmt yuv420p -movflags +faststart turntable.mp4
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=codec_name,pix_fmt,nb_read_frames,duration -of json turntable.mp4
ffmpeg -nostdin -v error -xerror -i turntable.mp4 -f null -
```

Compare the reported frame count and duration with the render plan. Inspect the encoded video for framing and visible articulation, then link it in the handoff.
