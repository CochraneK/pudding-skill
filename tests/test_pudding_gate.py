from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pudding_gate import benchmark, score_pitch


class PuddingGateTests(unittest.TestCase):
    def strong_pitch(self):
        return {
            "argument": "A familiar public metric hides two very different pathways, and showing those pathways changes how the apparent ranking should be interpreted.",
            "why_you": "I keep seeing people argue from the ranking without asking what sequence of events produced it.",
            "human_angle": "Readers recognize the frustration of being reduced to one score even when their trajectories are very different.",
            "tone_or_obsession": "obsession with the story hidden under a summary statistic",
            "aha": "Two cases can finish at the same score while following opposite trajectories, so the endpoint alone is misleading.",
            "distinctive_entry_point": "Start with two apparently identical endpoints and reveal their histories only after the reader has committed to the comparison.",
            "data_plan": {
                "status": "verified",
                "sources": ["primary longitudinal data"],
                "method": "Reconstruct trajectories from raw rows, verify the endpoint calculation, and preserve missing-wave caveats.",
                "fallback": "Use only complete trajectories if missing waves make imputation too assumption-heavy.",
            },
            "visual_case": {
                "why_visual": "The argument is about path shape over time, so aligned trajectories let readers perceive divergence and convergence that a final score or prose summary flattens.",
                "first_whiteboard": "Draw two lines that share an endpoint but arrive there by visibly different paths.",
                "visual_concepts": ["paired trajectories", "small-multiple paths", "endpoint-first reveal"],
            },
            "interaction": {
                "job": "reveal",
                "rationale": "The reveal makes the reader experience the mistaken endpoint assumption before the histories appear.",
            },
            "prototype_plan": "Build three static states and one working reveal before implementing the full story.",
            "iteration_plan": "Compare three visual concepts on desktop and mobile and keep only the one that makes the mistaken inference obvious.",
            "kill_conditions": [
                "The trajectories are too incomplete to support comparison.",
                "Seeing the path adds no interpretation beyond the endpoint.",
            ],
        }

    def test_strong_pitch_continues(self):
        report = score_pitch(self.strong_pitch())
        self.assertEqual(report["decision"], "CONTINUE")
        self.assertGreaterEqual(report["score"], 75)

    def test_topic_without_argument_must_pivot(self):
        pitch = self.strong_pitch()
        pitch["argument"] = ""
        pitch["question"] = "What is happening in this industry?"
        self.assertEqual(score_pitch(pitch)["decision"], "PIVOT")

    def test_blocked_data_without_fallback_puts_story_down(self):
        pitch = self.strong_pitch()
        pitch["data_plan"] = {"status": "blocked", "sources": [], "method": "", "fallback": ""}
        report = score_pitch(pitch)
        self.assertEqual(report["decision"], "PUT_DOWN")
        self.assertIn("blocked", report["notes"][0].lower())

    def test_strong_text_story_can_pivot_nonvisual(self):
        pitch = self.strong_pitch()
        pitch["visual_case"] = {
            "why_visual": "Not essential.",
            "first_whiteboard": "",
            "visual_concepts": ["annotated quotation"],
        }
        pitch["interaction"] = {"job": "none", "rationale": ""}
        report = score_pitch(pitch)
        self.assertEqual(report["decision"], "PIVOT_NONVISUAL")

    def test_gratuitous_interaction_does_not_earn_points(self):
        pitch = self.strong_pitch()
        pitch["interaction"] = {"job": "spin", "rationale": "A 3D wheel makes the page feel interactive."}
        report = score_pitch(pitch)
        self.assertEqual(report["dimensions"]["interaction_earned"], 0)
        self.assertTrue(any("Interaction" in note for note in report["notes"]))

    def test_explicit_no_interaction_is_not_penalized(self):
        pitch = self.strong_pitch()
        pitch["interaction"] = {"job": "none", "rationale": ""}
        report = score_pitch(pitch)
        self.assertEqual(report["dimensions"]["interaction_earned"], 5)

    def test_committed_corpus_and_holdout_pass(self):
        report = benchmark(ROOT / "benchmarks" / "pudding-dna-corpus.json")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["passed"], report["total"])
        self.assertGreaterEqual(report["holdout_total"], 5)
        self.assertEqual(report["holdout_passed"], report["holdout_total"])
        self.assertGreaterEqual(report["anti_pattern_total"], 4)
        self.assertEqual(report["anti_pattern_passed"], report["anti_pattern_total"])

    def test_report_disclaimer_rejects_false_authority(self):
        report = score_pitch(self.strong_pitch())
        self.assertEqual(report["status"], "EDITORIAL_TRIAGE_ONLY")
        self.assertIn("not an official Pudding rubric", report["disclaimer"])


if __name__ == "__main__":
    unittest.main()
