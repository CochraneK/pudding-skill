#!/usr/bin/env python3
"""Recompute quantitative evidence from raw data and fail on story-spec drift.

This is deliberately independent of the prose claim. It verifies the numeric evidence
object that the prose is expected to summarize, creating an auditable data -> evidence chain.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from derive_story import pearson
from profile_data import load_rows, parse_number


def close(a: Any, b: Any, tol: float = 1e-7) -> bool:
    try:
        return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)
    except (TypeError, ValueError):
        return False


def result(name: str, ok: bool, expected: Any, actual: Any) -> dict[str, Any]:
    return {"field": name, "ok": bool(ok), "expected": expected, "actual": actual}


def verify_evidence(evidence: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    kind = evidence.get("kind")
    checks: list[dict[str, Any]] = []

    if kind == "change_gap":
        category = evidence["group_field"]
        group_name = str(evidence["group"])
        time_field = evidence["time_field"]
        metric_a, metric_b = evidence["metric_a"], evidence["metric_b"]
        group_rows = [row for row in rows if str(row.get(category, "")) == group_name]
        group_rows.sort(key=lambda row: str(row.get(time_field, "")))
        if len(group_rows) < 2:
            return {"kind": kind, "status": "FAIL", "checks": [], "error": "Selected group has fewer than two time observations."}
        start, end = group_rows[0], group_rows[-1]
        a0, a1 = parse_number(str(start.get(metric_a, ""))), parse_number(str(end.get(metric_a, "")))
        b0, b1 = parse_number(str(start.get(metric_b, ""))), parse_number(str(end.get(metric_b, "")))
        if None in (a0, a1, b0, b1):
            return {"kind": kind, "status": "FAIL", "checks": [], "error": "Evidence metrics are not numeric in selected start/end rows."}
        da, db = a1 - a0, b1 - b0
        gap = db - da
        checks.extend([
            result("start_period", str(evidence.get("start_period")) == str(start.get(time_field)), evidence.get("start_period"), str(start.get(time_field))),
            result("end_period", str(evidence.get("end_period")) == str(end.get(time_field)), evidence.get("end_period"), str(end.get(time_field))),
            result("change_a", close(evidence.get("change_a"), da), evidence.get("change_a"), da),
            result("change_b", close(evidence.get("change_b"), db), evidence.get("change_b"), db),
            result("gap", close(evidence.get("gap"), gap), evidence.get("gap"), gap),
        ])

    elif kind == "change":
        metric = evidence["metric"]
        group_field = evidence.get("group_field")
        group_name = evidence.get("group")
        working = rows
        if group_field and group_name is not None:
            working = [row for row in rows if str(row.get(group_field, "")) == str(group_name)]
        start_info, end_info = evidence["start"], evidence["end"]
        start_period, end_period = str(start_info["period"]), str(end_info["period"])
        # Locate period field by searching rows for the stored period. Candidate specs use a single temporal field.
        temporal_field = None
        for key in (working[0].keys() if working else []):
            values = {str(row.get(key, "")) for row in working}
            if start_period in values and end_period in values:
                temporal_field = key
                break
        if not temporal_field:
            return {"kind": kind, "status": "FAIL", "checks": [], "error": "Could not resolve temporal field for change evidence."}
        start_rows = [row for row in working if str(row.get(temporal_field, "")) == start_period]
        end_rows = [row for row in working if str(row.get(temporal_field, "")) == end_period]
        if not start_rows or not end_rows:
            return {"kind": kind, "status": "FAIL", "checks": [], "error": "Stored start/end periods are absent from raw data."}
        sv = parse_number(str(start_rows[0].get(metric, "")))
        ev = parse_number(str(end_rows[0].get(metric, "")))
        if sv is None or ev is None:
            return {"kind": kind, "status": "FAIL", "checks": [], "error": "Stored change metric is not numeric."}
        checks.extend([
            result("start.value", close(start_info.get("value"), sv), start_info.get("value"), sv),
            result("end.value", close(end_info.get("value"), ev), end_info.get("value"), ev),
            result("change", close(evidence.get("change"), ev - sv), evidence.get("change"), ev - sv),
        ])

    elif kind == "group_mean":
        metric, group_field, group_name = evidence["metric"], evidence["group_field"], str(evidence["group"])
        values = [parse_number(str(row.get(metric, ""))) for row in rows if str(row.get(group_field, "")) == group_name]
        values = [v for v in values if v is not None]
        if not values:
            return {"kind": kind, "status": "FAIL", "checks": [], "error": "No numeric observations for selected group mean."}
        mean = statistics.fmean(values)
        checks.extend([
            result("value", close(evidence.get("value"), mean), evidence.get("value"), mean),
            result("n", int(evidence.get("n", -1)) == len(values), evidence.get("n"), len(values)),
        ])
        if evidence.get("lowest_group") is not None:
            grouped: dict[str, list[float]] = defaultdict(list)
            for row in rows:
                value = parse_number(str(row.get(metric, "")))
                label = str(row.get(group_field, ""))
                if label and value is not None:
                    grouped[label].append(value)
            means = sorted((statistics.fmean(vals), label) for label, vals in grouped.items() if vals)
            low_value, low_group = means[0]
            checks.extend([
                result("lowest_group", str(evidence.get("lowest_group")) == low_group, evidence.get("lowest_group"), low_group),
                result("lowest_value", close(evidence.get("lowest_value"), low_value), evidence.get("lowest_value"), low_value),
            ])

    elif kind == "correlation":
        x_field, y_field = evidence["x"], evidence["y"]
        pairs = []
        for row in rows:
            x, y = parse_number(str(row.get(x_field, ""))), parse_number(str(row.get(y_field, "")))
            if x is not None and y is not None:
                pairs.append((x, y))
        if len(pairs) < 3:
            return {"kind": kind, "status": "FAIL", "checks": [], "error": "Too few paired observations for correlation."}
        xs, ys = zip(*pairs)
        r = pearson(list(xs), list(ys))
        checks.extend([
            result("r", r is not None and close(evidence.get("r"), r), evidence.get("r"), r),
            result("n", int(evidence.get("n", -1)) == len(pairs), evidence.get("n"), len(pairs)),
        ])

    elif kind == "distribution":
        metric = evidence["metric"]
        values = [parse_number(str(row.get(metric, ""))) for row in rows]
        values = [v for v in values if v is not None]
        if not values:
            return {"kind": kind, "status": "FAIL", "checks": [], "error": "No numeric values for distribution evidence."}
        actual = {"min": min(values), "median": statistics.median(values), "max": max(values), "n": len(values)}
        for key, value in actual.items():
            ok = int(evidence.get(key, -1)) == value if key == "n" else close(evidence.get(key), value)
            checks.append(result(key, ok, evidence.get(key), value))

    else:
        return {"kind": kind, "status": "FAIL", "checks": [], "error": f"Unsupported evidence kind: {kind}"}

    status = "PASS" if checks and all(check["ok"] for check in checks) else "FAIL"
    return {"kind": kind, "status": status, "checks": checks}


def verify(spec: dict[str, Any], data_path: Path) -> dict[str, Any]:
    rows = load_rows(data_path)
    evidence_items = spec.get("evidence", [])
    reports = [verify_evidence(item, rows) for item in evidence_items if isinstance(item, dict)]
    status = "PASS" if reports and all(report["status"] == "PASS" for report in reports) else "FAIL"
    return {
        "status": status,
        "source_file": data_path.name,
        "evidence_count": len(reports),
        "reports": reports,
        "note": "Quantitative evidence was independently recomputed from the raw source rows. Prose still requires editorial review.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("data", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    report = verify(spec, args.data)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(f"{report['status']}: recomputed {report['evidence_count']} evidence object(s) from {report['source_file']}")
    for evidence_report in report["reports"]:
        print(f"- {evidence_report['kind']}: {evidence_report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
