# Reference generation boundaries

Prefer the environment's supported image tools over custom API clients. Use only the files needed for this task. Do not reuse the upstream project's PowerShell or Node upload helpers without repairing their trust boundaries.

## Local files and jobs

For automated jobs, use a validated manifest of relative reference names and generated output identifiers. Resolve inputs under a dedicated reference root; require actual path-component containment after resolving symlinks. A string-prefix comparison is insufficient. Reject absolute paths, parent traversal and unexpected fields. Validate image signatures, decoded dimensions, pixel count and byte size before upload. An image extension or a base64 data-URL label is not validation.

Create outputs under a separate generated root. Validate the existing parent directories and reject symlink escapes. For untrusted concurrent writers, path validation alone has a check/use race: use an isolated filesystem or descriptor-relative no-follow operations. Do not overwrite source references. Upload only validated image bytes and intended prompts; never auto-discover references in home directories or follow arbitrary job paths.

## Network and spend

If a custom client is actually required, use official provider documentation and an established client where suitable. Before sending a credential, require HTTPS and an exact approved API origin (scheme, hostname, port). Do not attach credentials to arbitrary response URLs, redirects, or result downloads. Validate each redirect or disable redirects. No credentials in URLs, prompts, logs, or saved job manifests.

Validate result destinations independently. For unattended workers, enforce egress rules that block loopback, private, link-local, metadata and other non-public addresses for both IPv4 and IPv6. URL string checks alone do not prevent DNS rebinding; enforce the policy at connection time or through a constrained downloader. Allow only documented asset hosts and verify downloaded file type and size.

Set explicit request deadlines, streamed byte limits, polling duration and concurrency before starting. Keep retry counts and spending within the authorized scope. Do not blindly resubmit a generation after a timeout: first reconcile its job ID/status to avoid duplicate charges. Save a job ID for resumable polling, without secrets.

If an upload or spend falls outside existing authorization, prepare the exact file list, provider, batch size and available cost estimate before asking. A missing credential must use the environment's secret mechanism, never chat.

## Provenance

Record provider/model, prompt, authorized input filenames and hashes, job identifier and output hash when available. Keep sensitive prompts and inputs out of public exports. Building approved local geometry should not need the generation credential.
