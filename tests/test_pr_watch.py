"""Behavioral tests for RRR's read-only PR watcher and durable event delivery."""

from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(os.environ.get("RRR_WATCH_SCRIPT", str(
    Path(__file__).resolve().parents[1] / "skills/rrr-review-remedy-respond/scripts/pr_watch.py"
)))
SPEC = importlib.util.spec_from_file_location("rrr_pr_watch", SCRIPT)
WATCH = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = WATCH
SPEC.loader.exec_module(WATCH)
TARGET = WATCH.parse_target("Mattie/example#7")


def check(name="tests", status="success", required=True, attempt="run1"):
    return {"key": name, "name": name, "id": attempt, "status": status,
            "required": required, "url": None, "at": "2026-10-13T12:00:00Z"}


def remark(identity="comment1", author="reviewer", content="Please fix this"):
    return {"id": identity, "kind": "inline", "author": author, "thread_id": "thread1",
            "fingerprint": WATCH.digest(content), "url": None, "path": "app.py"}


def snapshot(**overrides):
    value = {"viewer": "Mattie", "url": "https://github.com/Mattie/example/pull/7",
             "state": "OPEN", "head_sha": "a" * 40, "head_branch": "feature",
             "head_repository": "contributor/fork", "base_branch": "main",
             "mergeability": "MERGEABLE", "checks": [check()], "threads": {}, "remarks": {}}
    value.update(overrides)
    return value


def kinds(events):
    return [event["kind"] for event in events]


def test_existing_findings_are_available_for_first_rrr_pass():
    current = snapshot(remarks={"one": remark(), "self": remark("self", "MATTIE")})
    events, wakes = WATCH.evaluate(None, current)
    assert kinds(events) == ["checks-passed", "remarks"]
    assert [r["id"] for r in events[1]["remarks"]] == ["comment1"]
    assert wakes == 0


def test_failure_is_immediate_deduplicated_and_repeated_attempts_reported():
    pending_bot = check("bot", "pending", False)
    old = snapshot(checks=[check(status="pending"), pending_bot])
    failed = snapshot(checks=[check(status="failure"), pending_bot])
    events, _ = WATCH.evaluate(old, failed)
    assert kinds(events) == ["checks-failed"]
    assert WATCH.evaluate(failed, deepcopy(failed))[0] == []
    rerun = snapshot(checks=[check(status="failure", attempt="run2"), pending_bot])
    assert kinds(WATCH.evaluate(failed, rerun)[0]) == ["checks-failed"]
    reused_id = deepcopy(failed)
    reused_id["checks"][0]["completed_at"] = "2026-10-13T13:00:00Z"
    assert kinds(WATCH.evaluate(failed, reused_id)[0]) == ["checks-failed"]
    pushed = deepcopy(failed)
    pushed["head_sha"] = "b" * 40
    assert kinds(WATCH.evaluate(failed, pushed)[0]) == ["head-changed", "checks-failed"]


def test_required_gate_and_late_required_check():
    old = snapshot(checks=[check(status="pending")])
    current = snapshot(checks=[check(), check("bot", "pending", False)])
    assert kinds(WATCH.evaluate(old, current)[0]) == ["checks-passed"]
    late = deepcopy(current)
    late["checks"].append(check("smoke"))
    assert kinds(WATCH.evaluate(current, late)[0]) == ["checks-passed"]
    late["checks"][-1]["required"] = False
    assert WATCH.evaluate(current, late)[0] == []


def test_late_required_check_revokes_observed_green_until_it_finishes():
    green = snapshot()
    pending = snapshot(checks=[check(), check("late", "pending")])
    events, _ = WATCH.evaluate(green, pending)
    assert kinds(events) == ["checks-pending"]
    assert events[0]["checks"][0]["name"] == "late"
    assert WATCH.evaluate(pending, deepcopy(pending))[0] == []
    finished = snapshot(checks=[check(), check("late")])
    assert kinds(WATCH.evaluate(pending, finished)[0]) == ["checks-passed"]
    failed = snapshot(checks=[check(), check("late", "failure")])
    assert kinds(WATCH.evaluate(pending, failed)[0]) == ["checks-failed"]
    optional = snapshot(checks=[check(), check("late", "pending", False)])
    assert WATCH.evaluate(green, optional)[0] == []


