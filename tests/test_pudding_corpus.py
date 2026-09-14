import json
import tempfile
import unittest
from pathlib import Path

from scripts.pudding_corpus import render_markdown, validate_corpus


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "benchmarks" / "pudding-study-corpus.json"


class PuddingCorpusTests(unittest.TestCase):
    def test_public_story_corpus_is_diverse_and_valid(self):
        corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
        report = validate_corpus(corpus)
        self.assertEqual(report["status"], "PASS", report["errors"])
        self.assertGreaterEqual(report["metrics"]["stories"], 10)
        self.assertGreaterEqual(report["metrics"]["story_families"], 6)
        self.assertGreaterEqual(report["metrics"]["data_strategies"], 6)
        self.assertGreaterEqual(report["metrics"]["interaction_jobs"], 6)
        self.assertGreaterEqual(report["metrics"]["interaction_modes"], 6)

    def test_corpus_rejects_style_clone_urls_and_thin_annotations(self):
        bad = {
            "stories": [
                {
                    "id": "bad",
                    "title": "Bad",
                    "url": "https://example.com/not-pudding",
                    "published_year": 2025,
                    "story_family": "clone",
                    "question": "short",
                    "argument_pattern": "short",
                    "human_angle": "short",
                    "data_strategy": "none",
                    "visual_necessity": "short",
                    "interaction_jobs": [],
                    "interaction_mode": "none",
                    "design_move": "short",
                    "caveat_mode": "short",
                    "editorial_lesson": "short",
                    "anti_copy_note": "copy it"
                }
            ]
        }
        report = validate_corpus(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("pudding.cool" in error for error in report["errors"]))
        self.assertTrue(any("too thin" in error for error in report["errors"]))

    def test_markdown_report_emphasizes_operations_not_surface_style(self):
        corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
        report = validate_corpus(corpus)
        markdown = render_markdown(corpus, report)
        self.assertIn("increase* format diversity", markdown)
        self.assertIn("Anti-copy guardrail", markdown)
        self.assertIn("multiple *operations*", markdown)


if __name__ == "__main__":
    unittest.main()
