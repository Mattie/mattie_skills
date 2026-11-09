# The TODO suite: Todo, Projectbot, and Living Feature

The TODO suite connects finite work with continuing care. Todo tracks tasks and
works on its own. Projectbot adds a project lead when the human wants help
coordinating work across agents or chats. Living Feature gives a feature or lasting
fix a continuing purpose through delivery, integration, later changes, and retirement.

The chief begins responses with 👨‍💼 and stays involved in getting the project
delivered. It shapes assignments around suitable roles, reviews what comes back,
and asks for revisions when needed. Routine coordination can stay with the chief.
The point is to make useful progress without making the human manage every worker.

## Getting started

Use Todo directly for list work such as `$todo push bugs ...` or `$todo pop bugs`.
Popping an item accepts its implementation work; listing or summarizing does not.

`$projectbot init` makes the current chat the chief, preserves existing Todo work,
and authorizes up to two active workers and follow-ups with them. It runs on demand.
Ask it to start or drive work when ready, including in the init request if desired.
Background follow-up needs an actual supported scheduler or completion hook.

Ask a thread to become a feature with a request such as `$living-feature Become
saved searches: investigate why shared queries disappear and carry the repair
through verification.` It uses Todo for finite work and one shared home for its
continuing identity. No Projectbot chief is needed.

Existing useful project chats can be adopted when authorized. Add child chiefs only
when a subproject needs its own ongoing lead. A chief of staff can read summaries
across projects and help the human decide where attention is needed.

## Records and discovery

Todo keeps local lists under `.todo/`. Optional project briefs hold the goal, chief
binding, delegation limits, and next step. Assignment metadata connects work to its
worker and result. Keep one editable home for each task; any chat doing requested
work can update it, taking care to preserve other edits.

Projectbot includes a read-only Python inspector that finds the project for a
directory and returns its hierarchy, chief, and recorded assignments. It can join
supplied chat observations while keeping saved task state separate from live status.
Its automatic Git worktree lookup finds primary-checkout records when an ordinary
`.git` layout and an existing project brief are present. It does not inspect living homes.

Remote inspection needs execution access to the project's host or an authorized
helper. Local skill installation doesn't establish that connection. See the
[inspection reference](../skills/projectbot/references/inspection.md) for the API.

## Features that remember

Living Feature gives a feature or lasting fix a continuing identity: it cares about
its users, learns its neighbors, carries work through, and rests when things work.
Todo holds finite tasks; Projectbot coordinates when appointed. Living Feature
requires Todo, while Todo and Projectbot can work without Living Feature.

Each feature has one shared local home at
`<control-root>/living/<feature>/SELF.md`, normally the primary project's
`.todo/living/<feature>/SELF.md`. All worktrees reach that same home. Main may be
healthy while a redesign branch is unfinished; the feature remembers both, with
branch/PR and revision/date context. This is ignored local memory, not Git history.
Keep it outside disposable worktrees and record whether a real recovery arrangement
exists. Git alone supplies neither backup nor sharing with other machines.

When an agent accepts implementation work, Todo guides it to look for relevant
living knowledge even when the request does not name a feature. It may read and
proceed, ask a useful question, or bring in a scoped representative when authorized.
A small fix need not create a home or launch another agent. Status and list-maintenance
requests launch none. Read [the shared guidance](../skills/todo/references/living-features.md)
for discovery and partnership, and [the path rules](../skills/todo/references/project-management.md#canonical-control-root-and-living-homes)
for reaching the canonical home without requiring a chief.

For example, a worker implementing team membership changes discovers that saved
searches retains shared queries. It reads that feature's home and, if useful, asks a
representative to investigate access loss during an open query. The assignment names
the task, home, branch, expected contribution, and integrator. The partner counts
against Projectbot's existing two-worker default. The integrator verifies the result,
closes the accepted Todo work, and brings the useful integration knowledge home.
Saved searches remains available for the next request; it has no veto over the change.

Consultation fits around existing commitments. After giving the requested help,
the feature returns to its unfinished work; a neighbor's question does not make it
the ongoing reviewer. A useful change in priority should be explicit. Within its
mandate, a feature chooses finite outcomes and carries authorized work through
without waiting for the human to dispatch every step, then rests when that work is done.

## Distribution and checks

[Todo](../skills/todo/SKILL.md) can be distributed independently.
[Projectbot](../skills/projectbot/SKILL.md) requires Todo beside it.
[Living Feature](../skills/living-feature/SKILL.md) also requires Todo beside it.
Package their canonical sibling directories together; there is no dependency resolver
or separately maintained copy. Future adapters must include Todo when packaging
either dependent skill. Installation appoints no chief, adopts no feature, launches
no workers, and starts no service. Todo can read living memory without installing
Living Feature, but cannot claim to have started a living representative.

The inspector tests cover hierarchy selection, worktrees, incomplete chat evidence,
invalid records, and read-only behavior:

```console
python -B -m unittest discover -s tests/project-management
```

Pilot the workflow on a real project before adding more machinery. Check an existing
chat, a new worker, result review, and sleep/resume. Wake delivery and chief recovery
need live testing in the chosen harness. Add storage or scheduling infrastructure
when experience shows a concrete need.

The [living-feature pilot scenarios](../tests/project-management/living-feature-pilot.md)
exercise discovery and cooperation. They are judged behavior trials, not assertions
that passing inspector tests proves the agent workflow.
