# Mathematical research

Read this for proofs, Lean libraries, mathematical theory, or bounded novelty
searches in any mode. Use the entry skill's privacy, trust, adoption, and
effort rules. This reference specializes discovery and comparison; research
alone does not validate a proof. Continue implementation already in scope.

## Frame the proposition

Record the intended definitions, hypotheses, conclusion, and mathematical
domain. Distinguish finding a proof or useful technique from finding a Lean
formalization, and from asking whether a result is already known. For Lean
reuse, discover the project's toolchain, pinned dependencies, and imports.
For an informal theory question, do not invent a Lean environment requirement.

Build queries from theorem names, synonyms, equivalent formulations,
stronger results implying the target, special cases, and proof techniques.
Include key assumptions and counterexamples to nearby claims. An existing
general theorem may settle the question even when our wording is unfamiliar.
Compare definitions, quantifiers, domains, hypotheses, and conclusions before
calling two results equivalent or one a replacement.

## Choose sources by purpose

These are source choices, not a checklist for every query. Start with local
material and sources appropriate to the target, then follow promising leads.

| Purpose | Sources and use |
|---|---|
| Existing Lean declarations | Current project and pinned dependencies; [mathlib source](https://github.com/leanprover-community/mathlib4) and [documentation](https://leanprover-community.github.io/mathlib4_docs/); [Loogle](https://loogle.lean-lang.org/) for names and expression patterns; [LeanSearch](https://leansearch.net/) for natural-language queries. Confirm hits against the target revision. |
| Libraries and ongoing formalizations | [Reservoir](https://reservoir.lean-lang.org/), GitHub code/issues/PRs, [Lean projects and intentions](https://leanprover-community.github.io/lean_projects.html), project blueprints, and [public Lean Zulip archives](https://leanprover-community.github.io/archive/). A listing, intention, or blueprint is a discovery lead; inspect the actual proof source and progress. |
| Conjecture statements and status | [FormalConjectures](https://github.com/google-deepmind/formal-conjectures), its cited sources, and linked external proofs. Check current status and later solutions; a catalogue entry can contain only a statement or retain a placeholder beside an external proof link. |
| Mathematical literature | [arXiv](https://arxiv.org/), original papers, books, author pages, journal versions, citation trails, [zbMATH Open](https://zbmath.org/), and [MathSciNet](https://mathscinet.ams.org/mathscinet/help/about.html) when accessible. Reviews and indexes identify sources; inspect the original result before relying on its scope. |
| Topic-specific leads | [Stacks Project](https://stacks.math.columbia.edu/) for algebraic geometry, [DLMF](https://dlmf.nist.gov/) for special functions, [OEIS](https://oeis.org/) for sequences, [MathOverflow](https://mathoverflow.net/) and [Mathematics Stack Exchange](https://math.stackexchange.com/) for terminology, references, and proof ideas. Follow discussion claims to primary evidence. |
| Proofs in other systems | [Isabelle AFP](https://isa-afp.org/), [Rocq/MathComp](https://math-comp.github.io/), and [Metamath](https://us.metamath.org/) when a formal proof or technique could be ported. Record differences in foundations and library definitions; availability there does not establish Lean compatibility. |

Search engines and theorem indexes can use a different library revision from
the project. Missing results, stale status, access restrictions, and index
coverage limit the conclusion. Report an unavailable source as a gap, not an
empty search. Do not require subscriptions or new tools just to finish a
bounded search.

## Check relevant open PRs

When ongoing formalization matters to a default or deep search, search open
PRs, including drafts, in relevant projects. For Lean, these may include
[mathlib](https://github.com/leanprover-community/mathlib4/pulls) and
[FormalConjectures](https://github.com/google-deepmind/formal-conjectures/pulls).
Search the target's theorem names, concepts, and equivalent terms; refine when
the first query misses relevant vocabulary. Check ongoing work even if merged
source already provides a useful result when the question calls for it.

For promising PRs, inspect the current diff, proposed statements and proofs,
imports, relevant toolchain, review status, and available CI evidence tied to
the PR's current head. Distinguish CI scope and result from proof completeness.
Label open results as pending/unmerged, and note draft status when applicable;
do not describe their declarations as already available in released or merged
libraries. Record the PR link and evaluated head revision when reporting a hit.

If PR search or evidence is inaccessible or truncated, name the coverage gap
in the Search note; do not report that no relevant PR exists. Quick mode keeps
its existing bounds and does not require this additional pass.

## Preserve the selected mode

- **Quick:** Search the current project and available pinned libraries with
  the exact term and one synonym or expression pattern. Check the strongest
  local candidate. If it does not settle reuse, run one focused external
  search using the most relevant theorem index, Reservoir, GitHub, or
  literature source. Open primary evidence for the strongest hit; stop at a
  credible direct answer or after one refinement. Return one to three leads
  using the entry skill's inline fit format. Quick mode cannot establish
  originality; say when a novelty question needs default or deep coverage.
- **Default:** Search relevant formalization and literature sources with
  exact, equivalent, and adjacent-result terms. Follow citations, terminology,
  and related projects one level outward; verify the leading results and
  check relevant ongoing work when it matters. For reuse, stop when the
  recommendation is supported and further search is unlikely to change it.
  For a novelty question, also compare
  closest known results and applicable literature even if a local proof
  settles reuse. Report bounded findings and remaining gaps.
- **Deep:** Cover applicable mathematical lanes, including relevant ongoing work.
  Trace predecessor results, generalizations, equivalent formulations,
  counterexamples, corrections, and formalizations.
  Report meaningful gaps and stop when further searching is unlikely to change
  the assessment. A bounded search is not a certificate of originality.

Honor an explicitly requested lower mode as an effort ceiling. Automatic
checks before substantial proof work look for reuse; do not expand them into
a novelty investigation without a request or a novelty claim to evaluate.

## Compare results and proof evidence

Describe the relationship to our target: an exact result, a stronger theorem
that implies it, a special case, a related result with different hypotheses,
a proof technique, or a counterexample. Keep this relationship separate from
practical fit and from the strength of the evidence.

Inspect the leading candidate's actual statement and proof location. Identify
whether it is an informal proof, formal statement, incomplete proof, or
checked formal proof. A declaration with `sorry`, `admit`, or an unproved
assumption establishing the target is not a proof of the intended claim.
FormalConjectures entries and successful catalogue builds must not be
presented as proof of their statements; inspect linked external proofs
separately. Compilation also does not establish faithful translation.

For Lean results, record the declaration and module, source revision, and
Lean/mathlib versions when they affect reuse. Distinguish inspected source
from existing build evidence and from a check we actually ran. A green build
alone does not exclude proof placeholders. Missing placeholder text alone
does not audit all dependencies. Do not claim compatibility or a checked
proof beyond the available evidence tied to that declaration and revision.
Full specification, axiom, and artifact audits belong to a separately
requested proof-review workflow.

For literature, identify the theorem or proposition, author, source, and
relevant version or date. Separate an announced claim from an available
proof, and a preprint from a published version. Check material corrections or
later versions when they affect the result.

## Assess novelty separately

Distinguish a new mathematical result from a new proof, a new special case,
and a new formalization. A known theorem can still have no discovered Lean
proof; the absence of Lean code does not establish mathematical novelty.
Likewise, an intention or incomplete formalization does not establish a
completed proof, though it may reveal ongoing related work.

Compare closest known results under their actual hypotheses, including
stronger theorems and immediate corollaries. Trace original citations and
publication chronology before assigning priority. Identify counterexamples
or corrections that change whether the target is true or already settled.

Use searched-source language: "I found no earlier result in the sources
searched," with coverage, date, closest results, and meaningful gaps. Do not
conclude "original," "unproved," or "first formalization" from a failed
search. If a missing source or unresolved statement comparison could change
the assessment, leave novelty inconclusive and name the next useful check.

Use the mathematical-candidate guidance in
[Reuse Shortlist](reuse-shortlist.md) for default and deep output. Citing
mathematics and copying proof text or code are different uses; apply the
existing adoption checks when copying material or adding a Lean dependency.
