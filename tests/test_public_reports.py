from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublicReportContractTests(unittest.TestCase):
    def test_report_registry_has_bilingual_public_copy(self):
        registry = json.loads((ROOT / "src/data/report-index.json").read_text(encoding="utf-8"))
        self.assert_localized(registry["site_dek"])
        self.assertGreaterEqual(len(registry["reports"]), 1)

        for report in registry["reports"]:
            for field in ("eyebrow", "title", "subtitle", "dek", "status"):
                self.assert_localized(report[field])
            for stat in report["stats"]:
                self.assert_localized(stat["label"])
            for route in report.get("secondary_routes", []):
                self.assert_localized(route["label"])
                self.assert_localized(route["description"])

    def test_global_mental_health_public_story_follows_tournament_winner(self):
        story = (ROOT / "src/routes/stories/global-mental-health/+page.svelte").read_text(encoding="utf-8")
        self.assertIn('data-production-winner="static-gap-atlas"', story)
        self.assertIn('data-primary-interaction="none"', story)
        self.assertIn('data-story-beat="need"', story)
        self.assertIn('data-story-beat="priority"', story)
        self.assertIn('data-story-beat="capacity"', story)
        self.assertIn('data-optional-depth="country-capacity-explorer"', story)
        self.assertIn("LanguageToggle", story)
        self.assertNotIn("GlobalMentalHealthScrolly", story)
        self.assertNotIn("GlobalMentalHealthExplorer", story)

        contract = json.loads(
            (ROOT / "stories/global-mental-health/production-contract.json").read_text(encoding="utf-8")
        )
        self.assertEqual(contract["decision"]["winner_concept_ids"], ["static-gap-atlas"])
        self.assertEqual(contract["primary_interaction_job"], "none")
        self.assertEqual(contract["required_sequence"], ["need", "priority", "capacity"])

    def test_research_waste_public_story_uses_reusable_scrolly_shell(self):
        story = (ROOT / "src/routes/stories/research-waste/+page.svelte").read_text(encoding="utf-8")
        self.assertIn("ScrollyShell", story)
        self.assertIn("steps={stepData()}", story)
        for state in (
            "volume",
            "reading",
            "boundary",
            "hidden",
            "contamination",
            "cost",
            "crossing",
        ):
            self.assertIn(f"id: '{state}'", story)
        self.assertIn("bind:value={papersPerDay}", story)
        self.assertIn("scenario === 'long'", story)
        self.assertIn("scenario === 'spike'", story)
        self.assertIn("prefers-reduced-motion", story)
        self.assertIn("LanguageToggle", story)

    def test_optional_capacity_atlas_remains_available(self):
        atlas = (ROOT / "src/routes/stories/global-mental-health/atlas/+page.svelte").read_text(encoding="utf-8")
        self.assertIn("selectedMetric", atlas)
        self.assertIn("metric-controls", atlas)
        self.assertIn("No WHO observation", atlas)
        self.assertIn("missing never means zero", atlas)
        self.assertIn("/stories/global-mental-health", atlas)

    def test_interaction_grammar_is_documented(self):
        grammar = (ROOT / "references/interaction-grammar.md").read_text(encoding="utf-8")
        for phrase in ("guide → hand off", "No scroll-jacking", "Guide, then explore", "Bilingual interaction"):
            self.assertIn(phrase, grammar)

    def assert_localized(self, value):
        self.assertIsInstance(value, dict)
        self.assertTrue(value.get("zh"))
        self.assertTrue(value.get("en"))


if __name__ == "__main__":
    unittest.main()
