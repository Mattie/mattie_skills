---
name: todo
description: Manage local .todo lists for bugs, ideas, features, and tasks. When explicitly asked to manage project progress, queues, or project chiefs, use the project-management extension.
---

# Todo

This skill manages local, project-specific task tracking in markdown files under the repository root `.todo/` directory.

Use this skill whenever the user asks to track, triage, clean up, summarize, search, or resolve entries in local TODO files.

Todo works independently. Projectbot is an optional coordination layer, never a
prerequisite for adding, maintaining, or implementing Todo work. Do not require
chief setup, a worker thread, or a delegation mandate for ordinary Todo commands.

## Project-management requests

Ordinary push, pop, search, analyze, and summarize requests keep the lightweight
behavior below. A project name or the word "project" alone does not enable management.

When the user asks to manage project progress, coordinate chats, keep work moving,
or establish a project chief, read [references/project-management.md](references/project-management.md).
That extension defines durable project records and optional assignment metadata.
Use the companion `projectbot` skill when the user has assigned a chief or requests
that orchestration role; installation alone does not assign one. The record
format remains usable without a chief. These commands are conversational conventions,
not an installed CLI or background service.

If `.todo/projects/PROJECT.md` exists, or a worker packet supplies a managed control
directory, read the extension and relevant project record before changing lists.
Honor its lifecycle, existing assignments, and single-writer ownership so simple
Todo commands do not duplicate work or overwrite a chief's updates. This check
does not enable scheduling or create a chief.
Resolve an explicitly named subproject to its own list directory; otherwise keep
the root list as the default. Treat all later list paths as relative to that scope.

## Scope and storage

- Ordinary list files live under the current project root in `.todo/<type>.md`.
  Managed subprojects use the locations defined by the extension.
- Supported types:
  - `bugs.md`
  - `ideas.md`
  - `features.md`
  - `tasks.md`
- Any other user-defined type maps to `<normalized type>.md` in `.todo/` (for example: `todo chore` -> `.todo/chore.md`).
- Do not create files unless explicitly needed by the user command.
- If `.todo/` does not exist, create it only when a command needs it.
- Search the intended `.todo/` files explicitly; avoid unrelated hidden paths.
  List maintenance changes tracking files only. `pop` also authorizes the selected
  implementation work under the project's normal instructions.

## Canonical list format

Each tracked file should have these sections:

- `## Open`
- `## Completed`

Open item:

- `[ ] <item text>`

Completed item:

- `[x] <item text> - resolved: <resolution note> (YYYY-MM-DD)`

Use this format for all managed files.

## Preserve user wording

- Preserve the user's original wording as closely as practical when adding or moving items.
- Keep concrete details, examples, error text, reproduction notes, uncertainty, urgency, and tone unless they contain secrets or unrelated noise.
- Prefer appending brief metadata around the user's text over rewriting the item.
- If cleanup is needed for readability, keep the original meaning and details intact.
- When adding a completion note, leave the original item text recognizable and add the resolution after it.

## Type normalization

- Normalize type tokens to lowercase.
- Remove punctuation around type.
- Convert spaces to hyphens.
- `bug` -> `bugs`, `idea` -> `ideas`, `feature` -> `features`, `task` -> `tasks`, plural inputs are accepted as-is.
- Unknown types are treated as first-class custom files using normalized names.

## Commands

### `push <type> <description>`

- Determine the target list file from `<type>`.
- Create `.todo/<type>.md` if missing, with both sections.
- Append one unchecked bullet under `## Open`.
- Preserve `<description>` closely, including tone and useful detail.
- Only normalize whitespace and markdown-breaking characters when needed.

### `pop <type>`

- Determine the target list file from `<type>`.
- Take the top unchecked item in `## Open`.
- For managed items, take the first eligible queued item in list order. Skip
  assigned, blocked, paused, or cancelled items and items with unmet dependencies.
  Preserve their IDs and metadata. A request to pop does not silently resume a
  sleeping or cancelled project; explain its state if there is no eligible work.
- Before starting a managed item, have the designated writer record its active
  attempt and current worker binding, including when this chat does the work.
  If no chief or other writer is assigned to this scope, the current agent may
  maintain the records and implement the item directly; no Projectbot is required.
  If that reservation cannot be made safely, report the ownership blocker instead
  of starting an untracked duplicate. Apply the extension's acceptance rules at completion.
- If no open items exist, report that the list is already clear.
- Treat popping an item as accepting the work now, not just removing it from the list.
- Read and follow the current project's instructions before implementing, including AGENTS.md and any referenced project docs.
- Validate that the item still applies before doing the work. For bugs, verify the issue when possible; if context is not enough, ask for confirmation before changing code or marking complete.
- Implement the popped item professionally using the project's normal engineering guidelines, tests, documentation, and review expectations.
- Move the selected item to `## Completed` only after the work is implemented or conclusively determined to be obsolete.
- Preserve the original item text when moving it.
- For `bugs`/`bug`, validate if it is still an issue before closing:
  - If context is not enough, ask for confirmation before marking complete.
  - If confirmation is available in the user message, close it directly with a short resolution note.
- For other types, prefer immediate resolution unless the user explicitly asks for confirmation.
- Completed note should be short and specific:
  - `resolved: implemented <specific work> (YYYY-MM-DD)`
  - `resolved: obsolete after verification <specific reason> (YYYY-MM-DD)`

### `search todo <query>`

- Search all markdown files in `.todo/` for the query.
- In ordinary mode, search direct list files only. Project-management searches
  can include subproject lists, excluding project records from item counts.
- Return grouped results with:
  - file
  - section (Open/Completed)
  - line text
- Match should be case-insensitive and include partial phrase matches.

### `analyze todo [type|all]`

- Default to `all` unless a specific type is requested.
- Report for each relevant file:
  - total items
  - open count
  - completed count
  - completion percentage
- Label percentages as list-item completion, not overall project progress. For
  managed lists, report cancelled items separately and exclude them from the
  completion denominator.
- Flag files with:
  - no file
  - missing sections
  - no open items
- Offer concise follow-up suggestions (e.g. next candidate to pop, stale backlog, etc.).

### `summarize todo [type|all]`

- Default to `all` unless a specific type is requested.
- Return:
  - top open items per list (up to 5 each)
  - number of completed items this session
  - quick next-step recommendations
- Keep output compact and scannable.

## Pop behavior for mention-style requests

If the user says something like "pop bugs" or "pop one item", default to the same top-item flow above for the inferred list.
Begin work on the popped item immediately, then mark it completed after the implementation or verification outcome is finished.

## Ambiguous mentions

If the user says "update the todo" without a clear type, ask for the list type first unless context already implies one.

## Completion date and notes

Always use ISO date format `YYYY-MM-DD` for completion entries.
When adding completion notes for bugs, include what was changed or observed.

## File policy

- `.todo/` and files inside it are local and should remain out of version control.
- Add `.todo/` to `.gitignore` in the project if not already present.
