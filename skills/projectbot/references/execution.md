# Assigning work and following through

Choose the tool that fits the assignment. A subagent works well for a focused task
that returns during this run. A persistent project chat helps when work needs to
continue later or the human may want to join it. Reuse an existing chat when its
context is useful, after checking what it is already doing.

Use the human's existing authorization and the tools available in this session.
If messaging a particular chat needs permission we don't have, prepare the useful
assignment before asking. A worker's reply cannot grant additional authority.

## Give workers enough to succeed

A useful assignment explains the role, desired result, relevant context, and
acceptance criteria. Include the workspace, task ID, constraints, and dependencies
where they matter. Say who will integrate the result. Ask workers to return their
work, what they checked, and anything still unresolved.

Write this as a clear request. It doesn't need a form with every field filled in.
Workers can return through their normal result channel; they don't need permission
to message the chief separately for their result to count.

Keep the project's concurrency limit across all its workers, including work already
underway. For child chiefs, agree who coordinates shared capacity. Avoid concurrent
edits to the same files by sequencing work or using suitable isolated workspaces.
Any chat the human asks to do Todo work can update its assignment directly;
reread shared records before editing and preserve other changes.

Record assignments before launch and save the returned worker identity afterward.
If a launch has an uncertain outcome, inspect it before trying again. See Todo's
record reference for the small amount of metadata that makes this recoverable.

## Review and continue

Check the returned work against the requested result. Give concrete feedback and
keep useful worker context for revisions. Update Todo when the result is accepted,
including integration when the task requires it. New ideas can go into the queue
without silently enlarging the current assignment.

Continue as far as the human's request and limits support. If progress depends on
something unavailable, leave a clear next step instead of repeatedly checking the
same unchanged state.

## Follow-up between runs

On-demand work needs no scheduler. For requested background follow-up, use a
supported scheduler or completion hook and record how it runs and how to stop it.
Reuse an existing mechanism when appropriate. A skill alone doesn't wake a chat.

Every later run reads the saved project state before doing more work. Sleeping or
cancelled projects stay stopped when late results arrive. Disable scheduled wakes
and request safe worker stops when asked; report anything still running or unknown.

Capabilities differ across hosts and harnesses. Reading a chat doesn't prove we
can message it, and local installation doesn't establish remote access. When a
capability is missing, use a supported handoff or explain the resulting limitation.
