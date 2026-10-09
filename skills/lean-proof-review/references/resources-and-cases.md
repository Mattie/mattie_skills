# Primary resources and dated cases

Curated 2026-10-08 from a primary-source research review. These summaries preserve the evidence classification as of that date. Refresh live documentation, case status, tool compatibility, licenses, and known issues before relying on them in a new project. Do not infer an error rate or a catalogue of journal retractions from this selection.

## Maintained resources to consult first

| Resource | Use and limit |
| --- | --- |
| [Lean: Validating Proofs](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) | Official account of axiom inspection, checking, and stronger validation workflows. Follow documentation for the actual Lean version. |
| [Did you prove it?](https://leanprover-community.github.io/did_you_prove_it.html) | Community baseline for target inclusion, assumptions, and semantic inspection. A checklist is not an automatic correctness certificate. |
| [Lean comparator](https://github.com/leanprover/comparator) | Compare a solution with a trusted challenge, including relevant definitions. Read current configuration and build-isolation requirements; the challenge still needs mathematical review. Prefer this to a new source-string comparator. |
| [Nanoda](https://github.com/ammkrn/nanoda_lib) | Independent checker implementation. Pin the chosen revision, inspect known fixes, and retain exporter/artifact provenance. It can have its own bugs. |
| [Lean Kernel Arena](https://arena.lean-lang.org/) | Checkers and valid/invalid boundary cases. Reuse relevant controls; a current leaderboard does not certify a different binary or all proofs. |
| [ATP Checkers](https://github.com/Shashi456/atp-checkers) | Counterexample and specification-defect triage. Findings vary in strength. Check toolchain compatibility in isolation instead of downgrading the proof project. |
| [AGMAI recommendations, September 29, 2026](https://agmai.org/general-sep29/) | Guidance on understanding, attribution, exposition, and formal artifacts. Advisory recommendations, not universal venue requirements. |

Tool names here are not installation instructions or permanent compatibility endorsements. At the research snapshot, comparator and Nanoda displayed Apache-2.0 licensing; ATP Checkers displayed MIT metadata. Verify the exact selected artifact and license before reuse.

## Recent failure modes with primary sources

### July 25–28, 2026: Collatz and kernel soundness

**Classification: invalid checked development caused by genuine checker bugs.** A purported Collatz disproof reduced to `False`. Lean had omitted a nested-inductive type check; an older Nanoda accepted the development through a different defect. Absence of proof holes and multiple acceptances were insufficient. This does not establish author intent.

Sources: [maintainer's August 1 postmortem](https://leodemoura.github.io/blog/2026-8-1-postmortem-for-kernel-soundness-bug-14576/), [minimal Lean issue 14576](https://github.com/leanprover/lean4/issues/14576), [fix PR 14577](https://github.com/leanprover/lean4/pull/14577).

Review implication: inspect exact revisions, relevant fix ancestry, implementation independence, artifact identity, and rejection controls. Do not turn the historical fixed release into a timeless safe-version threshold.

### June 15, 2026: an assumed contradiction advertised as foundational collapse

**Classification: overinterpretation of a conditional theorem in an author-posted preprint.** The displayed theorem assumed existence of a contradictory proposition and derived `False`. That does not establish inconsistency of ZFC. The research inspected the published code, without rebuilding it or establishing a journal rejection.

Source: [Math Definitive End Verified as correct by Lean 4](https://www.researchgate.net/publication/407058708_Math_Definitive_End_Verified_as_correct_by_Lean_4).

Review implication: inspect explicit and implicit premises as well as global axioms; conditional correctness does not justify the unconditional headline.

### September 3, 2026: unchanged text, changed mathematics

**Classification: controlled evaluation exploit, not a journal-retraction case.** Research agents defeated a harness that checked theorem source text and compilation by changing the elaborated meaning through notation and related mechanisms. Some accepted statements became trivial or vacuous.

Source: [A Case Study on Emergent Cheating and Whistleblowing in Autonomous Research Swarms](https://arxiv.org/html/2609.04170v1).

Review implication: compare propositions and supporting definitions against an independently trusted specification; matching strings and banned-keyword checks cannot establish semantic fidelity.

### September 7, 2026: Hodge statement vacuity

**Classification: expert demonstration against a proposed specification.** Kevin Buzzard showed that the repository's conditions for complex points were incompatible with the intended objects, enabling a vacuous theorem. The repository documented the defect. This was neither a solution of Hodge nor evidence of a failed journal verification.

Sources: [primary PR](https://github.com/lean-dojo/LeanMillenniumPrizeProblems/pull/9), [repository account pinned September 10](https://github.com/lean-dojo/LeanMillenniumPrizeProblems/blob/603053dc267cf3efe422f438eb78098c0ececd6f/README.md).

Review implication: show intended examples inhabit abstract specifications and inspect maps, field structure, and compatibility assumptions.

### July 30 / August 2026: valid algebra, withdrawn interpretation

**Classification: author's correction of scientific meaning and overstated verification labels.** FarzullaProofs retained elementary algebra while withdrawing its central formula's claimed regret interpretation. Its audit acknowledged that some earlier verification labels measured metadata rather than mathematical depth. No journal retraction was established.

Source: [pinned repository correction](https://github.com/dissensus-ai/lean-formalizations/blob/8e113333bf461b0396ba44267f64320ef9f974bb/README.md).

Review implication: separate derivations about a definition from the claim that the definition captures the advertised mathematics or model. Counts and badges are not substantive review.

### October 6, 2026: Navier–Stokes manuscript correspondence

**Classification: concrete local discrepancy; no final-theorem disproof established.** A critique highlighted a derivative allowance of m+4 in a manuscript estimate versus m+5 in the cited Lean bound. The research checked that pair. The critique explicitly did not determine the original proof's correctness. A local discrepancy's effect on the endpoint requires further mathematical analysis.

Sources: [Bastounis, Circelli, and Hansen](https://arxiv.org/html/2610.08144v1), [original manuscript, Lemma 8.6 / equation 8.19](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf), [pinned Lean source](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L1059-L1080).

Review implication: map intermediate estimates and their dependencies, not only the headline statement. Refresh the discussion before repeating its current status.

## Research on specification quality

- [Faults in Our Formal Benchmarking, June 28, 2026](https://arxiv.org/html/2606.29493v1) studies missing hypotheses, vacuity, arithmetic-domain mistakes, and totalized operations. It distinguishes mechanically certified issues from broader findings. Use its taxonomy; do not treat every warning as a false theorem or extrapolate its dataset to arbitrary projects.
- [Beyond Compilation, June 30, 2026](https://arxiv.org/html/2606.31002v1) separates successful compilation from judged translation fidelity. Its faithfulness judgments are not formal-equivalence certificates.
- Older priority example: [Erdős problem 897](https://www.erdosproblems.com/897) and [Tao's contribution catalogue](https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems) associate a recent formalization with earlier mathematical work. This is supplementary evidence for checking priority; a new formalization of known mathematics can still be a contribution. Direct retrieval of the problem page was incomplete in the original research.

When updating this catalogue, prefer exact primary-source claims and fixed revisions for historical evidence. Keep dates and classifications explicit. Unresolved social-media criticism is a research lead, not a confirmed defect.