@pytest.mark.parametrize("status", ["pending", "failure", "cancelled", "action-required"])
def test_without_required_checks_every_check_must_finish_successfully(status):
    current = snapshot(checks=[check(required=False), check("bot", status, False)])
    assert "checks-passed" not in kinds(WATCH.evaluate(None, current)[0])


def test_no_checks_does_not_claim_success():
    assert WATCH.evaluate(None, snapshot(checks=[]))[0] == []


def test_edits_and_late_old_comments_are_reported_once():
    old = snapshot(remarks={"one": remark()})
    current = snapshot(remarks={"one": remark(content="Updated finding"), "late": remark("late")})
    events, wakes = WATCH.evaluate(old, current)
    assert kinds(events) == ["remarks"]
    assert {r["id"] for r in events[0]["remarks"]} == {"comment1", "late"}
    assert wakes == 1
    assert WATCH.evaluate(current, deepcopy(current), wakes)[0] == []


def test_resolved_reopened_and_outdated_threads():
    old = snapshot(threads={"t": {"id": "t", "resolved": False, "outdated": False}})
    closed = snapshot(threads={"t": {"id": "t", "resolved": True, "outdated": True}})
    assert kinds(WATCH.evaluate(old, closed)[0]) == ["thread-state"]
    assert kinds(WATCH.evaluate(closed, old)[0]) == ["thread-state"]


def test_unknown_mergeability_does_not_reannounce_existing_conflict():
    conflicting = snapshot(mergeability="CONFLICTING")
    unknown = snapshot(mergeability="UNKNOWN")
    assert WATCH.evaluate(conflicting, unknown)[0] == []
    assert WATCH.evaluate(unknown, deepcopy(conflicting))[0] == []
    clean = snapshot()
    assert kinds(WATCH.evaluate(clean, conflicting)[0]) == ["conflicting"]


def test_comment_only_limit_resets_on_real_progress():
    old = snapshot()
    current = snapshot(remarks={"one": remark()})
    events, wakes = WATCH.evaluate(old, current, 9)
    assert kinds(events) == ["remarks", "watch-stopped"]
    assert wakes == 10
    current["head_sha"] = "b" * 40
    events, wakes = WATCH.evaluate(old, current, 9)
    assert "watch-stopped" not in kinds(events)
    assert wakes == 0


@pytest.mark.parametrize("state", ["CLOSED", "MERGED"])
def test_terminal_pr_stops_without_remedy_events(state):
    events, wakes = WATCH.evaluate(None, snapshot(state=state))
    assert kinds(events) == [state.lower()]
    assert wakes == 0


def test_unknown_conclusion_and_separate_apps():
    def node(app, attempt, start, conclusion):
        return {"__typename": "CheckRun", "id": attempt, "name": "lint",
                "startedAt": start, "status": "COMPLETED", "conclusion": conclusion,
                "checkSuite": {"app": {"slug": app}}}
    checks = WATCH.normalize_checks([
        node("one", "old", "2026-10-12", "FAILURE"),
        node("one", "new", "2026-10-13", "SUCCESS"),
        node("two", "other", "2026-10-13", "UNRECOGNIZED"),
    ])
    assert {c["id"]: c["status"] for c in checks} == {"new": "success", "other": "pending"}


