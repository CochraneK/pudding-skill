from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_agent_visual_review import validate


CONTRACT = {
    "status": "PASS",
    "agent_review": {
        "screenshots": [
            {"route": "/", "viewport": "desktop", "position": "top", "path": ".qa/visual-home-desktop-top.png"},
            {"route": "/", "viewport": "desktop", "position": "mid", "path": ".qa/visual-home-desktop-mid.png"},
            {"route": "/", "viewport": "mobile", "position": "top", "path": ".qa/visual-home-mobile-top.png"},
            {"route": "/", "viewport": "mobile", "position": "mid", "path": ".qa/visual-home-mobile-mid.png"},
        ]
    },
}


class AgentVisualReviewContractTests(unittest.TestCase):
    def complete_review(self):
        return {
            "verdict": "pass",
            "reviewed_screenshots": [item["path"] for item in CONTRACT["agent_review"]["screenshots"]],
            "observations": [
                {
                    "route": "/",
                    "viewport": "mobile",
                    "position": "top",
                    "severity": "info",
                    "category": "hierarchy",
                    "note": "Opening hierarchy remains readable on the narrow viewport.",
                    "evidence": "Headline, dek, CTA, and workflow labels are visually separated without overlap.",
                    "proposed_action": "manual",
                }
            ],
        }

    def test_complete_pass_review_validates(self):
        self.assertEqual(validate(CONTRACT, self.complete_review()), [])

    def test_missing_screenshot_fails(self):
        review = self.complete_review()
        review["reviewed_screenshots"].pop()
        errors = validate(CONTRACT, review)
        self.assertTrue(any("missing required screenshots" in error for error in errors))

    def test_pass_cannot_hide_error_observation(self):
        review = self.complete_review()
        review["observations"][0]["severity"] = "error"
        errors = validate(CONTRACT, review)
        self.assertTrue(any("cannot be pass" in error for error in errors))

    def test_agent_cannot_override_deterministic_fail(self):
        contract = {**CONTRACT, "status": "FAIL"}
        errors = validate(contract, self.complete_review())
        self.assertTrue(any("cannot override" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
