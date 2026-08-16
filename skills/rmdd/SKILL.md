---
name: rmdd
description: Run ReadMe Driven Development only when explicitly invoked as `$rmdd`. Make a project's code and tests match its current root README and relevant linked documentation without editing those documents. Keep private, local run receipts under `.rmdd/rmdd/` in Git and non-Git projects. Do not invoke for ordinary README reading, writing, reviewing, or discussion.
---

# ReadMe Driven Development

Use the README as the description of the product we want. Read it, inspect the project, and make
the implementation agree with it.

## Keep the boundary clear

- Treat the current root `README.md` and any local documentation it relies on as product intent.
- Leave those documents untouched. A developer may update them while the run is in progress.
- Read prior `.rmdd/rmdd/` receipts only as execution history. The current documentation wins.
- Work directly inside `.rmdd/rmdd/`. Do not list `.rmdd/` or inspect `.rmdd/rmdv/`.
- Save authored progress and the final answer. Leave tool output, private reasoning, credentials,
  and unrelated conversation out of the receipt.

The README can use ordinary prose, links, and examples. It needs no RMDD-specific syntax.

## Start a receipt

1. Find the project root. Use the Git work-tree root when Git is available. Otherwise, walk upward
   to the nearest `README.md`.
2. Read the project instructions and the complete root README.
3. Resolve `scripts/receipt.py` relative to this skill. Run it with an available Python 3
   interpreter, preferring the project's environment when it has one:

   ```text
   receipt.py start --project-root <root> --readme <root>/README.md
   ```

4. Keep the returned `run_dir` for later commands. Mirror the opening progress update with:

   ```text
   receipt.py progress --run-dir <run_dir> --message <authored update>
   ```

The helper creates the snapshots, Git evidence, local `/.rmdd/` exclusion, and starting metadata.
If it cannot create writable local state, stop before changing project files. An exclude warning is
safe to continue past; mention it in the final answer.

## Reconcile the project

Read local documentation linked by the README when it helps define observable behavior. Before
relying on one, save its starting evidence:

```text
receipt.py document --run-dir <run_dir> --path <document>
```

Compare the complete current documentation with the code and tests. Preserve compatible behavior,
implement clear additions and changes, and remove behavior the documentation withdraws. Keep shared
or ambiguous code when removal could damage something still intended.

Use reasonable judgment when the README leaves room for a safe, reversible choice. Call out the
interpretation afterward. Finish compatible work before raising a narrow blocker that needs a
consequential product decision or new authority.

Add or update tests for changed behavior and run the checks that matter for this project. Record
useful receipt details as you go:

```text
receipt.py note --run-dir <run_dir> --kind changed --text <path>
receipt.py note --run-dir <run_dir> --kind check --text <command and result>
receipt.py note --run-dir <run_dir> --kind warning --text <warning>
```

For a non-Git project, send the relevant before/after edit evidence to `receipt.py evidence` on
standard input. Mirror each later user-facing progress update with `receipt.py progress` in the
same order it appears in chat.

## Check the latest save

Run `receipt.py refresh --run-dir <run_dir>` before finishing. Re-read the root README and every
recorded intent document. If `changed_sources` is non-empty, reconsider the affected work and rerun
its checks. Keep both README snapshots when the source changed during the run, and never overwrite
or revert the developer's edit.

Inspect the final implementation diff or recorded edits. Confirm that RMDD did not change the root
README or any linked intent document.

## Talk like a teammate

Keep progress updates to one or two useful sentences. Say what you found, what you are changing,
or what needs a decision. Keep receipt mechanics in the receipt unless a failure affects the run.

Make the final answer easy to skim. Cover:

- what changed;
- anything still open and why;
- checks that ran; and
- the receipt location.

Use plain descriptions instead of a status table for every behavior. Skip hashes, pointer rules,
Git plumbing, and repeated labels when everything worked. A natural update such as "The formatter
now preserves blank lines, and its focused tests pass" carries enough information.

Compose the complete final Markdown, then pass it on standard input to:

```text
receipt.py finish --run-dir <run_dir> --status FINISHED
```

Use `FAILED` only when the run itself could not complete. A focused product blocker can remain in a
finished run. If `finish` catches a newer documentation save, reconcile it, run `refresh` again,
and rewrite the final answer. Re-read `response.md` and return that Markdown verbatim.
