# Artifact and checker evidence

Use this pass for a claimed verified release or a review of an untrusted proof artifact. Scale execution to the requested assurance, available environment, and existing evidence.

## Preserve the chain of identity

Track the mathematical specification, source commit or file hashes, dependency lock and toolchain, compiled environment, exported artifact when used, and checker commands and outputs. The record should answer: which exact final declaration was checked, by which binary, against which specification?

Map each advertised statement to its exact final declaration and required evidence. When independent comparison is claimed, identify the separately compiled specification and relevant definition closure. A checked core export does not cover an omitted later wrapper, corollary, generated file, or supplementary module.

Verify explicit build and export targets, including required dependency targets. A successful default build may perform no relevant work. Run commands in the context that selects the pinned toolchain. A manifest check may permit missing optional assets; test the documented retrieval path with the intended reviewer's access before calling a release reproducible. Hashes connect artifacts but do not prove their mathematical meaning. Distinguish local verification, prepared distribution, and publicly reproducible evidence; an unpublished download remains a distribution gap.

Distinguish source rebuilt in this run, trusted dependency caches, reused compiled files, and earlier execution receipts. Do not describe a quick manifest check as a fresh Lean build, or a Lean build as an independent export replay. Preserve enough commands and outputs for another reviewer to reproduce the selected route.

## Use maintained validation mechanisms

When selecting or updating a validation route, consult current official Lean validation documentation and inspect the project's existing tools. For conventional mathematics, inspect the final declaration's transitive axiom list; `propext`, `Classical.choice`, and `Quot.sound` are normally expected. Other assumptions require interpretation and disclosure, not merely a name blacklist. A deliberate axiomatic theory can be legitimate when the claim is explicitly conditional on it.

For a new audit run, enforce the stated axiom policy on its fresh output with required declaration coverage. Reused audit results follow the evidence-reuse checks below. Empty, missing, malformed, or conflicting reports must not count as success. Merely printing an axiom list is not policy enforcement; retain the report and the enforcement result.

Source scans for proof holes, custom axioms, `native_decide`, unsafe or external declarations, and environment mutation help locate trust boundaries. Some mechanisms are legitimate with documented extra trust; inspect the actual checked dependency closure and intended assurance rather than declaring every keyword unsound. A source scan cannot certify imported or dynamically introduced declarations.

For proofs requiring stronger assurance, use fresh-environment checking and the maintained comparator with its documented isolation. Code executed during elaboration or build is part of the threat model. A new working directory alone is not a sandbox; do not expose a supposedly frozen challenge to writes from untrusted build steps. Follow the chosen tool's supported isolation mechanisms instead of claiming equivalent protection from an improvised setup.

An independent checker such as Nanoda adds implementation diversity. Record shared exporter, parser, and library dependencies. Two releases of Lean are related implementations, not two unrelated foundations. A checker derived from another kernel may share the same defect. No checker count is a proof that all possible soundness bugs are absent.

## Check the versions and the invocation

Before a substantial release check, review current known soundness issues and fixes for the exact source revisions in use. Historical minimum-version advice goes stale. Confirm ancestry of relevant patches or equivalent fixes, and record binary provenance; a version string alone does not authenticate a binary.

Where practical, run a known-valid acceptance control and appropriate rejection controls through each actual checking route. For an audit policy excluding admissions and extra axioms, test an imported admitted proof and an extra axiom through the actual audit invocation. Distinguish these policy controls from an ill-typed-proof rejection control for an independent kernel. Require the intended rejection diagnostic; an arbitrary failure or parser crash does not establish that the intended rule rejected the proof. Use maintained fixtures, including relevant Kernel Arena cases, rather than building a new adversarial-testing framework without need.

A successful control checks the invocation and the covered case, not universal checker correctness. Record timeouts, unsupported features, skipped declarations, and failures separately from acceptance.

Keep frozen dependency style warnings visible without editing inherited proofs merely to silence them. Validate final owned declarations under the intended strict policy. Do not broadly suppress warnings that could conceal proof holes or a changed claim.

## Preserve frozen artifacts and provenance

Record the protected baseline of proof sources, dependency and toolchain pins, manuscripts, exports, protected manifest entries, and historical receipts. Verify it after packaging or tooling repairs. Update manifest entries only for deliberate changes. Register new proof artifacts, corrections, or transport archives under distinct identities while preserving protected historical entries; never rewrite a protected expected hash to conceal a changed artifact. Give new wrapper exports and verification runs distinct identities while preserving historical artifacts and the scope of their original results.

Check inherited provenance against a pinned revision using complete inventories and contents, including missing and extra files and relevant configuration. Comparing only overlapping filenames is insufficient.

