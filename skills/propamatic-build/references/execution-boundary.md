# Blender execution boundary

Choose the boundary from the input, not from the filename extension.

## Reviewed local source and project assets

Use a dedicated generated directory and the known project Blender installation. Start with factory settings and automatic script execution disabled. Review any dependencies loaded by the script. Explicit Python execution still runs the entry point and imports: disabling auto-execution does not neutralize them.

Check project setup docs and tool config for pinned Blender, exporter, and runtime paths before falling back to tools on `PATH`. Record the versions actually used. Resolve the trusted output root first, for example `parent = trusted_root.resolve() / "runs"`. Then require `parent.resolve() == parent` to reject symlinks below that root while allowing a symlinked workspace. Validate the run ID with a full match such as `[a-z0-9][a-z0-9_-]{0,63}`, then create `(parent / run_id).mkdir(exist_ok=False)` in that parent. Resolve other asset paths with component-aware containment. Use an isolated filesystem if untrusted processes can modify those paths.

A typical command shape is:

```sh
blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python reviewed_build.py
```

Put `--python-exit-code` before the script so an uncaught Python exception fails the build command. Check operator results too, since Blender operators can return `CANCELLED` without raising. Confirm supported switches with the pinned Blender version. These flags change Blender startup and error handling. Use an execution boundary appropriate to the inputs.

## Supplied models, Blender files, scripts or unknown helpers

Static review can proceed without executing them. For execution, use an actual disposable VM or a hardened worker/container appropriate to the host threat model. Containers share the host kernel and are not equivalent to VMs for hostile native-code exploits.

The worker should have a non-privileged identity, no network, no secret environment, no host home/config/SSH/cloud mounts, no Docker socket, read-only staged inputs, and only its run output and scratch directories writable. Bound CPU, memory, process count, output size, runtime and storage. Avoid privileged mode and extra capabilities. GPU access expands the driver attack surface; use it only when needed.

Stage only required files; mount no broad project tree containing secrets. Run an updated Blender/importer even with script auto-execution off: binary parsers remain attack surface. Reject missing external dependencies rather than allowing assets to fetch or execute them. Treat an external render farm/client as a separate execution and upload boundary requiring review.

If isolation is unavailable, continue with static inspection or a source-only reconstruction. Do not run an untrusted asset merely to discover whether it is safe. Explain the specific missing boundary if it prevents requested execution.

## Promote outputs deliberately

A completed process is not proof that its files are safe or correct. Validate expected file names, types, sizes and hashes, reject output symlinks, and stage only intended exports for the consumer. Re-import candidate assets in a fresh isolated process when they came from untrusted execution. Do not run embedded text, install extensions, follow arbitrary linked files, or merge generated scripts into trusted tools as a verification step.

Preserve provenance and the run's actual exit status. Apply publication or deployment authorization separately from local generation; creating an asset does not authorize publishing it.
