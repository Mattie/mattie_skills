---
name: write-plainly
description: Write, rewrite, or review prose in plain language for its intended reader while preserving technical meaning, constraints, uncertainty, and protected literals. Use when the user asks for plain language or plain English, audience-appropriate clarity, an easier-to-understand explanation, or a meaning-preserving simplification of technical prose. When one of those triggers applies, use for public information, documentation, instructions, explanations, notices, and interface text. Do not invoke solely for proofreading, shortening, generic copyediting, humanizing prose, removing AI tells, marketing voice, or creative rewriting. When the user explicitly requests ASD-STE100, STE, or invokes $write-simplified-technical-english, use that skill instead.
---

# Write Plainly

Make prose easy for its intended reader to find, understand, and use. Preserve
meaning before improving style.

## Establish the task

1. Identify whether the user wants `WRITE`, `REWRITE`, or `REVIEW`.
2. Identify the intended reader, what they already know, why they need the
   content, and what they should understand or do next.
3. Infer the reader from the request and surrounding context. Ask only when
   different plausible readers would require materially different content.
4. Keep the requested language variety, voice, format, and level of formality
   unless they prevent the intended reader from using the content.

## Apply the requested operation

- For `WRITE`, turn the prompt and supplied sources into a requirements
  inventory before drafting. Include every fact, constraint, qualification,
  and requested action.
- For `REWRITE`, read the complete source, build the preservation inventory,
  rewrite it, and compare the result with the source.
- For `REVIEW`, identify the most important obstacles to finding,
  understanding, or using the content. Return prioritized findings and
  concrete corrections. Provide a complete rewrite only when requested.

## Start from the reader

- Put the answer, decision, conclusion, or required action first when the
  content supports one. Follow it with necessary detail and then background.
- Organize information around the reader's task. Keep prerequisites and
  conditions close to the actions they control.
- Give each sentence a clear job. Combine related ideas when their relationship
  matters to accuracy.
- Keep one main topic in each paragraph.
- Prefer concrete verbs and familiar words when they carry the same meaning.
- Keep necessary domain terms. Define a term at first use when the intended
  reader is unlikely to know it.
- Name the actor when the actor matters and is known. Keep passive voice when
  the actor is unknown, irrelevant, obvious, or intentionally withheld.
- Address the reader directly when that relationship is accurate. Do not
  invent a `you`, `we`, or responsible actor.
- Use `must` for requirements, `must not` for prohibitions, `may` for
  permission, and `should` for recommendations when those meanings match the
  source.
- Use headings, lists, steps, and tables when they make real groupings,
  sequences, conditions, or comparisons easier to scan.
- Prefer concise sentences while varying their length when precision or flow
  benefits. Apply no universal word or sentence-length cap.

## Preserve technical meaning

Before drafting from requirements or changing existing text, create an
internal preservation inventory containing every applicable item:

- Facts, claims, evidence, examples, citations, and source attribution.
- Requirements, prohibitions, permissions, recommendations, and their scope.
- Actors, objects, ownership, preconditions, dependencies, sequences, states,
  failures, outcomes, and cause-and-effect relationships.
- Uncertainty, confidence, estimates, assumptions, warnings, caveats,
  limitations, exceptions, and alternatives.
- Identifiers, API names, interface labels, commands, code, configuration,
  paths, links, version numbers, measurements, units, formulas, and quoted
  text.
- Established terminology, meaningful distinctions, language variety, author
  voice, and deliberate formatting.

Use the inventory as a semantic lock:

- Preserve the strength, scope, polarity, and uncertainty of every statement.
  Do not turn `may` into `will`, `should` into `must`, or a possibility into a
  fact.
- Preserve conditions, exceptions, and causal relationships with the claims
  and actions they govern.
- Keep protected literals exact unless the user explicitly requests a change.
- Keep direct quotations exact and distinguish quotation from paraphrase.
- Retain necessary technical terms and meaningful distinctions. Explain them
  through nearby context when the reader needs help.
- Add no unsupported fact, example, measurement, source, motive, causal claim,
  certainty, or promise.
- Resolve no source ambiguity silently. Ask when it blocks an accurate result;
  otherwise preserve or flag it in the requested deliverable.

## Check the final result

Compare the complete result with the requirements or source inventory:

1. Confirm that every required fact, constraint, warning, caveat, exception,
   identifier, protected literal, quotation, citation, and source attribution
   remains.
2. Confirm that modality, uncertainty, scope, conditions, sequence, and causal
   meaning have the same strength.
3. Confirm that the result introduces no unsupported claim or implication.
4. Confirm that the intended reader can find the main answer or action quickly.
5. Confirm that necessary technical terms remain and receive only the
   explanation the reader needs.
6. Confirm that actors, responsibilities, and next steps are clear where the
   source establishes them.

When a plain-language preference conflicts with accuracy, keep the accurate
wording. Briefly identify the constraint only when it prevents the requested
result or the user asks for an explanation.

## Return the result

- For `WRITE` and `REWRITE`, return only the requested content unless the user
  asks for rationale, alternatives, or a change summary.
- For `REVIEW`, return the prioritized findings and requested corrections.
- State a blocker when missing context prevents an accurate result.
- Do not claim a readability grade, plain-language certification, or
  ASD-STE100 compliance.