For compressed distribution, record and check sizes and hashes for both the transport archive and the uncompressed proof bytes. Use deterministic compression for newly prepared transports where practical; do not regenerate an existing archive merely for consistency. A transport change can require new archive and decompression checks without repeating verification of unchanged proof bytes.

## Review publication privacy

Restrict ordinary publication scans to intended source and documentation, excluding disposable dependency, cache, and build trees. Separately inspect the actual files being distributed: generated files that will ship remain in publication scope. Run publication checks after builds as well as before them.

Inspect prose, source comments, logs, receipts, archive member names, and document or PDF metadata where applicable. Remove unintended private workstation paths, usernames, hostnames, local-only filenames, contact details, and other personal information from the intended distribution. Preserve intended public filenames, repository-relative references, author names, and legitimate scholarly references. Use automated detection to find candidates, then review their context; permitted attribution and citations are not blanket exceptions for all information about an author.

Keep raw operational logs and receipts private when they contain local details. Public commands should use reproducible relative paths or documented placeholders, without requiring the author's private directory layout. Do not reproduce detected private strings in an audit report intended for publication.

Never silently redact a frozen artifact and retain its old digest. Produce a separately named public derivative, hash it, and record the relationship without exposing private content. If the checked proof payload itself changes, establish the required verification for the new payload before claiming that it was checked. Preserve sensitive originals privately; preservation does not require continued public access. Identify already-public exposures and handle public replacement or removal within the human's authorization.

## Record verification steps

Prefer structured receipts and extend the project's existing format instead of creating a competing system. A bare timestamp or pass marker cannot establish what was checked. The filename and serialization are less important than the following contents:

- Step identifier, validation claim, exact target declarations, outcome, and completion time in UTC.
- Relevant input manifest and digests, including specifications, dependency pins, or export inventories when they affect that step.
- Checker and tool identities, plus relevant runner, parser, configuration, and axiom-policy identities.
- Reproducible command, exit status, applicable acceptance and rejection controls, output artifact identities, and retained log digests.
- Material scope and trust limits, such as reused official dependency caches or absence of a full dependency bootstrap.
- Producing CI run or other accepted execution provenance when available.

A receipt records an executed check; it does not replace the check or authenticate itself. Keep immutable receipts per step and relevant input/checking identity. An optional current-result index should reference those records without overwriting history. Write a successful receipt only after acceptance criteria and required evidence retention complete. Automated pipelines should use atomic completion so interrupted writes cannot appear successful. Missing required reports or logs leave the auditable step incomplete even if Lean succeeded. Distinguish failed and interrupted attempts from successful results.

Keep proof checking, privacy review, upload, and download-access checks as separate steps. If upload fails after proof checking succeeds and the outputs and raw evidence remain available, retry upload rather than repeating the proof check. A reuse assessment should reference the original execution receipt and date rather than issue a receipt claiming a new execution.

## Reuse evidence according to what changed

Before reuse, verify accepted provenance, matching relevant inputs, targets, tools, and policies, and the existence and digests of outputs and required logs. Check that no known soundness issue invalidates the result. Report reused verification with its original date and identity. A matching source hash alone is insufficient when the checked target, specification, checker, or validation policy changed. Historical receipts for earlier identities remain history, not evidence of current coverage.

Use the dependency graph of checks to select affected work:

| Change | Reconsider or rerun |
| --- | --- |
| Proof source, mathematical dependency, or final target | Affected builds, exports, and downstream proof checks |
| Independent specification or comparison policy | Relevant statement and definition comparison |
| Checker, audit parser, axiom policy, or relevant runner configuration | Affected validation route and controls; prior receipts remain historical |
| Documentation or public log redaction | Publication/privacy checks and changed public artifact identities; reuse applicable verification of unchanged proof bytes |
| Transport compression | Archive identity and decompression checks; reuse applicable proof-byte verification |
| Release URL, access policy, or expired evidence link | Retrieval/access checks; reuse applicable proof-byte verification |

Network accessibility is time-dependent. Recheck it at publication and submission milestones. An old successful download is not perpetual evidence of availability; an expired link does not erase an otherwise valid historical proof check. For GitHub workflows and evidence retention, read [GitHub submission](github-submission.md) when that route applies.

## Evidence bundle for a substantive release

Adapt this list to the project; do not create ceremonial files for an ordinary proof edit:

- Exact theorem names and trusted statement/challenge identity.
- Source and dependency revisions, artifact digests, and meaningful build provenance.
- Checker and exporter revisions, binary provenance, configuration, and shared dependencies.
- Execution receipts, commands, exit status, retained output and logs, axiom/declaration audit, and controls actually run; identify any reused results by original date and identity.
- Final-wrapper coverage, external-asset retrieval instructions, and explicit unchecked boundaries.

If environment or resource limits prevent a selected check, retain completed evidence and state the limitation. Do not silently replace semantic comparison with a text match or label an earlier receipt a new reproduction.
