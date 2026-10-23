# Project-management extension

Read this only for project-management requests or assignment-aware work on an
already managed item. Ordinary lists need no migration. The agent maintains the
records; the human should be able to speak in outcomes and priorities.

Projectbot is optional, including when using these project records. With no chief
assigned to a scope (directly or through its parent), the agent handling the user's
Todo request maintains the applicable records and does the requested work. A
project record, `chief: null`, or an installed Projectbot skill does not require
appointing a chief. Still honor existing assignments, dependencies, and lifecycle.

## One home for each fact

Use the existing repository `.todo/` as the default control directory:

```text
.todo/
  features.md                    # Existing root lists, unchanged
  tasks.md
  projects/
    PROJECT.md                   # Root project brief and chief binding
    search/
      PROJECT.md                 # Optional subproject brief
      tasks.md                   # Work owned by this subproject
```

The root's lists stay directly in `.todo/`. Each subproject's lists live beside
its `PROJECT.md`. Keep subprojects as sibling directories under `projects/`,
with an explicit parent ID for deeper hierarchies. The directory describes an
ownership scope, not necessarily a source-code folder. Record source paths in
the brief. Use lowercase directory slugs and stable IDs that survive renaming.
Never create a subproject merely because a source directory exists.

The project brief owns intent, lifecycle, priority, chief identity, and delegation
authority. Todo items own task state, assignments, and acceptance evidence. Chat
status is execution evidence, not the task's outcome. A status summary is derived
and carries an observation time; it never becomes a second task list.

Create only the files needed by the current request. Keep `.todo/` ignored as in
the base skill. Local ignored files do not supply backup, cross-host sync, or
shared state between Git worktrees. Record one absolute control-directory path
in the brief and every worker packet; worktrees must not initialize competing
copies. If another host cannot reach it, return a result packet to its chief.
Do not silently copy state or claim it is synchronized. A user-selected durable
store can replace this path later; preserve IDs and ownership on migration.

## Project brief

Use Markdown with YAML frontmatter for the few fields agents must reconcile.
This is an illustrative active project, not authorization to start one:

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
Deliver usable search. Own src/search and its integration tests.
Done means the agreed search acceptance scenarios pass in the target branch.

## Mandate
Source: human instruction in <thread/message reference>, <date>.
May create worker threads in this project and follow up with those workers.
May inspect existing project chats; messaging pre-existing chats needs the
human's authorization unless already included in this mandate.
Maximum two concurrent worker attempts across this project and its children.
Run on request; dispatch at most one wave per invocation. No scheduled wake.
Stop dispatching when sleeping, cancelled, out of capacity, or lacking ready work.

## Next outcomes
1. Search returns useful results.
2. Search stays responsive on the agreed dataset.

## Dependencies
None known.

## Follow-up
On demand. No automatic follow-up is configured.
```

Use `chief: null` when there is no observed binding; never invent thread IDs.
A subproject has its own stable ID, parent ID, bounded scope, and optional chief.
It inherits ancestor restrictions; child authority cannot expand them. Check
parents for effective lifecycle and dispatch limits. Reject parent cycles.

Capture the user's actual delegation mandate, including permitted thread creation,
which existing chats may receive messages, scope, capacity, and any run/time/spend
limits they set. Preserve prior authorization instead of asking every time.
If no standing mandate exists, a status request is observation only; a request
to plan or queue work allows local tracking updates. A request to drive work
allows the requested work, with dispatch only through available, authorized tools.
Suggested initial capacity is two workers with on-demand runs; it is a convention,
not permission for unlimited spending or perpetual execution.

## Managed Todo items

Preserve the two sections, checkboxes, original wording, and completion notes.
Add metadata only when the item needs coordination. Existing unannotated items
are queued; they need an ID before delegation or dependency links.

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

An item ID is unique within the root project tree and never reused. For outside
dependencies, qualify it with the external project ID and locator. On retries,
keep the item ID and create a new attempt ID. Add fields such as priority,
artifact, blocker, or last accepted result only when useful. List order is the
default priority. Avoid mirroring the entire conversation in metadata.

| State | Meaning |
| --- | --- |
| queued | Available when acceptance, dependencies, authority, and capacity permit |
| active | A worker is assigned; includes dispatch with an uncertain outcome |
| review | Result returned; acceptance or integration is still being checked |
| blocked | Needs a named dependency, decision, or capability |
| paused | Work was deliberately suspended |
| cancelled | No longer wanted; retain unchecked with reason and date |
| done | Accepted; checked and moved to Completed with resolution evidence |

Do not put cancelled work under Completed or count it as delivered. Obsolete
work may follow Todo's verified-obsolete completion rule, with that outcome
distinguished from delivery. Reopening accepted work preserves its ID and prior
resolution evidence. Moving an item to a subproject moves its full entry; do not
leave a second editable copy. Use a link if the parent needs a pointer.

Before dispatch, record an active attempt with `dispatch: pending`. Persist the
observed worker identity and `dispatch: confirmed` after success. If the outcome
is ambiguous, use `dispatch: unknown`, keep the capacity reserved, and inspect
the harness before retrying. An idle, missing, or inaccessible chat does not prove
the attempt stopped. Repeated identical results for the same attempt must not
close work twice or schedule duplicate follow-ups. Accept a result only for the
current attempt; retain useful older results as evidence without changing ownership.

## Ownership and recovery

When a chief is assigned, that chief writes the scope's project brief and managed
lists. Without an assigned chief, the agent handling the Todo request can be the
writer; ordinary Todo use does not need a persistent chief binding. Serialize
edits and check for existing work in either case. Under a chief, delegated workers
return results rather than rewriting shared lists. A root chief may cover children
without child chiefs. When a child chief exists, the root requests changes through
the authorized channel rather than concurrently editing that child's records.
Direct human edits are authoritative: reread before updates and resolve conflicts
without overwriting them. A new Todo request in a worker chat returns a proposed
tracking change to the chief when it cannot safely serialize the edit.

This is a single-writer convention, not a distributed lock. If two chiefs or
hosts may be running, do not take over based on elapsed time. Verify the previous
writer has stopped or use a real serialized coordinator. A replacement chief
reads the brief, open work and attempt bindings, checks the associated threads,
then rebinds ownership. Missing evidence stays unknown, not queued or completed.

## Lifecycle and status

- **active:** eligible for authorized dispatch.
- **sleeping:** no new dispatch in this scope or descendants. Record a wake
  condition, or "until asked". A wake date alone does not schedule anything.
- **cancelled:** no new dispatch; preserve unfinished work and artifacts. Reopening
  requires explicit human direction. Killing a project means cancellation, not
  deleting files, branches, threads, or remote resources.
- **completed:** the project outcome has been accepted, including required
  integration. Empty queues or stopped chats alone are insufficient.

For sleep or cancel, persist the lifecycle first, then pause relevant scheduled
wakes and request that running workers stop safely when tools and authority allow.
Report each running attempt as stopped, still running, or unknown. Archiving a
thread is not proof of cancellation. Late results may be recorded and reviewed,
but must never resume the project or launch successors by themselves. Resuming
a parent does not clear a child's own sleeping or cancelled state.

Reprioritization changes future selection. Avoid interrupting useful in-flight
work unless the human asks or its outcome is no longer useful.

Report progress against outcomes: delivered evidence, active attempts, ready
queue, blockers, next action, and last observation time. Distinguish requested,
queued, started, returned, accepted, and integrated. Counts are useful; a percentage
of arbitrary tasks is not an overall project completion estimate. On a read-only
status request, report discrepancies without silently adopting chats or dispatching.
