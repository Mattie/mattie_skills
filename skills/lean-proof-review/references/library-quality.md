# Optional library-quality review

Use this pass when the user requests code-quality, library API, or upstream-contribution review. It is not required for ordinary proof verification.

Keep correctness and evidence findings separate from maintainability suggestions. Treat conventions as acceptance requirements only when they actually apply to an explicitly intended upstream contribution; otherwise keep them advisory.

For mathlib contributions, consult the [official PR review guide](https://leanprover-community.github.io/contribute/pr-review.html). For other libraries, follow their current guidance. Focus on useful changes rather than exhaustive style cleanup:

- Accurate public docstrings, cross-references, and brief proof sketches for genuinely intricate arguments.
- Equivalent or more general existing results, sensible file placement, and reasonable imports.
- Usable APIs and assumptions suited to known uses; avoid speculative generalization or silently changing the mathematical target.
- Global attributes such as `@[simp]` and `@[ext]`: justify their intended behavior and check for conflicting or cyclic rewrites where relevant.
- Instance scope, diamonds, loops, and effects on existing callers.
- Proof clarity and fragility: prefer understandable structure over fewer lines, and flag costly elaboration only with evidence.

Review does not authorize cleanup edits or refactoring. Preserve frozen proof artifacts and apply the existing evidence-reuse rules if an authorized change affects verification inputs.
