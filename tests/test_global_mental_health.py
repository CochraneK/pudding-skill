from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mental_health_story import build_capacity_dataset, import_ihme, latest_by_country, normalize_gho_record


class GlobalMentalHealthStoryTests(unittest.TestCase):
    def test_normalize_gho_record(self):
        row = {
            "SpatialDim": "JPN",
            "TimeDim": 2020,
            "NumericValue": 12.5,
            "Low": 10.0,
            "High": 15.0,
            "ParentLocationCode": "WPR",
            "ParentLocation": "Western Pacific",
            "IndicatorCode": "MH_6",
        }
        normalized = normalize_gho_record(row, "psychiatrists_per_100k")
        self.assertEqual(normalized["country_code"], "JPN")
        self.assertEqual(normalized["year"], 2020)
        self.assertEqual(normalized["value"], 12.5)
        self.assertEqual(normalized["metric"], "psychiatrists_per_100k")
        self.assertEqual(normalized["region_code"], "WPR")

    def test_latest_by_country_keeps_latest_non_missing_observation(self):
        rows = [
            {"country_code": "AAA", "year": 2014, "value": 2.0},
            {"country_code": "AAA", "year": 2017, "value": 3.0},
            {"country_code": "AAA", "year": 2020, "value": None},
            {"country_code": "BBB", "year": 2016, "value": 4.0},
        ]
        latest = latest_by_country(rows)
        self.assertEqual(latest["AAA"]["year"], 2017)
        self.assertEqual(latest["AAA"]["value"], 3.0)
        self.assertEqual(latest["BBB"]["value"], 4.0)

    def test_capacity_dataset_preserves_missingness_and_builds_historical_pair(self):
        country_dimension = [
            {"Code": "AAA", "Title": "Alpha", "ParentCode": "AFR", "ParentTitle": "Africa"},
            {"Code": "BBB", "Title": "Beta", "ParentCode": "EUR", "ParentTitle": "Europe"},
        ]
        indicator_rows = {
            "MH_21": [
                {"SpatialDim": "AAA", "TimeDim": 2016, "NumericValue": 2.0, "IndicatorCode": "MH_21"},
                {"SpatialDim": "BBB", "TimeDim": 2017, "NumericValue": 20.0, "IndicatorCode": "MH_21"},
            ],
            "MH_6": [],
            "MH_7": [],
            "MH_9": [],
            "MH_4": [
                {"SpatialDim": "AAA", "TimeDim": 2016, "NumericValue": 1.0, "IndicatorCode": "MH_4"},
            ],
            "MH_10": [],
            "GDO_q35": [
                {"SpatialDim": "AAA", "TimeDim": 2015, "NumericValue": 5.0, "IndicatorCode": "GDO_q35"},
                {"SpatialDim": "BBB", "TimeDim": 2015, "NumericValue": 3.0, "IndicatorCode": "GDO_q35"},
            ],
        }
        dataset = build_capacity_dataset(indicator_rows, country_dimension)
        alpha = next(country for country in dataset["countries"] if country["code"] == "AAA")
        beta = next(country for country in dataset["countries"] if country["code"] == "BBB")
        self.assertEqual(alpha["metrics"]["government_mental_health_spending_share"]["value"], 1.0)
        self.assertNotIn("government_mental_health_spending_share", beta["metrics"])
        self.assertEqual(dataset["historical_mismatch_lens"]["capacity_metric"], "total_mental_health_workforce_per_100k")
        self.assertEqual(dataset["historical_mismatch_lens"]["overlap_n"], 2)
        alpha_pair = next(row for row in dataset["historical_mismatch_lens"]["pairs"] if row["code"] == "AAA")
        self.assertEqual(alpha_pair["quadrant"], "higher_depression_lower_capacity")

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
