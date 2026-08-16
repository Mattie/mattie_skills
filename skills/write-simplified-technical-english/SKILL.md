---
name: write-simplified-technical-english
description: Write, rewrite, or review technical content with ASD-STE100 Simplified Technical English (STE), Issue 9. Use only when the user explicitly invokes $write-simplified-technical-english. Common requests mention ASD-STE100, STE, or "write STE"; do not use for general requests for clear, simple, concise, or technical writing.
---

# Write Simplified Technical English

Apply ASD-STE100 Issue 9 to the user content.

## Load the working reference

Before you use this skill, fully read the guide listed below.

Do not read the guide again when both conditions are true:

- You fully read the guide.
- The full guide stays in the active context.

Read [references/STE_AGENT_GUIDE.md](references/STE_AGENT_GUIDE.md).

Use the guide as the primary working authority.

For an exact rule or dictionary lookup, use an official copy of ASD-STE100
Issue 9. See
[references/ASD-STE100.md](references/ASD-STE100.md)
for the official source and important usage limits.

Read the complete rule or dictionary entry, including its help, examples, page
continuation, and supplemental material.

Read all 434 pages only when the user requests a full-standard review and an
official copy is available.

## Apply the standard

1. Identify the source as procedural text, descriptive text, or text with both
   types.
2. Keep technical facts, safety meaning, identifiers, interface labels, code,
   commands, measurements, and necessary terminology.
3. Apply all applicable writing rules in Part 1.
4. Use Part 2 to examine each word's meaning and part of speech.
5. Use each approved word only with its approved meaning and part of speech.
6. Use a permitted technical noun or technical verb only in an approved
   category.
7. Use one term for one concept.
8. Remove ambiguity before you make the text shorter.
9. Keep quoted material exact.
10. Clearly identify quoted non-STE text.
11. Obey project or customer rules that have more limits when the necessary
    meaning does not change.
12. If two rules do not agree, tell the user.

## Examine the result

Do the independent final compliance pass in Section 15 of the guide. This pass
is mandatory:

1. Start a fresh subagent that did not write the candidate text.
2. Use a context-free subagent when the platform supports it. Give the
   subagent only the source or requirements, the candidate text, the
   unverified candidate terminology list, and the path to the guide. Give it
   the official Issue 9 PDF when it is available.
3. Tell the subagent to do only the reviewer role in Section 15 and not to
   delegate the review.
4. Require the subagent to examine and record every word occurrence as
   specified in Section 15.
5. If the reviewer changes or recommends a change to any wording, treat the
   result as `CHANGES_REQUIRED`. Resolve each finding and send the complete
   revised candidate to a different fresh subagent.
6. Use the exact official entry when the guide does not resolve a word.

Give the result only after the last subagent pass examines the exact final text
without changing it and reports `PASS`, no unapproved ordinary word, and no
unresolved word.

Do not simulate or replace the subagent pass with a self-review. If you cannot
start an independent subagent or complete the pass, give only the incomplete
review status and its blocker. Do not include candidate text, partial rewritten
text, excerpts, or suggested wording. Do not describe the result as reviewed.

If the STE rules change necessary meaning or fixed text, give the most accurate
permitted version. Identify the exact constraint that prevents correct text.

Give only the requested content unless one of these conditions is true:

- The user wants a compliance report.
- Two rules do not agree.
- The STE rules change necessary meaning or fixed text.
