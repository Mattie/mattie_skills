# Specification and nonvacuity

Use this pass when drafting or changing the mathematical statement, or when a proof appears unexpectedly easy or strong. The goal is a faithful proposition, not simply a proposition the current proof can establish.

## Inspect the actual proposition

Read the declaration after elaboration, using the project's Lean version and appropriate pretty-printing options. Check all binders, implicit parameters, universe and typeclass assumptions, and dependencies of local definitions. Fully qualified names help inspection but are not a replacement for comparing their definitions in independently built environments.

Build a small correspondence table when it clarifies a substantive claim:

| Informal object or clause | Lean definition or binder | Meaning and obligations |
| --- | --- | --- |
| Domain of objects | Type plus structure fields | Intended examples inhabit it; fields do not already imply the conclusion. |
| Uniform estimate | Ordered quantifiers | Constants and thresholds depend only on permitted earlier variables. |
| Endpoint value | Fully specified expression | Signs, branches, normalizations, and coercions agree. |
| Named invariant | Definition and bridge lemmas | Conventions and finiteness assumptions match the paper. |

Look for a weaker substitute: pointwise instead of uniform bounds, one witness instead of all objects, an eventual inequality with the threshold chosen after the tested variable, extra regularity or nondegeneracy assumptions, or a conditional theorem presented as unconditional. Inspect inherited section variables and instances as well as visible theorem arguments.

## Check that the statement has content

Construct representative intended examples of abstract assumptions, where feasible. Examine zero, negative, boundary, finite, and degenerate cases relevant to the claim. Try simple counterexamples and compare known special cases. These checks can expose mistakes; finitely many examples cannot certify a universal proposition.

Pay attention to Lean's total and typed operations:

- Natural subtraction truncates. A difference over naturals may not mean the integer or real difference in prose.
- Division and real logarithm or square root have total definitions. Inspect actual library conventions and the domain hypotheses needed for the advertised identities.
- Suprema, infima, extrema, and limits need the correct ambient type and existence or boundedness assumptions. A real-valued convention may be unsuitable for an invariant that can be infinite.
- Finite sets can be empty; structures and typeclass hypotheses can be uninhabited or incompatible. Check intended examples before treating a universal result as substantive.
- Infinite representations are not necessarily infinitely many distinct objects. Reduced fractions, repeated indices, multiplicity, and image sets matter.
- An existential object defined by the desired property is not automatically constructed. Trace its existence proof and any assumptions it uses.

Standard global axioms such as choice do not hide an explicit premise of the form “assume a contradiction.” Conversely, their presence is not itself a defect. Interpret both the theorem's arguments and its axiom closure.

## Keep the trusted specification independent

For a release-level comparison, derive a challenge from the mathematical statement with trusted standard definitions and minimal imports. Do not fix a mismatch by weakening the challenge to match the current proof without identifying the changed mathematical claim.

Compare compiled propositions and the relevant transitive definition closure, not just source strings, declaration names, or pretty-printed text. Use the maintained comparator workflow linked in [resources](resources-and-cases.md), with its actual version-specific configuration and isolation requirements. A comparator can confirm agreement with a mistaken challenge, so mathematical review remains necessary.

A challenge placeholder is not a completed proof. Keep intentionally unproved specifications separate and use the comparator's documented mechanism rather than treating all occurrences of `sorry` as either harmless or fatal without examining their role.

Distinguish theorem-proof placeholders from [definition holes](https://github.com/leanprover/comparator#definition-holes) deliberately left for a solution to fill. Comparator checks the configured structural, axiom, and type-checking conditions for those definitions; their intended semantic constraints need separate validation through suitable formal conditions or mathematical inspection. For example, filling a truth-value hole with the original conjecture can make an equivalence reflexive without resolving the conjecture. Report what the additional check establishes.

## Optional automated triage

Counterexample, vacuity, unused-binder, and arithmetic-domain linters can prioritize inspection. Separate mechanically demonstrated counterexamples from heuristic warnings. Validate candidates against the exact theorem and imports; do not edit away an unused assumption solely to satisfy a linter. Compatibility work belongs in an isolated test environment when a tool targets a different Lean release.
