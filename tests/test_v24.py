from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from draft_story import build_draft
from pipeline import run_pipeline
from profile_data import load_rows, profile
from visual_grammar import plan_visual


class V24Tests(unittest.TestCase):
    def test_jsonl_loader_and_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.jsonl"
            path.write_text('{"group":"A","value":1}\n{"group":"B","value":3}\n', encoding="utf-8")
            rows = load_rows(path)
            self.assertEqual(len(rows), 2)
            result = profile(path)
            self.assertEqual(result["rows"], 2)
            self.assertEqual(result["column_count"], 2)

    def test_visual_grammar_change_gap_prefers_slopegraph_with_safe_fallback(self):
        spec = {
            "evidence": [{"kind": "change_gap"}],
            "visuals": [{"type": "bar"}],
            "production_mode": "annotated-static",
        }
        plan = plan_visual(spec)
        self.assertEqual(plan["recommended_visual"], "slopegraph")
        self.assertEqual(plan["baseline_renderer"], "bar")

    def test_draft_exposes_claim_provenance(self):
        spec = {
            "question": "What changed?",
            "audience": "general audience",
            "primary_insight": "Alpha rose by 12.",
            "evidence": [{"kind": "change", "group": "Alpha", "change": 12}],
            "beats": [{"operation": "reveal", "purpose": "Reveal the main change."}],
            "visuals": [{"type": "line", "purpose": "Show the change."}],
            "sources": [{"label": "sample.csv"}],
            "caveats": ["Synthetic data."],
        }
        draft = build_draft(spec, {"status": "PASS"})
        self.assertEqual(draft["status"], "EDITORIAL_REVIEW_REQUIRED")
        self.assertEqual(draft["provenance"]["claims"][0]["evidence_index"], 0)
        self.assertIn("Alpha rose by 12", draft["headline"])

    def test_pipeline_emits_visual_plan_and_first_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_pipeline(
                ROOT / "examples" / "sample-data.csv",
                "Which fictional cities saw housing costs separate most sharply from income after 2019?",
                "general audience",
                ROOT / "examples" / "data-schema.example.json",
                tmp_path / "generated",
                tmp_path / "auto-story.json",
                tmp_path / "candidates.json",
                tmp_path / "selection.json",
                tmp_path / "evaluation.json",
                tmp_path / "claim-audit.json",
                tmp_path / "story-draft.json",
            )
            self.assertEqual(result["claim_audit_report"]["status"], "PASS")
            self.assertTrue((tmp_path / "generated" / "visual-plan.json").exists())
            self.assertTrue((tmp_path / "generated" / "story-draft.md").exists())
            draft = json.loads((tmp_path / "story-draft.json").read_text(encoding="utf-8"))
            self.assertEqual(draft["visual_plan"]["recommended_visual"], "slopegraph")
            self.assertTrue(draft["provenance"]["claims"])


if __name__ == "__main__":
    unittest.main()
