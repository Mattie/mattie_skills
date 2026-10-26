#!/usr/bin/env python3
"""Read a Todo project tree and join optional, dated harness observations.

This command never writes project records, sends messages, or starts workers.
Chat observations are supplied by a caller using supported harness tools.
Requires Python 3.10+ and PyYAML.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    print(json.dumps({"schema_version": 1, "status": "error", "diagnostics": [
        "PyYAML is required. Install scripts/requirements.txt in the chosen Python environment."]}))
    sys.exit(2)


class RecordError(ValueError):
    """A record cannot be interpreted without guessing."""


PROJECT_STATES = {"active", "sleeping", "cancelled", "completed"}
TASK_STATES = {"queued", "active", "review", "blocked", "paused", "cancelled", "done"}


def load_yaml(text):
    """Parse data only; reject aliases to keep records finite and unambiguous."""
    if any(isinstance(token, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken))
           for token in yaml.scan(text)):
        raise RecordError("YAML anchors and aliases are not supported")
    def check_keys(node, depth=0):
        if depth > 64:
            raise RecordError("YAML nesting exceeds 64 levels")
        if isinstance(node, yaml.MappingNode):
            keys = set()
            for key, value in node.value:
                if key.tag != "tag:yaml.org,2002:str" or key.value in keys:
                    raise RecordError("YAML keys must be unique strings")
                keys.add(key.value)
                check_keys(value, depth + 1)
        elif isinstance(node, yaml.SequenceNode):
            for value in node.value:
                check_keys(value, depth + 1)

    check_keys(yaml.compose(text, Loader=yaml.SafeLoader))
    return yaml.safe_load(text)


def read_text(path, boundary=None):
    """Read a bounded UTF-8 record, refusing links outside its control directory."""
    if boundary and not path.resolve().is_relative_to(boundary.resolve()):
        raise RecordError(f"Record escapes control directory: {path}")
    if path.stat().st_size > 2_000_000:
        raise RecordError(f"Record exceeds 2 MB: {path}")
    return path.read_text(encoding="utf-8-sig")


def git_common_control(root):
    """Locate the primary worktree's control directory using read-only Git metadata."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, timeout=10, check=False, shell=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode == 0:
        common = Path(result.stdout.strip())
        candidate = common.parent / ".todo"
        if common.name == ".git" and (candidate / "projects/PROJECT.md").is_file():
            return candidate.resolve()
    return None


def discover(directory, control_root=None):
    """Find the nearest managed project without crossing an unmanaged Git boundary.

Return the control directory (possibly absent) and the current workspace root.
An explicit control root supports cross-worktree handoffs without copying records.
"""
    directory = Path(directory).resolve(strict=True)
    if not directory.is_dir():
        raise RecordError("directory must be an existing directory")
    workspace = directory
    for ancestor in (directory, *directory.parents):
        if (ancestor / ".todo/projects/PROJECT.md").is_file():
            return (Path(control_root).resolve() if control_root else ancestor / ".todo"), ancestor
        if (ancestor / ".git").exists():
            workspace = ancestor
            break
    if control_root:
        return Path(control_root).resolve(strict=True), workspace
    common = git_common_control(workspace) if (workspace / ".git").exists() else None
    return common, workspace


def binding(value):
    """Normalize a chief mapping or the existing 'harness / host / thread' notation."""
    if value is None:
        return None
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(" / ", 2)]
        value = dict(zip(("harness", "host", "thread"), parts)) if len(parts) == 3 else {}
    if not isinstance(value, dict) or not all(
        isinstance(value.get(key), str) and value[key] for key in ("harness", "host", "thread")
    ):
        raise RecordError("Binding requires nonempty harness, host, and thread strings")
    return {key: value[key] for key in ("harness", "host", "thread")}


def key_of(value):
    """Identify chats by harness and host as well as thread ID."""
    return tuple(value[key] for key in ("harness", "host", "thread"))


def observation_time(timestamp):
    """Return an aware timestamp, or None when the observation cannot be dated."""
    try:
        moment = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
        return moment if moment.tzinfo is not None else None
    except (ValueError, TypeError):
        return None


def freshness(timestamp, now, max_age):
    """Describe observation age without treating missing timestamps as fresh."""
    moment = observation_time(timestamp)
    if moment is None:
        return "unknown"
    age = (now - moment).total_seconds()
    return "unknown" if age < -60 else "fresh" if age <= max_age else "stale"


