---
name: aiconographer
description: Generate and select consistent two-color lore article icons, then compile candidate sheets into validated transparent SVGs and small-size previews. Use for Lorebubble-style article icon creation or refinement; avoid for general illustrations or maintenance of an existing third-party SVG set.
---

# Aiconographer

Create six distinct article-icon candidates, assess them at their real UI sizes, and retain a
transparent two-fill SVG as the canonical asset.

Keep the candidate provider replaceable. The current workflow uses built-in image generation;
another provider such as a Chatsnack app may later produce the same 3-by-2 sheet contract. The
deterministic compiler in `scripts/` begins at that sheet and remains unchanged.

## Choose the path

- **Full article run:** Read [references/production-guide.md](references/production-guide.md)
  completely, then generate, compile, judge, and select an icon.
- **Compile an existing candidate sheet:** Run `scripts/process-sheet.mjs --help`. The input must
  be a clean 3-by-2 sheet with six square cells. Read the normalization and validation sections of
  the production guide when interpreting failures.
- **Judge existing compiled candidates:** Read the judging section of the production guide and use
  the anonymous review pack produced by the compiler.
- **Finalize an already selected candidate:** Run `scripts/finalize-winner.mjs --help`.

## Non-negotiable asset contract

- Six materially different candidates.
- Charcoal `#2C2C2B` and coral `#F45138` are the only final SVG fills.
- The final SVG background is transparent.
- White `#FFFFFF` is a temporary generation and tracing background.
- Generate and trace at high resolution; judge direct SVG renders at 192px and 48px.
- The selected SVG is canonical. PNGs are derivatives.
- Do not pass article-page screenshots to the image model. Extract and use the article text.
- Do not create pixel art, text, labels, gradients, shadows, texture, or miniature scenes.

## Full-run workflow

1. Extract the article's primary identity, defining relationship, essential structure, emotional
   register, and useful motifs.
2. Draft six one-sentence concepts with genuinely different metaphors or compositions.
3. Generate one 3-by-2 candidate sheet on pure white using the production-guide prompt contract.
   A style reference is optional and must be identified as style-only.
4. Inspect the sheet. Regenerate when the grid is malformed, a candidate is clipped, or forbidden
   rendering appears.
5. Compile the retained sheet with `process-sheet.mjs`.
6. Give a `gpt-5.6-terra` judge only the article text and anonymous 192px/48px previews. Keep the
   alias mapping, prompts, concepts, positions, and creator preference hidden.
7. Score article specificity, 48px legibility, professional craft, silhouette/composition, and
   style compliance with the production-guide weights.
8. Finalize the winner with `finalize-winner.mjs`. Record the concept brief, exact prompt,
   scorecard, winner, and any refinement recommendation beside the run.

## Deterministic compiler setup

The scripts load pinned Node dependencies from a caller-supplied directory so `node_modules` never
needs to live inside the skill. Stage dependencies in a temporary directory:

```powershell
$skillRoot = '<absolute-path-to-this-skill>'
$depsRoot = Join-Path ([System.IO.Path]::GetTempPath()) 'aiconographer-node-deps'
$npm = (Get-Command npm.cmd -ErrorAction Stop).Source
$node = (Get-Command node.exe -ErrorAction Stop).Source
New-Item -ItemType Directory -Path $depsRoot -Force | Out-Null
Copy-Item -LiteralPath "$skillRoot\scripts\package.json" -Destination $depsRoot
Copy-Item -LiteralPath "$skillRoot\scripts\package-lock.json" -Destination $depsRoot
& $npm ci --prefix $depsRoot
```

Use equivalent `node` and `npm` commands on non-Windows systems. Never add these packages to the
host project's dependencies merely to process an icon sheet.

Compile a sheet:

```powershell
& $node "$skillRoot\scripts\process-sheet.mjs" `
  --input '<candidate-sheet.png>' `
  --output '<new-empty-run-directory>' `
  --deps-root $depsRoot `
  --article '<article-text-file>'
```

The compiler refuses a non-empty output directory. It writes normalized source tiles, SVGs,
192px and 48px transparent previews, white and dark contact sheets, an anonymous judge pack,
`review-map.json`, and `validation.json`.

After judging, finalize without overwriting prior output:

```powershell
& $node "$skillRoot\scripts\finalize-winner.mjs" `
  --run '<run-directory>' `
  --candidate c6 `
  --slug '<article-slug>'
```

## Completion

Inspect the generated contact sheets and winning 48px render before reporting success. Provide the
canonical SVG path, preview path, run record or scorecard, final generation prompt, and whether the
candidate provider was built-in image generation or another source.
