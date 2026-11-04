---
name: aiconographer
description: Generate, compile, blind-judge, and finalize consistent two-color lore article icons with a coding agent's native image tools. Use for subscription-backed agent runs; use the Aiconographer Python package for API, module, or pipx automation.
metadata:
  version: "0.1.0"
  edition: "coding-agent"
---

# Aiconographer — coding-agent edition

Create six distinct article-icon candidates, assess them at their real UI sizes, and retain one
transparent two-fill SVG as the canonical asset.

This skill is the coding-agent edition of Aiconographer. Use the host agent's native image
generation and reasoning capabilities under the user's coding subscription. It must not require
an API key or invoke the Python package merely to perform an ordinary skill run.

The separate Python package is the API edition: it exposes a module and pipx CLI and uses
Chatsnack for model calls. Provider plumbing intentionally differs. Keep the editions aligned on
their shared workflow and document any behavioral differences rather than assuming identical output.

## Choose the path

- **Full article run:** Read [references/production-guide.md](references/production-guide.md)
  completely, then plan, generate, inspect, compile, blind-judge, and finalize.
- **Compile an existing candidate sheet:** Read the compile and provided-sheet sections of the
  production guide. Run `scripts/check-sheet-padding.mjs --help` and
  `scripts/process-sheet.mjs --help` before compiling.
- **Judge existing compiled candidates:** Read the blind-judging section of the production guide.
  Use only the article text and the compiler's anonymous 192px/48px review pack.
- **Finalize an already selected candidate:** Run `scripts/finalize-winner.mjs --help`.

## Shared behavior contract

- When generating a sheet, plan exactly six materially different concepts.
- Generate one landscape 3-by-2 candidate sheet on pure white.
- Allow at most three generated-sheet attempts. Preserve every attempt and feed concrete rejection
  reasons into the next one.
- Use charcoal `#2C2C2B` and coral `#F45138` as the only final SVG fills.
- Keep final SVG backgrounds transparent; white is a temporary raster background.
- Validate tile padding deterministically before model inspection or compilation.
- Keep each icon roughly centered. The compiler shifts noticeably displaced artwork as a whole;
  small offsets and the design's internal composition remain unchanged.
- Trace at source resolution and judge direct SVG renders at 192px and 48px.
- Give the judge anonymous previews without candidate IDs, concepts, positions, prompts, or creator
  preference. A same-agent judging phase is not independent or fully blind if it saw the sheet.
- Produce a parsed scorecard, exclusive winner finalization, and a retained run record.
- Support a user-provided 3-by-2 sheet by skipping planning and generation while preserving
  deterministic validation, blind judging, and provenance.
- Derive the final slug from the article title: lowercase ASCII, replace non-alphanumeric runs
  with hyphens, trim hyphens, and fall back to `source-icon`. Never overwrite an existing result.

## Generated-sheet run

1. Extract the source text's primary identity, defining relationship, essential structure,
   emotional register, and useful motifs.
2. Write six genuinely different one-sentence icon concepts.
3. Generate a 1536×1024 candidate sheet with the host's native image tool. Request six square
   cells, generous padding, the exact palette, and no dividers or forbidden rendering effects.
4. Save the sheet as `candidate-sheet-attempt-N.png`. Run the deterministic padding check, then
   inspect the whole sheet visually. If rejected, retain the reasons and retry, up to three total
   attempts.
5. Compile the first accepted sheet with `process-sheet.mjs`. Treat compiler rejection like an
   inspection rejection when attempts remain.
6. Use a fresh judge context when available. Give it only the exact source text and paired
   anonymous 192px/48px previews.
7. Save the structured result as `aiconographer-scorecard.json`, verify its aliases and weighted
   arithmetic, and map the winner through `review-map.json`. Stop before finalization when the
   scorecard is structurally invalid.
8. Finalize exactly one candidate with `finalize-winner.mjs`.
9. Retain the source, concept brief, all attempts, inspections, accepted sheet, prompt, compiler
   outputs, scorecard, selection, provider label, tool versions, and checksums in
   `run-record.json`.

For a provided sheet, follow the guide's provided-sheet path instead of planning or generating.

## Deterministic compiler setup

The bundled scripts use pinned Node dependencies from a caller-supplied directory so
`node_modules` stays outside the skill. Stage them in a temporary directory:

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

Check the four-percent safety band before compilation:

```powershell
& $node "$skillRoot\scripts\check-sheet-padding.mjs" `
  --input '<candidate-sheet.png>' `
  --deps-root $depsRoot
```

Compile into a new or empty directory:

```powershell
& $node "$skillRoot\scripts\process-sheet.mjs" `
  --input '<candidate-sheet.png>' `
  --output '<new-empty-run-directory>' `
  --deps-root $depsRoot `
  --article '<source-text-file>'
```

After judging, finalize without overwriting prior output:

```powershell
& $node "$skillRoot\scripts\finalize-winner.mjs" `
  --run '<run-directory>' `
  --candidate c6 `
  --slug '<article-slug>'
```

Use equivalent `node` and `npm` commands on non-Windows systems. Do not add these dependencies
to the host project merely to process a sheet.

## Completion

Inspect the white and dark contact sheets and the winning 48px render before reporting success.
Provide the canonical SVG, preview, scorecard, run record, exact generation prompt, and candidate
provider. For a provided sheet, report the generation prompt as `null`. State that this was the
coding-agent edition so the provenance is unambiguous.