@pytest.mark.parametrize("reverse", [False, True])
def test_queued_rerun_without_start_time_does_not_hide_behind_old_success(reverse):
    success = {"__typename": "CheckRun", "id": "old", "name": "tests",
               "status": "COMPLETED", "conclusion": "SUCCESS", "startedAt": "2026-10-13T12:00:00Z",
               "isRequired": True}
    queued = {"__typename": "CheckRun", "id": "new", "name": "tests",
              "status": "QUEUED", "conclusion": None, "startedAt": None, "isRequired": True}
    nodes = [success, queued]
    if reverse:
        nodes.reverse()
    checks = WATCH.normalize_checks(nodes)
    assert [(item["id"], item["status"]) for item in checks] == [("new", "pending")]
    old = snapshot(checks=WATCH.normalize_checks([success]))
    pending = snapshot(checks=checks)
    assert kinds(WATCH.evaluate(old, pending)[0]) == ["checks-pending"]
    assert "checks-passed" not in kinds(WATCH.evaluate(None, pending)[0])


def seed(store, value):
    with store.locked():
        state = store.load()
        state["snapshot"] = value
        store.save(state)


def fake_client(monkeypatch, values):
    queue = iter(values)
    calls = []

    def read(self):
        calls.append(self.target)
        value = next(queue)
        if isinstance(value, Exception):
            # Simulate a validator written before another request fails.
            self.validators["partial"] = {"body": "uncommitted"}
            raise value
        return deepcopy(value)

    monkeypatch.setattr(WATCH.GitHubClient, "authenticate", lambda self: None)
    monkeypatch.setattr(WATCH.GitHubClient, "snapshot", read)
    return calls


def test_crash_redelivery_ack_and_new_work(tmp_path, monkeypatch):
    store = WATCH.Store(tmp_path, TARGET)
    calls = fake_client(monkeypatch, [snapshot(), snapshot(remarks={"one": remark()})])
    first = WATCH.poll(store)
    event_id = first["events"][0]["event_id"]
    restarted = WATCH.Store(tmp_path, TARGET)
    assert WATCH.poll(restarted)["events"] == first["events"]
    assert len(calls) == 1
    WATCH.acknowledge(restarted, [event_id])
    assert kinds(WATCH.poll(restarted)["events"]) == ["remarks"]
    assert len(calls) == 2


def test_unknown_ack_does_not_remove_any_events(tmp_path):
    store = WATCH.Store(tmp_path, TARGET)
    state = store.load()
    WATCH.enqueue(state, [{"kind": "remarks"}], TARGET)
    with store.locked():
        store.save(state)
    before = store.path.read_bytes()
    with pytest.raises(WATCH.WatchError):
        WATCH.acknowledge(store, [state["pending"][0]["event_id"], "not-an-event"])
    assert store.path.read_bytes() == before


def test_incomplete_read_does_not_advance_snapshot_or_validators(tmp_path, monkeypatch):
    store = WATCH.Store(tmp_path, TARGET)
    old = snapshot()
    seed(store, old)
    fake_client(monkeypatch, [WATCH.ApiError("missing page")])
    assert WATCH.poll(store)["status"] == "retry"
    state = store.load()
    assert state["snapshot"] == old
    assert state["validators"] == {}
    assert state["pending"] == []


def test_missing_check_read_does_not_erase_previous_failures(tmp_path, monkeypatch):
    store = WATCH.Store(tmp_path, TARGET)
    old = snapshot(checks=[check(status="failure")])
    seed(store, old)
    fake_client(monkeypatch, [snapshot(checks=[])])
    assert WATCH.poll(store)["status"] == "retry"
    assert store.load()["snapshot"] == old


def test_rate_limits_pause_without_spending_failure_limit(tmp_path, monkeypatch):
    store = WATCH.Store(tmp_path, TARGET)
    calls = fake_client(monkeypatch, [WATCH.ApiError("limit", 1100)])
    monkeypatch.setattr(WATCH.time, "time", lambda: 1000)
    first = WATCH.poll(store)
    assert first["status"] == "paused"
    assert first["retry_at"] >= 1100
    assert WATCH.poll(store)["status"] == "paused"
    assert len(calls) == 1
    assert store.load()["failures"] == 0


