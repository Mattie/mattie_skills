# Aiconographer Production Guide

Read this reference for a full article-icon run, prompt construction, visual validation, or blind
candidate judging.

## Output contract

Produce:

1. Six one-sentence concept descriptions.
2. One high-resolution 3-by-2 raster candidate sheet.
3. Six normalized high-resolution source tiles.
4. Six transparent two-fill SVG candidates.
5. Transparent 192px and 48px PNG renders from each SVG.
6. White and dark-neutral contact sheets.
7. An anonymous review pack, scorecard, and selected winner.
8. A run record containing the article text, brief, concepts, prompt, tools, validation, and result.

## Visual system

Palette:

- Charcoal `#2C2C2B`: primary silhouette and structure.
- Coral `#F45138`: active, magical, dangerous, or concept-defining feature.
- White `#FFFFFF`: temporary raster background, removed from the SVG.

Style:

- Bold, flat, geometric fantasy pictogram.
- Filled silhouette with deliberate negative space.
- Smooth curves, crisp intentional corners, balanced outer padding.
- One cohesive emblem that survives at 48px.
- Slight storybook character with professional application-UI discipline.

Apply coral consistently within each candidate. Repeated elements should keep the same color logic.

Forbidden:

- Pixel art or stepped-edge styling.
- Gradients, lighting, shadows, glow, texture, bevels, or 3D rendering.
- Thin outline-only art.
- Text, letters, numerals, labels, captions, or candidate numbers.
- Cards, tile frames, visible grid lines, checkerboards, or background scenes.
- Photorealism, painterly art, watermarks, signatures, copied franchise marks, or extra colors.

## Distill the article

Use the article title, subtitle, and body as plain text. Do not provide an article-page screenshot to
the image model.

Write a concept brief with:

- **Primary identity:** the named person, place, group, object, event, or principle.
- **Defining relationship:** the action or relationship that makes the subject specific.
- **Structural fact:** an essential count, pairing, hierarchy, cycle, or opposition.
- **Emotional register:** the intended feeling, such as whimsical, ominous, legalistic, or tragic.
- **Motifs:** concrete objects, silhouettes, gestures, transformations, and spatial arrangements.

Choose the article's semantic spine. An icon should express the article's identity rather than
inventory every detail.

## Draft six concepts

Write six materially different one-sentence concepts before generating. Changes in position,
reflection, or color alone do not make a new concept.

Explore a useful mix of:

- A literal emblem of the named subject.
- Two central ideas merged into one silhouette.
- A negative-space construction.
- A count or relationship encoded into the outer form.
- A gesture or action that expresses the article's governing idea.
- An abstract seal-like interpretation.

Prefer one dominant symbol plus one supporting relationship. Avoid arranging several unrelated
clip-art objects around a center. On a 512px source tile, important strokes and gaps should usually
remain at least 12px wide.

## Generate the source sheet

Use built-in image generation unless the user chose another candidate provider. A normal run may
include one optional style-reference sheet. A blind guide test uses no prior icon image.

Request a 1536-by-1024 landscape sheet when available, giving six 512px cells. If another size is
returned, verify it divides into three equal columns and two equal rows with square cells.

Prompt contract:

```text
Use case: logo-brand
Asset type: lore article UI icon candidate sheet
Primary request: Create six materially different pictogram concepts for the supplied article
concept brief. Follow the six concept descriptions closely enough that every tile is distinct.
Subject: <article concept brief and six numbered concept descriptions in prose>
Style/medium: bold flat geometric fantasy pictograms; cohesive emblem silhouettes; smooth vector-
friendly shapes; polished application icon design
Composition/framing: one centered icon per tile; three equal columns by two equal rows; generous
padding inside every tile; consistent scale and visual weight; no visible dividers
Color palette: only charcoal #2C2C2B and coral #F45138 on pure white #FFFFFF
Constraints: exactly six filled-icon designs; strong silhouette; no text; no numerals; no labels;
no watermark; no extra colors; no gradients; no shadows; no glow; no texture; no outlines; no
background objects; no pixel art; pure flat white background
```

Identify an input icon sheet as a style reference and request its visual grammar without copying its
subjects. Keep the article screenshot out of the image inputs.

Inspect the generated result. Regenerate when the layout is malformed, any candidate is clipped,
the background is not plain white, or forbidden effects appear. A rejected draft should remain out
of the compiler.

## Compile at high resolution

Use `scripts/process-sheet.mjs` from the skill. It performs these deterministic operations:

1. Verifies the sheet geometry and crops six source cells without resizing.
2. Maps every source pixel to the nearest of white, charcoal, and coral.
3. Runs VTracer with the fixed palette in spline/cutout mode.
4. Removes white paths, adds an SVG `viewBox`, and validates vector-only output.
5. Renders transparent previews directly from SVG using Resvg.
6. Checks dimensions, alpha coverage, and exact opaque RGB values.
7. Creates white/dark contact sheets and a randomized anonymous review pack.

Trace from the high-resolution cells. Keep 48px and 192px images as render targets only.
The normal generation contract is a 3-by-2 sheet. The compiler's explicit `--columns` and
`--rows` overrides are recovery/import controls for another six-cell arrangement; they do not
change the generation prompt or the six-candidate requirement.

## Blind judging

Use `gpt-5.6-terra` as the preferred judge. Give it:

- Exact article text.
- Randomly named 192px previews.
- The matching randomly named 48px previews.

Hide the alias map, generation prompt, concept descriptions, sheet positions, and creator
preference until scoring is complete.

Score every candidate from 1 to 5:

| Category | Weight | Test |
| --- | ---: | --- |
| Article specificity | 30% | Expresses this article rather than a generic fantasy topic. |
| 48px legibility | 25% | Central symbol remains immediately recognizable. |
| Professional craft | 20% | Balanced, intentional, and suitable for shipped UI. |
| Silhouette and composition | 15% | Clean outer form and controlled negative space. |
| Style compliance | 10% | Matches the two-fill flat pictogram system. |

Request one winner, one runner-up, a concise article-specific reason, and one small refinement when
needed. Disqualify text, embedded raster data, an opaque SVG background, extra fills, pixel-art
styling, or loss of the central feature at 48px.

## Select and refine

Run `scripts/finalize-winner.mjs` after the blind result is mapped back to a candidate ID. This
copies the chosen SVG and its PNG derivatives to stable slug-based names without overwriting files.

For refinement, change one high-resolution feature at a time, then repeat normalization,
vectorization, rendering, and judging. Leave small PNG derivatives untouched.

## Run record

Record:

- Article title, subtitle, and exact input text.
- Concept brief and six descriptions.
- Exact generation prompt and candidate provider.
- Source-sheet dimensions and checksum.
- Compiler dependency versions and settings.
- Validation summary.
- Anonymous judge model, category scores, winner, runner-up, and refinement recommendation.
- Canonical SVG and preview paths.
