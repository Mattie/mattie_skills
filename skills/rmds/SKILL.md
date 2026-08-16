---
name: rmds
description: Create or revise a project's public README as a ReadMe Desired State only when explicitly invoked as `$rmds`. Express requested features or bug fixes as if they already exist. When explicitly invoked as `$rmds clarify`, use the latest private RMDV advice to make the smallest useful desired-state clarification. Normal RMDS never reads `.rmdd/`. Do not invoke for ordinary README work, planning, or mentions of desired state.
---

# ReadMe Desired State

Run this workflow only when the user explicitly invokes `$rmds`.

Treat the user's desired behavior and the current public README as product intent. The finished
README must read like current documentation from a world where the requested work is complete. It
is the document that ReadMe Driven Development can later reconcile with the implementation.

## Choose the mode

### Normal mode

Use normal mode for `$rmds` and every explicit invocation that does not say `clarify`.

- Never enumerate, search, or read any part of `.rmdd/`.
- Treat prior RMDD or RMDV reports in conversation as non-authoritative implementation context.
- Incorporate an earlier report only when the user explicitly adopts its substance as desired
  behavior.

### Clarify mode

Use clarify mode only when the user explicitly invokes `$rmds clarify`.

1. Find the project root. Use the Git work-tree root when available; otherwise use the nearest
   ancestor containing `README.md`.
2. Read the complete current root README.
3. Select exactly one review source. When the user names an older review, resolve that reference
   directly and do not read `.rmdd/rmdv/latest`. Otherwise, read `.rmdd/rmdv/latest`. Treat the
   selected `<run-id>/<review-number>.md` value as relative to `.rmdd/rmdv/`, canonically resolve it
   strictly within that directory, and reject absolute paths, project-root-relative prefixes,
   traversal, symlink, or junction escapes.
4. Never enumerate, search, or read `.rmdd/rmdd/`.
5. Treat the RMDV review as advice about clarity, not as product intent or implementation
   authority.
6. Apply only advice that still fits the current README and the user's original desired outcome.

When no readable review exists, report that clarify mode has no RMDV advice to use and leave the
README unchanged. When the review refers to an older README, inspect the current wording and apply
only advice that remains relevant.

Clarify product behavior, defaults, boundaries, examples, or limitations where readers need them.
Do not rewrite the desired future to excuse unfinished code. If RMDV found implementation work and
no documentation ambiguity, leave the README unchanged and say that RMDD should continue the
implementation.

## Understand the request and project

1. Find the project root and read its agent instructions.
2. Read the complete root README.
3. In normal mode, inspect current Git changes when Git is available. Outside Git, work from the
   current document without requiring history.
4. Read nearby project files or linked local documentation only when they help preserve established
   names, commands, behavior, or context.
5. Build an internal requirements inventory from the user's request. Preserve every behavior,
   constraint, exception, example, uncertainty, and protected literal that belongs in public
   documentation.
6. Identify current README statements that the desired state changes or makes obsolete.

When no README exists, normal mode may create one that fits the project. Clarify mode requires an
existing README and review.

## Write the desired state

Edit the README directly. Keep the work documentation-only unless the user explicitly asks for
another artifact.

- Describe requested behavior as available now. Prefer present tense.
- Avoid roadmap language such as "will," "planned," "proposed," "TODO," or "once implemented."
- Do not mention RMDS, RMDD, RMDV, the prompt, run status, or implementation progress in the
  README.
- Preserve useful structure, voice, examples, badges, links, and terminology.
- Make the smallest coherent change that lets the document read naturally as a whole.
- Replace or remove claims that contradict the desired state. Leave unrelated content alone.
- Include concrete commands, examples, configuration, and limitations when readers need them.
- Do not invent unsupported guarantees, measurements, compatibility claims, or internal details.
- Prefer revising an existing passage over adding a new section solely to hold clarification.

The result must look like a real public README, not a specification or progress report. Do not add
requirement IDs, acceptance checklists, implementation plans, status markers, or custom syntax.

## Place features naturally

Work behavior into the sections where a finished project would explain it: overview, features,
quick start, usage, configuration, examples, or limitations. Explain enough observable behavior
for a reader to understand and use it. Keep internal architecture and task breakdowns out unless
they already serve the README's public purpose.

## Describe bug fixes as resolved

Update the README's main behavior descriptions so corrected behavior is the current truth. Use a
changelog entry only when the README already has that convention or the resolution deserves public
history. Keep user-visible outcomes and omit debugging history.

## Review the complete README

Before finishing:

1. Re-read the complete README as a new visitor.
2. Confirm the requested product state is clear, usable, and consistent.
3. Compare the result with the requirements inventory or the still-relevant clarify advice.
4. Confirm the edit introduced no unsupported claims and no accidental code changes.
5. Inspect the final documentation diff when Git is available; otherwise compare the final README
   with the starting content.

Report the README created or changed, summarize how desired state was expressed, and identify any
ambiguity that could not be represented accurately. Keep implementation progress out of the
README.
