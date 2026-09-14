import copy
import tempfile
import unittest
from pathlib import Path

from scripts.production_handoff import compile_contract, validate, validate_source


class ProductionHandoffTests(unittest.TestCase):
    def tournament(self):
        return {
            "story_id": "demo",
            "prototypes": [
                {"concept_id": "static", "form": "annotated_static", "interaction_job": "none"},
                {"concept_id": "guided", "form": "guided_sequence", "interaction_job": "reveal"},
                {"concept_id": "explore", "form": "explorable", "interaction_job": "compare"},
            ],
            "decision": {
                "outcome": "SELECT",
                "winner_concept_ids": ["static"],
                "production_contract": {
                    "route": "/stories/demo",
                    "primary_form": "annotated_static",
                    "primary_interaction_job": "none",
                    "required_sequence": ["need", "capacity"],
                    "required_claims": [
                        {"id": "gap", "tokens": ["1,647×", "$0.04", "$65.89"]}
                    ],
                    "borrowed_lessons": [
                        {
                            "from_concept_id": "guided",
                            "keep": "need to capacity sequence",
                            "reject_interaction_job": "reveal",
                        }
                    ],
                    "optional_depth": [
                        {
                            "from_concept_id": "explore",
                            "route": "/stories/demo/atlas",
                            "interaction_job": "compare",
                        }
                    ],
                    "forbidden_primary_interaction_jobs": ["reveal", "compare"],
                    "forbidden_source_tokens": ["OldScrolly", "OldExplorer"],
                },
            },
        }

    def source(self):
        return '''
<section data-production-winner="static" data-primary-interaction="none">
  <div data-story-beat="need"></div>
  <div data-story-beat="capacity" data-claim-id="gap">1,647× $0.04 $65.89</div>
  <div data-borrowed-from="guided"></div>
</section>
<div data-optional-depth="explore"><a href="/stories/demo/atlas">Atlas</a></div>
'''

    def test_compile_preserves_selected_form_and_contract(self):
        result = compile_contract(self.tournament())
        self.assertEqual(result["primary_form"], "annotated_static")
        self.assertEqual(result["primary_interaction_job"], "none")
        self.assertEqual(result["decision"]["winner_concept_ids"], ["static"])
        self.assertEqual(len(result["tournament_fingerprint"]), 64)

    def test_source_alignment_passes_for_selected_static_story(self):
        contract = compile_contract(self.tournament())
        self.assertEqual(validate_source(contract, self.source()), [])

    def test_losing_interaction_cannot_silently_return(self):
        contract = compile_contract(self.tournament())
        errors = validate_source(contract, self.source() + "\n<OldScrolly />")
        self.assertTrue(any("forbidden token" in item for item in errors))

    def test_stale_committed_contract_is_rejected(self):
        tournament = self.tournament()
        contract = compile_contract(tournament)
        stale = copy.deepcopy(contract)
        stale["primary_interaction_job"] = "reveal"
        report = validate(tournament, stale)
        self.assertEqual(report["status"], "REVISE")
        self.assertTrue(any("stale" in item for item in report["errors"]))

    def test_source_file_validation_is_part_of_contract_gate(self):
        tournament = self.tournament()
        contract = compile_contract(tournament)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "page.svelte"
            source.write_text(self.source(), encoding="utf-8")
            report = validate(tournament, contract, source)
        self.assertEqual(report["status"], "PRODUCTION_ALIGNED")

    def test_winner_form_mismatch_is_rejected(self):
        tournament = self.tournament()
        tournament["decision"]["production_contract"]["primary_form"] = "explorable"
        with self.assertRaises(ValueError):
            compile_contract(tournament)


if __name__ == "__main__":
    unittest.main()
