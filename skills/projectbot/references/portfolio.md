# Chief-of-staff view

The human and their Dot can inspect any individual work. The project chief owns
the routine accounting for its project and subprojects. A chief of staff helps
allocate attention across projects without taking over every work conversation.

## Find the project and keep context bounded

Use the harness's supported project/thread listing and explicit known project
bindings. MStatus can help locate a project when available. Match stable project
and host IDs, not just titles; title matches alone are ambiguous across machines.
Do not crawl every repository or load every chat to answer a portfolio question.

For a known directory, use [inspection.md](inspection.md). The inspector returns
the saved project tree even when its chief is unavailable, and can join dated
chat observations. Remote callers need an execution path to the directory's host;
the skill's local installation alone does not provide one.

For each relevant project, ask for or read a compact chief summary containing:

- project identity, lifecycle, human priority, chief binding;
- observed-at time and inaccessible or stale evidence;
- the outcome and recently accepted deliverables;
- active attempts, ready work, and the next useful action;
- blockers or decisions requiring attention;
- external dependencies and follow-up mode.

Start with the projects the human named. For an overall view, list known projects
and prioritize active projects and decision needs, marking uninspected projects as
such. Use summaries already available through authorized read access before asking
a chief to refresh. Messages to chiefs require the same authorization as other
cross-thread messages. An unavailable chief can be replaced from its durable
records once ownership is safely handed over.

An optional local directory of project IDs, control paths, and chief bindings is
a locator cache only. Add it only if the harness cannot supply discovery. Do not
duplicate task state or require the human to keep a second catalog current.

## Direction and dependencies

Translate the human's request into a bounded directive for the responsible chief:
requested outcome, priority change, lifecycle change, or explicit delegation budget.
Preserve the human's words and provenance. A read-only status question authorizes
no new workers. Existing human authorization need not be reconfirmed.

If the human asks to sleep or kill a project while its chief cannot be reached,
record the direction through the canonical writer when accessible and report
whether it is applied or still pending. Do not say it is stopped based only on
having queued a message. Maintain visibility of running/unknown attempts.

For an external dependency, the consuming chief records the producing project,
required item or artifact, acceptance condition/version, and last verified status.
The producer owns its work; the consumer owns the wait. Share only the required
interface, artifact, and deadline. Do not import the other project's backlog or
silently reprioritize it. Cross-project priority conflicts belong to the human
or an explicitly authorized chief of staff. Surface dependency cycles instead of
letting projects wait on each other indefinitely.

## Optional MStatus integration

Use MStatus as an index and evidence destination under its own installed policy.
The Todo records remain the local execution ledger. Emit a sanitized receipt
after a meaningful deliverable, decision, blocker, or next-step change; do not
mirror transcripts or send a receipt for every polling cycle.

Agent proposals must not overwrite human-owned MStatus titles, hierarchy,
lifecycle, or archive choices. A Todo lifecycle change can be reported or proposed
there without pretending it was applied. If local policy keeps MStatus in a
manual-refresh pilot, preserve that mode and its explicit approval requirements
for hooks or prepared automation.
This integration is optional; an absent MStatus installation must not block work.
