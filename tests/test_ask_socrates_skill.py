"""Contract checks for the ask-socrates skill."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "ask-socrates"
SKILL_PATH = SKILL_DIR / "SKILL.md"
OPENAI_PATH = SKILL_DIR / "agents" / "openai.yaml"
README_PATH = REPO_ROOT / "README.md"


def _skill_text() -> str:
    """Return the skill instructions under test."""

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


class AskSocratesSkillContractTests(unittest.TestCase):
    """Protect routing, lens selection, grounding, and the three-question result."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = _skill_text()
        cls.openai = OPENAI_PATH.read_text(encoding="utf-8")

    def test_frontmatter_routes_only_socratic_three_question_requests(self) -> None:
        self.assertIn("name: ask-socrates", self.text)

        description_match = re.search(r"(?m)^description: (.+)$", self.text)
        self.assertIsNotNone(description_match)
        description = description_match.group(1)

        for trigger in (
            "article, social situation, decision, or practical problem",
            "think like Socrates or Plato",
            "Socratic lens",
            "three high-leverage questions",
        ):
            self.assertIn(trigger, description)

        for boundary in (
            "sustained Socratic tutoring",
            "academic history",
            "ordinary fact-checking",
            "professional advice",
        ):
            self.assertIn(boundary, description)

    def test_catalog_contains_the_ten_approved_thought_tools(self) -> None:
        catalog = _section(self.text, "Use the thought tools faithfully")
        labels = re.findall(r"(?m)^\| \*\*(.+?)\*\* \|", catalog)

        self.assertEqual(
            [
                "Not-Knowing",
                "Definition",
                "Elenchus",
                "Midwife",
                "Perceived Good",
                "Care of the Soul",
                "Euthyphro",
                "Cave",
                "Divided Soul",
                "Hypothesis",
            ],
            labels,
        )

    def test_selection_requires_not_knowing_and_two_distinct_adaptive_tools(self) -> None:
        selection = _normalized(_section(self.text, "Choose three lenses"))

        self.assertIn("Always use **Not-Knowing**", selection)
        self.assertIn("relevance to the topic", selection)
        self.assertIn("difference from the Not-Knowing question", selection)
        self.assertIn("power to reveal a consequential blind spot", selection)
        self.assertIn("Select two different tools", selection)
        self.assertIn("Do not rotate tools for variety", selection)
        self.assertIn("aporia", selection)
        self.assertIn("sharpen the uncertainty", selection)

    def test_named_tools_keep_their_reasoning_patterns(self) -> None:
        catalog = _normalized(_section(self.text, "Use the thought tools faithfully"))

        required_patterns = (
            "Make the knowledge gap specific and name what could settle it",
            "two accepted commitments, examples, or consequences",
            "owned idea from a borrowed phrase",
            "Explanation must not excuse harm",
            "which standard could justify the approval itself",
            "proxy, metric, image, story, or incentive-shaped appearance",
            "reason from status or anger",
            "derive a concrete observable consequence",
        )
        for pattern in required_patterns:
            self.assertIn(pattern, catalog)

    def test_context_guidance_covers_articles_social_situations_and_problems(self) -> None:
        grounding = _normalized(_section(self.text, "Ground the questions in context"))

        self.assertIn("author's actual claim, evidence, key term, or authority", grounding)
        self.assertIn("Invent no missing premise or source detail", grounding)
        self.assertIn("distinguish observed behavior from inferred motive", grounding)
        self.assertIn("Examine the user's interpretation", grounding)
        self.assertIn("avoid blame, diagnosis, or therapeutic authority", grounding)
        self.assertIn("clarify the desired outcome and constraints", grounding)
        self.assertIn("downstream incentives or habits", grounding)

    def test_output_contract_is_one_frame_and_exactly_three_labeled_questions(self) -> None:
        output = _section(self.text, "Return the result")
        normalized = _normalized(output)

        self.assertIn("Frame: <one neutral sentence identifying the live issue>", output)
        self.assertIn("1. **Not-Knowing:** <one tailored question?>", output)
        self.assertIn("2. **<selected tool>:** <one tailored question?>", output)
        self.assertIn("3. **<selected tool>:** <one tailored question?>", output)
        self.assertIn("Return exactly three questions", normalized)
        self.assertIn("each one sentence long", normalized)
        self.assertIn("second and third labels must be distinct", normalized)
        self.assertIn("one declarative sentence and gives no verdict", normalized)

    def test_default_result_stays_crisp_and_preserves_explicit_extra_work(self) -> None:
        output = _normalized(_section(self.text, "Return the result"))

        self.assertIn("include no answers, advice, quotations", output)
        self.assertIn("explanation of tool selection", output)
        self.assertIn("Avoid role-playing Socrates", output)
        self.assertIn("invented quotations", output)
        self.assertIn("return the intact frame and three questions first", output)
        self.assertIn("additional work under a separate heading", output)

    def test_sparse_input_and_grounding_have_explicit_failure_behavior(self) -> None:
        inquiry = _normalized(_section(self.text, "Establish the object of inquiry"))
        quality = _normalized(_section(self.text, "Check the three questions"))

        self.assertIn("ask for the missing input and stop", inquiry)
        self.assertIn("strongest fair version", inquiry)
        self.assertIn("specific epistemic gap", quality)
        self.assertIn("would not fit an unrelated", quality)
        self.assertIn("remaining uncertainty is clearer and more useful", quality)

    def test_openai_metadata_exposes_the_approved_interface(self) -> None:
        self.assertIn('display_name: "Ask Socrates"', self.openai)
        self.assertIn(
            'short_description: "Three Socratic questions that expose hidden assumptions"',
            self.openai,
        )
        self.assertIn("Use $ask-socrates", self.openai)
        self.assertIn("one frame and three crisp questions", self.openai)
        self.assertIn("allow_implicit_invocation: true", self.openai)

    def test_v1_is_self_contained_and_registered_in_the_catalog(self) -> None:
        self.assertFalse((SKILL_DIR / "scripts").exists())
        self.assertFalse((SKILL_DIR / "references").exists())
        self.assertFalse((SKILL_DIR / "assets").exists())

        readme = README_PATH.read_text(encoding="utf-8")
        self.assertIn("[`ask-socrates`](skills/ask-socrates/)", readme)
        self.assertIn("Socratic and Platonic thought tools", readme)


if __name__ == "__main__":
    unittest.main()
