# Disposable spike

Use a small experiment when it can answer a fit question faster than further
research. Test a representative use case and report what was checked and any
limits that matter to the recommendation.

Small tests of project code, standard APIs, and already-approved dependencies
can use the existing development environment. Before running unfamiliar
third-party code, inspect the available source, install steps, provenance, and
expected behavior enough to give a best-effort safety assessment; report any
important unknowns. Run it in an isolated Docker container without exposing
host credentials or unnecessary workspace files, or get the user's approval
to try it outside the container. A temporary directory alone is not isolation.

Follow the user's existing authorization, project rules, and environment
constraints. If a necessary experiment is unavailable or outside the task's
scope, explain the gap and use the evidence available. Clean up temporary
artifacts created for the experiment.