def read_project(path, control):
    """Load one project brief, leaving narrative content as passive source material."""
    text = read_text(path, control)
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        raise RecordError(f"Missing YAML frontmatter: {path}")
    meta = load_yaml(match[1])
    if not isinstance(meta, dict) or not isinstance(meta.get("id"), str) or not meta["id"]:
        raise RecordError(f"Missing project ID: {path}")
    if meta.get("state") not in PROJECT_STATES:
        raise RecordError(f"Invalid project lifecycle: {path}")
    if meta.get("parent") is not None and not isinstance(meta["parent"], str):
        raise RecordError(f"Invalid parent ID: {path}")
    paths = meta.get("source_paths", [])
    if not isinstance(paths, list) or any(not isinstance(p, str) for p in paths):
        raise RecordError(f"source_paths must be a list of relative paths: {path}")
    if any(Path(p).is_absolute() or ".." in Path(p).parts for p in paths):
        raise RecordError(f"source_paths must stay inside the workspace: {path}")
    title = re.search(r"^# (.+)$", text[match.end():], re.M)
    brief = {}
    for section in ("Outcome and scope", "Next outcomes", "Dependencies", "Follow-up"):
        part = re.search(r"^## " + re.escape(section) + r"\s*\n(.*?)(?=^## |\Z)",
                         text[match.end():], re.M | re.S)
        if part:
            brief[section] = part[1].strip()
    return {
        "id": meta["id"], "parent": meta.get("parent"),
        "title": title.group(1) if title else meta["id"],
        "state": meta["state"], "priority": meta.get("priority"),
        "chief": binding(meta.get("chief")), "source_paths": paths,
        "updated_at": meta.get("updated_at"), "record": str(path),
        "declared_control_root": meta.get("control_root"), "brief": brief,
        "tasks": [], "children": [], "unreadable_lists": [],
    }


