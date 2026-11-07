# Setup and commands

Use an isolated environment with Python 3.12 for the pinned preparation dependencies. Install `scripts/requirements.txt` for CPU geometry and cached pack validation. Install a device-appropriate PyTorch build and `scripts/requirements-models.txt` only for inference. Install `scripts/requirements-check.txt` plus Playwright Chromium for render checks, or pass `--browser` with an installed Chromium/Edge executable. No server is needed.

The requirement files pin the directly used packages; they are not a transitive dependency lock. Transformers 5.22.2 and huggingface-hub 2.4.0 replace the experiment's older inference stack to address published advisories. The manifest records installed versions and includes them in its cache identity. Test a fresh environment before claiming reproduction. The originating experiment used Python 3.12, NumPy 1.26.4, Pillow 13.0.0, SciPy 1.17.1, PyTorch 2.11.0+cu128, Transformers 4.57.6, and Playwright 1.64.1 on an RTX 4090. Choose a compatible PyTorch build for the actual device rather than forcing the original CUDA wheel.

## Input contract

`prepare` accepts one local image and writes to a derived output directory. It applies EXIF orientation, converts an embedded ICC profile to sRGB, and flattens alpha against `--background` (default white). Invalid profiles fail rather than silently changing color. The manifest records the source-byte hash, decoded dimensions and pixel hash, alpha policy, and color/orientation transform. Never use a title as the cache identity.

An optional `--depth` is a single-channel, normalized 16-bit PNG registered to the **oriented** image's dimensions: 0 far, 65535 near. It is not resized or percentile-normalized again. Use `--depth-direction far` only for the opposite convention. Check one obvious foreground/background pair visually. A float `.npy` prediction is retained when inference runs, with a normalized native PNG for inspection. Per-image normalization gives relative depth, not metric distance.

The pinned estimator is `depth-anything/Depth-Anything-V2-Small-hf`, revision `5426e4f0f36572d16453bbda7a8389317b1bef99`. Its saved slow processor and safetensors model load from cache by default. `--depth-model` and `--depth-revision` can select another compatible Transformers estimator with an immutable 40-character revision; local model directories are rejected because their contents would not be identified by that revision. This requires rechecking depth direction and rendering. Flat depth is recorded as a static quality exception rather than amplified into motion.

LaMa is loaded once per preparation process from `--lama`. The reference TorchScript artifact is:

- URL: <https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt>
- SHA256: `7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c`

The default expected hash is pinned; a separately trusted compatible artifact needs its own `--lama-sha256`. Never bypass a mismatch. Models are executable inputs: obtain them from a trusted source with appropriate terms. Upstream LaMa code is Apache-2.0; the originating experiment did not resolve redistribution terms for this converted weight. Do not bundle its binary. [Depth Anything V2 Small's pinned model card](https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf/blob/5426e4f0f36572d16453bbda7a8389317b1bef99/README.md) declares Apache-2.0. Image rights are separate. See [provenance](provenance.md).

## Commands

```text
# Registered depth, default 3 px margin plus 14 px comparison
python scripts/parallax.py prepare --image art.png --depth depth.png --lama /models/big-lama.pt --out work/art

# Estimate depth from the local model cache
python scripts/parallax.py prepare --image art.png --lama /models/big-lama.pt --out work/art --device auto

# Deliberately scale source radii: 3 and 4 mean values at width 563
python scripts/parallax.py prepare --image art.png --depth depth.png --lama /models/big-lama.pt --reference-width 563 --width 400 --travel 6 --out work/art-400

# Structural checks, then actual GPU-renderer checks and contact sheet
python scripts/parallax.py verify work/art
python scripts/check_render.py work/art --browser /path/to/chromium

# Cached rendering: no model imports or inference
python scripts/parallax.py view work/art --out work/art-review.html
python scripts/parallax.py gallery work/art work/another --out work/gallery.html
```

Use `--margins 3` to omit the 14 px comparison, or `--margins 3 14 --selected-margin 14` to select the larger repair for runtime. Margins and ownership radius are source pixels unless a reference width is given; effective scaled radii are recorded. Travel always means runtime pixels per axis, independent of source resolution. For batches, loop `prepare` over selected local inputs, then build one gallery. Each process loads its models independently; the cache skips complete matching packs.

The 250 px width is a lightweight reference preset. Match larger exports to the intended display size: `--width 1000 --travel 12` gives approximately the same relative motion as a 250 px export with travel 3. Recheck the actual output, including nearby motion frames. A fixed processing-source margin already covers more output pixels when runtime width increases; enlarge it to address observed contour contamination rather than automatically multiplying it by the output scale.

`prepare` refuses an existing nonmatching output directory. Choose a new output directory for a different recipe. Matching packs are accepted only after their asset hashes and structural invariants are verified. No command deletes an output tree. Cache identity includes source bytes/pixels, supplied depth bytes or model ID/revision, LaMa hash, every preparation setting, dependency versions, and hashes of the preparation script and renderer.

## Outputs and integration

`manifest.json` describes geometry, texture conventions, source registration, variants, selected runtime files, per-surface gradient bounds, model identities, full cache identity, diagnostics, quality exceptions, and relative-file SHA256/size inventory. `receipt.json` records stage times, actual environment, reproduction argv, output bytes, and CUDA tensor allocation/reservation when available. These CUDA numbers do not measure whole-device memory.

Runtime requires source RGB, the continuous depth atlas, ownership map, and **one** repaired color atlas, plus the manifest. Data textures must stay linear. The PNG color atlas stores straight alpha; upload premultiplies once. Source RGB is a runtime-resolution, lossless derived image. The untouched input stays where it was.

`verifier.html` embeds lossless assets and makes no network requests. It supports image/margin selection, pointer and slider motion, static comparison, surface/depth/ownership/removal diagnostics, neutral reset, and optional playback. A gallery can be large; it is not a production payload. Its WebGL-to-2D copy is for comparison and capture. Integrate the shader into the application's own GPU renderer for production, with shared immutable textures and separate motion state. Check production crop, input envelope, lifecycle, frame time, and reduced motion separately.

The render checker uses a headless local browser, without starting a server. It compares full RGBA neutral renders exactly, captures all eight extremes, checks intermediate motion and return-to-neutral, resizes, revisits variants, and exercises playback/reduced motion. A 41-position diagonal probe records large second frame differences and saves enlarged crops before, at, and after its peak event. Its RGB-channel spike count is a discontinuity diagnostic, not a universal aesthetic threshold; inspect the crops and actual motion. Lossless PNG pixel transport keeps large-output checks practical. Opacity checks alone cannot detect edge-clamped smearing. Review `contact-sheet.png` and actual motion; record visual approval separately from automated results.

The `ownership-overlap-v2` renderer smooths visible-source transitions between depth bands with a normalized-depth half-width of 0.02. It keeps the original RGB across the complete neighboring ownership ramp and samples source directly at zero shift. New preparation manifests record this revision and blend width. Older texture packs remain structurally compatible; rebuilding a verifier uses the current renderer, whose revision is identified in the HTML metadata. A new preparation cache key includes the changed renderer and settings.
