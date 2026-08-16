# ReadMe Driven Development

ReadMe Driven Development (RMDD) is a coordinated set of three explicitly
invoked skills. Together they turn a project's public README into a desired
state, reconcile the implementation with that state, and validate the result.

## Skills

| Skill | Responsibility |
| --- | --- |
| [`rmds`](../skills/rmds/) | Write or revise the public README so it describes the requested product state as current behavior. |
| [`rmdd`](../skills/rmdd/) | Immediately makes the implementation/tests agree with the current README. It never modifies the README itself. |
| [`rmdv`](../skills/rmdv/) | Validate the latest RMDD run against its documentation, implementation, tests, and saved evidence. |

## Typical workflow

1. Write about the product you'd like to see in your README.
Or invoke `$rmds` to express the desired behavior for you.
2. Invoke `$rmdd` to reconcile the project with that README, it will begin implementation immediately.
3. If you want the full lifecycle, invoke `$rmdv` to review the results and identify what is blocked or unclear.
4. Use `$rmds clarify` to look at the last validation and improve the README based on the result.

Each skill retains its own activation boundary. Normal RMDS can be used by
itself. RMDD can work from an existing README without a preceding RMDS run.
RMDV requires an RMDD receipt to have been created, and RMDS clarify requires an RMDV review to have been run recently.

## Shared project state

The skills coordinate primarily through the README, but can track useful info through private project-local state under `.rmdd/`:

- RMDD writes execution receipts under `.rmdd/rmdd/`.
- RMDV reads RMDD receipts and writes reviews under `.rmdd/rmdv/`.
- RMDS clarify reads a selected RMDV review as advice about documentation
  clarity.

Each skill limits itself to the part of `.rmdd/` needed for its job. The public
README remains ordinary project documentation and uses no RMDD-specific syntax.

## Installation

Install all three skill directories into the same agent skill root:

```text
skills/
├── rmds/
├── rmdd/
└── rmdv/
```

The included OpenAI agent manifests keep implicit invocation disabled. Invoke
the skills explicitly as `$rmds`, `$rmdd`, and `$rmdv`.
