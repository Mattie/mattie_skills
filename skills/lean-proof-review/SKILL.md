---
name: lean-proof-review
description: Review Lean theorem production and publication claims for specification fidelity, nonvacuity, trustworthy checking, prose correspondence, and mathematical contribution. Use for substantive theorem milestones or requested Lean proof audits, not every routine tactic edit.
---

# Lean Proof Review

Connect the intended mathematical claim to the exact checked declaration, then assess what the evidence supports. Successful compilation, a faithful specification, an accurate manuscript, and a worthwhile contribution are separate findings.

## Choose the review depth

For a local proof change, inspect the affected statement, definitions, and dependencies; run the relevant build or check. Do not impose a publication audit on an ordinary tactic refactor.

For a new theorem or substantive statement change, add a specification and nonvacuity pass. For a release, submission, or explicit deep audit, inspect the final artifact and scholarly claims as well. Reuse trustworthy evidence tied to an unchanged artifact; repeat costly checks when the artifact, checking route, or known-risk picture changes. State material checks that were not performed.

Human specialist review is optional unless explicitly requested by the user or required by an applicable policy for their chosen submission venue. A light recommendation is welcome when useful; its absence alone is not a defect or an automatic completion or publication gate. Use the formal journal-submission mode only when the user explicitly wants to prepare or send the work to a journal or comparable formal venue. A manuscript draft, preprint, GitHub release, or deep proof audit alone does not activate that mode.

Read the relevant references:

- [Specification and nonvacuity](references/specification.md): when creating statements, extending abstract hypotheses, translating mathematics, or reviewing a surprising endpoint.
- [Library quality](references/library-quality.md): when the user requests code-quality, library API, or upstream-contribution review. Otherwise these recommendations are optional.
- [Artifact and checker evidence](references/artifact-validation.md): when validating unreviewed generated proofs, claiming independent verification, or preparing a reproducible release.
- [GitHub submission](references/github-submission.md): only when GitHub PRs, Actions, or releases are the submission or distribution route.
- [Prose and contribution](references/publication.md): when writing or reviewing a paper, assessing novelty, or deciding how strongly to describe a result.
- [Journal submission](references/journal-submission.md): only for an explicit request to prepare or send work to a journal, refereed proceedings, or a comparable formal submission venue. Otherwise its recommendations are optional.
- [Resources and dated cases](references/resources-and-cases.md): when selecting maintained tools, explaining a failure mode, or refreshing known soundness and specification risks. Historical cases are examples, not a current bug database.

## Establish the target first

Record the checkout or artifact identity, exact final declaration names, intended mathematical statements, scope, and expected evidence. Include final corollary or catalogue wrappers when the publication names them. Inspect existing commands and receipts before inventing a new pipeline.

Review hypotheses and the elaborated proposition, including definitions, notation, coercions, implicit arguments, and instances that give it meaning. Ask whether the formal objects have the intended examples and whether the conclusion follows for the intended reasons. An independently authored trusted statement helps; copying the solution's definition imports into the challenge can preserve the same mistake.

Prefer the maintained Lean validation workflow and comparator over a bespoke string comparator. Standard axiom inspection is useful but cannot detect a theorem whose explicit hypothesis already assumes its conclusion. Source searches are triage, not a semantic certificate. Native proof checking does not establish novelty or manuscript correspondence.

## Complete a release or submission review

Reconcile every advertised validation claim with its exact final declaration, checked artifact, recorded result, and reviewer retrieval path, including supplementary wrappers and corollaries. Distinguish local verification, prepared distribution, and publicly reproducible evidence. Missing coverage, unavailable artifacts, or incomplete records remain explicit gaps; they neither authorize publication nor invalidate an otherwise supported mathematical result.

Preserve frozen proof artifacts and historical receipts. Reuse prior verification only when its receipt covers the current target and the relevant inputs and checking conditions still match; give new artifacts or runs separate identities. Complete the applicable privacy and submission checks before describing the evidence as ready for its intended audience. Follow the [artifact evidence and reuse guidance](references/artifact-validation.md), plus the [GitHub guidance](references/github-submission.md) when that route applies.

## Report evidence precisely

Separate:

- **Confirmed defect:** identify the actual failed claim, minimal example or exact declaration, and consequence.
- **Evidence gap:** say what the check fails to establish; do not recast it as a false theorem.
- **Unresolved concern:** give the smallest useful discriminating check.
- **Supported result:** name the exact scope and artifact, and distinguish a fresh run from an earlier receipt or source inspection.

For a deep pass, leave a compact review artifact with claim-to-declaration mapping, findings ordered by consequence, commands and results actually obtained, trust dependencies, and remaining work. Match publication wording to that evidence. Describe model and human review at their documented scope, without implying peer review or acceptance.

This skill does not authorize contacting authors, installing tools, changing global environments, or publishing. Continue the authorized review and reversible local fixes without inventing extra approval gates. Preserve source and evidence provenance; keep diagnostic experiments separate from the release artifact.
