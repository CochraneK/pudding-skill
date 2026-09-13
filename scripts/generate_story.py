#!/usr/bin/env python3
"""Generate normalized story data consumed by AutoStory.svelte.

The renderer is intentionally generic and deterministic. Agents can replace or extend
the generated route after the baseline is proven to build.
"""
from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from profile_data import load_rows, parse_number
from validate_story import validate


def serializable_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{str(k): v for k, v in row.items()} for row in rows]


def prepare_chart(spec: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    visual_type = spec["visuals"][0]["type"]
    fields = spec.get("fields", {})
    metadata = spec.get("field_metadata", {}) if isinstance(spec.get("field_metadata"), dict) else {}

    def field_label(field: str) -> str:
        meta = metadata.get(field, {}) if isinstance(metadata.get(field, {}), dict) else {}
        return str(meta.get("label") or field.replace("_", " "))

    if visual_type == "bar":
        category = fields["category"]
        if fields.get("derive") == "change_gap":
            time_field, metric_a, metric_b = fields["time"], fields["metric_a"], fields["metric_b"]
            grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in rows:
                label = str(row.get(category, "")).strip()
                if label:
                    grouped_rows[label].append(row)
            data = []
            for label, group_rows in grouped_rows.items():
                group_rows.sort(key=lambda row: str(row.get(time_field, "")))
                if len(group_rows) < 2:
                    continue
                start, end = group_rows[0], group_rows[-1]
                a0, a1 = parse_number(str(start.get(metric_a, ""))), parse_number(str(end.get(metric_a, "")))
                b0, b1 = parse_number(str(start.get(metric_b, ""))), parse_number(str(end.get(metric_b, "")))
                if None in (a0, a1, b0, b1):
                    continue
                data.append({
                    "label": label,
                    "value": (b1 - b0) - (a1 - a0),
                    "change_a": a1 - a0,
                    "change_b": b1 - b0,
                })
            data.sort(key=lambda item: abs(item["value"]), reverse=True)
            return {
                "type": "bar", "x_label": field_label(category),
                "y_label": f"Δ {field_label(metric_b)} − Δ {field_label(metric_a)}",
                "data": data[:20], "zero_centered": True
            }

        metric = fields["y"]
        grouped: dict[str, list[float]] = defaultdict(list)
        for row in rows:
            value = parse_number(str(row.get(metric, "")))
            label = str(row.get(category, "")).strip()
            if label and value is not None:
                grouped[label].append(value)
        data = [
            {"label": label, "value": sum(values) / len(values)}
            for label, values in grouped.items() if values
        ]
        data.sort(key=lambda item: item["value"], reverse=True)
        return {"type": "bar", "x_label": field_label(category), "y_label": field_label(metric), "data": data[:20]}

    if visual_type == "line":
        x, y = fields["x"], fields["y"]
        series_field = fields.get("series")
        data = []
        for row in rows:
            value = parse_number(str(row.get(y, "")))
            xv = str(row.get(x, "")).strip()
            if value is None or not xv:
                continue
            data.append({"x": xv, "y": value, "series": str(row.get(series_field, "All")) if series_field else "All"})
        data.sort(key=lambda item: (item["series"], item["x"]))
        return {"type": "line", "x_label": field_label(x), "y_label": field_label(y), "series_label": field_label(series_field) if series_field else None, "data": data[:500]}

    if visual_type == "scatter":
        x, y = fields["x"], fields["y"]
        data = []
        for row in rows:
            xv = parse_number(str(row.get(x, "")))
            yv = parse_number(str(row.get(y, "")))
            if xv is not None and yv is not None:
                data.append({"x": xv, "y": yv})
        return {"type": "scatter", "x_label": field_label(x), "y_label": field_label(y), "data": data[:1000]}

    if visual_type == "histogram":
        metric = fields["y"]
        values = [parse_number(str(row.get(metric, ""))) for row in rows]
        values = [v for v in values if v is not None]
        if not values:
            return {"type": "histogram", "x_label": field_label(metric), "data": []}
        lo, hi = min(values), max(values)
        bins = min(12, max(5, round(len(values) ** 0.5)))
        if lo == hi:
            data = [{"label": str(lo), "value": len(values)}]
        else:
            width = (hi - lo) / bins
            counts = [0] * bins
            for value in values:
                index = min(bins - 1, int((value - lo) / width))
                counts[index] += 1
            data = [
                {"label": f"{lo + i * width:.2g}–{lo + (i + 1) * width:.2g}", "value": count}
                for i, count in enumerate(counts)
            ]
        return {"type": "histogram", "x_label": field_label(metric), "y_label": "count", "data": data}

    raise ValueError(f"Unsupported visual type for baseline renderer: {visual_type}")


def generate(spec_path: Path, data_path: Path, output_path: Path) -> dict[str, Any]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    errors = validate(spec)
    if errors:
        raise ValueError("Invalid story spec:\n- " + "\n- ".join(errors))
    rows = load_rows(data_path)
    chart = prepare_chart(spec, rows)
    bundle = {"spec": spec, "chart": chart, "row_count": len(rows), "source_file": data_path.name}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("data", type=Path)
    parser.add_argument("--output", type=Path, default=Path("src/data/auto-story.json"))
    args = parser.parse_args()
    bundle = generate(args.spec, args.data, args.output)
    print(f"Wrote {args.output} ({bundle['chart']['type']}, {bundle['row_count']} source rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
