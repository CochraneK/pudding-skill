from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mental_health_story import import_ihme, normalize_gho_record


class GlobalMentalHealthStoryTests(unittest.TestCase):
    def test_normalize_gho_record(self):
        row = {
            "SpatialDim": "JPN",
            "TimeDim": 2020,
            "NumericValue": 12.5,
            "Low": 10.0,
            "High": 15.0,
        }
        normalized = normalize_gho_record(row, "psychiatrists_per_100k")
        self.assertEqual(normalized["country_code"], "JPN")
        self.assertEqual(normalized["year"], 2020)
        self.assertEqual(normalized["value"], 12.5)
        self.assertEqual(normalized["metric"], "psychiatrists_per_100k")

    def test_import_ihme_accepts_common_export_columns(self):
        csv_text = "Location,Year,Val,Measure,Cause,Metric,Sex,Age\nJapan,2023,4.2,Prevalence,Depressive disorders,Percent,Both,Age-standardized\n"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "ihme.csv"
            output = root / "normalized.json"
            source.write_text(csv_text, encoding="utf-8")
            import_ihme(source, output)
            rows = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["country"], "Japan")
            self.assertEqual(rows[0]["year"], 2023)
            self.assertEqual(rows[0]["value"], 4.2)
            self.assertEqual(rows[0]["cause"], "Depressive disorders")


if __name__ == "__main__":
    unittest.main()
