#!/usr/bin/env python3
"""Read-only GitHub PR watcher with durable, explicitly acknowledged JSON events.

Uses Python 3.10+ and an authenticated GitHub CLI. The comparison policy is
adapted from T3 Code at df26ef99859ac757409f5332b185a89cc7f40267; see ../NOTICE.txt.
It never edits a checkout, posts comments, resolves threads, or merges a PR.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterator
from urllib.parse import urlsplit
import uuid

VERSION = 1
FAILURES = {"failure", "cancelled", "action-required"}
PASSED = {"success", "neutral", "skipped"}
COMMENT_LIMIT = 10
READ_FAILURE_LIMIT = 8
PAGE_INFO = "pageInfo { hasNextPage endCursor }"


class WatchError(Exception):
    """An invalid target, incomplete read, or unavailable local state."""


class ApiError(WatchError):
    """A failed GitHub read, optionally carrying a rate-limit retry time."""

    def __init__(self, message: str, retry_at: float | None = None):
        super().__init__(message)
        self.retry_at = retry_at


@dataclass(frozen=True)
class Target:
    """The base repository that owns a PR number, including fork PRs."""

    host: str
    owner: str
    repo: str
    number: int

    @property
    def key(self) -> str:
        """Return a stable identity for persistence and emitted events."""
        return f"{self.host}/{self.owner}/{self.repo}#{self.number}".lower()

    @property
    def variables(self) -> dict[str, Any]:
        """Return GraphQL variables without interpolating repository names."""
        return {"owner": self.owner, "repo": self.repo, "number": self.number}

    @property
    def root(self) -> str:
        """Return the repository's REST path."""
        return f"repos/{self.owner}/{self.repo}"


def parse_target(value: str, host: str = "github.com") -> Target:
    """Accept a PR URL or OWNER/REPO#NUMBER; never infer a fork's PR identity."""
    if value.startswith("https://"):
        url = urlsplit(value)
        if url.username or url.password or url.port or url.query:
            raise WatchError("Use an HTTPS PR URL without credentials, port, or query.")
        host = url.hostname or ""
        match = re.fullmatch(r"/([^/]+)/([^/]+)/pull/([1-9][0-9]*)/?", url.path)
    else:
        match = re.fullmatch(r"([^/]+)/([^/#]+)#([1-9][0-9]*)", value)
    if not match or not re.fullmatch(r"[a-zA-Z0-9.-]+", host):
        raise WatchError("Specify https://HOST/OWNER/REPO/pull/NUMBER or OWNER/REPO#NUMBER.")
    owner, repo, number = match.groups()
    if any(not re.fullmatch(r"[a-zA-Z0-9_.-]+", part) or part in {".", ".."}
           for part in (owner, repo)):
        raise WatchError("Invalid repository selector.")
    return Target(host.lower(), owner, repo, int(number))


def check_status(node: dict[str, Any]) -> str:
    """Normalize check runs and legacy statuses without treating unknown as green."""
    if node.get("__typename") == "CheckRun" and node.get("status") != "COMPLETED":
        return "pending"
    value = (node.get("conclusion") or node.get("state") or "").upper()
    return {
        "SUCCESS": "success", "NEUTRAL": "neutral", "SKIPPED": "skipped",
        "FAILURE": "failure", "ERROR": "failure", "TIMED_OUT": "failure",
        "STARTUP_FAILURE": "failure", "CANCELLED": "cancelled",
        "ACTION_REQUIRED": "action-required",
    }.get(value, "pending")


