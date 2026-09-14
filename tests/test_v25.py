from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from refine_visual import build_plan, collect_actions, render_css
from visual_critic import build_review


def case(viewport: str = "desktop", **overrides):
    metrics = {
        "viewport": {"width": 1440 if viewport == "desktop" else 390, "height": 900 if viewport == "desktop" else 844},
        "copy": {"blockCount": 4, "maxMeasureEm": 64, "medianMeasureEm": 52, "minFontPx": 16, "minLineHeightRatio": 1.5, "samples": []},
        "headings": {"sequence": [{"level": 1, "text": "Story"}, {"level": 2, "text": "Section"}], "jumps": []},
        "controls": {"count": 2, "smallTargetCount": 0, "smallTargets": []},
        "clipping": {"count": 0, "samples": []},
        "contrast": {"lowCount": 0, "severeCount": 0, "lowSamples": [], "severeSamples": []},
        "visuals": {"count": 1, "items": [{"aspect": 1.5}], "wideMobileCount": 0},
        "composition": {"h1Bottom": 240, "firstVisualTop": 800, "stickyCount": 1, "textCharsPerViewport": 900},
    }
    for key, value in overrides.items():
        metrics[key] = value
    return {"route": "/generated", "viewport": viewport, "screenshot": f".qa/generated-{viewport}.png", "metrics": metrics}


class VisualReviewTests(unittest.TestCase):
    def test_healthy_probe_requires_agent_review_but_has_no_deterministic_findings(self):
        review = build_review({"results": [case("desktop"), case("mobile")]})
        self.assertEqual(review["status"], "PASS")
        self.assertEqual(review["score"], 100)
        self.assertEqual(review["agent_review"]["status"], "PENDING")
        self.assertEqual(len(review["agent_review"]["screenshots"]), 2)

    def test_probe_findings_generate_only_allowlisted_auto_actions(self):
        review = build_review({
            "results": [case(
                "mobile",
                copy={"blockCount": 3, "maxMeasureEm": 96, "medianMeasureEm": 70, "minFontPx": 16, "minLineHeightRatio": 1.2, "samples": [{"selector": "p"}]},
                controls={"count": 3, "smallTargetCount": 1, "smallTargets": [{"selector": "button", "width": 32, "height": 30}]},
                clipping={"count": 1, "samples": [{"selector": "h1"}]},
            )]
        })
        self.assertEqual(review["status"], "FAIL")
        self.assertIn("tighten_copy_measure", review["safe_auto_actions"])
        self.assertIn("increase_text_leading", review["safe_auto_actions"])
        self.assertIn("increase_touch_targets", review["safe_auto_actions"])
        self.assertTrue(all(action in {"tighten_copy_measure", "increase_text_leading", "increase_touch_targets"} for action in review["safe_auto_actions"]))

    def test_agent_cannot_smuggle_arbitrary_auto_action(self):
        review = {"safe_auto_actions": ["tighten_copy_measure"], "findings": [], "status": "REVIEW", "score": 90}
        agent = {"verdict": "revise", "observations": [{"proposed_action": "rewrite_entire_stylesheet"}, {"proposed_action": "increase_touch_targets"}]}
        actions, rejected = collect_actions(review, agent)
        self.assertEqual(actions, ["increase_touch_targets", "tighten_copy_measure"])
        self.assertEqual(rejected[0]["action"], "rewrite_entire_stylesheet")

    def test_refinement_css_is_bounded_and_does_not_touch_claim_or_chart_logic(self):
        review = {"safe_auto_actions": ["increase_text_leading", "increase_touch_targets"], "findings": [], "status": "REVIEW", "score": 86}
        plan = build_plan(review, {"verdict": "revise", "observations": []}, iteration=1)
        css = render_css(plan)
        self.assertEqual(plan["max_iterations"], 2)
        self.assertIn("line-height: 1.55", css)
        self.assertIn("min-block-size: 44px", css)
        self.assertNotIn("primary_insight", css)
        self.assertNotIn("svg", css)


if __name__ == "__main__":
    unittest.main()
