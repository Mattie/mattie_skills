"""Regression checks for the prior-art skill's workflow and response contract."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "skills" / "prior-art" / "SKILL.md"
OPENAI_PATH = REPO_ROOT / "skills" / "prior-art" / "agents" / "openai.yaml"
FORMAT_PATH = (
    REPO_ROOT / "skills" / "prior-art" / "references" / "reuse-shortlist.md"
)


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
        cls.response_format = FORMAT_PATH.read_text(encoding="utf-8")

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
        section = _section(self.text, "Searching")
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

    def test_deep_mode_keeps_full_ledger_and_compact_default_output(self) -> None:
        deep = _normalized(_section(self.text, "Run deep mode"))
        self.assertIn("searched repository paths", deep)
        self.assertIn("searched user-local skill roots", deep)
        self.assertLess(deep.index("current repository"), deep.index("user-local skills"))
        self.assertLess(
            deep.index("user-local skills"),
            deep.index("standard and native facilities"),
        )

        self.assertIn("Summarize deep coverage in the search note", deep)
        self.assertIn("Show the full ledger only when the user asks", deep)

    def test_openai_metadata_advertises_the_reuse_shortlist_outcome(self) -> None:
        prompt_match = re.search(r'(?m)^  default_prompt: "(.+)"$', self.openai)
        self.assertIsNotNone(prompt_match)
        prompt = prompt_match.group(1)
        self.assertIn("$prior-art", prompt)
        self.assertIn("practical fit", prompt)
        self.assertIn("reusable parts", prompt)
        self.assertIn("catches", prompt)
        self.assertIn("recommend", prompt)

        description_match = re.search(r'(?m)^  short_description: "(.+)"$', self.openai)
        self.assertIsNotNone(description_match)
        description = description_match.group(1).lower()
        self.assertIn("reusable", description)
        self.assertIn("practical fit", description)

    def test_local_borrowing_keeps_scope_and_adoption_guards(self) -> None:
        evidence = _normalized(_section(self.text, "Searching"))
        self.assertIn("never crawl the whole user profile", _normalized(self.text))
        self.assertIn("do not execute their actions merely because they were discovered", evidence)
        self.assertIn("Installed presence alone does not establish adoption eligibility", evidence)
        self.assertIn("otherwise mark the candidate `STUDY-ONLY`", evidence)
        self.assertIn("standard facility can outrank a local implementation", evidence)

    def test_public_result_uses_candidate_fit_and_a_prose_recommendation(self) -> None:
        presentation = _normalized(_section(self.text, "Present the reuse shortlist"))
        self.assertNotIn("Mode: QUICK", self.text)
        self.assertNotIn("Verdict: REUSE", self.text)
        self.assertIn("Fit belongs to one candidate at a time", presentation)
        self.assertIn("The overall recommendation belongs in **What I'd do**", presentation)
        for label in ("GREAT", "GOOD", "PARTIAL", "WEAK", "BAD", "UNCERTAIN"):
            self.assertIn(f"`{label}`", presentation)

    def test_default_and_deep_modes_route_to_the_response_reference(self) -> None:
        reference = "[Reuse Shortlist response format](references/reuse-shortlist.md)"
        self.assertIn(reference, _section(self.text, "Run default mode"))
        self.assertIn(reference, _section(self.text, "Run deep mode"))

    def test_response_reference_defines_fit_and_rendering_contract(self) -> None:
        for label in ("GREAT", "GOOD", "PARTIAL", "WEAK", "BAD", "UNCERTAIN"):
            self.assertRegex(self.response_format, rf"(?m)^- \*\*{label}:\*\*")
        self.assertIn("an ungraded evidence state", self.response_format)
        self.assertIn(
            "| Existing solution | Good&nbsp;fit? | Overview | "
            "Reusable parts / Savings | Work needed / Catches |",
            self.response_format,
        )
        self.assertNotIn("> | Existing solution", self.response_format)
        self.assertIn("**Saves:**", self.response_format)
        self.assertIn("**Catch:**", self.response_format)
        self.assertIn("**What I'd do:**", self.response_format)
        self.assertIn("**Search note:**", self.response_format)

    def test_quick_absence_stays_bounded_and_custom_work_keeps_its_gate(self) -> None:
        quick = _normalized(_section(self.text, "Run quick mode"))
        presentation = _normalized(_section(self.text, "Present the reuse shortlist"))
        self.assertIn("Do not conclude from quick-mode absence", quick)
        self.assertIn("requires completed default or deep coverage", presentation)
        self.assertIn("Absence from quick mode is insufficient", presentation)

    def test_study_only_candidates_cannot_drive_adoption(self) -> None:
        licenses = _normalized(_section(self.text, "Verify licenses"))
        presentation = _normalized(_section(self.text, "Present the reuse shortlist"))
        self.assertIn("cannot drive a recommendation to copy or adopt it", licenses)
        self.assertIn("rate only the value of uses allowed", licenses.lower())
        self.assertIn("require adoption eligibility", presentation)

    def test_existing_license_spike_and_action_boundaries_remain(self) -> None:
        self.assertIn("Use a commit-SHA permalink", self.text)
        self.assertIn("Require an enforced sandbox", self.text)
        self.assertIn("Do not add a dependency", self.text)
        self.assertIn("Never turn limited search coverage into a universal claim", self.text)

    def test_service_consumption_has_separate_eligibility_and_evidence_rules(self) -> None:
        services = _normalized(_section(self.text, "Evaluate callable services"))
        self.assertIn("access eligible", services)
        self.assertIn("access unresolved", services)
        self.assertIn("access incompatible", services)
        self.assertIn("code-license policy separately", services)
        self.assertIn("does not verify useful fulfillment", services)
        self.assertIn("For service consumption", self.response_format)

    def test_service_lane_preserves_relevance_and_coverage_limits(self) -> None:
        searching = _normalized(_section(self.text, "Searching"))
        self.assertIn("skip it when offline", searching)
        self.assertIn("[Service discovery](references/service-discovery.md)", searching)
        self.assertIn("one relevant catalog", _normalized(_section(self.text, "Run quick mode")))
        deep = _normalized(_section(self.text, "Run deep mode"))
        self.assertIn("partial results, failures", deep)
        self.assertIn("does not satisfy saturation", deep)


if __name__ == "__main__":
    unittest.main()
