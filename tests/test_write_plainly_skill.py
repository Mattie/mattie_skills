"""Contract checks for the write-plainly skill."""

from __future__ import annotations

import hashlib
import os
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL_DIR = REPO_ROOT / "skills" / "write-plainly"
SKILL_DIR = Path(os.environ.get("WRITE_PLAINLY_SKILL_DIR", DEFAULT_SKILL_DIR))
SKILL_PATH = SKILL_DIR / "SKILL.md"
OPENAI_PATH = SKILL_DIR / "agents" / "openai.yaml"
README_PATH = REPO_ROOT / "README.md"
NOTICES_PATH = REPO_ROOT / "THIRD_PARTY_NOTICES.md"
STE_PATH = REPO_ROOT / "skills" / "write-simplified-technical-english" / "SKILL.md"
INSTALLED_SKILL_VALUE = os.environ.get("WRITE_PLAINLY_INSTALLED_DIR")
INSTALLED_SKILL_DIR = Path(INSTALLED_SKILL_VALUE) if INSTALLED_SKILL_VALUE else None


def _skill_text() -> str:
    """Return the skill contract under test."""

    return SKILL_PATH.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Extract one second-level Markdown section."""

    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    if match is None:
        raise AssertionError(f"Missing section: {heading}")
    return match.group(1)


def _normalized(value: str) -> str:
    """Collapse Markdown wrapping so assertions describe behavior."""

    return " ".join(value.split())


def _manifest(root: Path) -> dict[str, str]:
    """Return a content manifest for a skill directory."""

    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class WritePlainlySkillContractTests(unittest.TestCase):
    """Protect the routing, plain-language workflow, and semantic lock."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = _skill_text()
        cls.openai = OPENAI_PATH.read_text(encoding="utf-8")

    def test_frontmatter_uses_targeted_plain_language_triggers(self) -> None:
        description_match = re.search(r"(?m)^description: (.+)$", self.text)
        self.assertIsNotNone(description_match)
        description = description_match.group(1)

        for trigger in (
            "plain language",
            "plain English",
            "audience-appropriate clarity",
            "meaning-preserving simplification",
        ):
            self.assertIn(trigger, description)

        for exclusion in (
            "proofreading",
            "shortening",
            "generic copyediting",
            "humanizing prose",
            "removing AI tells",
            "marketing voice",
            "creative rewriting",
        ):
            self.assertIn(exclusion, description)

        self.assertIn("When one of those triggers applies", description)
        self.assertIn("explicitly requests ASD-STE100", description)
        self.assertIn("$write-simplified-technical-english", description)

    def test_all_three_operations_have_distinct_contracts(self) -> None:
        task = _normalized(_section(self.text, "Establish the task"))
        operations = _normalized(_section(self.text, "Apply the requested operation"))

        self.assertIn("`WRITE`, `REWRITE`, or `REVIEW`", task)
        self.assertIn("For `WRITE`", operations)
        self.assertIn("requirements inventory before drafting", operations)
        self.assertIn("For `REWRITE`", operations)
        self.assertIn("compare the result with the source", operations)
        self.assertIn("For `REVIEW`", operations)
        self.assertIn("prioritized findings", operations)
        self.assertIn("complete rewrite only when requested", operations)

    def test_base_workflow_starts_with_reader_and_action(self) -> None:
        task = _normalized(_section(self.text, "Establish the task"))
        reader = _normalized(_section(self.text, "Start from the reader"))

        self.assertIn("intended reader", task)
        self.assertIn("what they should understand or do next", task)
        self.assertIn("answer, decision, conclusion, or required action first", reader)
        self.assertIn("concrete verbs and familiar words", reader)
        self.assertIn("Keep necessary domain terms", reader)
        self.assertIn("Keep passive voice", reader)
        self.assertIn("Apply no universal word or sentence-length cap", reader)
        self.assertNotRegex(reader, r"\b(?:15|20|25) words\b")

    def test_preservation_inventory_covers_technical_meaning(self) -> None:
        preservation = _normalized(_section(self.text, "Preserve technical meaning"))

        required_categories = (
            "Facts, claims, evidence, examples, citations, and source attribution",
            "Requirements, prohibitions, permissions, recommendations",
            "Actors, objects, ownership, preconditions, dependencies, sequences, states",
            "failures, outcomes, and cause-and-effect relationships",
            "Uncertainty, confidence, estimates, assumptions, warnings, caveats",
            "limitations, exceptions, and alternatives",
            "Identifiers, API names, interface labels, commands, code, configuration",
            "paths, links, version numbers, measurements, units, formulas",
            "quoted text",
            "Established terminology, meaningful distinctions, language variety, author voice",
        )
        for category in required_categories:
            self.assertIn(category, preservation)

    def test_semantic_lock_preserves_modality_and_avoids_invention(self) -> None:
        preservation = _normalized(_section(self.text, "Preserve technical meaning"))

        self.assertIn("strength, scope, polarity, and uncertainty", preservation)
        self.assertIn("Do not turn `may` into `will`, `should` into `must`", preservation)
        self.assertIn("Preserve conditions, exceptions, and causal relationships", preservation)
        self.assertIn("Add no unsupported fact, example, measurement, source", preservation)
        self.assertIn("Resolve no source ambiguity silently", preservation)

    def test_protected_literals_and_quotations_stay_exact(self) -> None:
        preservation = _normalized(_section(self.text, "Preserve technical meaning"))

        self.assertIn("Keep protected literals exact", preservation)
        self.assertIn("Keep direct quotations exact", preservation)

    def test_final_comparison_follows_the_inventory(self) -> None:
        preservation_position = self.text.index("## Preserve technical meaning")
        comparison_position = self.text.index("## Check the final result")
        self.assertLess(preservation_position, comparison_position)

        final_check = _normalized(_section(self.text, "Check the final result"))
        self.assertIn("Compare the complete result with the requirements or source inventory", final_check)
        self.assertIn("every required fact, constraint, warning, caveat, exception", final_check)
        self.assertIn("quotation, citation, and source attribution", final_check)
        self.assertIn("modality, uncertainty, scope, conditions, sequence, and causal meaning", final_check)
        self.assertIn("introduces no unsupported claim or implication", final_check)

    def test_output_contract_avoids_false_compliance_claims(self) -> None:
        output = _normalized(_section(self.text, "Return the result"))

        self.assertIn("For `WRITE` and `REWRITE`, return only the requested content", output)
        self.assertIn("For `REVIEW`, return the prioritized findings", output)
        self.assertIn("Do not claim a readability grade", output)
        self.assertIn("plain-language certification", output)
        self.assertIn("ASD-STE100 compliance", output)

    def test_openai_metadata_enables_targeted_implicit_invocation(self) -> None:
        self.assertIn('display_name: "Write Plainly"', self.openai)
        self.assertIn(
            'short_description: "Plain language that preserves technical meaning"',
            self.openai,
        )
        self.assertIn("Use $write-plainly", self.openai)
        self.assertIn("allow_implicit_invocation: true", self.openai)

    def test_v1_has_no_runtime_scripts_or_linter(self) -> None:
        self.assertFalse((SKILL_DIR / "scripts").exists())
        self.assertNotIn("linter", self.text.lower())

    def test_existing_ste_skill_remains_explicit_only(self) -> None:
        ste = STE_PATH.read_text(encoding="utf-8")
        self.assertIn("Use only when the user explicitly invokes", ste)
        self.assertIn("do not use for general requests for clear, simple", ste)

    def test_repository_catalog_and_provenance_are_recorded(self) -> None:
        readme = README_PATH.read_text(encoding="utf-8")
        notices = NOTICES_PATH.read_text(encoding="utf-8")

        self.assertIn("[`write-plainly`](skills/write-plainly/)", readme)
        self.assertIn("ddf4f46fbddf6ba59071994a9c2a1c141dce5005", notices)
        self.assertIn("1052bef674ce17bef9b71a815152c6747585c168", notices)
        self.assertGreaterEqual(_normalized(notices).count("MIT License"), 2)

    @unittest.skipUnless(
        INSTALLED_SKILL_DIR is not None,
        "Set WRITE_PLAINLY_INSTALLED_DIR to verify an installed copy.",
    )
    def test_installed_copy_matches_repo_and_has_routed_ste_dependency(self) -> None:
        assert INSTALLED_SKILL_DIR is not None
        self.assertEqual(_manifest(DEFAULT_SKILL_DIR), _manifest(INSTALLED_SKILL_DIR))

        installed_ste = INSTALLED_SKILL_DIR.parent / "write-simplified-technical-english"
        installed_ste_skill = installed_ste / "SKILL.md"
        self.assertTrue(installed_ste_skill.is_file())
        self.assertIn(
            "name: write-simplified-technical-english",
            installed_ste_skill.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
