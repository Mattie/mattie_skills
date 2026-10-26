"""Behavioral tests for read-only project discovery and chat reconciliation."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml


SCRIPT = Path(os.environ.get("PROJECTBOT_INSPECTOR", Path(__file__).resolve().parents[2]
                            / "skills/projectbot/scripts/inspect_project.py"))
SPEC = importlib.util.spec_from_file_location("projectbot_inspector", SCRIPT)
inspector = importlib.util.module_from_spec(SPEC)
with patch.object(sys, "dont_write_bytecode", True):
    SPEC.loader.exec_module(inspector)


class InspectorTests(unittest.TestCase):
    """Exercise decisions visible to a remote reader, using isolated records."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.control = self.root / ".todo"

    def project(self, identity="root", parent=None, state="active", **fields):
        """Write one fixture brief in the documented flat storage layout."""
        path = self.control / "projects"
        if identity != "root":
            path /= identity
        path.mkdir(parents=True, exist_ok=True)
        meta = {"id": identity, "parent": parent, "state": state,
                "control_root": str(self.control), **fields}
        (path / "PROJECT.md").write_text("---\n" + yaml.safe_dump(meta)
                                        + "---\n# " + identity + "\n", encoding="utf-8")
        return path

    def tasks(self, content, directory=None):
        """Write fixture tasks without production side effects."""
        directory = directory or self.control
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "tasks.md").write_text(content, encoding="utf-8")

    def test_nested_tree_selection_and_sleep_inheritance(self):
        self.project(state="sleeping")
        child = self.project("search", "root", source_paths=["src/search"])
        self.project("ranking", "search", source_paths=["src/search/ranking"])
        directory = self.root / "src/search/ranking"
        directory.mkdir(parents=True)
        self.tasks("## Open\n- [ ] Search\n  - id: search-1\n## Completed\n", child)
        report = inspector.inspect(directory)
        self.assertEqual(report["selected_project"], "ranking")
        search = report["tree"]["children"][0]
        self.assertEqual(search["children"][0]["id"], "ranking")
        self.assertEqual(search["task_counts"], {"queued": 1})
        self.assertEqual(search["dispatch_blocked_by"], [{"id": "root", "state": "sleeping"}])

    def test_unknown_chief_never_means_missing_or_completed(self):
        self.project(chief={"harness": "codex", "host": "local", "thread": "chief"})
        report = inspector.inspect(self.root)
        self.assertEqual(report["tree"]["chief"]["reachability"], "unknown")
        self.assertEqual(report["tree"]["chief"]["execution_status"], "unknown")
        self.assertEqual(report["chat_inventory"]["coverage"], "unknown")

    def test_partial_snapshot_preserves_work_and_unassigned_chats(self):
        self.project(chief={"harness": "codex", "host": "local", "thread": "chief"})
        self.tasks("## Open\n- [ ] Ship\n  - id: ship\n  - state: review\n"
                   "  - worker: codex / local / worker\n## Completed\n")
        snapshot = {"observed_at": "2000-01-01T00:00:00Z", "coverage": "partial",
                    "projects": [{"projectId": "p", "hostId": "local", "path": str(self.root)}],
                    "threads": [
                        {"id": "chief", "hostId": "local", "projectId": "p", "status": "idle"},
                        {"id": "worker", "hostId": "local", "projectId": "p", "status": "idle"},
                        {"id": "human", "hostId": "local", "projectId": "p", "status": "active"},
                        {"id": "human", "hostId": "remote", "projectId": "p", "status": "active"},
                        {"id": "foreign", "hostId": "local", "projectId": "other", "cwd": str(self.root)}]}
        report = inspector.inspect(self.root, snapshot=snapshot)
        self.assertEqual([chat["thread"] for chat in report["unassigned_chats"]], ["human"])
        self.assertEqual(report["tree"]["tasks"][0]["state"], "review")
        self.assertEqual(report["tree"]["chief"]["reachability"], "listed")
        self.assertEqual(report["tree"]["chief"]["freshness"], "stale")
        self.assertEqual(report["tree"]["chief"]["messageability"], "unknown")

    def test_read_result_does_not_claim_messageability(self):
        b = {"harness": "codex", "host": "local", "thread": "chief"}
        self.project(chief=b)
        report = inspector.inspect(self.root, snapshot={"reads": [{"binding": b, "ok": True,
                                   "status": "idle", "observed_at": "2000-01-01T00:00:00Z"}]})
        self.assertEqual(report["tree"]["chief"]["reachability"], "readable")
        self.assertEqual(report["tree"]["chief"]["messageability"], "unknown")

    def test_cycles_and_missing_parents_are_errors(self):
        self.project()
        self.project("a", "b")
        with self.assertRaisesRegex(inspector.RecordError, "Missing parent"):
            inspector.inspect(self.root)
        self.project("b", "a")
        with self.assertRaisesRegex(inspector.RecordError, "cycle"):
            inspector.inspect(self.root)

    def test_duplicate_project_ids_are_errors(self):
        self.project()
        other = self.project("child", "root")
        (other / "PROJECT.md").write_text("---\nid: root\nstate: active\n---\n", encoding="utf-8")
        with self.assertRaisesRegex(inspector.RecordError, "Duplicate project"):
            inspector.inspect(self.root)

    def test_duplicate_task_ids_make_report_partial(self):
        self.project()
        self.tasks("## Open\n- [ ] First\n  - id: duplicate\n- [ ] Second\n  - id: duplicate\n")
        report = inspector.inspect(self.root)
        self.assertEqual(report["status"], "partial")
        self.assertTrue(any("duplicate item" in issue for issue in report["diagnostics"]))

    def test_checkbox_disagreement_not_reported_as_delivery(self):
        self.project()
        self.tasks("## Completed\n- [x] Test passed\n  - state: review\n")
        report = inspector.inspect(self.root)
        self.assertEqual(report["status"], "partial")
        self.assertEqual(report["tree"]["task_counts"], {})

    def test_fenced_examples_are_not_tasks(self):
        self.project()
        self.tasks("## Open\n```markdown\n- [ ] Example\n```\n- [ ] Real work\n")
        self.assertEqual(inspector.inspect(self.root)["tree"]["task_counts"], {"queued": 1})

    def test_mistyped_metadata_is_partial_not_queued(self):
        self.project()
        for field in ("  - State: active", "  - state : active", "    - state: active"):
            with self.subTest(field=field):
                self.tasks("## Open\n- [ ] Already running\n" + field + "\n")
                report = inspector.inspect(self.root)
                self.assertEqual(report["status"], "partial")
                self.assertFalse(report["tree"]["counts_complete"])
                self.assertEqual(report["tree"]["tasks"], [])
                self.assertTrue(any("Malformed item metadata" in d for d in report["diagnostics"]))
        self.tasks("## Open\n- [ ] Ordinary task\n    - A prose note without metadata\n")
        self.assertEqual(inspector.inspect(self.root)["tree"]["task_counts"], {"queued": 1})

    def test_external_control_without_workspace_needs_explicit_scope(self):
        self.project()
        self.project("search", "root", source_paths=["src/search"])
        external = self.root / "external-control"
        self.control.rename(external)
        for path in external.glob("projects/**/PROJECT.md"):
            path.write_text(path.read_text(encoding="utf-8").replace(str(self.control), str(external)),
                            encoding="utf-8")
        directory = self.root / "src/search"
        directory.mkdir(parents=True)
        report = inspector.inspect(directory, control_root=external)
        self.assertEqual(report["status"], "ambiguous")
        self.assertIsNone(report["selected_project"])
        self.assertEqual(set(report["selection_candidates"]), {"root", "search"})
        self.assertTrue(any("Workspace root is unknown" in d for d in report["diagnostics"]))
        report = inspector.inspect(directory, control_root=external, project_id="search")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["selected_project"], "search")

    def test_nested_unmanaged_git_repo_does_not_inherit_outer_chief(self):
        self.project()
        nested = self.root / "other"
        (nested / ".git").mkdir(parents=True)
        with patch.object(inspector, "git_common_control", return_value=None):
            self.assertEqual(inspector.inspect(nested)["status"], "unmanaged")

    def test_worktree_uses_common_control_directory(self):
        self.project()
        worktree = self.root / "worktree"
        worktree.mkdir()
        (worktree / ".git").write_text("gitdir: unused\n", encoding="utf-8")
        result = subprocess.CompletedProcess([], 0, str(self.root / ".git") + "\n", "")
        with patch.object(inspector.subprocess, "run", return_value=result):
            report = inspector.inspect(worktree)
        self.assertEqual(report["control_root"], str(self.control))
        self.assertEqual(report["selected_project"], "root")
        self.assertFalse((worktree / ".todo").exists())

    def test_equal_source_scopes_are_ambiguous_until_explicitly_selected(self):
        self.project()
        self.project("a", "root", source_paths=["src"])
        self.project("b", "root", source_paths=["src"])
        directory = self.root / "src"
        directory.mkdir()
        report = inspector.inspect(directory)
        self.assertEqual(report["status"], "ambiguous")
        self.assertIsNone(report["selected_project"])
        self.assertEqual(inspector.inspect(directory, project_id="b")["selected_project"], "b")

    def test_copied_control_directory_requests_explicit_redirect(self):
        self.project(control_root="X:/elsewhere/.todo")
        report = inspector.inspect(self.root)
        self.assertEqual(report["status"], "redirect_required")
        self.assertIsNone(report["tree"])

    def test_cli_explicit_control_requires_root_brief(self):
        absent = self.root / "absent-control"
        empty = self.root / "empty-control"
        empty.mkdir()
        invalid = self.root / "invalid-control"
        (invalid / "projects").mkdir(parents=True)
        (invalid / "projects/PROJECT.md").write_text("No frontmatter\n", encoding="utf-8")
        for managed in (False, True):
            if managed:
                self.project()
            for control in (absent, empty, invalid):
                with self.subTest(managed=managed, control=control.name):
                    result = subprocess.run(
                        [sys.executable, str(SCRIPT), str(self.root), "--control-root", str(control)],
                        capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2, result.stdout)
                    report = json.loads(result.stdout)
                    self.assertEqual(report["status"], "error")
                    self.assertTrue(report["diagnostics"])

    def test_redirect_requires_available_canonical_records(self):
        canonical = self.root / "canonical-control"
        self.project(control_root=str(canonical))
        redirect = inspector.inspect(self.root)
        self.assertEqual(redirect["status"], "redirect_required")
        with self.assertRaises((OSError, inspector.RecordError)):
            inspector.inspect(self.root, control_root=redirect["declared_control_root"])
        (canonical / "projects").mkdir(parents=True)
        shutil.copyfile(self.control / "projects/PROJECT.md", canonical / "projects/PROJECT.md")
        report = inspector.inspect(self.root, control_root=canonical)
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["selected_project"], "root")
        self.assertEqual(report["control_root"], str(canonical))

    def test_chat_relationships_include_nested_workers_without_guessing(self):
        chief = {"harness": "codex", "host": "local", "thread": "chief"}
        child = {**chief, "thread": "child"}
        grandchild = {**chief, "thread": "grandchild"}
        self.project(chief=chief)
        report = inspector.inspect(self.root, snapshot={"relations": [
            {"parent": child, "child": grandchild}, {"parent": chief, "child": child}]})
        self.assertEqual(len(report["chat_relations"]), 2)
        self.assertEqual(report["chat_relations"][0]["child"]["reachability"], "unknown")

    def test_rollup_marks_counts_incomplete_when_descendant_list_is_invalid(self):
        self.project()
        child = self.project("child", "root")
        self.tasks("## Open\n- [ ] Root task\n")
        self.tasks("## Completed\n- [ ] Inconsistent\n", child)
        report = inspector.inspect(self.root)
        self.assertEqual(report["tree"]["subtree_task_counts"], {"queued": 1})
        self.assertFalse(report["tree"]["counts_complete"])

    def test_malformed_snapshot_fails_clearly(self):
        with self.assertRaisesRegex(inspector.RecordError, "threads must be an array"):
            inspector.inspect(self.root, snapshot={"threads": "not a list"})

    def test_older_read_does_not_override_newer_list_observation(self):
        b = {"harness": "codex", "host": "local", "thread": "chief"}
        self.project(chief=b)
        report = inspector.inspect(self.root, snapshot={
            "observed_at": "2026-10-16T14:00:00Z",
            "threads": [{"id": "chief", "hostId": "local", "status": "active"}],
            "reads": [{"binding": b, "ok": False, "status": "unknown",
                       "observed_at": "2000-01-01T00:00:00Z"}]})
        self.assertEqual(report["tree"]["chief"]["execution_status"], "active")
        self.assertEqual(report["tree"]["chief"]["reachability"], "listed")

    @unittest.skipUnless(shutil.which("git"), "Git is required for real worktree discovery")
    def test_real_git_worktree_reads_primary_records(self):
        self.project()
        def git(*args):
            return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                                  capture_output=True, text=True)
        git("init", "-q")
        git("-c", "user.name=Inspector test", "-c", "user.email=test@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", "Fixture")
        worktree = self.root / "checkout"
        git("worktree", "add", "--detach", str(worktree), "HEAD")
        report = inspector.inspect(worktree)
        self.assertEqual(report["control_root"], str(self.control))
        self.assertEqual(report["tree"]["id"], "root")
        self.assertFalse((worktree / ".todo").exists())

    def test_duplicate_yaml_keys_and_aliases_rejected(self):
        with self.assertRaises(inspector.RecordError):
            inspector.load_yaml("state: active\nstate: completed\n")
        with self.assertRaises(inspector.RecordError):
            inspector.load_yaml("a: &a [*a]\n")

    def test_inspection_does_not_modify_records(self):
        self.project()
        self.tasks("## Open\n- [ ] Task\n## Completed\n")
        before = {path: path.read_bytes() for path in self.control.rglob("*") if path.is_file()}
        inspector.inspect(self.root)
        after = {path: path.read_bytes() for path in self.control.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_cli_unmanaged_and_invalid_input_are_json(self):
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "unmanaged")
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root / "absent")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "error")


if __name__ == "__main__":
    unittest.main()
