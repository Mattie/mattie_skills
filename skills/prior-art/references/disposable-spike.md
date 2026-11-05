# Disposable spike

Use a small experiment when it can answer a fit question faster than further
research. Test a representative use case and report what was checked and any
limits that matter to the recommendation.

Match precautions to the candidate and experiment. Small tests of project
code, standard APIs, and already-approved dependencies can use the existing
development environment. For unfamiliar executable code, inspect its source,
install steps, and expected behavior as appropriate; use a disposable
environment or stronger isolation when the concrete risks warrant it. A
temporary directory organizes files but does not itself isolate execution.
Avoid exposing private data or credentials unnecessarily.

Follow the user's existing authorization, project rules, and environment
constraints. If a necessary experiment is unavailable or outside the task's
scope, explain the gap and use the evidence available. Clean up temporary
artifacts created for the experiment.
