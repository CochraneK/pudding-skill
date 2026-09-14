from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from benchmark import aggregate, gate, materialize_case, validate_provenance
from profile_data import load_rows


class BenchmarkTests(unittest.TestCase):
    def test_materialize_supported_formats_round_trip(self):
        rows = [{"group": "A", "value": 1}, {"group": "B", "value": None}]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for fmt in ("csv", "tsv", "json", "jsonl", "ndjson"):
                path = materialize_case({"id": f"case-{fmt}", "format": fmt, "rows": rows}, root)
                loaded = load_rows(path)
                self.assertEqual(len(loaded), 2)
                self.assertEqual(str(loaded[0]["group"]), "A")

    def test_provenance_requires_one_verified_mapping_per_evidence_item(self):
        spec = {"evidence": [{"kind": "distribution"}, {"kind": "distribution"}]}
        draft = {
            "status": "EDITORIAL_REVIEW_REQUIRED",
            "provenance": {
                "claims": [
                    {"claim_ref": 0, "evidence_index": 0, "verified": True},
                    {"claim_ref": 1, "evidence_index": 1, "verified": True},
                ]
            },
            "sections": [{"id": "section-1", "claim_refs": [0, 1]}],
        }
        ok, errors = validate_provenance(spec, draft)
        self.assertTrue(ok)
        self.assertEqual(errors, [])
        draft["provenance"]["claims"][1]["verified"] = False
        ok, errors = validate_provenance(spec, draft)
        self.assertFalse(ok)
        self.assertTrue(errors)

    def test_gate_fails_dimension_regression_even_when_average_is_high(self):
        report = {
            "overall_score": 98,
            "case_pass_rate": 0.9,
            "hard_failures": 0,
            "dimensions": {
                "selection": {"pass_rate": 0.9},
                "visual_grammar": {"pass_rate": 1.0},
                "claim_audit": {"pass_rate": 1.0},
                "editorial_gate": {"pass_rate": 1.0},
                "provenance": {"pass_rate": 1.0},
            },
        }
        baseline = {
            "minimum_overall_score": 95,
            "minimum_case_pass_rate": 0.9,
            "max_hard_failures": 0,
            "minimum_dimension_pass_rates": {"selection": 1.0},
        }
        failures = gate(report, baseline)
        self.assertEqual(len(failures), 1)
        self.assertIn("dimension selection", failures[0])

    def test_aggregate_weights_dimensions_without_hiding_case_failures(self):
        checks_pass = {name: {"ok": True, "weight": weight, "detail": "PASS"} for name, weight in {
            "selection": 35, "visual_grammar": 20, "claim_audit": 25, "editorial_gate": 10, "provenance": 10
        }.items()}
        checks_fail = json.loads(json.dumps(checks_pass))
        checks_fail["visual_grammar"]["ok"] = False
        cases = [
            {"id": "a", "score": 100, "passed": True, "hard_failure": None, "checks": checks_pass},
            {"id": "b", "score": 80, "passed": False, "hard_failure": None, "checks": checks_fail},
        ]
        report = aggregate({"schema_version": 1}, cases)
        self.assertEqual(report["overall_score"], 90)
        self.assertEqual(report["passed_cases"], 1)
        self.assertEqual(report["dimensions"]["visual_grammar"]["pass_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
