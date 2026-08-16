"""Lifecycle tests for RMDD's local receipt helper."""

from __future__ import annotations

import json
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[2]
HELPER = REPOSITORY / "skills" / "rmdd" / "scripts" / "receipt.py"
HELPER_SPEC = importlib.util.spec_from_file_location("rmdd_receipt_helper", HELPER)
assert HELPER_SPEC is not None and HELPER_SPEC.loader is not None
RECEIPT = importlib.util.module_from_spec(HELPER_SPEC)
HELPER_SPEC.loader.exec_module(RECEIPT)


class ReceiptHelperTests(unittest.TestCase):
    """Exercise receipts through the same command line the skill uses."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.readme = self.root / "README.md"
        self.readme.write_text("# Tiny app\n\nReturn blue.\n", encoding="utf-8")
        (self.root / "app.py").write_text("def color():\n    return 'red'\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def helper(
        self,
        *arguments: str,
        input_bytes: bytes | None = None,
        expected: int = 0,
        environment: dict[str, str] | None = None,
    ) -> tuple[subprocess.CompletedProcess[bytes], dict[str, object] | None]:
        """Run one helper command and decode its JSON response."""

        result = subprocess.run(
            [sys.executable, str(HELPER), *arguments],
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=environment,
        )
        self.assertEqual(
            result.returncode,
            expected,
            result.stderr.decode("utf-8", errors="replace"),
        )
        payload = json.loads(result.stdout) if result.stdout else None
        return result, payload

    def start(self) -> tuple[Path, dict[str, object]]:
        """Start a receipt for the temporary project."""

        _, payload = self.helper(
            "start",
            "--project-root",
            str(self.root),
            "--readme",
            str(self.readme),
        )
        assert payload is not None
        return Path(str(payload["run_dir"])), payload

    def test_non_git_lifecycle_keeps_exact_chat_and_refresh_evidence(self) -> None:
        run_dir, payload = self.start()
        self.assertFalse(payload["git"])
        self.assertEqual((self.root / ".rmdd" / "rmdd" / "latest").read_text().strip(), payload["run_id"])
        self.assertEqual((run_dir / "README.md").read_bytes(), self.readme.read_bytes())
        self.assertIn("Return blue.", (run_dir / "diffs.txt").read_text(encoding="utf-8"))

        first = "I found the color function. I’m updating it and its focused test."
        second = "The implementation is aligned. I’m running the checks now."
        self.helper("progress", "--run-dir", str(run_dir), "--message", first)
        self.helper("progress", "--run-dir", str(run_dir), "--message", second)
        progress = (run_dir / "progress.md").read_text(encoding="utf-8")
        self.assertLess(progress.index(first), progress.index(second))

        linked = self.root / "BEHAVIOR.md"
        linked.write_text("The value is blue.\n", encoding="utf-8")
        self.helper("document", "--run-dir", str(run_dir), "--path", str(linked))
        self.readme.write_text("# Tiny app\n\nReturn green.\n", encoding="utf-8")
        linked.write_text("The value is green.\n", encoding="utf-8")

        _, refresh = self.helper("refresh", "--run-dir", str(run_dir))
        assert refresh is not None
        self.assertEqual(set(refresh["changed_sources"]), {"README.md", "BEHAVIOR.md"})
        _, unchanged = self.helper("refresh", "--run-dir", str(run_dir))
        assert unchanged is not None
        self.assertEqual(unchanged["changed_sources"], [])
        diffs = (run_dir / "diffs.txt").read_text(encoding="utf-8")
        self.assertEqual(diffs.count("README source refresh"), 1)
        self.assertEqual(diffs.count("Intent document refresh: BEHAVIOR.md"), 1)
        self.assertEqual((run_dir / "README.latest.md").read_bytes(), self.readme.read_bytes())
        run_text = (run_dir / "run.md").read_text(encoding="utf-8")
        self.assertIn("Active README snapshot: README.latest.md", run_text)
        self.assertIn(f"Final README SHA-256: {hashlib.sha256(self.readme.read_bytes()).hexdigest()}", run_text)

        self.helper("note", "--run-dir", str(run_dir), "--kind", "changed", "--text", "app.py")
        self.helper("note", "--run-dir", str(run_dir), "--kind", "check", "--text", "unittest: passed")
        self.helper(
            "evidence",
            "--run-dir",
            str(run_dir),
            "--label",
            "app.py before and after",
            input_bytes=b"red -> green\n",
        )
        response = b"Changed the color to green.\n\nChecks: unittest passed.\n"
        self.helper(
            "finish",
            "--run-dir",
            str(run_dir),
            "--status",
            "FINISHED",
            input_bytes=response,
        )
        self.assertEqual((run_dir / "response.md").read_bytes(), response)
        run_text = (run_dir / "run.md").read_text(encoding="utf-8")
        self.assertIn("Status: FINISHED", run_text)
        self.assertIn("Changed path: app.py", run_text)
        self.assertIn("Check: unittest: passed", run_text)

    def test_finish_rejects_a_readme_change_after_the_last_refresh(self) -> None:
        run_dir, _ = self.start()
        self.readme.write_text("# Tiny app\n\nReturn violet.\n", encoding="utf-8")
        stale = b"Changed the result to violet.\n"
        result, _ = self.helper("finish", "--run-dir", str(run_dir), input_bytes=stale, expected=2)
        self.assertIn(b"Documentation changed after the last acknowledged refresh", result.stderr)
        self.assertFalse((run_dir / "response.md").exists())
        self.assertIn("Status: WORKING", (run_dir / "run.md").read_text(encoding="utf-8"))
        self.assertEqual((run_dir / "README.latest.md").read_bytes(), self.readme.read_bytes())
        _, refresh = self.helper("refresh", "--run-dir", str(run_dir))
        assert refresh is not None
        self.assertEqual(refresh["changed_sources"], [])
        fresh = b"The violet behavior is implemented and checked.\n"
        self.helper("finish", "--run-dir", str(run_dir), input_bytes=fresh)
        self.assertEqual((run_dir / "response.md").read_bytes(), fresh)

    def test_refresh_records_a_readme_that_returns_to_its_start(self) -> None:
        run_dir, _ = self.start()
        starting = self.readme.read_bytes()
        self.readme.write_text("# Tiny app\n\nReturn green.\n", encoding="utf-8")
        self.helper("refresh", "--run-dir", str(run_dir))
        self.readme.write_bytes(starting)
        _, refresh = self.helper("refresh", "--run-dir", str(run_dir))
        assert refresh is not None
        self.assertEqual(refresh["changed_sources"], ["README.md"])
        self.assertEqual((run_dir / "README.latest.md").read_bytes(), starting)
        self.assertEqual(
            (run_dir / "run.md").read_text(encoding="utf-8").count("Active README snapshot: README.latest.md"),
            1,
        )
        self.assertEqual((run_dir / "diffs.txt").read_text(encoding="utf-8").count("README source refresh"), 2)

    def test_linked_document_refresh_tracks_each_new_saved_state(self) -> None:
        run_dir, _ = self.start()
        linked = self.root / "BEHAVIOR.md"
        linked.write_text("blue\n", encoding="utf-8")
        self.helper("document", "--run-dir", str(run_dir), "--path", str(linked))
        for value in ("green\n", "blue\n", "green\n"):
            linked.write_text(value, encoding="utf-8")
            _, refresh = self.helper("refresh", "--run-dir", str(run_dir))
            assert refresh is not None
            self.assertEqual(refresh["changed_sources"], ["BEHAVIOR.md"])
        _, unchanged = self.helper("refresh", "--run-dir", str(run_dir))
        assert unchanged is not None
        self.assertEqual(unchanged["changed_sources"], [])
        self.assertEqual(
            (run_dir / "diffs.txt").read_text(encoding="utf-8").count("Intent document refresh: BEHAVIOR.md"),
            3,
        )

    def test_repeated_non_git_runs_preserve_history_and_advance_latest(self) -> None:
        first_dir, first = self.start()
        self.helper("finish", "--run-dir", str(first_dir), input_bytes=b"First run complete.\n")
        self.readme.write_text("# Tiny app\n\nReturn amber.\n", encoding="utf-8")
        second_dir, second = self.start()
        self.assertNotEqual(first["run_id"], second["run_id"])
        self.assertTrue(first_dir.is_dir())
        self.assertEqual(second["previous_run"], first["run_id"])
        self.assertEqual((self.root / ".rmdd" / "rmdd" / "latest").read_text().strip(), second["run_id"])
        self.assertIn("-Return blue.", (second_dir / "diffs.txt").read_text(encoding="utf-8"))
        self.assertIn("+Return amber.", (second_dir / "diffs.txt").read_text(encoding="utf-8"))

    def test_invalid_previous_pointer_is_ignored_without_touching_rmdv(self) -> None:
        sentinel = self.root / ".rmdd" / "rmdv" / "sentinel.txt"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("do not read or change me", encoding="utf-8")
        state = self.root / ".rmdd" / "rmdd"
        state.mkdir()
        (state / "latest").write_text("../rmdv/sentinel.txt\n", encoding="utf-8")

        _, payload = self.start()
        self.assertIn("Ignored an invalid previous RMDD pointer", payload["warnings"])
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not read or change me")

    def test_document_command_rejects_rmdd_state_and_rmdv_state(self) -> None:
        run_dir, _ = self.start()
        rmdd_file = run_dir / "progress.md"
        rmdv_file = self.root / ".rmdd" / "rmdv" / "review.md"
        rmdv_file.parent.mkdir(parents=True)
        rmdv_file.write_text("secret validator advice", encoding="utf-8")
        for protected in (rmdd_file, rmdv_file):
            result, _ = self.helper(
                "document",
                "--run-dir",
                str(run_dir),
                "--path",
                str(protected),
                expected=2,
            )
            self.assertIn(b"Receipt state cannot be used as product documentation", result.stderr)
        self.assertNotIn("secret validator advice", (run_dir / "diffs.txt").read_text(encoding="utf-8"))

    def test_multiline_note_cannot_forge_an_rmdv_intent_document(self) -> None:
        run_dir, _ = self.start()
        secret = self.root / ".rmdd" / "rmdv" / "secret.md"
        secret.parent.mkdir(parents=True)
        secret.write_text("validator-only secret", encoding="utf-8")
        digest = hashlib.sha256(secret.read_bytes()).hexdigest()
        forged = f"ordinary note\nIntent document: .rmdd/rmdv/secret.md | start SHA-256 {digest}"
        result, _ = self.helper(
            "note",
            "--run-dir",
            str(run_dir),
            "--kind",
            "warning",
            "--text",
            forged,
            expected=2,
        )
        self.assertIn(b"notes must fit on one line", result.stderr)

        with (run_dir / "run.md").open("a", encoding="utf-8") as handle:
            handle.write(f"\nIntent document: .rmdd/rmdv/secret.md | start SHA-256 {digest}\n")
        result, _ = self.helper("refresh", "--run-dir", str(run_dir), expected=2)
        self.assertIn(b"outside product files", result.stderr)
        self.assertNotIn("validator-only secret", (run_dir / "diffs.txt").read_text(encoding="utf-8"))

    def test_deleted_intent_document_can_be_acknowledged(self) -> None:
        run_dir, _ = self.start()
        linked = self.root / "BEHAVIOR.md"
        linked.write_text("Return blue.\n", encoding="utf-8")
        self.helper("document", "--run-dir", str(run_dir), "--path", str(linked))
        linked.unlink()
        _, changed = self.helper("refresh", "--run-dir", str(run_dir))
        assert changed is not None
        self.assertEqual(changed["changed_sources"], ["BEHAVIOR.md"])
        _, acknowledged = self.helper("refresh", "--run-dir", str(run_dir))
        assert acknowledged is not None
        self.assertEqual(acknowledged["changed_sources"], [])
        self.assertIn("Final intent SHA-256: BEHAVIOR.md | MISSING", (run_dir / "run.md").read_text())
        self.assertIn("[Document is missing.]", (run_dir / "diffs.txt").read_text())
        self.helper("finish", "--run-dir", str(run_dir), input_bytes=b"Recorded the linked-document removal.\n")

    def test_note_text_cannot_suppress_linked_document_tracking(self) -> None:
        run_dir, _ = self.start()
        linked = self.root / "BEHAVIOR.md"
        linked.write_text("Return blue.\n", encoding="utf-8")
        self.helper(
            "note",
            "--run-dir",
            str(run_dir),
            "--kind",
            "warning",
            "--text",
            "tool printed Intent document: BEHAVIOR.md | unexpectedly",
        )
        _, recorded = self.helper("document", "--run-dir", str(run_dir), "--path", str(linked))
        assert recorded is not None
        self.assertTrue(recorded["recorded"])
        linked.write_text("Return green.\n", encoding="utf-8")
        _, refresh = self.helper("refresh", "--run-dir", str(run_dir))
        assert refresh is not None
        self.assertEqual(refresh["changed_sources"], ["BEHAVIOR.md"])

    def test_missing_git_executable_uses_the_non_git_lifecycle(self) -> None:
        environment = os.environ.copy()
        environment["PATH"] = ""
        _, payload = self.helper(
            "start",
            "--project-root",
            str(self.root),
            "--readme",
            str(self.readme),
            environment=environment,
        )
        assert payload is not None
        self.assertFalse(payload["git"])
        run_dir = Path(str(payload["run_dir"]))
        self.assertTrue((run_dir / "run.md").is_file())
        self.assertEqual((self.root / ".rmdd" / "rmdd" / "latest").read_text().strip(), payload["run_id"])

    def test_state_setup_failure_stops_cleanly(self) -> None:
        (self.root / ".rmdd").write_text("blocked", encoding="utf-8")
        original = (self.root / "app.py").read_bytes()
        result, payload = self.helper(
            "start",
            "--project-root",
            str(self.root),
            "--readme",
            str(self.readme),
            expected=2,
        )
        self.assertIsNone(payload)
        self.assertIn(b"RMDD receipt error", result.stderr)
        self.assertEqual((self.root / "app.py").read_bytes(), original)

    def test_redirected_run_directory_is_rejected(self) -> None:
        run_dir, _ = self.start()
        alias = self.root / "run-alias"
        try:
            alias.symlink_to(run_dir, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"Directory symlinks are unavailable: {exc}")
        result, _ = self.helper(
            "progress",
            "--run-dir",
            str(alias),
            "--message",
            "should not be recorded",
            expected=2,
        )
        self.assertIn(b"Refusing redirected RMDD run directory", result.stderr)
        self.assertEqual((run_dir / "progress.md").read_bytes(), b"")

    def test_refresh_rejects_a_readme_redirected_into_rmdv(self) -> None:
        run_dir, _ = self.start()
        secret = self.root / ".rmdd" / "rmdv" / "secret.md"
        secret.parent.mkdir(parents=True)
        secret.write_text("validator-only secret", encoding="utf-8")
        self.readme.unlink()
        try:
            self.readme.symlink_to(secret)
        except OSError as exc:
            self.skipTest(f"File symlinks are unavailable: {exc}")
        result, _ = self.helper("refresh", "--run-dir", str(run_dir), expected=2)
        self.assertIn(b"Root README is no longer a local project file", result.stderr)
        self.assertFalse((run_dir / "README.latest.md").exists())
        self.assertNotIn("validator-only secret", (run_dir / "diffs.txt").read_text(encoding="utf-8"))

    def test_finished_receipt_rejects_later_mutation(self) -> None:
        run_dir, _ = self.start()
        response = b"Run complete.\n"
        self.helper("finish", "--run-dir", str(run_dir), input_bytes=response)
        before = {path.name: path.read_bytes() for path in run_dir.iterdir() if path.is_file()}
        attempts = [
            ("progress", "--run-dir", str(run_dir), "--message", "late update"),
            ("note", "--run-dir", str(run_dir), "--kind", "check", "--text", "late check"),
            ("refresh", "--run-dir", str(run_dir)),
        ]
        for arguments in attempts:
            result, _ = self.helper(*arguments, expected=2)
            self.assertIn(b"already closed", result.stderr)
        result, _ = self.helper("finish", "--run-dir", str(run_dir), input_bytes=b"replacement\n", expected=2)
        self.assertIn(b"already closed", result.stderr)
        after = {path.name: path.read_bytes() for path in run_dir.iterdir() if path.is_file()}
        self.assertEqual(after, before)

    @unittest.skipUnless(shutil.which("git"), "Git is unavailable")
    def test_finish_rechecks_sources_after_git_evidence_capture(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        run_dir, _ = self.start()

        def mutate_during_capture(root: Path) -> tuple[str, str, str]:
            self.readme.write_text("# Tiny app\n\nReturn gold.\n", encoding="utf-8")
            return "", "", ""

        with mock.patch.object(RECEIPT, "capture_ending_git_evidence", side_effect=mutate_during_capture):
            with self.assertRaises(RECEIPT.ReceiptError) as caught:
                RECEIPT.finish_run(str(run_dir), "FINISHED", b"Stale response.\n")
        self.assertIn("Documentation changed after the last acknowledged refresh", str(caught.exception))
        self.assertFalse((run_dir / "response.md").exists())
        self.assertIn("Status: WORKING", (run_dir / "run.md").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("git"), "Git is unavailable")
    def test_git_receipt_uses_one_local_ignore_entry(self) -> None:
        linked = self.root / "BEHAVIOR.md"
        linked.write_text("The value is blue.\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "rmdd@example.test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "RMDD Test"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "README.md", "BEHAVIOR.md", "app.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "initial"], cwd=self.root, check=True)

        first_dir, first = self.start()
        self.assertTrue(first["git"])
        self.helper("document", "--run-dir", str(first_dir), "--path", str(linked))
        intent_evidence = (first_dir / "diffs.txt").read_text(encoding="utf-8")
        self.assertIn("Most recent committed intent change: BEHAVIOR.md", intent_evidence)
        self.helper("finish", "--run-dir", str(first_dir), input_bytes=b"No changes needed.\n")
        self.start()
        exclude_text = subprocess.run(
            ["git", "rev-parse", "--git-path", "info/exclude"],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            check=True,
        ).stdout.strip()
        exclude = Path(exclude_text)
        if not exclude.is_absolute():
            exclude = self.root / exclude
        entries = [line.strip() for line in exclude.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(entries.count("/.rmdd/"), 1)
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            check=True,
        ).stdout
        self.assertNotIn(".rmdd", status)

    @unittest.skipUnless(shutil.which("git"), "Git is unavailable")
    def test_git_receipt_records_changed_paths_without_diff_contents(self) -> None:
        config = self.root / "config.py"
        config.write_text('API_TOKEN = "starting-value"\n', encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "rmdd@example.test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "RMDD Test"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "README.md", "app.py", "config.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "initial"], cwd=self.root, check=True)

        unstaged_secret = "unstaged-sensitive-value"
        staged_secret = "staged-sensitive-value"
        self.root.joinpath("app.py").write_text(
            f'API_TOKEN = "{unstaged_secret}"\n',
            encoding="utf-8",
        )
        config.write_text(f'API_TOKEN = "{staged_secret}"\n', encoding="utf-8")
        subprocess.run(["git", "add", "config.py"], cwd=self.root, check=True)

        run_dir, _ = self.start()
        self.helper("finish", "--run-dir", str(run_dir), input_bytes=b"Recorded changed paths.\n")
        evidence = (run_dir / "diffs.txt").read_text(encoding="utf-8")

        self.assertIn("Starting unstaged project paths", evidence)
        self.assertIn("Starting staged project paths", evidence)
        self.assertIn("Ending unstaged project paths", evidence)
        self.assertIn("Ending staged project paths", evidence)
        self.assertIn("app.py", evidence)
        self.assertIn("config.py", evidence)
        self.assertNotIn(unstaged_secret, evidence)
        self.assertNotIn(staged_secret, evidence)

    @unittest.skipUnless(shutil.which("git"), "Git is unavailable")
    def test_local_exclude_failure_warns_and_continues(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        exclude = self.root / ".git" / "info" / "exclude"
        exclude.unlink()
        exclude.mkdir()

        run_dir, payload = self.start()
        self.assertTrue(run_dir.is_dir())
        self.assertTrue(any("Could not update" in warning for warning in payload["warnings"]))
        self.assertIn("Warning: Could not update", (run_dir / "run.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