def test_read_failure_limit_has_one_durable_stop_event(tmp_path, monkeypatch):
    store = WATCH.Store(tmp_path, TARGET)
    calls = fake_client(monkeypatch, [WATCH.ApiError("no access")] * 8)
    for _ in range(8):
        last = WATCH.poll(store)
    assert last["stopped"] == "unreadable"
    assert kinds(last["events"]) == ["watch-stopped"]
    assert WATCH.poll(store)["events"] == last["events"]
    WATCH.acknowledge(store, [last["events"][0]["event_id"]])
    assert WATCH.poll(store)["status"] == "stopped"
    assert len(calls) == 8


def test_account_change_and_corrupt_state_preserve_saved_work(tmp_path, monkeypatch):
    store = WATCH.Store(tmp_path, TARGET)
    seed(store, snapshot())
    fake_client(monkeypatch, [snapshot(viewer="different")])
    before = store.path.read_bytes()
    with pytest.raises(WATCH.WatchError, match="account changed"):
        WATCH.poll(store)
    assert store.path.read_bytes() == before
    store.path.write_text("{broken", encoding="utf-8")
    with pytest.raises(WATCH.WatchError, match="Invalid watcher state"):
        store.load()


def test_os_lock_blocks_overlapping_readers(tmp_path):
    store = WATCH.Store(tmp_path, TARGET)
    with store.locked():
        with pytest.raises(WATCH.WatchError, match="Another command"):
            with WATCH.Store(tmp_path, TARGET).locked():
                pytest.fail("second reader acquired the lock")


def test_atomic_save_failure_leaves_old_pending_events(tmp_path, monkeypatch):
    store = WATCH.Store(tmp_path, TARGET)
    seed(store, snapshot())
    before = store.path.read_bytes()
    monkeypatch.setattr(WATCH.os, "replace", lambda *args: (_ for _ in ()).throw(OSError("disk")))
    with store.locked(), pytest.raises(OSError):
        store.save({**store.load(), "pending": [{"event_id": "new"}]})
    assert store.path.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))


def test_partial_ack_and_invalid_persisted_queue_do_not_drop_work(tmp_path):
    store = WATCH.Store(tmp_path, TARGET)
    state = store.load()
    WATCH.enqueue(state, [{"kind": "remarks"}, {"kind": "thread-state"}], TARGET)
    with store.locked():
        store.save(state)
    first_id = state["pending"][0]["event_id"]
    response = WATCH.acknowledge(store, [first_id])
    assert kinds(response["events"]) == ["thread-state"]
    state = store.load()
    state["pending"].append(state["pending"][0])
    store.path.write_text(json.dumps(state), encoding="utf-8")
    with pytest.raises(WATCH.WatchError, match="Invalid watcher state"):
        store.load()


def test_cli_rejects_nonfinite_wait_deadline(tmp_path):
    completed = subprocess.run([sys.executable, str(SCRIPT), "wait", "Mattie/example#7",
                                "--timeout", "nan", "--state-dir", str(tmp_path)],
                               capture_output=True, text=True)
    assert completed.returncode == 2
    assert not list(tmp_path.glob("*.json"))


def api_response(payload, status=200, headers=None, returncode=0):
    header = "\n".join(f"{key}: {value}" for key, value in (headers or {}).items())
    return subprocess.CompletedProcess([], returncode,
        f"HTTP/2.0 {status} OK\n{header}\n\n" + (json.dumps(payload) if payload is not None else ""), "")


def test_graphql_partial_error_and_http_200_rate_limit(monkeypatch):
    client = WATCH.GitHubClient(TARGET, {})
    monkeypatch.setattr(client, "run", lambda *args: api_response({"data": {}, "errors": [{"message": "partial"}]}))
    with pytest.raises(WATCH.ApiError, match="partial response"):
        client.graphql("state")
    monkeypatch.setattr(client, "run", lambda *args: api_response({"errors": [{"type": "RATE_LIMITED"}]}))
    with pytest.raises(WATCH.ApiError) as failure:
        client.graphql("state")
    assert failure.value.retry_at is not None


