#!/usr/bin/env python3
"""Keep RMDD run receipts consistent without taking product decisions away from the agent."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Iterable


RUN_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{8}(?:-\d+)?$")


class ReceiptError(RuntimeError):
    """Report a receipt problem in language suitable for the calling agent."""


def utc_now() -> str:
    """Return a sortable UTC timestamp without fractional seconds."""

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_id_time() -> str:
    """Return the timestamp prefix used in a receipt run ID."""

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    """Hash a file as bytes so snapshots remain exact across platforms."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    """Replace a receipt file only after its complete contents reach disk."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def append_text(path: Path, text: str) -> None:
    """Append UTF-8 receipt text while preserving earlier history."""

    with path.open("a", encoding="utf-8", newline="") as handle:
        handle.write(text)


def within(path: Path, root: Path) -> bool:
    """Return whether a resolved path stays inside a resolved root."""

    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def project_paths(project_root: str, readme: str) -> tuple[Path, Path]:
    """Resolve and validate the project root and its root README."""

    root = Path(project_root).expanduser().resolve(strict=True)
    source = Path(readme).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ReceiptError(f"Project root is not a directory: {root}")
    if source != root / "README.md":
        raise ReceiptError(f"RMDD needs the root README at {root / 'README.md'}")
    if not source.is_file():
        raise ReceiptError(f"README is not a file: {source}")
    return root, source


def prepare_state_root(root: Path) -> tuple[Path, Path]:
    """Create the RMDD-only state tree and reject redirected state paths."""

    dot_rmdd = root / ".rmdd"
    if dot_rmdd.exists() and dot_rmdd.resolve() != dot_rmdd:
        raise ReceiptError(f"Refusing redirected receipt directory: {dot_rmdd}")
    dot_rmdd.mkdir(exist_ok=True)
    if dot_rmdd.resolve() != dot_rmdd or not dot_rmdd.is_dir():
        raise ReceiptError(f"Receipt directory is not a local directory: {dot_rmdd}")

    state = dot_rmdd / "rmdd"
    if state.exists() and state.resolve() != state:
        raise ReceiptError(f"Refusing redirected RMDD state directory: {state}")
    runs = state / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    if state.resolve() != state or runs.resolve() != runs:
        raise ReceiptError("RMDD state resolves outside the local project")
    return state, runs


def validate_run_dir(value: str) -> tuple[Path, Path]:
    """Resolve an existing run directory strictly inside `.rmdd/rmdd/runs`."""

    requested = Path(os.path.abspath(Path(value).expanduser()))
    run_dir = requested.resolve(strict=True)
    if run_dir != requested:
        raise ReceiptError(f"Refusing redirected RMDD run directory: {requested}")
    if not RUN_ID_RE.fullmatch(run_dir.name):
        raise ReceiptError(f"Invalid RMDD run ID: {run_dir.name}")
    runs = run_dir.parent
    state = runs.parent
    dot_rmdd = state.parent
    root = dot_rmdd.parent
    expected = root / ".rmdd" / "rmdd" / "runs" / run_dir.name
    if (
        runs.name != "runs"
        or state.name != "rmdd"
        or dot_rmdd.name != ".rmdd"
        or expected.resolve(strict=True) != run_dir
    ):
        raise ReceiptError(f"Run directory is outside `.rmdd/rmdd/runs`: {run_dir}")
    return run_dir, root


