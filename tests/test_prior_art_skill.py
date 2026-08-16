"""Regression checks for the prior-art skill's search order and safeguards."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "skills" / "prior-art" / "SKILL.md"
OPENAI_PATH = REPO_ROOT / "skills" / "prior-art" / "agents" / "openai.yaml"


def _skill_text() -> str:
    """Return the source skill text used by the repository."""

    return SKILL_PATH.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Extract one second-level Markdown section by its heading text."""

    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    if match is None:
        raise AssertionError(f"Missing section: {heading}")
    return match.group(1)


def _normalized(value: str) -> str:
    """Collapse Markdown line wrapping so assertions describe content."""

    return " ".join(value.split())


class PriorArtSkillContractTests(unittest.TestCase):
    """Protect the local-first workflow and its existing evidence gates."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = _skill_text()
        cls.openai = OPENAI_PATH.read_text(encoding="utf-8")

    def test_routing_description_advertises_local_first_order(self) -> None:
        description_match = re.search(r"(?m)^description: (.+)$", self.text)
        self.assertIsNotNone(description_match)
        description = description_match.group(1)

        repository = description.index("current repository")
        local_skills = description.index("user-local skills")
        standard = description.index("standard and platform facilities")
        self.assertLess(repository, local_skills)
        self.assertLess(local_skills, standard)

    def test_evidence_lanes_put_local_sources_before_standard_library(self) -> None:
        section = _section(self.text, "Follow the evidence order")
        items = re.findall(
            r"(?ms)^(\d+)\. (.*?)(?=^\d+\. |\Z)",
            section,
        )
        self.assertGreaterEqual(len(items), 7)

        expected = (
            "current repository",
            "user-local skills",
            "Standard-library",
            "Permissively licensed open-source",
            "other languages or technologies",
            "Public software behavior",
            "Standards, technical literature",
        )
        for position, needle in enumerate(expected, start=1):
            number, item = items[position - 1]
            self.assertEqual(str(position), number)
            self.assertIn(needle, _normalized(item))

    def test_quick_and_default_modes_keep_the_same_lane_order(self) -> None:
        quick = _normalized(_section(self.text, "Run quick mode"))
        self.assertLess(
            quick.index("current-repository code"),
            quick.index("configured user-local skill roots"),
        )
        self.assertLess(
            quick.index("configured user-local skill roots"),
            quick.index("current stack's standard"),
        )
        self.assertLess(
            quick.index("current stack's standard"),
            quick.index("focused GitHub"),
        )

        default = _normalized(_section(self.text, "Run default mode"))
        self.assertLess(
            default.index("current-repository implementations"),
            default.index("configured user-local skill roots"),
        )
        self.assertLess(
            default.index("configured user-local skill roots"),
            default.index("standard and native facilities"),
        )
        self.assertLess(
            default.index("standard and native facilities"),
            default.index("Search GitHub"),
        )

    def test_deep_mode_and_output_ledger_record_local_coverage(self) -> None:
        deep = _normalized(_section(self.text, "Run deep mode"))
        self.assertIn("searched repository paths", deep)
        self.assertIn("searched user-local skill roots", deep)
        self.assertLess(deep.index("current repository"), deep.index("user-local skills"))
        self.assertLess(
            deep.index("user-local skills"),
            deep.index("standard and native facilities"),
        )

        delivery = _normalized(_section(self.text, "Deliver the verdict"))
        self.assertIn("searched repository paths and user-local skill roots", delivery)

    def test_openai_routing_metadata_names_all_three_initial_lanes(self) -> None:
        prompt_match = re.search(r'(?m)^  default_prompt: "(.+)"$', self.openai)
        self.assertIsNotNone(prompt_match)
        prompt = prompt_match.group(1)
        self.assertLess(prompt.index("current repository"), prompt.index("user-local skills"))
        self.assertLess(prompt.index("user-local skills"), prompt.index("standard/native"))

        description_match = re.search(r'(?m)^  short_description: "(.+)"$', self.openai)
        self.assertIsNotNone(description_match)
        description = description_match.group(1).lower()
        self.assertLess(description.index("repository"), description.index("user-local skills"))
        self.assertLess(description.index("user-local skills"), description.index("standard"))

    def test_local_borrowing_keeps_scope_and_adoption_guards(self) -> None:
        evidence = _normalized(_section(self.text, "Follow the evidence order"))
        self.assertIn("never crawl the whole user profile", _normalized(self.text))
        self.assertIn("do not execute their actions merely because they were discovered", evidence)
        self.assertIn("Installed presence alone does not establish adoption eligibility", evidence)
        self.assertIn("otherwise mark the candidate `STUDY-ONLY`", evidence)
        self.assertIn("standard facility can outrank a local implementation", evidence)

    def test_existing_license_spike_and_action_boundaries_remain(self) -> None:
        self.assertIn("Use a commit-SHA permalink", self.text)
        self.assertIn("Require an enforced sandbox", self.text)
        self.assertIn("Do not add a dependency", self.text)
        self.assertIn("Never turn limited search coverage into a universal claim", self.text)


if __name__ == "__main__":
    unittest.main()
