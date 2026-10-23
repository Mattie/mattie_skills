# Todo and project chiefs

Todo works on its own. Projectbot adds a project lead when the human wants help
coordinating work across agents or chats.

The chief begins responses with 👨‍💼 and stays involved in getting the project
delivered. It shapes assignments around suitable roles, reviews what comes back,
and asks for revisions when needed. Routine coordination can stay with the chief.
The point is to make useful progress without making the human manage every worker.

## Getting started

`$projectbot init` makes the current chat the chief, preserves existing Todo work,
and authorizes up to two active workers and follow-ups with them. It runs on demand.
Ask it to start or drive work when ready, including in the init request if desired.
Background follow-up needs an actual supported scheduler or completion hook.

Existing useful project chats can be adopted when authorized. Add child chiefs only
when a subproject needs its own ongoing lead. A chief of staff can read summaries
across projects and help the human decide where attention is needed.

## Records and discovery

Todo keeps local lists under `.todo/`. Optional project briefs hold the goal, chief
binding, delegation limits, and next step. Assignment metadata connects work to its
worker and result. Keep one editable home for each task and one writer per scope.

Projectbot includes a read-only Python inspector that finds the project for a
directory and returns its hierarchy, chief, and recorded assignments. It can join
supplied chat observations while keeping saved task state separate from live status.
It also resolves Git worktrees to their primary checkout's records.

Remote inspection needs execution access to the project's host or an authorized
helper. Local skill installation doesn't establish that connection. See the
[inspection reference](../skills/projectbot/references/inspection.md) for the API.

## Distribution and checks

[Todo](../skills/todo/SKILL.md) can be distributed independently.
[Projectbot](../skills/projectbot/SKILL.md) requires Todo beside it.
Neither skill installs a service or starts background work by being installed.

The inspector tests cover hierarchy selection, worktrees, incomplete chat evidence,
invalid records, and read-only behavior:

```console
python -B -m unittest discover -s tests/project-management
```

Pilot the workflow on a real project before adding more machinery. Check an existing
chat, a new worker, result review, and sleep/resume. Wake delivery and chief recovery
need live testing in the chosen harness. Add storage or scheduling infrastructure
when experience shows a concrete need.
