# Project records

Use these records when coordinating assignments or when a project already uses
them. Ordinary Todo lists need no setup. Without an assigned chief, the agent
handling the Todo request can maintain the records and do the work itself.

## Where things live

```text
.todo/
  features.md
  tasks.md
  projects/
    PROJECT.md
    search/
      PROJECT.md
      tasks.md
```

Root lists keep their existing location. Optional subprojects keep lists beside
their own brief. Subproject directories are siblings under `projects/`; parent IDs
express deeper relationships. Add a subproject when it helps manage real work.

Keep one editable home for each task. `.todo/` stays ignored by Git, so workers in
other worktrees or hosts need the canonical control path or a way to return results
to its writer. Ignored files aren't a backup or a synchronization mechanism.

## Project brief

Use Markdown with YAML frontmatter so the inspector can find the project and chief:

```markdown
---
id: atlas
parent: null
state: active
priority: 1
control_root: D:/Dev/atlas/.todo
chief: {harness: codex, host: local, thread: observed-thread-id}
updated_at: 2026-10-16T18:00:00Z
---
# Atlas

## Outcome and scope
Deliver useful search in src/search. Done means the agreed search scenarios pass
in the target branch.

## Mandate
Source: human instruction in <thread/message reference>, <date>.
May create workers and follow up with them; up to two active across this project.
Work on demand within the requested scope.

## Next outcomes
Search tolerates spelling mistakes.

## Dependencies
None known.

## Follow-up
On demand.
```

Keep IDs stable. Use `chief: null` without a known binding. A child has its own ID
and a parent ID; its authority and lifecycle remain subject to the parent's limits.
Optional `source_paths` map source directories to subprojects for inspection.

The prose should capture the goal, actual delegation authority, important limits,
and next step. Adapt the headings to the project. Record any configured follow-up
mechanism and how to stop it. Preserve existing authorization rather than asking
for it on every invocation.

## Assignments on Todo items

Keep the normal Open and Completed sections and the user's wording. Add metadata
when coordination needs it. Unannotated open items are queued.

```markdown
## Open

- [ ] Search should tolerate spelling mistakes.
  - id: atlas-search-01
  - state: active
  - accepts: Misspelled queries find the agreed fixture results.
  - depends_on: []
  - attempt: atlas-search-01-a1
  - worker: codex / local / observed-thread-id
  - dispatch: confirmed
  - observed_at: 2026-10-16T18:05:00Z

## Completed
```

Use single-line YAML values for metadata. An item needs a unique, stable ID before
it is delegated or referenced as a dependency. List order supplies the default
priority. Add artifact links, blockers, or other fields only when useful.

States are `queued`, `active`, `review`, `blocked`, `paused`, `cancelled`, and `done`.
Use `review` while checking a returned result. Check and move accepted work to
Completed with its resolution evidence. Keep cancelled work unchecked with a reason;
it wasn't delivered. Todo's verified-obsolete completion rule still applies.

Before launching a worker, save its attempt with `dispatch: pending`; save the
observed binding and `dispatch: confirmed` after launch. An ambiguous launch stays
`dispatch: unknown` and occupies capacity until checked. On retry, retain the item
ID and create a new attempt ID. Accept results for the current attempt once; retain
older results as useful evidence without letting them overwrite current ownership.

## Ownership and resuming work

Any chat may do Todo work the human requests and update the corresponding shared
records, including when a chief is assigned. The chief coordinates the project;
it does not have exclusive editing rights. Record this chat's assignment directly
and proceed without routing the request through the chief. A worker delegated a
specific assignment can still return its results through the agreed channel.

Reread before editing and preserve other changes. Check whether the item is already
being worked on; an actual conflicting assignment needs coordination. A chief
binding or the possibility of concurrent edits is not itself a reason to stop.

Doing a Todo item does not replace the chief. A replacement chief reads the saved brief and assignments, checks ongoing work,
and establishes the handoff before taking ownership. An inaccessible chat is unknown,
not evidence that its work stopped.

## Project lifecycle

- `active`: work may proceed within the human's instructions.
- `sleeping`: hold new work until resumed.
- `cancelled`: stop future work and preserve existing artifacts.
- `completed`: the project outcome has been accepted.

Sleep and cancellation apply to descendants. Save that state before disabling wakes
or requesting worker stops, and report what actually stopped. Late results can be
reviewed without restarting the project. Resuming a parent preserves a child's own
pause or cancellation. Reopening cancelled work requires human direction.

Priorities usually change what starts next. Avoid interrupting useful work unless
asked or its result is no longer wanted. Report progress through delivered outcomes,
current work, and blockers; task counts alone don't measure project completion.
