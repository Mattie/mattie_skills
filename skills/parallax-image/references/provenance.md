# Provenance and scope

This skill was adapted from Mattie's ManaSplash parallax experiment and its November 6, 2026 handoff, **Reproducing depth-mask parallax with clean background infill**. The recipe, surface construction, LaMa input contract, and ownership/inverse-warp shader come from that project-owned implementation. The portable CLI, registered-input handling, complete pack cache identity, and synthetic validation were added while packaging this skill.

The later `ownership-overlap-v2` renderer revises the reference shader's hard ownership tests after a 1000 px token photograph exposed frame-to-frame popping. It overlaps source ownership transitions while retaining the eight-step solve, existing texture format, and exact neutral source sampling. The frozen source fingerprints below identify the historical implementation, not this subsequent fix.

`source-provenance.json` records SHA256 fingerprints of the source guide and implementation files read during adaptation. These fingerprints identify the original local evidence without requiring its paths or corpus. The skill does not include artwork, model binaries, the research environment, or copied third-party library implementations.

The originating experiment checked 50 artworks with two margins and eight extremes, with exact neutral comparisons and opaque outputs; its gallery also had 250/400 px layout checks. All contact sheets were inspected. It did not establish a quantified aesthetic success rate or mobile qualification. Its Small preparation median of 0.974 s and p95 of 1.529 s used cached depth on a local RTX 4090, with median effect textures of 268 KiB at 250 px width. These are historical observations, not guarantees for this CLI. This package's own checks and limitations are in `validation.md`.

Models are obtained separately. The pinned V2 Small model card declares Apache-2.0. Upstream LaMa code is Apache-2.0, while the converted Big-LaMa weight's redistribution terms remain unresolved by the source experiment. See the artifact URL and digest in [usage](usage.md). Do not treat a code license as establishing rights to redistribute a converted weight or input artwork.
