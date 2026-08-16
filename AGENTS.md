# Repository Agent Instructions

Placeholder for repository-specific agent guidance.

Until this file is expanded, follow the applicable user and global agent
instructions.

## Repository destination

This repository is intended to be published at
[Mattie/mattie_skills](https://github.com/Mattie/mattie_skills).

## Repository structure

- Store each independently invoked skill at `skills/<skill-name>/`.
- Keep the canonical files for a skill in one directory. Harness manifests and
  distribution adapters should reference or package that directory without
  introducing maintained copies.
- Keep coordinated skill sets as sibling directories under `skills/`. Document
  the shared workflow in `docs/<set-name>.md` and group shared tests under
  `tests/<set-name>/`.