def normalize_checks(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Use the newest attempt for each named check from the same app and workflow."""
    checks: dict[str, dict[str, Any]] = {}
    for node in nodes:
        suite = node.get("checkSuite") or {}
        workflow = ((suite.get("workflowRun") or {}).get("workflow") or {}).get("name", "")
        app = (suite.get("app") or {}).get("slug", "")
        name = node.get("name") or node.get("context")
        if not name:
            raise WatchError("GitHub returned a check without a name.")
        key = json.dumps([node["__typename"], app, workflow, name], separators=(",", ":"))
        check = {
            "key": key, "id": node["id"], "name": name,
            "status": check_status(node), "required": node.get("isRequired") is True,
            "url": node.get("detailsUrl") or node.get("targetUrl"),
            "at": node.get("startedAt") or node.get("createdAt") or "",
            "completed_at": node.get("completedAt"),
        }
        # GitHub connection order breaks ties when runs have identical start times.
        if key not in checks or check["at"] >= checks[key]["at"]:
            checks[key] = check
    return list(checks.values())


def digest(value: Any) -> str:
    """Hash JSON content consistently, including bot edits without timestamp changes."""
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()


def evaluate(previous: dict[str, Any] | None, current: dict[str, Any],
             wakes: int = 0) -> tuple[list[dict[str, Any]], int]:
    """Compare complete snapshots; return new events and the comment-only wake count.

    A first read reports existing remarks for the initial RRR pass. Comparison
    includes each remark's content, avoiding timestamp-watermark loss for late
    pages or edits. Events remain pending until the consumer acknowledges them.
    An unknown conflict answer retains the previous conflict in current in place.
    """
    events: list[dict[str, Any]] = []
    if current["state"] != "OPEN":
        return [{"kind": current["state"].lower()}], 0
    moved = previous is not None and previous["head_sha"] != current["head_sha"]
    old_checks = {} if previous is None or moved else {
        check["key"]: check for check in previous["checks"]
    }
    if moved:
        events.append({"kind": "head-changed", "previous_head_sha": previous["head_sha"]})
    failed = [check for check in current["checks"] if check["status"] in FAILURES and (
        check["key"] not in old_checks or
        old_checks[check["key"]]["status"] not in FAILURES or
        old_checks[check["key"]]["id"] != check["id"] or
        old_checks[check["key"]].get("at") != check.get("at") or
        old_checks[check["key"]].get("completed_at") != check.get("completed_at")
    )]
    if failed:
        events.append({"kind": "checks-failed", "checks": failed})

    def gate(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [check for check in checks if check["required"]] or checks

    required = any(check["required"] for check in current["checks"])
    gate_now = gate(current["checks"])
    old_gate = gate(list(old_checks.values()))
    green = bool(gate_now) and all(check["status"] in PASSED for check in gate_now)
    old_green = bool(old_gate) and all(check["status"] in PASSED for check in old_gate)
    pending = [check for check in gate_now if check["status"] == "pending"]
    if previous is not None and not moved and old_green and pending:
        events.append({"kind": "checks-pending", "checks": pending})
    grew = required and bool({check["key"] for check in gate_now} - {
        check["key"] for check in old_gate
    })
    if green and (not old_green or grew):
        events.append({"kind": "checks-passed", "required": required, "count": len(gate_now)})

    old_remarks = (previous or {}).get("remarks", {})
    fresh = [remark for key, remark in current["remarks"].items()
             if remark["author"].lower() != current["viewer"].lower()
             and old_remarks.get(key, {}).get("fingerprint") != remark["fingerprint"]]
    if fresh:
        events.append({"kind": "remarks", "remarks": fresh})
    old_threads = (previous or {}).get("threads", {})
    changed_threads = [thread for key, thread in current["threads"].items()
                       if key in old_threads and (
                           thread["resolved"] != old_threads[key]["resolved"] or
                           thread["outdated"] != old_threads[key]["outdated"])]
    if changed_threads:
        events.append({"kind": "thread-state", "threads": changed_threads})
    was_conflicting = (previous or {}).get("mergeability") == "CONFLICTING"
    if current["mergeability"] == "CONFLICTING" and not was_conflicting:
        events.append({"kind": "conflicting", "base_branch": current["base_branch"]})
    # An unknown answer is computation in progress, not a resolved conflict.
    if current["mergeability"] == "UNKNOWN" and was_conflicting:
        current["mergeability"] = "CONFLICTING"
    comments_only = bool(events) and all(event["kind"] == "remarks" for event in events)
    wakes = wakes + 1 if comments_only else (0 if events or moved else wakes)
    if comments_only and wakes >= COMMENT_LIMIT:
        events.append({"kind": "watch-stopped", "reason": "comment-limit"})
    return events, wakes


class GitHubClient:
    """Read GitHub through gh, with persisted REST validators and bounded commands."""

    def __init__(self, target: Target, validators: dict[str, Any], gh: str = "gh"):
        self.target, self.validators, self.gh = target, validators, gh

    def run(self, args: list[str], body: str | None = None) -> subprocess.CompletedProcess[str]:
        """Execute argument arrays without a shell or exposing credential values."""
        try:
            return subprocess.run([self.gh, *args], input=body, capture_output=True,
                                  text=True, encoding="utf-8", timeout=60, check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ApiError(f"GitHub CLI unavailable or timed out: {type(error).__name__}") from error

    def authenticate(self) -> None:
        """Verify GitHub CLI authentication for the active account."""
        result = self.run(["auth", "status", "--active", "--hostname", self.target.host])
        if result.returncode:
            raise ApiError("Active GitHub authentication failed; authenticate gh or use Joydex.")

    def request(self, endpoint: str, body: dict[str, Any] | None = None,
                etag: str | None = None) -> tuple[int, dict[str, str], Any]:
        """Read JSON and response headers; rate-limit errors carry a retry deadline."""
        args = ["api", "--hostname", self.target.host, "--include", endpoint]
        if body is not None:
            args += ["--input", "-"]
        if etag:
            args += ["-H", f"If-None-Match: {etag}"]
        result = self.run(args, json.dumps(body) if body is not None else None)
        raw = result.stdout.replace("\r\n", "\n")
        headers: dict[str, str] = {}
        status = 0
        if raw.startswith("HTTP/"):
            head, _, raw = raw.partition("\n\n")
            lines = head.splitlines()
            status = int(lines[0].split()[1])
            headers = {key.strip().lower(): value.strip() for line in lines[1:]
                       if ":" in line for key, value in [line.split(":", 1)]}
        try:
            payload = json.loads(raw) if raw.strip() else None
        except json.JSONDecodeError as error:
            if status == 429 or (status == 403 and headers.get("x-ratelimit-remaining") == "0"):
                payload = None  # Some rate-limit responses are HTML, but the headers still apply.
            else:
                raise ApiError("GitHub CLI returned invalid JSON.") from error
        # gh can exit nonzero for a successful conditional read with no response body.
        if status == 304 and body is None and etag:
            return status, headers, None
        errors = payload.get("errors") if isinstance(payload, dict) else None
        # Review bodies may themselves mention rate limits. Only error messages and
        # transport headers establish that GitHub refused a request.
        message = (json.dumps(errors or (payload.get("message", "") if isinstance(payload, dict)
                                       else "")) + result.stderr)
        limited = (status == 429 or headers.get("x-ratelimit-remaining") == "0" or
                   "rate limit" in message.lower() or '"RATE_LIMITED"' in message)
        if limited and (result.returncode or status >= 400 or errors):
            now = time.time()
            retry_at = now + 60
            if headers.get("retry-after", "").isdigit():
                retry_at = max(retry_at, now + int(headers["retry-after"]))
            if headers.get("x-ratelimit-remaining") == "0":
                retry_at = max(retry_at, float(headers.get("x-ratelimit-reset", now + 60)))
            raise ApiError("GitHub rate limited this credential.", retry_at)
        if result.returncode or status >= 400:
            raise ApiError(f"GitHub read failed (HTTP {status or 'unknown'}); check gh access.")
        if isinstance(payload, dict) and payload.get("errors"):
            raise ApiError("GitHub GraphQL returned errors; the partial response was discarded.")
        return status, headers, payload

    def graphql(self, selection: str, variables: dict[str, Any] | None = None,
                declaration: str = "") -> dict[str, Any]:
        """Execute a read-only PR selection with separately encoded variables."""
        query = ("query($owner: String!, $repo: String!, $number: Int!" + declaration +
                 ") { viewer { login } repository(owner: $owner, name: $repo) { " +
                 "pullRequest(number: $number) { " + selection + " } } }")
        values = {**self.target.variables, **(variables or {})}
        _, _, payload = self.request("graphql", {"query": query, "variables": values})
        data = (payload or {}).get("data")
        if not data or not (data.get("repository") or {}).get("pullRequest"):
            raise ApiError("GitHub returned no accessible PR or node.")
        return data

    @staticmethod
    def page(connection: dict[str, Any], seen: set[str]) -> str | None:
        """Validate a connection and refuse missing, repeated, or truncated cursors."""
        if not isinstance(connection.get("nodes"), list) or "pageInfo" not in connection:
            raise ApiError("Incomplete GitHub connection.")
        info = connection["pageInfo"]
        if not info["hasNextPage"]:
            return None
        cursor = info.get("endCursor")
        if not cursor or cursor in seen or len(seen) >= 1000:
            raise ApiError("GitHub pagination did not advance.")
        seen.add(cursor)
        return cursor

    def rest_list(self, endpoint: str) -> list[dict[str, Any]]:
        """Read every REST page, reusing a cached body only after HTTP 304."""
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        endpoint += "?per_page=100"
        while endpoint:
            if endpoint in seen or len(seen) >= 1000:
                raise ApiError("GitHub REST pagination did not advance.")
            seen.add(endpoint)
            previous = self.validators.get(endpoint, {})
            status, headers, payload = self.request(endpoint, etag=previous.get("etag"))
            if status == 304:
                if "body" not in previous:
                    raise ApiError("A conditional response has no cached body.")
                payload = previous["body"]
                link = headers.get("link", previous.get("link", ""))
            else:
                link = headers.get("link", "")
            if not isinstance(payload, list):
                raise ApiError("GitHub returned an incomplete REST list.")
            self.validators[endpoint] = {"etag": (headers.get("etag", previous.get("etag"))
                                                  if status == 304 else headers.get("etag")),
                                         "link": link, "body": payload}
            items.extend(payload)
            next_url = re.search(r'<([^>]+)>;\s*rel="next"', link)
            if not next_url:
                break
            url = urlsplit(next_url[1])
            expected = "api.github.com" if self.target.host == "github.com" else self.target.host
            prefix = "/" if self.target.host == "github.com" else "/api/v3/"
            if url.scheme != "https" or url.netloc != expected or not url.path.startswith(prefix):
                raise ApiError("GitHub pagination points outside the selected API host.")
            endpoint = url.path[len(prefix):] + ("?" + url.query if url.query else "")
        return items

    def snapshot(self) -> dict[str, Any]:
        """Fetch complete checks, remarks, and thread states for one PR head."""
        required = "isRequired(pullRequestNumber: $number)" if self.target.host == "github.com" else ""
        check_nodes = ("nodes { __typename ... on CheckRun { id name status conclusion "
                       "startedAt completedAt detailsUrl " + required +
                       " checkSuite { app { slug } workflowRun { workflow { name } } } } "
                       "... on StatusContext { id context state targetUrl createdAt " + required + " } }")
        selection = ("number url state headRefOid headRefName baseRefName mergeable "
                     "headRepository { nameWithOwner } "
                     "commits(last: 1) { nodes { commit { id oid statusCheckRollup { "
                     "contexts(first: 100) { " + PAGE_INFO + check_nodes + " } } } } }")
        data = self.graphql(selection)
        pr = data["repository"]["pullRequest"]
        viewer = (data.get("viewer") or {}).get("login")
        if not viewer:
            raise ApiError("GitHub did not identify the authenticated viewer.")
        checks: list[dict[str, Any]] = []
        if pr["state"] == "OPEN":
            commits = pr["commits"]["nodes"]
            if not commits or commits[0]["commit"]["oid"] != pr["headRefOid"]:
                raise ApiError("The head commit and check snapshot disagree; retry the read.")
            commit = commits[0]["commit"]
            connection = (commit.get("statusCheckRollup") or {}).get("contexts")
            seen: set[str] = set()
            # Later pages must still describe the same PR head.
            while connection is not None:
                checks.extend(connection["nodes"])
                cursor = self.page(connection, seen)
                if cursor is None:
                    break
                # Requiredness needs the PR number, so use the PR query and verify its head.
                page = self.graphql("headRefOid commits(last: 1) { nodes { commit { "
                                    "statusCheckRollup { contexts(first: 100, after: $cursor) { " +
                                    PAGE_INFO + check_nodes + " } } } } }",
                                    {"cursor": cursor}, ", $cursor: String")
                paged_pr = page["repository"]["pullRequest"]
                if paged_pr["headRefOid"] != pr["headRefOid"]:
                    raise ApiError("The PR head moved during check pagination; retry.")
                connection = paged_pr["commits"]["nodes"][0]["commit"]["statusCheckRollup"]["contexts"]

        threads: dict[str, Any] = {}
        remarks: dict[str, Any] = {}
        if pr["state"] == "OPEN":
            cursor = None
            seen = set()
            while True:
                data = self.graphql("reviewThreads(first: 100, after: $cursor) { " + PAGE_INFO +
                    " nodes { id isResolved isOutdated path line comments(first: 1) { "
                    "totalCount nodes { id } } } }", {"cursor": cursor}, ", $cursor: String")
                connection = data["repository"]["pullRequest"]["reviewThreads"]
                for thread in connection["nodes"]:
                    roots = thread["comments"]["nodes"]
                    if not roots:
                        raise ApiError("GitHub returned a review thread without its root.")
                    threads[thread["id"]] = {
                        "id": thread["id"], "resolved": thread["isResolved"],
                        "outdated": thread["isOutdated"], "path": thread["path"],
                        "line": thread["line"], "root_id": roots[0]["id"],
                        "comment_count": thread["comments"]["totalCount"],
                    }
                cursor = self.page(connection, seen)
                if cursor is None:
                    break
            conversation = self.rest_list(f"{self.target.root}/issues/{self.target.number}/comments")
            reviews = self.rest_list(f"{self.target.root}/pulls/{self.target.number}/reviews")
            inline = self.rest_list(f"{self.target.root}/pulls/{self.target.number}/comments")
            roots = {thread["root_id"]: thread["id"] for thread in threads.values()}
            numeric = {comment["id"]: comment for comment in inline}
            counts = dict.fromkeys(threads, 0)
            for kind, items in (("comment", conversation), ("review", reviews), ("inline", inline)):
                for item in items:
                    if kind == "review" and item.get("state") == "PENDING":
                        continue  # An unsubmitted draft is not published review activity.
                    thread_id = None
                    if kind == "inline":
                        root = numeric.get(item.get("in_reply_to_id"), item)
                        thread_id = roots.get(root["node_id"])
                        if thread_id is None:
                            raise ApiError("Thread and comment reads disagree; retry the complete read.")
                        counts[thread_id] += 1
                    key = f"{kind}:{item['node_id']}"
                    remarks[key] = {
                        "id": item["node_id"], "kind": kind,
                        "author": (item.get("user") or {}).get("login") or "",
                        "url": item.get("html_url"), "thread_id": thread_id,
                        "path": item.get("path"),
                        "fingerprint": digest([item.get("body"), item.get("updated_at"),
                                               item.get("state")]),
                    }
            if any(counts[key] != thread["comment_count"] for key, thread in threads.items()):
                raise ApiError("A review thread's comments are incomplete; retry without advancing state.")
        return {
            "viewer": viewer, "url": pr["url"], "state": pr["state"],
            "head_sha": pr["headRefOid"], "head_branch": pr["headRefName"],
            "head_repository": (pr.get("headRepository") or {}).get("nameWithOwner"),
            "base_branch": pr["baseRefName"], "mergeability": pr["mergeable"] or "UNKNOWN",
            "checks": normalize_checks(checks), "threads": threads, "remarks": remarks,
        }


def default_state_dir() -> Path:
    """Choose a private user state directory outside repositories and installed skills."""
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local"))) / "rrr-pr-watch"
    return Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "rrr-pr-watch"


class Store:
    """Persist snapshots and pending events atomically, serialized by an OS lock."""

    def __init__(self, root: Path, target: Target):
        self.root, self.target = root, target
        self.path = root / (digest(target.key)[:24] + ".json")

    @contextmanager
    def locked(self) -> Iterator[None]:
        """Hold a nonblocking process lock that the OS releases after a crash."""
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.path.with_suffix(".lock").open("a+b") as handle:
            handle.seek(0, 2)
            if handle.tell() == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                raise WatchError("Another command is reading this PR; try again after it finishes.") from error
            try:
                yield
            finally:
                handle.seek(0)
                if os.name == "nt":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def load(self) -> dict[str, Any]:
        """Read saved state; refuse corruption rather than dropping pending events."""
        if not self.path.exists():
            return {"version": VERSION, "target": self.target.key, "snapshot": None,
                    "pending": [], "validators": {}, "wakes": 0, "failures": 0,
                    "rate_limits": 0, "paused_until": 0, "stopped": None}
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
            if state["version"] != VERSION or state["target"] != self.target.key:
                raise ValueError("incompatible identity or version")
            for key in ("snapshot", "pending", "validators", "wakes", "failures",
                        "rate_limits", "paused_until", "stopped"):
                state[key]
            if (not isinstance(state["pending"], list) or not isinstance(state["validators"], dict)
                    or state["snapshot"] is not None and not isinstance(state["snapshot"], dict)
                    or any(not isinstance(event, dict) or not isinstance(event.get("event_id"), str)
                           or not event["event_id"]
                           for event in state["pending"])):
                raise ValueError("invalid event queue or snapshot")
            if len({event["event_id"] for event in state["pending"]}) != len(state["pending"]):
                raise ValueError("duplicate pending event IDs")
            if any(not isinstance(state[key], int) or state[key] < 0
                   for key in ("wakes", "failures", "rate_limits")):
                raise ValueError("invalid counters")
            if not isinstance(state["paused_until"], (int, float)) or not math.isfinite(state["paused_until"]):
                raise ValueError("invalid pause deadline")
            if state["snapshot"] is not None and not {
                "viewer", "head_sha", "checks", "threads", "remarks", "mergeability"
            } <= state["snapshot"].keys():
                raise ValueError("incomplete snapshot")
            return state
        except (ValueError, KeyError, TypeError) as error:
            raise WatchError("Invalid watcher state; preserve it and use a new state directory.") from error

    def save(self, state: dict[str, Any]) -> None:
        """Atomically write the complete PR snapshot and pending event queue to JSON."""
        descriptor, temporary = tempfile.mkstemp(prefix=self.path.stem, suffix=".tmp", dir=self.root)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2, allow_nan=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def result(store: Store, state: dict[str, Any], status: str, **extra: Any) -> dict[str, Any]:
    """Return the stable machine-readable response shared by all subcommands."""
    return {"target": store.target.key, "status": status, "state_file": str(store.path),
            "events": state["pending"], "stopped": state["stopped"], **extra}


def enqueue(state: dict[str, Any], events: list[dict[str, Any]], target: Target) -> None:
    """Give events durable IDs before they can be printed or acknowledged."""
    snapshot = state["snapshot"] or {}
    for event in events:
        state["pending"].append({**event, "event_id": str(uuid.uuid4()), "target": target.key,
                                 "head_sha": snapshot.get("head_sha"),
                                 "observed_at": time.time()})


def poll(store: Store, gh: str = "gh") -> dict[str, Any]:
    """Read once, or redeliver pending events without spending another API request."""
    with store.locked():
        state = store.load()
        if state["pending"]:
            return result(store, state, "events")
        if state["stopped"]:
            return result(store, state, "stopped")
        if state["paused_until"] > time.time():
            return result(store, state, "paused", retry_at=state["paused_until"])
        candidate = deepcopy(state)
        client = GitHubClient(store.target, candidate["validators"], gh)
        try:
            client.authenticate()
            current = client.snapshot()
            old = state["snapshot"]
            if old and old["viewer"].lower() != current["viewer"].lower():
                raise WatchError("GitHub account changed; use a separate state directory for this account.")
            if (old and old["head_sha"] == current["head_sha"] and old["checks"]
                    and not current["checks"] and current["state"] == "OPEN"):
                raise ApiError("Previously observed checks are missing; retry without advancing state.")
            events, candidate["wakes"] = evaluate(old, current, state["wakes"])
            candidate.update(snapshot=current, failures=0, rate_limits=0, paused_until=0)
            enqueue(candidate, events, store.target)
            if current["state"] != "OPEN":
                candidate["stopped"] = current["state"].lower()
            elif candidate["wakes"] >= COMMENT_LIMIT:
                candidate["stopped"] = "comment-limit"
            store.save(candidate)
            return result(store, candidate, "events" if events else "quiet")
        except ApiError as error:
            # Discard partial validators with the partial snapshot. Otherwise a later 304
            # could hide remarks we never committed to the pending event queue.
            if error.retry_at is not None:
                state["rate_limits"] += 1
                delay = min(3600, 60 * 2 ** min(state["rate_limits"] - 1, 6))
                state["paused_until"] = max(error.retry_at, time.time() + delay)
                store.save(state)
                return result(store, state, "paused", retry_at=state["paused_until"], error=str(error))
            state["failures"] += 1
            if state["failures"] >= READ_FAILURE_LIMIT:
                state["stopped"] = "unreadable"
                enqueue(state, [{"kind": "watch-stopped", "reason": "unreadable"}], store.target)
            store.save(state)
            return result(store, state, "events" if state["pending"] else "retry",
                          failures=state["failures"], error=str(error))


def acknowledge(store: Store, ids: list[str]) -> dict[str, Any]:
    """Remove only specified pending events; unknown IDs fail without changing state."""
    with store.locked():
        state = store.load()
        known = {event["event_id"] for event in state["pending"]}
        if not set(ids) <= known:
            raise WatchError("An event ID is not pending; no events were acknowledged.")
        state["pending"] = [event for event in state["pending"] if event["event_id"] not in ids]
        store.save(state)
        return result(store, state, "acknowledged", acknowledged=ids)


def wait(store: Store, gh: str, interval: float, timeout: float) -> dict[str, Any]:
    """Poll quietly until an event, error, stop, or bounded waiting deadline."""
    deadline = time.monotonic() + timeout
    while True:
        response = poll(store, gh)
        if response["status"] not in {"quiet", "paused"}:
            return response
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return {**response, "status": "timeout"}
        delay = max(interval, response.get("retry_at", 0) - time.time())
        # Short chunks keep Ctrl+C responsive without polling GitHub before the deadline.
        wake_at = time.monotonic() + min(delay, remaining)
        while time.monotonic() < wake_at:
            time.sleep(max(0, min(1, wake_at - time.monotonic())))
        if time.monotonic() >= deadline:
            return {**response, "status": "timeout"}


def main(argv: list[str] | None = None) -> int:
    """Run the helper; operational errors use exit 2 and pending events stay saved."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("poll", "wait", "ack", "stop", "resume"))
    parser.add_argument("pr", help="PR URL or OWNER/REPO#NUMBER (base repository)")
    parser.add_argument("event_ids", nargs="*", help="Only for ack: event IDs that were handled")
    parser.add_argument("--host", default="github.com", help="Host for OWNER/REPO#NUMBER")
    parser.add_argument("--state-dir", type=Path, default=default_state_dir())
    parser.add_argument("--gh", default="gh", help="GitHub CLI executable")
    parser.add_argument("--interval", type=float, default=120, help="Seconds between wait reads (minimum 60)")
    parser.add_argument("--timeout", type=float, default=600, help="Maximum wait duration in seconds")
    args = parser.parse_args(argv)
    if args.command == "ack" and not args.event_ids:
        parser.error("ack requires explicit event IDs")
    if args.command != "ack" and args.event_ids:
        parser.error("event IDs are accepted only by ack")
    if not math.isfinite(args.interval) or not math.isfinite(args.timeout) or args.interval < 60 or args.timeout <= 0:
        parser.error("interval must be at least 60 and timeout must be positive")
    try:
        store = Store(args.state_dir.expanduser().resolve(), parse_target(args.pr, args.host))
        if args.command == "ack":
            response = acknowledge(store, args.event_ids)
        elif args.command in {"stop", "resume"}:
            with store.locked():
                state = store.load()
                if args.command == "stop":
                    state["stopped"] = "manual"
                else:
                    state.update(stopped=None, wakes=0, failures=0)
                store.save(state)
                response = result(store, state, "stopped" if args.command == "stop" else "resumed")
        elif args.command == "wait":
            response = wait(store, args.gh, args.interval, args.timeout)
        else:
            response = poll(store, args.gh)
        print(json.dumps(response, ensure_ascii=False))
        return 2 if response["status"] == "retry" else 0
    except (WatchError, OSError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
