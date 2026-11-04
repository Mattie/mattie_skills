# Search recipes

Choose sources from the project's actual language, release channels, command names, audience, and selected depth. These are starting points, not a checklist every project must exhaust. A result is an observation made at a particular time, not a reservation.

## Local and package checks

Inspect the relevant repository manifests and documentation for the proposed package and command names. Search only useful project paths; avoid unrelated hidden or credential files. `rg -n --fixed-strings -- <name> <relevant-path>` searches literal names when ripgrep is available. On the user's machine, `Get-Command <name> -ErrorAction SilentlyContinue` on PowerShell or `command -v <name>` on a POSIX shell can reveal a local executable; a local miss says nothing about other machines. Quote or pass candidate names as literal arguments appropriate to the shell and tool.

Query the intended registry directly where possible. For example, use `cargo search` for discovery and `cargo info` or official crates.io metadata to verify an exact Rust package; npm's `view` command or its registry metadata for npm; the official PyPI JSON endpoint for Python. A registry search result can be fuzzy; check the exact namespace separately. For a CLI, inspect package metadata, manifest entry points, or the official README to establish the installed command. A package named `example-rs` may install `example`.

For a cross-ecosystem executable, npm, PyPI, crates.io, and platform package managers can be relevant even if the implementation uses only one language. Add Homebrew, WinGet, Chocolatey, Scoop, Go packages, Docker Hub, or other channels when they match the user's distribution plan. For a library with no global command, favor likely import/namespace overlap over unrelated global-binary searches.

Record the relevant package and executable separately, current official description, audience, and observed activity where available. A registry outage, ambiguous manifest, authentication failure, or missing CLI is unresolved coverage; an HTTP error is not evidence that a name is free. A verified exact package can still have a different command or audience.

## Source hosts and products

Search an available source host for exact names and category terms; use code search selectively when documented command or import usage matters. `gh search repos` and `gh search code` can help when GitHub CLI and access are available. Follow local user and repository instructions for GitHub access. Prefer connector capabilities when provided; otherwise use an appropriate read-only search method.

Search quoted and unquoted names, plausible suffixes, category terms, and command usage through available web search. Check official product pages for consequential matches, including major-company tools in the same category. Search domains, stores, organizations, or handles when the user expects those channels to matter. Search results and snippets are leads; cite primary pages for the conclusions they support. Search depth and number of leads follow the chosen mode and user constraints.
