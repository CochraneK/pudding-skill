from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_story import derive
from generate_story import generate
from validate_story import validate


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

    def test_category_numeric_generates_bar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.write(root, "groups.csv", "group,value\nA,10\nA,14\nB,3\nB,5\nC,8\nC,8\n")
            spec = derive(data)
            self.assertEqual(spec["visuals"][0]["type"], "bar")
            self.assertIn("highest average", spec["primary_insight"])

    def test_numeric_pair_generates_scatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.write(root, "pairs.csv", "x,y\n1,2\n2,4\n3,6\n4,8\n5,10\n")
            spec = derive(data)
            self.assertEqual(spec["visuals"][0]["type"], "scatter")
            self.assertGreater(spec["evidence"][0]["r"], 0.99)

    def test_generate_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = ROOT / "examples" / "sample-data.csv"
            spec = derive(data)
            spec_path = root / "spec.json"
            out = root / "bundle.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            bundle = generate(spec_path, data, out)
            self.assertTrue(out.exists())
            self.assertEqual(bundle["chart"]["type"], "bar")
            self.assertEqual(bundle["chart"]["data"][0]["label"], "Harbor")


if __name__ == "__main__":
    unittest.main()
