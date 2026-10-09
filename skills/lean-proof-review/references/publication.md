# Prose, contribution, and responsible publication

Use this pass for a manuscript, release announcement, or claim that a formal result constitutes new mathematics. Review conclusions at the level supported by the evidence.

## Map the mathematical bottlenecks

Start with the main theorem and the steps on which its strength depends. Connect manuscript claims to exact Lean declarations, hypotheses, and proof dependencies. For a requested full correspondence review, continue through the remaining substantive claims; identify any portion only sampled.

For each decisive imported result, record its exact statement, parameter substitutions, and where each hypothesis is discharged. When prose combines or adapts several formal developments, check each application separately and identify which intermediate claims the cited artifacts actually cover.

Track constants, derivative or degree budgets, normalization factors, branches, strict versus weak inequalities, and parameter dependencies. Verify that limits and asymptotic choices occur in the stated order and that the prose has not silently claimed an effective constant from a non-effective argument.

Do not transfer an invariant under a transformation without its actual invariance theorem and hypotheses. Rational scaling does not automatically justify arbitrary algebraic scaling. A bound on a product of conjugate values does not imply the same bound on each value. When arguments compare embeddings, matrices, minors, or witnesses, establish that the formal proof uses the same object where the prose requires it.

A stronger assumption or weaker estimate in one Lean lemma is a correspondence finding. Determine whether subsequent steps still establish the advertised endpoint before escalating it to a false-theorem claim. Correct the prose or proof at the smallest faithful point; avoid broad verdicts based on one mismatch.

## Establish what is new

Separate the new mathematical result, new proof, formalization of known mathematics, reusable library infrastructure, and exposition. Any can be a worthwhile contribution; do not relabel one as another. Declaration counts, token counts, short or long tactic proofs, checker badges, and AI assistance do not establish importance or novelty.

Trace the first substantive new steps relative to inherited source. Search equivalent formulations, exact specializations, stronger general theorems, older terminology, and bibliographies—not only matching titles. An empty search result is not a priority certificate. A related finite upper bound, irrationality proof, or transcendence theorem need not imply a claimed exact invariant.

Record source versions and attribution for inherited arguments. Distinguish code provenance from the origin of mathematical ideas: for important inherited ingredients, trace the cited exposition and bibliography, record the present modification, and mark unresolved attribution honestly. A source commit alone does not establish priority. Check licenses before reuse. Mathematical-community guidance can inform recommendations; formal venue requirements belong in the [journal-submission mode](journal-submission.md), activated only by the user's explicit formal-submission intent.

For AI-assisted work, describe the development process from available records when it bears on the publication claim: tool or model identities when known, their roles, target selection, substantive author decisions, and relevant unsuccessful attempts. Separate proof-development time and cost from checker runtime. Do not infer success rates from selected successes; leave unavailable counts or versions unknown. Use user-visible prompts, revisions, experiments, and check records while redacting private material; do not solicit or reconstruct hidden model chain of thought.

## Match the claim to the review

When discussing author or specialist review, describe what is documented and any unresolved steps. Distinguish completed understanding, explicitly pending understanding, and unknown status. Model reviews can add useful scrutiny; describe that evidence accurately without presenting it as human review, peer review, or acceptance. Missing records do not establish that human understanding is absent.

Human specialist review is optional unless explicitly requested by the user or required by an applicable submission policy for their chosen venue. Suggest it lightly when it would help; do not turn its absence into an automatic completion or publication gate, or require arranging additional review to finish an ordinary proof or manuscript audit. If a particular assurance claim depends on human review, state the evidence needed for that claim without treating the mathematical result as invalid. Stronger formal-submission guidance is in [journal submission](journal-submission.md) and applies only when the user explicitly chooses that route.

Avoid inferring misconduct from a technical mistake. When using an incident to explain risk, distinguish a genuine soundness failure, wrong specification, overinterpretation, experimental exploit, author's correction, and unresolved critique. See the dated [case catalogue](resources-and-cases.md).

A useful conclusion says which claims are supported, which defects or evidence gaps remain, and the next check that would change the decision. Publication worthiness involves expert judgment; no automated pass can guarantee it.
