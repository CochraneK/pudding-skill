from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from research_dossier import compile_dossier, scaffold, validate_dossier


class ResearchDossierTests(unittest.TestCase):
    def valid_dossier(self):
        dossier = scaffold("What changed?", "Example industry")
        dossier["status"] = "EDITORIAL_REVIEW_REQUIRED"
        dossier["sources"] = [
            {
                "id": "official-1",
                "tier": "T1",
                "type": "official_dataset",
                "title": "Official table",
                "publisher": "Example statistical office",
                "url": "https://example.org/table",
                "retrieved_at": "2026-09-14",
            }
        ]
        dossier["claims"] = [
            {
                "id": "claim-1",
                "kind": "numeric",
                "statement": "The indicator reached 42 in 2025.",
                "value": 42,
                "unit": "index points",
                "geography": "Exampleland",
                "period": "2025",
                "population": "All covered units",
                "source_ids": ["official-1"],
                "locator": "Table 1, row 4",
                "status": "VERIFIED",
                "confidence": "high",
                "verification_note": "Read directly from the primary table.",
            },
            {
                "id": "lead-1",
                "kind": "numeric",
                "statement": "A secondary article mentions 99.",
                "value": 99,
                "unit": "index points",
                "geography": "Exampleland",
                "period": "2025",
                "population": "Unknown universe",
                "source_ids": ["official-1"],
                "locator": "Discovery note",
                "status": "LEAD_ONLY",
                "confidence": "low",
            },
        ]
        dossier["data_targets"] = [
            {
                "id": "dataset-1",
                "dataset": "Official time series",
                "purpose": "Build a longitudinal chart",
                "preferred_source": "https://example.org/data",
                "access_mode": "direct_download",
                "license_note": "Open data",
                "query_spec": "all years",
                "next_action": "Download CSV and inspect fields.",
            }
        ]
        return dossier

    def test_scaffold_has_source_strategy(self):
        dossier = scaffold("Why?", "Topic")
        self.assertEqual(dossier["status"], "RESEARCH_REQUIRED")
        self.assertGreaterEqual(len(dossier["source_strategy"]), 5)
        self.assertEqual(dossier["source_strategy"][0]["tier"], "T0")

    def test_validation_rejects_unknown_source(self):
        dossier = self.valid_dossier()
        dossier["claims"][0]["source_ids"] = ["missing"]
        result = validate_dossier(dossier)
        self.assertFalse(result.ok)
        self.assertTrue(any("unknown source_id" in item for item in result.errors))

    def test_compile_exports_only_publishable_numeric_claims(self):
        dossier = self.valid_dossier()
        with tempfile.TemporaryDirectory() as temp:
            outdir = Path(temp)
            result = compile_dossier(dossier, outdir)
            self.assertTrue(result.ok, result.errors)
            self.assertTrue((outdir / "research-report.md").exists())
            self.assertTrue((outdir / "source-ledger.json").exists())
            self.assertTrue((outdir / "data-acquisition-plan.md").exists())
            with (outdir / "numeric-evidence.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["claim_id"], "claim-1")

    def test_example_dossier_is_valid(self):
        example = json.loads((ROOT / "examples" / "research-dossier.example.json").read_text(encoding="utf-8"))
        result = validate_dossier(example)
        self.assertTrue(result.ok, result.errors)


if __name__ == "__main__":
    unittest.main()
