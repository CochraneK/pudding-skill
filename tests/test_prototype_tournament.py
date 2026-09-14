import unittest

from scripts.prototype_tournament import CRITERION_IDS, scaffold, validate


def board():
    return {
        "story_id": "demo",
        "question": "What changed?",
        "argument": "The change is uneven.",
        "concepts": [
            {"id": "static", "form": "annotated_static", "interaction_job": "none"},
            {"id": "guided", "form": "guided_sequence", "interaction_job": "reveal"},
            {"id": "explore", "form": "explorable", "interaction_job": "compare"},
        ],
    }


def score(row, value=4, *, verdict="SURVIVE", notes=None):
    row["judge"] = {
        "scores": {key: value for key in CRITERION_IDS},
        "hard_failures": [],
        "verdict": verdict,
        "notes": notes or "The screenshots make the intended evidence legible at both desktop and mobile widths without adding avoidable complexity.",
    }


class TournamentTests(unittest.TestCase):
    def test_scaffold_preserves_static_and_all_concepts(self):
        data = scaffold(board(), "board.json", "/prototypes")
        self.assertEqual([row["alias"] for row in data["prototypes"]], ["A", "B", "C"])
        self.assertEqual({row["concept_id"] for row in data["prototypes"]}, {"static", "guided", "explore"})
        self.assertEqual(data["prototypes"][0]["interaction_job"], "none")
        report = validate(data, "manifest")
        self.assertEqual(report["status"], "READY_FOR_PROTOTYPE", report["errors"])

    def test_static_can_win_without_interaction_penalty(self):
        data = scaffold(board(), "board.json", "/prototypes")
        for row in data["prototypes"]:
            score(row, 4)
        static = data["prototypes"][0]
        static["judge"]["scores"]["reader_realization"] = 5
        static["judge"]["scores"]["interaction_economy"] = 5
        data["decision"] = {
            "outcome": "SELECT",
            "winner_concept_ids": ["static"],
            "reason": "The static prototype communicates the core comparison fastest, preserves the evidence cleanly, and makes interaction unnecessary rather than treating no interaction as a deficiency.",
            "implementation_handoff": [
                "Keep direct labels and the two claim-bearing comparisons visible without hover.",
                "Preserve reporting-year and missingness caveats next to the evidence rather than hiding them in notes.",
            ],
            "discarded_lessons": [],
        }
        report = validate(data, "decision")
        self.assertEqual(report["status"], "WINNER_SELECTED", report["errors"])
        self.assertEqual(report["ranking"][0]["concept_id"], "static")

    def test_hard_gate_eliminates_a_high_total(self):
        data = scaffold(board(), "board.json", "/prototypes")
        for row in data["prototypes"]:
            score(row, 5)
        victim = data["prototypes"][1]
        victim["judge"]["scores"]["accessibility_equivalence"] = 2
        victim["judge"]["verdict"] = "ELIMINATE"
        data["decision"] = {
            "outcome": "SELECT",
            "winner_concept_ids": ["static"],
            "reason": "The guided prototype scores highly in several dimensions but fails the accessibility hard gate, so the static survivor is the strongest implementation candidate without trading away equivalent access.",
            "implementation_handoff": ["Retain the strongest guided annotation as static callout copy.", "Keep the winning prototype keyboard- and motion-independent."],
            "discarded_lessons": [],
        }
        report = validate(data, "decision")
        guided = next(row for row in report["ranking"] if row["concept_id"] == "guided")
        self.assertEqual(guided["verdict"], "ELIMINATE")
        self.assertEqual(report["status"], "WINNER_SELECTED", report["errors"])

    def test_rejects_forced_winner_that_did_not_survive(self):
        data = scaffold(board(), "board.json", "/prototypes")
        for row in data["prototypes"]:
            score(row, 2, verdict="ELIMINATE")
        data["decision"] = {
            "outcome": "SELECT",
            "winner_concept_ids": ["guided"],
            "reason": "This deliberately tries to force a winner even though all prototypes fail the tournament threshold and should instead trigger a pivot or put-down decision.",
            "implementation_handoff": ["One", "Two"],
            "discarded_lessons": [],
        }
        report = validate(data, "decision")
        self.assertEqual(report["status"], "REVISE")
        self.assertTrue(any("must survive" in item for item in report["errors"]))


if __name__ == "__main__":
    unittest.main()
