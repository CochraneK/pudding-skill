import json
import unittest
from pathlib import Path

from scripts.concept_board import scaffold, validate


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "benchmarks" / "pudding-study-corpus.json"


def filled_concept(cid, form, job, inspiration_id):
    return {
        "id": cid,
        "title": f"Concept {cid}",
        "form": form,
        "interaction_job": job,
        "reader_realization": "The reader should see a concrete relationship that is difficult to retain from prose alone.",
        "why_visual": "The visual keeps several comparable quantities in one frame so the evidence can be inspected rather than merely asserted.",
        "evidence_dependencies": ["verified source rows and reporting-year metadata"],
        "visual_metaphor": "A stable frame that turns abstract differences into visible distance and density.",
        "mobile_strategy": "Use stacked states with direct labels and preserve the conclusion without hover or a wide viewport.",
        "accessibility_equivalent": "Provide a concise textual conclusion plus a keyboard-readable table for the same underlying evidence.",
        "prototype_test": "Build one representative state at desktop and phone widths and test whether the intended comparison is understood.",
        "kill_condition": "Stop this direction if the prototype needs explanatory prose longer than the visual insight it is supposed to clarify.",
        "inspiration": [
            {
                "story_id": inspiration_id,
                "transfer": "Borrow the editorial operation of moving from a concrete example to a broader pattern, not the surface design."
            }
        ]
    }


class ConceptBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
        cls.corpus_ids = {row["id"] for row in corpus["stories"]}

    def test_scaffold_forces_three_contrasting_starting_points(self):
        board = scaffold("story", "What changed?", "The change is uneven across places.")
        self.assertEqual(len(board["concepts"]), 3)
        self.assertEqual(board["concepts"][0]["interaction_job"], "none")
        self.assertEqual(len({row["form"] for row in board["concepts"]}), 3)

    def test_complete_diverse_board_is_ready_for_prototype(self):
        board = {
            "story_id": "example",
            "question": "What changed?",
            "argument": "The change is uneven across places.",
            "concepts": [
                filled_concept("static", "annotated_static", "none", "outkast-in-charts"),
                filled_concept("guided", "guided_sequence", "reveal", "stand-up-structure"),
                filled_concept("explore", "explorable", "explore", "microbrew-capital"),
            ],
        }
        report = validate(board, self.corpus_ids)
        self.assertEqual(report["status"], "READY_FOR_PROTOTYPE", report["errors"])
        self.assertEqual(report["metrics"]["static_alternatives"], 1)
        self.assertEqual(report["metrics"]["distinct_forms"], 3)

    def test_board_rejects_interactive_monoculture(self):
        board = {
            "concepts": [
                filled_concept("one", "scrolly", "reveal", "stand-up-structure"),
                filled_concept("two", "scrolly", "reveal", "stand-up-structure"),
                filled_concept("three", "scrolly", "reveal", "stand-up-structure"),
            ]
        }
        report = validate(board, self.corpus_ids)
        self.assertEqual(report["status"], "REVISE")
        self.assertTrue(any("static/no-interaction" in error for error in report["errors"]))
        self.assertTrue(any("distinct forms" in error for error in report["errors"]))

    def test_board_rejects_surface_style_imitation(self):
        concept = filled_concept("bad", "annotated_static", "none", "outkast-in-charts")
        concept["inspiration"][0]["transfer"] = "Copy the same style and typography because it looks recognizably like The Pudding."
        board = {
            "concepts": [
                concept,
                filled_concept("guided", "guided_sequence", "reveal", "stand-up-structure"),
                filled_concept("explore", "explorable", "explore", "microbrew-capital"),
            ]
        }
        report = validate(board, self.corpus_ids)
        self.assertEqual(report["status"], "REVISE")
        self.assertTrue(any("surface imitation" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