def command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a bounded Git query and return its captured result."""

    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )


def git_context(root: Path) -> dict[str, str | bool]:
    """Collect optional Git identity for a project root."""

    try:
        probe = command(["git", "rev-parse", "--show-toplevel"], root)
    except FileNotFoundError:
        return {"available": False, "branch": "", "head": ""}
    if probe.returncode != 0:
        return {"available": False, "branch": "", "head": ""}
    git_root = Path(probe.stdout.strip()).resolve(strict=True)
    if os.path.normcase(str(git_root)) != os.path.normcase(str(root)):
        raise ReceiptError(f"Project root must be the Git work-tree root: {git_root}")
    branch = command(["git", "branch", "--show-current"], root)
    head = command(["git", "rev-parse", "HEAD"], root)
    return {
        "available": True,
        "branch": branch.stdout.strip() if branch.returncode == 0 else "",
        "head": head.stdout.strip() if head.returncode == 0 else "",
    }


def ensure_local_ignore(root: Path) -> str | None:
    """Add one local `/.rmdd/` rule without touching tracked ignore files."""

    location = command(["git", "rev-parse", "--git-path", "info/exclude"], root)
    if location.returncode != 0:
        return location.stderr.strip() or "Git could not locate its local exclude file"
    exclude = Path(location.stdout.strip())
    if not exclude.is_absolute():
        exclude = root / exclude
    try:
        exclude.parent.mkdir(parents=True, exist_ok=True)
        if exclude.exists() and not os.access(exclude, os.W_OK):
            return f"Could not update read-only local exclude file: {exclude}"
        existing_mode = stat.S_IMODE(exclude.stat().st_mode) if exclude.exists() else None
        data = exclude.read_bytes() if exclude.exists() else b""
        lines = [
            line
            for line in data.splitlines(keepends=True)
            if line.strip(b" \t\r\n") != b"/.rmdd/"
        ]
        updated = b"".join(lines)
        if updated and not updated.endswith((b"\n", b"\r")):
            updated += b"\n"
        updated += b"/.rmdd/\n"
        atomic_write(exclude, updated)
        if existing_mode is not None:
            os.chmod(exclude, existing_mode)
    except OSError as exc:
        return f"Could not update {exclude}: {exc}"

    verify = command(["git", "check-ignore", "-q", "--no-index", ".rmdd/probe"], root)
    if verify.returncode != 0:
        return "Git local exclusion was written but could not be verified"
    return None


def git_output(root: Path, arguments: list[str]) -> str:
    """Return Git output or a readable evidence-gap note."""

    result = command(["git", *arguments], root)
    if result.returncode == 0:
        return result.stdout
    detail = result.stderr.strip() or f"git {' '.join(arguments)} exited {result.returncode}"
    return f"[Evidence unavailable: {detail}]\n"


def append_section(path: Path, title: str, content: str) -> None:
    """Append one labeled evidence section."""

    body = content if content.endswith("\n") else f"{content}\n"
    append_text(path, f"\n## {title}\n\n{body}")


def previous_run(state: Path, runs: Path) -> tuple[str | None, str | None]:
    """Resolve the previous direct-child pointer without directory discovery."""

    latest = state / "latest"
    if not latest.exists():
        return None, None
    try:
        value = latest.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return None, f"Could not read the previous RMDD pointer: {exc}"
    if not RUN_ID_RE.fullmatch(value):
        return None, "Ignored an invalid previous RMDD pointer"
    candidate = runs / value
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        return None, "Ignored a previous RMDD pointer whose run is missing"
    if resolved.parent != runs.resolve() or resolved.name != value:
        return None, "Ignored a previous RMDD pointer outside the runs directory"
    return value, None


def unified(before: bytes, after: bytes, before_name: str, after_name: str) -> str:
    """Build a readable diff while keeping byte-exact snapshots elsewhere."""

    old = before.decode("utf-8", errors="replace").splitlines(keepends=True)
    new = after.decode("utf-8", errors="replace").splitlines(keepends=True)
    return "".join(difflib.unified_diff(old, new, fromfile=before_name, tofile=after_name))


def create_run(project_root: str, readme: str) -> dict[str, object]:
    """Start a receipt before project implementation changes begin."""

    root, source = project_paths(project_root, readme)
    git = git_context(root)
    state, runs = prepare_state_root(root)
    prior, prior_warning = previous_run(state, runs)
    readme_hash = sha256_file(source)
    warnings = [warning for warning in [prior_warning] if warning]
    if git["available"]:
        ignore_warning = ensure_local_ignore(root)
        if ignore_warning:
            warnings.append(ignore_warning)

    base_id = f"{run_id_time()}-{readme_hash[:8]}"
    run_id = base_id
    suffix = 2
    while (runs / run_id).exists():
        run_id = f"{base_id}-{suffix}"
        suffix += 1

    run_dir = runs / run_id
    run_dir.mkdir()
    shutil.copyfile(source, run_dir / "README.md")

    status = git_output(root, ["status", "--short"]) if git["available"] else "Git is not available.\n"
    fields = [
        "# RMDD Run",
        "",
        f"Status: WORKING",
        f"Started: {utc_now()}",
        f"Run ID: {run_id}",
        f"Project root: {root}",
        f"Git available: {'yes' if git['available'] else 'no'}",
        f"Git branch: {git['branch']}",
        f"Git HEAD: {git['head']}",
        f"Previous RMDD run: {prior or ''}",
        f"Starting README SHA-256: {readme_hash}",
        f"Final README SHA-256: {readme_hash}",
        "Active README snapshot: README.md",
        "Source refresh pending: no",
        "",
        "## Starting project status",
        "",
        "```text",
        status.rstrip(),
        "```",
        "",
    ]
    for warning in warnings:
        fields.append(f"Warning: {warning}")
    atomic_write(run_dir / "run.md", "\n".join(fields).encode("utf-8"))
    atomic_write(run_dir / "progress.md", b"")
    atomic_write(run_dir / "diffs.txt", b"RMDD evidence\n")

    if git["available"]:
        unstaged = git_output(root, ["diff", "--", "README.md"])
        staged = git_output(root, ["diff", "--cached", "--", "README.md"])
        append_section(run_dir / "diffs.txt", "Starting unstaged README diff", unstaged or "[No changes]\n")
        append_section(run_dir / "diffs.txt", "Starting staged README diff", staged or "[No changes]\n")
        if not unstaged and not staged:
            recent = git_output(root, ["log", "-1", "-p", "--", "README.md"])
            append_section(run_dir / "diffs.txt", "Most recent committed README change", recent or "[No history]\n")
        append_section(
            run_dir / "diffs.txt",
            "Starting unstaged project paths",
            git_output(root, ["diff", "--name-status"]) or "[No changes]\n",
        )
        append_section(
            run_dir / "diffs.txt",
            "Starting staged project paths",
            git_output(root, ["diff", "--cached", "--name-status"]) or "[No changes]\n",
        )
    elif prior:
        old_snapshot = runs / prior / "README.latest.md"
        if not old_snapshot.exists():
            old_snapshot = runs / prior / "README.md"
        if old_snapshot.is_file():
            comparison = unified(old_snapshot.read_bytes(), source.read_bytes(), f"{prior}/README", "current/README")
            append_section(run_dir / "diffs.txt", "README change since previous RMDD run", comparison or "[No changes]\n")
        else:
            append_section(run_dir / "diffs.txt", "README history", "[Previous README snapshot is unavailable]\n")
    else:
        append_section(run_dir / "diffs.txt", "First non-Git README", source.read_text(encoding="utf-8", errors="replace"))

    atomic_write(state / "latest", f"{run_id}\n".encode())

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "git": bool(git["available"]),
        "previous_run": prior,
        "warnings": warnings,
    }


def record_progress(run_dir_value: str, message: str) -> dict[str, object]:
    """Append one authored user-facing progress update."""

    run_dir, _ = validate_run_dir(run_dir_value)
    require_working(run_dir)
    clean = message.strip()
    if not clean:
        raise ReceiptError("Progress text is empty")
    append_text(run_dir / "progress.md", f"[{utc_now()}]\n\n{clean}\n\n")
    return {"run_dir": str(run_dir), "recorded": True}


def metadata_value(run_dir: Path, label: str) -> str:
    """Read one single-line field from run.md."""

    text = (run_dir / "run.md").read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(label)}: (.*)$", text, flags=re.MULTILINE)
    if not match:
        raise ReceiptError(f"Receipt is missing `{label}`")
    return match.group(1)


def require_working(run_dir: Path) -> None:
    """Protect a closed receipt from later mutation."""

    status = metadata_value(run_dir, "Status")
    if status != "WORKING":
        raise ReceiptError(f"RMDD run is already closed with status {status}")


def replace_metadata(run_dir: Path, label: str, value: str) -> None:
    """Replace one receipt field while leaving appended evidence intact."""

    path = run_dir / "run.md"
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        rf"^{re.escape(label)}: .*$",
        f"{label}: {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ReceiptError(f"Receipt is missing `{label}`")
    atomic_write(path, updated.encode("utf-8"))


def record_document(run_dir_value: str, document: str) -> dict[str, object]:
    """Save a linked intent document's starting hash and exact text."""

    run_dir, root = validate_run_dir(run_dir_value)
    require_working(run_dir)
    path = Path(document).expanduser().resolve(strict=True)
    if not path.is_file() or not within(path, root):
        raise ReceiptError(f"Intent document must be a local project file: {path}")
    if within(path, root / ".rmdd"):
        raise ReceiptError("Receipt state cannot be used as product documentation")
    relative = path.relative_to(root).as_posix()
    if any(character in relative for character in ("\r", "\n", "|", "\\")):
        raise ReceiptError(f"Intent document path cannot be stored safely: {relative!r}")
    run_text = (run_dir / "run.md").read_text(encoding="utf-8")
    recorded_line = rf"^Intent document: {re.escape(relative)} \| start SHA-256 [0-9a-f]{{64}}$"
    if re.search(recorded_line, run_text, flags=re.MULTILINE):
        return {"path": relative, "recorded": False, "reason": "already recorded"}
    digest = sha256_file(path)
    append_text(run_dir / "run.md", f"Intent document: {relative} | start SHA-256 {digest}\n")
    content = path.read_text(encoding="utf-8", errors="replace")
    append_section(run_dir / "diffs.txt", f"Intent document start: {relative} (SHA-256 {digest})", content)
    if metadata_value(run_dir, "Git available") == "yes":
        unstaged = git_output(root, ["diff", "--", relative])
        staged = git_output(root, ["diff", "--cached", "--", relative])
        append_section(run_dir / "diffs.txt", f"Starting unstaged intent diff: {relative}", unstaged or "[No changes]\n")
        append_section(run_dir / "diffs.txt", f"Starting staged intent diff: {relative}", staged or "[No changes]\n")
        if not unstaged and not staged:
            recent = git_output(root, ["log", "-1", "-p", "--", relative])
            append_section(run_dir / "diffs.txt", f"Most recent committed intent change: {relative}", recent or "[No history]\n")
    return {"path": relative, "sha256": digest, "recorded": True}


