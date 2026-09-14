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

    def test_global_mental_health_public_story_uses_guide_then_explore(self):
        story = (ROOT / "src/routes/stories/global-mental-health/+page.svelte").read_text(encoding="utf-8")
        self.assertIn("GlobalMentalHealthScrolly", story)
        self.assertIn("GlobalMentalHealthExplorer", story)
        self.assertIn("LanguageToggle", story)

        scrolly = (ROOT / "src/components/GlobalMentalHealthScrolly.svelte").read_text(encoding="utf-8")
        self.assertIn("IntersectionObserver", scrolly)
        self.assertIn("prefers-reduced-motion", scrolly)
        self.assertIn("data-mental-step", scrolly)

        explorer = (ROOT / "src/components/GlobalMentalHealthExplorer.svelte").read_text(encoding="utf-8")
        self.assertIn("selectedMetric", explorer)
        self.assertIn("selectedCode", explorer)
        self.assertIn("No usable WHO observation", explorer)

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
