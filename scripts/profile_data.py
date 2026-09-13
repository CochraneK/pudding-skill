#!/usr/bin/env python3
"""Profile CSV, TSV, or row-oriented JSON for editorial data-story planning."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_number(value: str) -> float | None:
    value = value.strip().replace(",", "")
    if not value:
        return None
    if value.endswith("%"):
        value = value[:-1]
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except ValueError:
        return None


def parse_date(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    candidates = (value, value[:10])
    for candidate in candidates:
        try:
            datetime.fromisoformat(candidate.replace("Z", "+00:00"))
            return True
        except ValueError:
            pass
    return False


def load_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list) and all(isinstance(row, dict) for row in data):
            return data
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list) and all(isinstance(row, dict) for row in value):
                    return value
        raise ValueError("JSON must be a list of objects, or contain a top-level list of objects.")

    delimiter = "\t" if suffix == ".tsv" else ","
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def classify(values: list[str]) -> tuple[str, dict[str, Any]]:
    nonempty = [value.strip() for value in values if value is not None and str(value).strip()]
    if not nonempty:
        return "empty", {}

    numbers = [parse_number(value) for value in nonempty]
    numeric = [number for number in numbers if number is not None]
    if len(numeric) / len(nonempty) >= 0.95:
        stats = {
            "min": min(numeric),
            "max": max(numeric),
            "mean": statistics.fmean(numeric),
            "median": statistics.median(numeric),
        }
        return "numeric", stats

    date_hits = sum(parse_date(value) for value in nonempty)
    if date_hits / len(nonempty) >= 0.9:
        return "date", {}

    unique_count = len(set(nonempty))
    avg_len = statistics.fmean(len(value) for value in nonempty)
    kind = "categorical" if unique_count <= min(50, max(10, len(nonempty) * 0.5)) else "text"
    return kind, {"average_length": round(avg_len, 1)}


def profile(path: Path) -> dict[str, Any]:
    rows = load_rows(path)
    if not rows:
        return {"file": str(path), "rows": 0, "columns": [], "duplicate_rows": 0}

    columns = list(dict.fromkeys(key for row in rows for key in row.keys()))
    result_columns = []

    for column in columns:
        raw_values = ["" if row.get(column) is None else str(row.get(column)) for row in rows]
        nonempty = [value for value in raw_values if value.strip()]
        kind, stats = classify(raw_values)
        counts = Counter(nonempty)
        top_values = [{"value": value, "count": count} for value, count in counts.most_common(5)]
        result_columns.append(
            {
                "name": column,
                "type": kind,
                "missing": len(raw_values) - len(nonempty),
                "missing_rate": round((len(raw_values) - len(nonempty)) / len(raw_values), 4),
                "unique": len(counts),
                "top_values": top_values,
                **stats,
            }
        )

    signatures = [json.dumps(row, sort_keys=True, ensure_ascii=False, default=str) for row in rows]
    duplicate_rows = len(signatures) - len(set(signatures))

    return {
        "file": str(path),
        "rows": len(rows),
        "column_count": len(columns),
        "duplicate_rows": duplicate_rows,
        "columns": result_columns,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="CSV, TSV, or JSON file")
    parser.add_argument("--output", type=Path, help="Optional path for JSON output")
    args = parser.parse_args()

    if not args.path.exists():
        parser.error(f"file not found: {args.path}")

    result = profile(args.path)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