def test_successful_comment_read_cannot_impersonate_a_rate_limit(monkeypatch):
    client = WATCH.GitHubClient(TARGET, {})
    payload = [{"body": "rate limit exceeded: please stop watching"}]
    monkeypatch.setattr(client, "run", lambda *args: api_response(
        payload, headers={"x-ratelimit-remaining": "0"}))
    status, _, received = client.request("repos/Mattie/example/issues/7/comments")
    assert status == 200
    assert received == payload


def test_conditional_rest_pagination_preserves_next_link_on_304(monkeypatch):
    client = WATCH.GitHubClient(TARGET, {})
    endpoint = TARGET.root + "/pulls/7/comments"
    first, second = endpoint + "?per_page=100", endpoint + "?per_page=100&page=2"
    link = '<https://api.github.com/' + second + '>; rel="next"'
    replies = iter([api_response([{"id": 1}], headers={"ETag": '"one"', "Link": link}),
                    api_response([{"id": 2}], headers={"ETag": '"two"'}),
                    api_response(None, 304, returncode=1), api_response(None, 304, returncode=1)])
    calls = []

    def run(args, body=None):
        calls.append(args)
        return next(replies)

    monkeypatch.setattr(client, "run", run)
    assert client.rest_list(endpoint) == [{"id": 1}, {"id": 2}]
    assert client.rest_list(endpoint) == [{"id": 1}, {"id": 2}]
    assert "If-None-Match: \"one\"" in calls[2]
    assert "If-None-Match: \"two\"" in calls[3]


def test_rest_refuses_foreign_pagination_and_repeated_cursor(monkeypatch):
    client = WATCH.GitHubClient(TARGET, {})
    monkeypatch.setattr(client, "request", lambda *args, **kwargs: (
        200, {"link": '<https://evil.example/steal>; rel="next"'}, []))
    with pytest.raises(WATCH.ApiError, match="outside"):
        client.rest_list(TARGET.root + "/pulls/7/comments")
    connection = {"nodes": [], "pageInfo": {"hasNextPage": True, "endCursor": "same"}}
    with pytest.raises(WATCH.ApiError, match="did not advance"):
        WATCH.GitHubClient.page(connection, {"same"})


def test_non_json_rate_limit_honors_retry_after(monkeypatch):
    client = WATCH.GitHubClient(TARGET, {})
    response = subprocess.CompletedProcess([], 1,
        "HTTP/2.0 429 Too Many Requests\nRetry-After: 300\n\n<html>slow down</html>", "")
    monkeypatch.setattr(client, "run", lambda *args: response)
    monkeypatch.setattr(WATCH.time, "time", lambda: 1000)
    with pytest.raises(WATCH.ApiError) as failure:
        client.request("graphql", {})
    assert failure.value.retry_at == 1300