def read_tasks(path, control):
    """Parse checkbox entries and their two-space metadata, ignoring fenced examples."""
    items, current, section, fence = [], None, None, None
    for line_number, line in enumerate(read_text(path, control).splitlines(), 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        if line.startswith("## "):
            section, current = line[3:].strip(), None
        match = re.match(r"^- \[([ xX])\] (.+)$", line)
        if match:
            if section not in {"Open", "Completed"}:
                raise RecordError(f"Task outside Open/Completed: {path}:{line_number}")
            checked = match[1].lower() == "x"
            current = {"text": match[2], "checked": checked, "section": section,
                       "source": str(path), "line": line_number, "metadata": {}}
            items.append(current)
        elif current and re.match(r"^  - [a-z_]+:", line):
            field = load_yaml(line[4:])
            for name, value in field.items():
                if name in current["metadata"]:
                    raise RecordError(f"Duplicate item field {name}: {path}:{line_number}")
                current["metadata"][name] = value
        elif current and re.match(r"^\s+-\s+[A-Za-z_][\w-]*\s*:", line):
            raise RecordError(f"Malformed item metadata: {path}:{line_number}; use two spaces and lowercase keys")
    for item in items:
        meta = item.pop("metadata")
        state = meta.get("state", "done" if item["checked"] else "queued")
        if state not in TASK_STATES:
            raise RecordError(f"Invalid task state: {path}:{item['line']}")
        if item["checked"] != (state == "done") or item["checked"] != (item["section"] == "Completed"):
            raise RecordError(f"Checkbox, section, and task state disagree: {path}:{item['line']}")
        item.update({"id": meta.get("id"), "state": state, "attempt": meta.get("attempt"),
                     "worker": binding(meta.get("worker")), "details": meta})
    return items


def join_chats(nodes, snapshot, workspace, control, host_id, now, max_age):
    """Join supplied tool observations without pretending to perform live tool calls."""
    snapshot = snapshot or {}
    for name in ("projects", "threads", "reads", "relations"):
        if not isinstance(snapshot.get(name, []), list) or any(
            not isinstance(entry, dict) for entry in snapshot.get(name, [])
        ):
            raise RecordError(f"Snapshot {name} must be an array of objects")
    observed = snapshot.get("observed_at")
    inventory = {"provided": bool(snapshot), "coverage": snapshot.get("coverage", "unknown"),
                 "observed_at": observed, "freshness": freshness(observed, now, max_age)}
    if inventory["coverage"] not in {"partial", "complete", "unknown"}:
        raise RecordError("Snapshot coverage must be partial, complete, or unknown")
    project_roots = {workspace.resolve()}
    if control:
        project_roots.add(control.parent.resolve())
    project_ids = {
        (p.get("harness", "codex"), p.get("projectId")) for p in snapshot.get("projects", [])
        if p.get("hostId") == host_id and p.get("path")
        and Path(p["path"]).resolve() in project_roots
    }
    chats = {}
    for item in snapshot.get("threads", []):
        b = binding({"harness": item.get("harness", "codex"),
                     "host": item.get("hostId"), "thread": item.get("id")})
        state = item.get("status", "unknown")
        if isinstance(state, dict):
            state = state.get("type", "unknown")
        chats[key_of(b)] = {**b, "title": item.get("title"), "execution_status": state,
                           "reachability": "listed", "messageability": "unknown",
                           "observed_at": observed, "freshness": inventory["freshness"],
                           "project_id": item.get("projectId"), "cwd": item.get("cwd")}
    for item in snapshot.get("reads", []):
        b = binding(item["binding"])
        entry = chats.setdefault(key_of(b), {**b, "title": None})
        prior_time, read_time = observation_time(entry.get("observed_at")), observation_time(item.get("observed_at"))
        if prior_time and (read_time is None or read_time < prior_time):
            continue
        entry.update({"reachability": "readable" if item.get("ok") is True else "unreachable",
                      "execution_status": item.get("status", "unknown"),
                      "messageability": "unknown", "observed_at": item.get("observed_at"),
                      "freshness": freshness(item.get("observed_at"), now, max_age)})
    used = set()

    def attach(b):
        if not b:
            return None
        identity = key_of(b)
        used.add(identity)
        return chats.get(identity, {**b, "execution_status": "unknown", "reachability": "unknown",
                                   "messageability": "unknown", "observed_at": None, "freshness": "unknown"})

    for node in nodes.values():
        node["chief"] = attach(node["chief"])
        for task in node["tasks"]:
            task["worker"] = attach(task["worker"])
    unassigned = []
    for identity, chat in chats.items():
        if identity in used or chat["host"] != host_id:
            continue
        associated = (chat["harness"], chat.get("project_id")) in project_ids
        # Explicit foreign project membership outranks a coincidental cwd match.
        if not chat.get("project_id") and chat.get("cwd"):
            associated = any(Path(chat["cwd"]).resolve().is_relative_to(root) for root in project_roots)
        if associated:
            unassigned.append(chat)
    edges = []
    for relation in snapshot.get("relations", []):
        parent, child = binding(relation.get("parent")), binding(relation.get("child"))
        if not parent or not child:
            raise RecordError("Chat relations require explicit parent and child bindings")
        edges.append((parent, child))
    connected = used | {key_of(chat) for chat in unassigned}
    while True:
        previous = len(connected)
        for parent, child in edges:
            if key_of(parent) in connected or key_of(child) in connected:
                connected.update((key_of(parent), key_of(child)))
        if len(connected) == previous:
            break
    relations = [{"parent": attach(parent), "child": attach(child)}
                 for parent, child in edges if key_of(parent) in connected]
    # Relations are evidence edges, not inferred parentage or a second ownership tree.
    return inventory, unassigned, relations


def inspect(directory, *, control_root=None, project_id=None, snapshot=None,
            host_id="local", max_age=300):
    """Return a recursive, read-only report for one directory and optional chat snapshot.

    Invalid hierarchy is an error, never a silently truncated tree. Unreadable
    list files yield a partial report with diagnostics. Missing chats stay unknown.
    """
    now = datetime.now(timezone.utc)
    directory = Path(directory).resolve(strict=True)
    control, workspace = discover(directory, control_root)
    if control_root is not None and not (control / "projects/PROJECT.md").is_file():
        raise RecordError(f"Explicit control root has no readable root brief: {control / 'projects/PROJECT.md'}")
    report = {"schema_version": 1, "inspected_at": now.isoformat(), "directory": str(directory),
              "host": {"id": host_id, "machine": platform.node()}, "workspace": str(workspace),
              "control_root": str(control) if control else None, "status": "unmanaged",
              "selected_project": None, "tree": None, "diagnostics": [], "live_checks_performed": False}
    nodes = {}
    if control and (control / "projects/PROJECT.md").is_file():
        root_path = control / "projects/PROJECT.md"
        records = [root_path, *sorted((control / "projects").glob("*/PROJECT.md"))]
        if len(records) > 1000:
            raise RecordError("More than 1000 project records; narrow or repair this project")
        for path in records:
            node = read_project(path, control)
            if node["id"] in nodes:
                raise RecordError(f"Duplicate project ID: {node['id']}")
            nodes[node["id"]] = node
        root = nodes[next(iter(nodes))]
        declared = root["declared_control_root"]
        if declared and Path(declared).resolve() != control.resolve():
            report.update(status="redirect_required", declared_control_root=declared)
            report["diagnostics"].append("Rerun with the canonical --control-root; do not use this copy.")
            return report
        if root["parent"] is not None:
            raise RecordError("Root project must have parent: null")
        for node in nodes.values():
            trail, current = set(), node
            while current["id"] != root["id"]:
                if current["id"] in trail:
                    raise RecordError(f"Parent cycle at {current['id']}")
                trail.add(current["id"])
                if len(trail) > 64:
                    raise RecordError("Project hierarchy exceeds 64 levels")
                if current["parent"] not in nodes:
                    raise RecordError(f"Missing parent for {current['id']}")
                current = nodes[current["parent"]]
            if node is not root:
                nodes[node["parent"]]["children"].append(node)
        task_ids = set()
        for node in nodes.values():
            list_dir = control if node is root else Path(node["record"]).parent
            for path in sorted(list_dir.glob("*.md")):
                if path.name == "PROJECT.md":
                    continue
                try:
                    tasks = read_tasks(path, control)
                    for task in tasks:
                        if task["id"] is not None:
                            if not isinstance(task["id"], str) or task["id"] in task_ids:
                                raise RecordError(f"Invalid or duplicate item ID: {task['id']}")
                            task_ids.add(task["id"])
                    node["tasks"].extend(tasks)
                except (OSError, ValueError, yaml.YAMLError) as exc:
                    report["diagnostics"].append(f"{path}: {exc}")
                    node["unreadable_lists"].append(str(path))
            node["task_counts"] = dict(Counter(task["state"] for task in node["tasks"]))
            node["dispatch_blocked_by"] = []
            current = node
            while current:
                if current["state"] != "active":
                    node["dispatch_blocked_by"].append({"id": current["id"], "state": current["state"]})
                current = nodes.get(current["parent"])

        def roll_up(node):
            counts = Counter(node["task_counts"])
            complete = not node["unreadable_lists"]
            for child in node["children"]:
                roll_up(child)
                counts.update(child["subtree_task_counts"])
                complete = complete and child["counts_complete"]
            node["subtree_task_counts"], node["counts_complete"] = dict(counts), complete

        roll_up(root)
        selected, best = [root["id"]], -1
        workspace_known = ((workspace / ".git").exists()
                           or (workspace / ".todo/projects/PROJECT.md").is_file())
        relative = directory.relative_to(workspace)
        for node in nodes.values():
            for scope in node["source_paths"]:
                scope_path = Path(scope)
                if relative.is_relative_to(scope_path):
                    depth = len(scope_path.parts)
                    if depth > best:
                        selected, best = [node["id"]], depth
                    elif depth == best and node["id"] not in selected:
                        selected.append(node["id"])
        selection_unknown = (not workspace_known and not project_id
                             and any(node["source_paths"] for node in nodes.values()))
        if selection_unknown:
            selected = list(nodes)
            report["diagnostics"].append("Workspace root is unknown; select a scope with --project-id.")
        if project_id:
            if project_id not in nodes:
                raise RecordError(f"Unknown project ID in this tree: {project_id}")
            selected = [project_id]
        report.update(status="partial" if report["diagnostics"] else "ok", tree=root)
        if len(selected) == 1 and not selection_unknown:
            report["selected_project"] = selected[0]
        else:
            report.update(status="ambiguous", selection_candidates=selected)
    elif project_id:
        raise RecordError("Cannot select a project ID in an unmanaged directory")
    report["chat_inventory"], report["unassigned_chats"], report["chat_relations"] = join_chats(
        nodes, snapshot, workspace, control, host_id, now, max_age)
    return report


def main():
    """Print one JSON report; exit 2 on malformed input, not on unmanaged projects."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--control-root", type=Path)
    parser.add_argument("--project-id")
    parser.add_argument("--host-id", default="local")
    parser.add_argument("--chat-snapshot", type=Path)
    parser.add_argument("--max-age-seconds", type=int, default=300)
    args = parser.parse_args()
    try:
        if args.max_age_seconds < 0:
            raise RecordError("max-age-seconds must be nonnegative")
        snapshot = json.loads(read_text(args.chat_snapshot)) if args.chat_snapshot else None
        if snapshot is not None and not isinstance(snapshot, dict):
            raise RecordError("Chat snapshot must be an object")
        report = inspect(args.directory, control_root=args.control_root, project_id=args.project_id,
                         snapshot=snapshot, host_id=args.host_id, max_age=args.max_age_seconds)
        print(json.dumps(report, indent=2, ensure_ascii=True, default=str))
        return 0
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        print(json.dumps({"schema_version": 1, "status": "error", "diagnostics": [str(exc)]}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
