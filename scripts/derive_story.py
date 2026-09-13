#!/usr/bin/env python3
"""Derive a conservative baseline story spec from a tabular dataset.

This is intentionally heuristic. It gives an agent a grounded starting point, not a
finished editorial claim. Supported baseline patterns:
- time + category + numeric -> change-over-time comparison
- time + numeric -> time-series trend
- category + numeric -> ranked comparison
- two numeric fields -> correlation / scatter
- numeric field -> distribution summary
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from profile_data import load_rows, parse_number, profile


def fmt(value: float) -> str:
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    if abs(value) >= 100:
        return f"{value:.0f}"
    if abs(value) >= 10:
        return f"{value:.1f}".rstrip("0").rstrip(".")
    return f"{value:.2f}".rstrip("0").rstrip(".")


def numeric_values(rows: list[dict[str, Any]], field: str) -> list[float]:
    out: list[float] = []
    for row in rows:
        value = parse_number(str(row.get(field, "")))
        if value is not None:
            out.append(value)
    return out


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(v * v for v in dx) * sum(v * v for v in dy))
    if not denom:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / denom


def clean_rows(rows: list[dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
    return [row for row in rows if all(str(row.get(field, "")).strip() for field in fields)]


def derive(path: Path, question: str | None = None, audience: str = "general audience") -> dict[str, Any]:
    rows = load_rows(path)
    prof = profile(path)
    by_type: dict[str, list[str]] = defaultdict(list)
    for column in prof.get("columns", []):
        by_type[column["type"]].append(column["name"])

    dates = by_type["date"]
    cats = by_type["categorical"]
    numeric_columns = by_type["numeric"]
    temporal_names = {"year", "date", "time", "month", "quarter", "period"}
    numeric_time = [name for name in numeric_columns if name.lower() in temporal_names or name.lower().endswith("_year")]
    dates = list(dict.fromkeys(dates + numeric_time))
    nums = [name for name in numeric_columns if name not in dates]
    caveats = [
        "This spec was produced by deterministic heuristics and should be editorially reviewed before publication."
    ]
    sources = [{"label": path.name, "path": str(path)}]

    if dates and cats and len(nums) >= 2:
        date, category = dates[0], cats[0]
        metric_a, metric_b = nums[0], nums[1]
        grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in clean_rows(rows, [date, category, metric_a, metric_b]):
            grouped_rows[str(row[category])].append(row)
        gaps = []
        for name, group_rows in grouped_rows.items():
            group_rows.sort(key=lambda row: str(row[date]))
            if len(group_rows) < 2:
                continue
            start, end = group_rows[0], group_rows[-1]
            a0, a1 = parse_number(str(start[metric_a])), parse_number(str(end[metric_a]))
            b0, b1 = parse_number(str(start[metric_b])), parse_number(str(end[metric_b]))
            if None in (a0, a1, b0, b1):
                continue
            change_a = a1 - a0
            change_b = b1 - b0
            gap = change_b - change_a
            gaps.append((gap, name, str(start[date]), str(end[date]), change_a, change_b))
        if gaps:
            gaps.sort(key=lambda item: abs(item[0]), reverse=True)
            gap, name, start_period, end_period, change_a, change_b = gaps[0]
            verb = "outpaced" if gap >= 0 else "lagged"
            insight = (
                f"{metric_b} {verb} {metric_a} most in {name}: their changes differed by "
                f"{fmt(abs(gap))} between {start_period} and {end_period}."
            )
            return {
                "question": question or f"Where did {metric_b} diverge most from {metric_a} over time?",
                "audience": audience,
                "primary_insight": insight,
                "evidence": [{
                    "kind": "change_gap", "group_field": category, "group": name,
                    "time_field": date, "start_period": start_period, "end_period": end_period,
                    "metric_a": metric_a, "metric_b": metric_b,
                    "change_a": change_a, "change_b": change_b, "gap": gap
                }],
                "beats": [
                    {"operation": "establish", "purpose": f"Establish the common starting point for {metric_a} and {metric_b}."},
                    {"operation": "reveal", "purpose": f"Reveal how the two measures change by {date}."},
                    {"operation": "reorder", "purpose": f"Rank {category} by the divergence in change."},
                    {"operation": "highlight", "purpose": f"Highlight {name} as the largest absolute divergence."},
                ],
                "visuals": [{"type": "bar", "purpose": "Rank groups by the difference between two start-to-end changes.", "operation": "compare"}],
                "production_mode": "annotated-static",
                "fields": {
                    "category": category, "time": date, "metric_a": metric_a, "metric_b": metric_b,
                    "derive": "change_gap"
                },
                "sources": sources,
                "caveats": caveats,
            }

    if dates and cats and nums:
        date, category, metric = dates[0], cats[0], nums[0]
        grouped: dict[str, list[tuple[str, float]]] = defaultdict(list)
        for row in clean_rows(rows, [date, category, metric]):
            value = parse_number(str(row[metric]))
            if value is not None:
                grouped[str(row[category])].append((str(row[date]), value))
        changes = []
        for name, points in grouped.items():
            points.sort(key=lambda p: p[0])
            if len(points) >= 2:
                changes.append((points[-1][1] - points[0][1], name, points[0], points[-1]))
        if changes:
            changes.sort(key=lambda item: abs(item[0]), reverse=True)
            delta, name, start, end = changes[0]
            direction = "rose" if delta >= 0 else "fell"
            insight = f"{name} {direction} the most on {metric}, changing by {fmt(abs(delta))} from {start[0]} to {end[0]}."
            return {
                "question": question or f"How did {metric} change over time across {category}?",
                "audience": audience,
                "primary_insight": insight,
                "evidence": [
                    {
                        "kind": "change",
                        "metric": metric,
                        "group_field": category,
                        "group": name,
                        "start": {"period": start[0], "value": start[1]},
                        "end": {"period": end[0], "value": end[1]},
                        "change": delta,
                    }
                ],
                "beats": [
                    {"operation": "establish", "purpose": f"Establish the starting level of {metric} across {category}."},
                    {"operation": "reveal", "purpose": f"Reveal how {metric} changes over {date}."},
                    {"operation": "highlight", "purpose": f"Highlight {name} as the largest absolute change."},
                    {"operation": "annotate", "purpose": "State the strongest supported change and its limits."},
                ],
                "visuals": [
                    {"type": "line", "purpose": "Preserve time context while comparing groups.", "operation": "reveal"}
                ],
                "production_mode": "scrollytelling" if len(grouped) <= 8 else "small-multiples",
                "fields": {"x": date, "series": category, "y": metric},
                "sources": sources,
                "caveats": caveats,
            }

    if dates and nums:
        date, metric = dates[0], nums[0]
        points = []
        for row in clean_rows(rows, [date, metric]):
            value = parse_number(str(row[metric]))
            if value is not None:
                points.append((str(row[date]), value))
        points.sort(key=lambda p: p[0])
        if len(points) >= 2:
            delta = points[-1][1] - points[0][1]
            direction = "increased" if delta >= 0 else "decreased"
            insight = f"{metric} {direction} by {fmt(abs(delta))} between {points[0][0]} and {points[-1][0]}."
            return {
                "question": question or f"How has {metric} changed over time?",
                "audience": audience,
                "primary_insight": insight,
                "evidence": [{"kind": "change", "metric": metric, "start": points[0], "end": points[-1], "change": delta}],
                "beats": [
                    {"operation": "establish", "purpose": "Establish the starting level."},
                    {"operation": "reveal", "purpose": "Reveal the time trend."},
                    {"operation": "annotate", "purpose": "Annotate the start-to-end change."},
                ],
                "visuals": [{"type": "line", "purpose": "Show the time trend.", "operation": "reveal"}],
                "production_mode": "annotated-static",
                "fields": {"x": date, "y": metric},
                "sources": sources,
                "caveats": caveats,
            }

    if cats and nums:
        category, metric = cats[0], nums[0]
        grouped_numbers: dict[str, list[float]] = defaultdict(list)
        for row in clean_rows(rows, [category, metric]):
            value = parse_number(str(row[metric]))
            if value is not None:
                grouped_numbers[str(row[category])].append(value)
        summary = [(statistics.fmean(vals), name, len(vals)) for name, vals in grouped_numbers.items() if vals]
        summary.sort(reverse=True)
        if len(summary) >= 2:
            hi, lo = summary[0], summary[-1]
            gap = hi[0] - lo[0]
            insight = f"{hi[1]} has the highest average {metric} ({fmt(hi[0])}), {fmt(gap)} above {lo[1]}."
            return {
                "question": question or f"How does {metric} differ across {category}?",
                "audience": audience,
                "primary_insight": insight,
                "evidence": [
                    {"kind": "group_mean", "metric": metric, "group_field": category, "group": hi[1], "value": hi[0], "n": hi[2]},
                    {"kind": "group_mean", "metric": metric, "group_field": category, "group": lo[1], "value": lo[0], "n": lo[2]},
                ],
                "beats": [
                    {"operation": "establish", "purpose": f"Show the distribution of average {metric} by {category}."},
                    {"operation": "reorder", "purpose": "Order groups to make rank immediately legible."},
                    {"operation": "highlight", "purpose": f"Highlight {hi[1]} and the gap to {lo[1]}."},
                ],
                "visuals": [{"type": "bar", "purpose": "Compare ranked group averages.", "operation": "compare"}],
                "production_mode": "annotated-static",
                "fields": {"category": category, "y": metric, "aggregate": "mean"},
                "sources": sources,
                "caveats": caveats,
            }

    if len(nums) >= 2:
        x_field, y_field = nums[0], nums[1]
        xs, ys = [], []
        for row in rows:
            x = parse_number(str(row.get(x_field, "")))
            y = parse_number(str(row.get(y_field, "")))
            if x is not None and y is not None:
                xs.append(x)
                ys.append(y)
        r = pearson(xs, ys)
        if r is not None:
            strength = "strong" if abs(r) >= 0.7 else "moderate" if abs(r) >= 0.4 else "weak"
            direction = "positive" if r >= 0 else "negative"
            insight = f"{x_field} and {y_field} show a {strength} {direction} association (r={r:.2f}) in these observations."
            caveats.append("Correlation does not establish causation.")
            return {
                "question": question or f"How are {x_field} and {y_field} related?",
                "audience": audience,
                "primary_insight": insight,
                "evidence": [{"kind": "correlation", "x": x_field, "y": y_field, "r": r, "n": len(xs)}],
                "beats": [
                    {"operation": "establish", "purpose": "Show the full set of observations."},
                    {"operation": "reveal", "purpose": "Reveal the direction and strength of association."},
                    {"operation": "annotate", "purpose": "State the correlation without implying causation."},
                ],
                "visuals": [{"type": "scatter", "purpose": "Show the relationship between two numeric variables.", "operation": "compare"}],
                "production_mode": "annotated-static",
                "fields": {"x": x_field, "y": y_field},
                "sources": sources,
                "caveats": caveats,
            }

    if nums:
        metric = nums[0]
        values = numeric_values(rows, metric)
        if values:
            med = statistics.median(values)
            insight = f"The median {metric} is {fmt(med)}, spanning {fmt(min(values))} to {fmt(max(values))}."
            return {
                "question": question or f"What is the distribution of {metric}?",
                "audience": audience,
                "primary_insight": insight,
                "evidence": [{"kind": "distribution", "metric": metric, "min": min(values), "median": med, "max": max(values), "n": len(values)}],
                "beats": [
                    {"operation": "establish", "purpose": "Show the overall distribution."},
                    {"operation": "annotate", "purpose": "Mark the center and range."},
                    {"operation": "highlight", "purpose": "Call out notable extremes for review."},
                ],
                "visuals": [{"type": "histogram", "purpose": "Show distribution shape and spread.", "operation": "establish"}],
                "production_mode": "annotated-static",
                "fields": {"y": metric},
                "sources": sources,
                "caveats": caveats,
            }

    raise ValueError("No supported quantitative story pattern was found. Add/clean numeric fields or write the story spec manually.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--question", help="Optional research question")
    parser.add_argument("--audience", default="general audience")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    spec = derive(args.path, args.question, args.audience)
    payload = json.dumps(spec, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