def intent_documents(run_dir: Path, root: Path) -> Iterable[tuple[str, str, Path]]:
    """Yield recorded intent paths, including safe paths whose files were deleted."""

    pattern = re.compile(r"^Intent document: (.+) \| start SHA-256 ([0-9a-f]{64})$", re.MULTILINE)
    text = (run_dir / "run.md").read_text(encoding="utf-8")
    for relative, digest in pattern.findall(text):
        if any(character in relative for character in ("\r", "\n", "|", "\\")):
            raise ReceiptError(f"Recorded intent document has an unsafe path: {relative!r}")
        parsed = PurePosixPath(relative)
        if parsed.is_absolute() or not parsed.parts or ".." in parsed.parts:
            raise ReceiptError(f"Recorded intent document has an unsafe path: {relative!r}")
        path = root.joinpath(*parsed.parts).resolve(strict=False)
        if not within(path, root) or within(path, root / ".rmdd"):
            raise ReceiptError(f"Recorded intent document is outside product files: {relative}")
        yield relative, digest, path


def refresh_sources(run_dir_value: str, *, acknowledge: bool = True) -> dict[str, object]:
    """Refresh README and linked-document evidence before final reporting."""

    run_dir, root = validate_run_dir(run_dir_value)
    require_working(run_dir)
    expected_readme = root / "README.md"
    try:
        readme = expected_readme.resolve(strict=True)
    except OSError:
        raise ReceiptError(f"Root README disappeared during the run: {expected_readme}") from None
    if readme != expected_readme or not readme.is_file() or within(readme, root / ".rmdd"):
        raise ReceiptError(f"Root README is no longer a local project file: {expected_readme}")
    start_snapshot = run_dir / "README.md"
    start_hash = metadata_value(run_dir, "Starting README SHA-256")
    previous_final_hash = metadata_value(run_dir, "Final README SHA-256")
    current_hash = sha256_file(readme)
    changed: list[str] = []
    latest = run_dir / "README.latest.md"
    if current_hash != start_hash or latest.exists():
        shutil.copyfile(readme, latest)
        if current_hash != previous_final_hash:
            comparison = unified(start_snapshot.read_bytes(), readme.read_bytes(), "README.start.md", "README.latest.md")
            detail = comparison or "[README returned to its starting content after an earlier refresh]\n"
            append_section(run_dir / "diffs.txt", f"README source refresh at {utc_now()}", detail)
            changed.append("README.md")
        replace_metadata(run_dir, "Active README snapshot", "README.latest.md")
    replace_metadata(run_dir, "Final README SHA-256", current_hash)

    doc_hashes: dict[str, str] = {}
    for relative, old_hash, path in intent_documents(run_dir, root):
        current = sha256_file(path) if path.is_file() else "MISSING"
        doc_hashes[relative] = current
        prior_lines = re.findall(
            rf"^Final intent SHA-256: {re.escape(relative)} \| ([0-9a-f]{{64}}|MISSING)$",
            (run_dir / "run.md").read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
        previous_doc_hash = prior_lines[-1] if prior_lines else old_hash
        if current != previous_doc_hash:
            content = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else "[Document is missing.]\n"
            append_section(
                run_dir / "diffs.txt",
                f"Intent document refresh: {relative} at {utc_now()} ({'SHA-256 ' + current if current != 'MISSING' else 'missing'})",
                content,
            )
            changed.append(relative)
            append_text(run_dir / "run.md", f"Final intent SHA-256: {relative} | {current}\n")
        elif not prior_lines:
            append_text(run_dir / "run.md", f"Final intent SHA-256: {relative} | {current}\n")
    if acknowledge:
        replace_metadata(run_dir, "Source refresh pending", "no")
    elif changed:
        replace_metadata(run_dir, "Source refresh pending", "yes")
    return {"readme_sha256": current_hash, "documents": doc_hashes, "changed_sources": changed}


def add_note(run_dir_value: str, kind: str, text: str) -> dict[str, object]:
    """Add a concise changed-path, check, or warning entry to run.md."""

    run_dir, _ = validate_run_dir(run_dir_value)
    require_working(run_dir)
    clean = text.strip()
    if not clean:
        raise ReceiptError("Note text is empty")
    if "\n" in clean or "\r" in clean:
        raise ReceiptError("Receipt notes must fit on one line")
    labels = {"changed": "Changed path", "check": "Check", "warning": "Warning"}
    append_text(run_dir / "run.md", f"{labels[kind]}: {clean}\n")
    return {"kind": kind, "recorded": True}


def add_evidence(run_dir_value: str, label: str, content: bytes) -> dict[str, object]:
    """Append agent-selected evidence, including non-Git before/after edits."""

    run_dir, _ = validate_run_dir(run_dir_value)
    require_working(run_dir)
    title = label.strip()
    if not title:
        raise ReceiptError("Evidence label is empty")
    if "\n" in title or "\r" in title:
        raise ReceiptError("Evidence labels must fit on one line")
    append_section(run_dir / "diffs.txt", title, content.decode("utf-8", errors="replace"))
    return {"label": title, "recorded": True}


def require_fresh_sources(run_dir_value: str) -> dict[str, object]:
    """Refuse closure until the agent acknowledges the newest documentation save."""

    run_dir, _ = validate_run_dir(run_dir_value)
    refresh = refresh_sources(run_dir_value, acknowledge=False)
    if refresh["changed_sources"]:
        changed = ", ".join(refresh["changed_sources"])
        raise ReceiptError(
            f"Documentation changed after the last acknowledged refresh: {changed}. "
            "Reconcile it, run `receipt.py refresh`, and compose a new final response."
        )
    if metadata_value(run_dir, "Source refresh pending") == "yes":
        raise ReceiptError("A documentation refresh still needs reconciliation before this run can finish")
    return refresh


def capture_ending_git_evidence(root: Path) -> tuple[str, str, str]:
    """Collect final Git path evidence before the last source-freshness check."""

    return (
        git_output(root, ["status", "--short"]),
        git_output(root, ["diff", "--name-status"]),
        git_output(root, ["diff", "--cached", "--name-status"]),
    )


def finish_run(run_dir_value: str, status: str, response: bytes) -> dict[str, object]:
    """Save the exact response and close only against freshly checked sources."""

    run_dir, root = validate_run_dir(run_dir_value)
    require_working(run_dir)
    if not response:
        raise ReceiptError("Final response text is empty")
    refresh = require_fresh_sources(run_dir_value)
    git = metadata_value(run_dir, "Git available") == "yes"
    if git:
        final_status, unstaged_paths, staged_paths = capture_ending_git_evidence(root)
    else:
        final_status = "Git is not available."
        unstaged_paths = staged_paths = ""
    refresh = require_fresh_sources(run_dir_value)
    if git:
        append_section(
            run_dir / "diffs.txt",
            "Ending unstaged project paths",
            unstaged_paths or "[No changes]\n",
        )
        append_section(
            run_dir / "diffs.txt",
            "Ending staged project paths",
            staged_paths or "[No changes]\n",
        )
    atomic_write(run_dir / "response.md", response)
    refresh = require_fresh_sources(run_dir_value)
    run_path = run_dir / "run.md"
    run_text = run_path.read_text(encoding="utf-8")
    closed_text, count = re.subn(
        r"^Status: WORKING$",
        f"Status: {status}",
        run_text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ReceiptError("Receipt status changed before the run could close")
    closed_text += f"\nFinished: {utc_now()}\n\n## Ending project status\n\n```text\n{final_status.rstrip()}\n```\n"
    atomic_write(run_path, closed_text.encode("utf-8"))
    return {
        "run_dir": str(run_dir),
        "status": status,
        "response": str(run_dir / "response.md"),
        "source_refresh": refresh,
    }


def parser() -> argparse.ArgumentParser:
    """Build the command-line interface used by the RMDD skill."""

    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    start = commands.add_parser("start", help="start a local RMDD receipt")
    start.add_argument("--project-root", required=True)
    start.add_argument("--readme", required=True)

    progress = commands.add_parser("progress", help="record one authored progress update")
    progress.add_argument("--run-dir", required=True)
    progress.add_argument("--message", required=True)

    document = commands.add_parser("document", help="record a linked intent document")
    document.add_argument("--run-dir", required=True)
    document.add_argument("--path", required=True)

    refresh = commands.add_parser("refresh", help="refresh documentation evidence")
    refresh.add_argument("--run-dir", required=True)

    note = commands.add_parser("note", help="record a changed path, check, or warning")
    note.add_argument("--run-dir", required=True)
    note.add_argument("--kind", choices=["changed", "check", "warning"], required=True)
    note.add_argument("--text", required=True)

    evidence = commands.add_parser("evidence", help="append labeled evidence from stdin")
    evidence.add_argument("--run-dir", required=True)
    evidence.add_argument("--label", required=True)

    finish = commands.add_parser("finish", help="save the response from stdin and close the run")
    finish.add_argument("--run-dir", required=True)
    finish.add_argument("--status", choices=["FINISHED", "FAILED"], default="FINISHED")
    return root


def main(argv: list[str] | None = None) -> int:
    """Run one receipt operation and emit a compact JSON result."""

    args = parser().parse_args(argv)
    try:
        if args.command == "start":
            result = create_run(args.project_root, args.readme)
        elif args.command == "progress":
            result = record_progress(args.run_dir, args.message)
        elif args.command == "document":
            result = record_document(args.run_dir, args.path)
        elif args.command == "refresh":
            result = refresh_sources(args.run_dir)
        elif args.command == "note":
            result = add_note(args.run_dir, args.kind, args.text)
        elif args.command == "evidence":
            result = add_evidence(args.run_dir, args.label, sys.stdin.buffer.read())
        else:
            result = finish_run(args.run_dir, args.status, sys.stdin.buffer.read())
    except (OSError, ReceiptError, subprocess.SubprocessError) as exc:
        print(f"RMDD receipt error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
