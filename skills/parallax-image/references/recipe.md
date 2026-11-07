# Five continuous surfaces: recipe and invariants

The tested preset is a shallow camera approximation. It does not recover real hidden geometry, choose semantic objects reliably, or establish mobile performance. Keep these invariants when adapting the bundled renderer.

1. **Register first.** Apply the same orientation/color policy to the art and depth. Source hashes, dimensions, aspect, depth convention, and UV orientation must agree. Use an asymmetric fixture to expose flips.
2. **Normalize inferred depth.** Resize float predictions bicubically to native source size, reject nonfinite values, then clip the image's 1st–99th percentile range into [0,1]. Near is one. Save raw predictions and a 16-bit normalized PNG. Flat or implausible depth is a reason for static fallback.
3. **Ownership is separate.** Construction bins are `min(int(depth * 5), 4)`. For runtime visible RGB, compute a maximum over a circular radius-four native footprint. Adopt that maximum only where it gains more than 0.25 depth. Do not globally dilate construction bands. Bicubically resize and quantize ownership for runtime.
4. **Continue continuous depth.** For each band use a Euclidean distance transform to extend depth from the nearest visible band pixel into hidden regions. Preserve visible depth. Under nearer bands, overlap alpha is `clip((reach - distance) / 3, 0, 1)`; visible alpha is one and other alpha zero. The farthest surface is opaque everywhere. Empty higher bands stay transparent with a harmless constant depth.
5. **Budget diagonals.** The reference reach is `ceil(travel * sqrt(2) * source_width / output_width) + 4` source pixels. With source-radius scaling, the bundled pipeline uses at least the effective ownership radius for the final guard. Six pixels per axis means up to 8.49 px relative diagonal travel before crop scaling. Increasing travel requires a new check.
6. **Regularize actual stored depth.** Downsample each field, quantize to 8 bits, then check the largest cell finite-difference gradient norm times `travel * sqrt(2) <= 0.70`. Increase Gaussian sigma by 0.5 up to 12 and recheck the quantized map each time. Reject if the bound cannot be met. This supports the eight-step fixed-point solve within the envelope; it does not certify aesthetics.
7. **Erase contours before resizing.** For each band's nearer pixels, remove `distance_transform_edt(~nearer) <= repair_margin`. The reference margins are 3 and 14 native source pixels, using a circular Euclidean margin. Skip infill when there is no nearer content. LaMa receives RGB float32 NCHW in [0,1] and a float32 N1HW replacement mask; symmetrically pad bottom/right to multiples of eight, then crop back. Preserve native source RGB exactly outside the mask and generated RGB throughout the whole mask, including its halo. Never restore original edge RGB in that halo. Form RGBA, zero RGB where alpha is zero, and resize through Pillow's RGBA Lanczos path.
8. **Pack with gutters.** Stack five surfaces vertically. Each has two copies of its first row above and two copies of its last row below, giving `width × [5 * (height + 4)]`. Clamp atlas lookups to that surface's interior texel centers. Keep depth/ownership/removal data linear and lossless.
9. **Inverse-warp and overlap ownership.** From cropped coordinate `u`, repeat `q = u - shift * (sampleDepth(q) - 0.5)` eight times. Sample premultiplied repaired RGBA and guarded ownership `d` at q. For `lo=i/5`, `hi=(i+1)/5`, and `w=.02`, let `enter = smoothstep(lo-w,lo+w,d)` (one on the farthest surface), and `original = 1-smoothstep(hi+w,hi+3*w,d)` (one on the nearest). Use `mix(repaired, vec4(originalRGB,1), original) * enter`, then composite. The lower surface keeps original RGB through the upper surface's full entry ramp, so ownership changes smoothly without exposing repaired background for a frame. Hard `d<lo` / `d<hi` switches caused visible pops at 1000 px even when neutral and extremes passed. The overlap changes visible-source selection, not construction bands or removal masks. Zero motion samples original source directly to retain bit-exact neutral output. `assets/viewer.html` carries the current `ownership-overlap-v2` renderer; the frozen experiment used the old hard condition.
10. **Composite once-premultiplied.** Color PNGs hold straight alpha. WebGL sets `UNPACK_PREMULTIPLY_ALPHA_WEBGL=true` once at upload. Composite far to near with `out = layer.rgb + (1-layer.a)*out`. Do not double-premultiply. The verifier also accumulates coverage alpha so the checker can detect transparent output rather than forcing opaque alpha unconditionally.

At zero shift the owner selects original visible RGB. The verifier compares against static source with the same `zoom = 1 - (travel + 2) / min(width,height)` crop. This is exact equality for a lossless path under that crop, not equality with the whole uncropped source rectangle. Keep crop stable through live toggles or manage the transition deliberately.

## Interpreting failures

| Symptom | Inspect first |
| --- | --- |
| Duplicate dark contour | Nearer RGB still present behind foreground; original RGB restored in repair halo |
| Thin rim after downsampling | Removal mask missed antialiasing, or halo RGB was restored before resizing |
| Thin foreground breaks | Guarded ownership versus construction bins; avoid globally expanding all bands |
| Rubber motion | Loss of continuous depth or excessive travel; five bands are not five rigid objects |
| Diagonal holes | Both-axis overlap budget and actual valid source coverage |
| Speckles or folds | Quantized gradient bound and inverse solver |
| Brief holes or flashes inside a moving subject | Hard visible-source ownership switches; compare adjacent frames and use overlapping transitions |
| Atlas seams | Repeated edge gutters and interior texel clamp |
| Bright/dark translucent fringe | Alpha convention at preparation, upload, and composition |
| Stable but smeared edges | Edge-clamped texels can be opaque while geometrically wrong; inspect images |

Compare small/large margins on thin branches, petals, cords, high contrast outlines, and ambiguous painted scenes. Larger margins erase more foreground residue but also sacrifice useful background context. Inspect intermediate motion, return-to-neutral, selection revisits and production lifecycle; do not approve from a contact sheet alone.

Margins are native processing-image pixels. Increasing runtime width alone already increases the number of output pixels covered by the same native margin. Revalidate at the actual display size; do not assume a fourfold output enlargement requires a fourfold native removal radius. In the 1000 px token test, increasing the margin from 3 to 12 or 24 worsened the temporal discontinuity proxy; overlapping ownership transitions addressed the observed pop instead.
