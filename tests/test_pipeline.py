from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from candidate_story import build_candidates, candidate_to_spec
from data_contract import load_contract
from derive_story import derive
from evaluate_story import evaluate
from generate_story import generate
from select_story import select
from validate_story import validate
from verify_claims import verify


class PipelineTests(unittest.TestCase):
    def write(self, directory: Path, name: str, text: str) -> Path:
        path = directory / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_sample_detects_change_gap(self):
        spec = derive(ROOT / "examples" / "sample-data.csv")
        self.assertEqual(spec["evidence"][0]["kind"], "change_gap")
        self.assertEqual(spec["evidence"][0]["group"], "Harbor")
        self.assertAlmostEqual(spec["evidence"][0]["gap"], 31.0)
        self.assertFalse(validate(spec))

    def test_candidate_pool_ranks_question_aligned_change_gap_first(self):
        pool = build_candidates(
            ROOT / "examples" / "sample-data.csv",
            "Which fictional cities saw housing costs separate most sharply from income after 2019?",
        )
        self.assertGreaterEqual(pool["candidate_count"], 6)
        self.assertEqual(pool["candidates"][0]["pattern"], "change_gap")
        self.assertEqual(pool["candidates"][0]["evidence"]["group"], "Harbor")
        scores = [candidate["score"] for candidate in pool["candidates"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_candidate_specs_validate(self):
        data = ROOT / "examples" / "sample-data.csv"
        pool = build_candidates(data, "Where did housing costs diverge from income?")
        for candidate in pool["candidates"][:5]:
            spec = candidate_to_spec(candidate, data, pool["question"])
            self.assertFalse(validate(spec), candidate["id"])

    def test_selection_report_is_explicit_and_passes(self):
        spec, pool, report = select(
            ROOT / "examples" / "sample-data.csv",
            "Which cities saw housing costs separate most sharply from income?",
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["selected_rank"], 1)
        self.assertEqual(report["selected_candidate_id"], pool["candidates"][0]["id"])
        self.assertEqual(evaluate(spec)["status"], "PASS")


    def test_data_contract_labels_and_roles_flow_into_output(self):
        data = ROOT / "examples" / "sample-data.csv"
        contract = load_contract(ROOT / "examples" / "data-schema.example.json")
        spec, pool, report = select(
            data,
            "Which cities saw housing costs separate most sharply from income?",
            contract=contract,
        )
        self.assertEqual(report["selected_rank"], 1)
        self.assertIn("Housing cost index", spec["primary_insight"])
        self.assertEqual(spec["field_metadata"]["city"]["label"], "City")
        self.assertTrue(pool["data_contract_applied"])

    def test_category_numeric_generates_bar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.write(root, "groups.csv", "group,value\nA,10\nA,14\nB,3\nB,5\nC,8\nC,8\n")
            spec = derive(data)
            self.assertEqual(spec["visuals"][0]["type"], "bar")
            self.assertIn("highest average", spec["primary_insight"])

    def test_numeric_pair_question_selects_correlation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.write(root, "pairs.csv", "x,y\n1,2\n2,4\n3,6\n4,8\n5,10\n")
            pool = build_candidates(data, "What is the relationship between x and y?")
            self.assertEqual(pool["candidates"][0]["pattern"], "correlation")
            spec, _, report = select(data, "What is the relationship between x and y?")
            self.assertEqual(spec["visuals"][0]["type"], "scatter")
            self.assertEqual(report["status"], "PASS")


    def test_claim_audit_recomputes_selected_evidence(self):
        data = ROOT / "examples" / "sample-data.csv"
        spec, _, _ = select(data, "Where did housing costs diverge most from income?")
        report = verify(spec, data)
        self.assertEqual(report["status"], "PASS")
        tampered = json.loads(json.dumps(spec))
        tampered["evidence"][0]["gap"] = 999
        bad = verify(tampered, data)
        self.assertEqual(bad["status"], "FAIL")

    def test_generate_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = ROOT / "examples" / "sample-data.csv"
            spec, _, _ = select(data, "Where did housing costs diverge most from income?")
            spec_path = root / "spec.json"
            out = root / "bundle.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            bundle = generate(spec_path, data, out)
            self.assertTrue(out.exists())
            self.assertEqual(bundle["chart"]["type"], "bar")
            self.assertEqual(bundle["chart"]["data"][0]["label"], "Harbor")


if __name__ == "__main__":
    unittest.main()