def test_wait_deadline_does_not_make_an_extra_read(monkeypatch, tmp_path):
    now = [1000.0]
    calls = []
    def quiet(*args):
        calls.append(now[0])
        return {"status": "quiet", "events": []}
    monkeypatch.setattr(WATCH, "poll", quiet)
    monkeypatch.setattr(WATCH.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(WATCH.time, "time", lambda: now[0])
    monkeypatch.setattr(WATCH.time, "sleep", lambda duration: now.__setitem__(0, now[0] + duration))
    response = WATCH.wait(WATCH.Store(tmp_path, TARGET), "gh", 120, 2)
    assert response["status"] == "timeout"
    assert calls == [1000]
    assert now[0] == 1002


def connection(nodes, next_cursor=None):
    return {"nodes": nodes, "pageInfo": {"hasNextPage": next_cursor is not None,
                                          "endCursor": next_cursor}}


def core(checks=None):
    return {"viewer": {"login": "Mattie"}, "repository": {"pullRequest": {
        "number": 7, "url": "https://github.com/Mattie/example/pull/7", "state": "OPEN",
        "headRefOid": "a" * 40, "headRefName": "feature", "baseRefName": "main",
        "mergeable": "MERGEABLE", "headRepository": {"nameWithOwner": "contributor/fork"},
        "commits": {"nodes": [{"commit": {"id": "commit", "oid": "a" * 40,
                                             "statusCheckRollup": {"contexts": checks or connection([])}}}]},
    }}}


def test_snapshot_paginates_checks_threads_and_more_than_100_replies(monkeypatch):
    client = WATCH.GitHubClient(TARGET, {})
    def raw_check(i):
        return {"id": str(i), "__typename": "StatusContext", "context": f"job{i}",
                "state": "SUCCESS", "createdAt": "2026-10-13", "isRequired": True}
    first_core = core(connection([raw_check(i) for i in range(100)], "check-tail"))
    tail_core = core(connection([raw_check(100)]))
    def thread(identity, root, count):
        return {"id": identity, "isResolved": False, "isOutdated": False, "path": "app.py",
                "line": 1, "comments": {"nodes": [{"id": root}], "totalCount": count}}
    graph = iter([first_core, tail_core,
        {"repository": {"pullRequest": {"reviewThreads": connection([thread("t1", "c0", 101)], "thread-tail")}}},
        {"repository": {"pullRequest": {"reviewThreads": connection([thread("t2", "c101", 1)])}}}])
    monkeypatch.setattr(client, "graphql", lambda *args, **kwargs: next(graph))
    comments = [{"id": i, "node_id": f"c{i}", "body": str(i), "user": {"login": "reviewer"},
                 **({"in_reply_to_id": 0} if 0 < i < 101 else {})} for i in range(102)]
    pages = iter([
        (200, {}, []), (200, {}, []),
        (200, {"link": '<https://api.github.com/repos/Mattie/example/pulls/7/comments?per_page=100&page=2>; rel="next"'}, comments[:100]),
        (200, {}, comments[100:])])
    monkeypatch.setattr(client, "request", lambda *args, **kwargs: next(pages))
    value = client.snapshot()
    assert len(value["checks"]) == 101
    assert len(value["remarks"]) == 102
    assert len(value["threads"]) == 2
    assert value["remarks"]["inline:c100"]["thread_id"] == "t1"
    assert value["head_repository"] == "contributor/fork"


def test_cli_ack_stop_resume_preserve_queue_across_processes(tmp_path):
    store = WATCH.Store(tmp_path, TARGET)
    state = store.load()
    WATCH.enqueue(state, [{"kind": "remarks"}, {"kind": "thread-state"}], TARGET)
    with store.locked():
        store.save(state)
    def command(*args):
        completed = subprocess.run([sys.executable, str(SCRIPT), *args, TARGET.key.split("/", 1)[1],
                                    "--state-dir", str(tmp_path)], capture_output=True, text=True)
        assert completed.returncode == 0, completed.stderr
        return json.loads(completed.stdout)
    assert command("poll")["events"] == state["pending"]
    assert command("stop")["status"] == "stopped"
    assert command("poll")["stopped"] == "manual"
    assert command("resume")["events"] == state["pending"]
    completed = subprocess.run([sys.executable, str(SCRIPT), "ack", "Mattie/example#7",
        state["pending"][0]["event_id"], "--state-dir", str(tmp_path)], capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    assert kinds(json.loads(completed.stdout)["events"]) == ["thread-state"]


@pytest.mark.parametrize("value", ["Mattie/example#0", "https://github.com/a/../pull/7",
                                  "https://user:secret@github.com/a/b/pull/7", "a/b#7;whoami"])
def test_invalid_selectors_are_rejected(value):
    with pytest.raises((WATCH.WatchError, ValueError)):
        WATCH.parse_target(value)
