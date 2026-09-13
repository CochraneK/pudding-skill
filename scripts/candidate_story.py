#!/usr/bin/env python3
"""Generate and score multiple defensible story candidates from tabular data.

The scores are deterministic editorial-priority proxies, not claims of newsworthiness.
They help an agent compare supported directions before exercising human/LLM judgment.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from derive_story import fmt, pearson
from data_contract import field_meta, label_for, load_contract
from profile_data import load_rows, parse_number, profile

TEMPORAL_NAMES = {"year", "date", "time", "month", "quarter", "period"}


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def words(value: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", value.lower().replace("_", " "))
    normalized = set()
    for token in tokens:
        if len(token) > 3 and token.endswith("s"):
            token = token[:-1]
        normalized.add(token)
    return normalized


QUESTION_STOPWORDS = {
    "which", "what", "where", "when", "how", "did", "does", "do", "the", "a", "an", "of", "to", "from",
    "after", "before", "over", "across", "in", "on", "and", "or", "most", "more", "less", "saw", "show", "shows",
    "fictional", "sharp", "sharply", "much", "many", "these", "those", "their", "between",
}


def question_relevance(question: str | None, fields: list[str], claim: str, pattern: str = "") -> float:
    if not question:
        return 70.0
    q_all = words(question)
    q = {token for token in q_all if token not in QUESTION_STOPWORDS}
    if not q:
        return 60.0
    candidate_terms = words(" ".join(fields) + " " + claim)
    overlap = len(q & candidate_terms)
    base = 30.0 + 70.0 * overlap / max(1, min(6, len(q)))
    intent_bonus = 0.0
    if q_all & {"separate", "diverge", "divergence", "gap", "difference", "outpace", "lag"}:
        intent_bonus += 18.0 if pattern == "change_gap" else -4.0
    if q_all & {"relationship", "related", "association", "correlation"}:
        intent_bonus += 18.0 if pattern == "correlation" else -4.0
    if q_all & {"distribution", "spread", "median", "range"}:
        intent_bonus += 18.0 if pattern == "distribution" else -4.0
    if q_all & {"change", "trend", "trajectory", "grew", "growth", "fell", "rose"}:
        intent_bonus += 12.0 if pattern == "group_change" else 0.0
    if q_all & {"highest", "lowest", "rank", "ranking", "average", "mean"}:
        intent_bonus += 12.0 if pattern == "group_mean" else 0.0
    return clamp(base + intent_bonus)


def evidence_score(n: int) -> float:
    if n <= 0:
        return 0.0
    return clamp(38.0 + 18.0 * math.log2(max(1, n)))


def simplicity_score(field_count: int, transformations: int = 1) -> float:
    return clamp(100.0 - max(0, field_count - 2) * 9.0 - max(0, transformations - 1) * 8.0)


def score_candidate(candidate: dict[str, Any], total_rows: int, question: str | None) -> dict[str, Any]:
    n = int(candidate.get("n", 0))
    components = {
        "evidence": evidence_score(n),
        "coverage": clamp(100.0 * n / max(1, total_rows)),
        "effect": clamp(float(candidate.get("effect", 50.0))),
        "distinctiveness": clamp(float(candidate.get("distinctiveness", 50.0))),
        "visual_fit": clamp(float(candidate.get("visual_fit", 80.0))),
        "simplicity": simplicity_score(len(candidate.get("fields_used", [])), int(candidate.get("transformations", 1))),
        "question_relevance": question_relevance(question, candidate.get("fields_used", []), candidate.get("claim", ""), candidate.get("pattern", "")),
    }
    penalty = clamp(float(candidate.get("risk_penalty", 0.0)), 0.0, 35.0)
    weighted = (
        components["evidence"] * 0.22
        + components["coverage"] * 0.14
        + components["effect"] * 0.20
        + components["distinctiveness"] * 0.14
        + components["visual_fit"] * 0.10
        + components["simplicity"] * 0.06
        + components["question_relevance"] * 0.14
        - penalty
    )
    candidate["score"] = round(clamp(weighted), 1)
    candidate["score_components"] = {k: round(v, 1) for k, v in components.items()}
    candidate["risk_penalty"] = round(penalty, 1)
    return candidate


def candidate_id(pattern: str, *parts: str) -> str:
    raw = "-".join((pattern,) + parts)
    return re.sub(r"[^a-z0-9-]+", "-", raw.lower().replace("_", "-")).strip("-")


def numeric_types(path: Path, contract: dict[str, Any] | None = None) -> tuple[list[dict[str, Any]], list[str], list[str], list[str]]:
    rows = load_rows(path)
    prof = profile(path)
    by_type: dict[str, list[str]] = defaultdict(list)
    for column in prof.get("columns", []):
        by_type[column["type"]].append(column["name"])
    dates = list(by_type["date"])
    numeric_columns = list(by_type["numeric"])
    numeric_time = [name for name in numeric_columns if name.lower() in TEMPORAL_NAMES or name.lower().endswith("_year")]
    dates = list(dict.fromkeys(dates + numeric_time))
    nums = [name for name in numeric_columns if name not in dates]
    cats = list(by_type["categorical"])

    if contract:
        for field, meta in contract.get("fields", {}).items():
            role = meta.get("role") if isinstance(meta, dict) else None
            if role in {"identifier", "ignore"}:
                dates = [name for name in dates if name != field]
                cats = [name for name in cats if name != field]
                nums = [name for name in nums if name != field]
            elif role == "time":
                if field not in dates:
                    dates = [field] + dates
                cats = [name for name in cats if name != field]
                nums = [name for name in nums if name != field]
            elif role == "category":
                if field not in cats:
                    cats = [field] + cats
                dates = [name for name in dates if name != field]
                nums = [name for name in nums if name != field]
            elif role == "measure":
                if field not in nums:
                    nums.append(field)
                dates = [name for name in dates if name != field]
                cats = [name for name in cats if name != field]
    return rows, list(dict.fromkeys(dates)), list(dict.fromkeys(cats)), list(dict.fromkeys(nums))


def complete_rows(rows: list[dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
    return [row for row in rows if all(str(row.get(field, "")).strip() for field in fields)]


def change_gap_candidates(rows: list[dict[str, Any]], date: str, category: str, nums: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for metric_a, metric_b in itertools.combinations(nums[:6], 2):
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        usable = complete_rows(rows, [date, category, metric_a, metric_b])
        for row in usable:
            grouped[str(row[category])].append(row)
        gaps = []
        max_change = 0.0
        for name, group in grouped.items():
            group.sort(key=lambda row: str(row[date]))
            if len(group) < 2:
                continue
            start, end = group[0], group[-1]
            vals = [parse_number(str(start[metric_a])), parse_number(str(end[metric_a])), parse_number(str(start[metric_b])), parse_number(str(end[metric_b]))]
            if any(v is None for v in vals):
                continue
            a0, a1, b0, b1 = vals  # type: ignore[misc]
            da, db = a1 - a0, b1 - b0
            gap = db - da
            max_change = max(max_change, abs(da), abs(db))
            gaps.append((abs(gap), gap, name, str(start[date]), str(end[date]), da, db))
        if not gaps:
            continue
        gaps.sort(reverse=True)
        abs_gap, gap, name, start_period, end_period, da, db = gaps[0]
        second = gaps[1][0] if len(gaps) > 1 else 0.0
        distinct = 100.0 * max(0.0, abs_gap - second) / max(abs_gap, 1e-9)
        effect = 100.0 * abs_gap / max(max_change, 1e-9)
        verb = "outpaced" if gap >= 0 else "lagged"
        claim = f"{metric_b} {verb} {metric_a} most in {name}: their changes differed by {fmt(abs_gap)} between {start_period} and {end_period}."
        out.append({
            "id": candidate_id("change-gap", metric_a, metric_b),
            "pattern": "change_gap",
            "claim": claim,
            "question": f"Where did {metric_b} diverge most from {metric_a} over time?",
            "n": len(usable),
            "effect": effect,
            "distinctiveness": distinct,
            "visual_fit": 96,
            "transformations": 2,
            "risk_penalty": 0 if len(gaps) >= 3 else 5,
            "fields_used": [date, category, metric_a, metric_b],
            "visual": "bar",
            "production_mode": "annotated-static",
            "evidence": {
                "kind": "change_gap", "group_field": category, "group": name, "time_field": date,
                "start_period": start_period, "end_period": end_period, "metric_a": metric_a, "metric_b": metric_b,
                "change_a": da, "change_b": db, "gap": gap,
            },
            "fields": {"category": category, "time": date, "metric_a": metric_a, "metric_b": metric_b, "derive": "change_gap"},
            "rationale": "Compares start-to-end changes across groups and isolates the strongest divergence between two measures.",
        })
    return out


def group_change_candidates(rows: list[dict[str, Any]], date: str, category: str, nums: list[str]) -> list[dict[str, Any]]:
    out = []
    for metric in nums[:8]:
        usable = complete_rows(rows, [date, category, metric])
        grouped: dict[str, list[tuple[str, float]]] = defaultdict(list)
        for row in usable:
            value = parse_number(str(row[metric]))
            if value is not None:
                grouped[str(row[category])].append((str(row[date]), value))
        changes = []
        all_values = []
        for name, points in grouped.items():
            points.sort(key=lambda p: p[0])
            all_values.extend(v for _, v in points)
            if len(points) >= 2:
                changes.append((abs(points[-1][1] - points[0][1]), points[-1][1] - points[0][1], name, points[0], points[-1]))
        if not changes:
            continue
        changes.sort(reverse=True)
        abs_delta, delta, name, start, end = changes[0]
        second = changes[1][0] if len(changes) > 1 else 0
        data_range = max(all_values) - min(all_values) if all_values else 0
        direction = "rose" if delta >= 0 else "fell"
        out.append({
            "id": candidate_id("group-change", metric),
            "pattern": "group_change",
            "claim": f"{name} {direction} the most on {metric}, changing by {fmt(abs_delta)} from {start[0]} to {end[0]}.",
            "question": f"How did {metric} change over time across {category}?",
            "n": len(usable),
            "effect": 100.0 * abs_delta / max(abs(start[1]), 1e-9),
            "distinctiveness": 100.0 * max(0.0, abs_delta - second) / max(abs_delta, 1e-9),
            "visual_fit": 92,
            "transformations": 1,
            "risk_penalty": 0 if len(grouped) >= 3 else 4,
            "fields_used": [date, category, metric],
            "visual": "line",
            "production_mode": "scrollytelling" if len(grouped) <= 8 else "small-multiples",
            "evidence": {"kind": "change", "metric": metric, "group_field": category, "group": name, "start": {"period": start[0], "value": start[1]}, "end": {"period": end[0], "value": end[1]}, "change": delta},
            "fields": {"x": date, "series": category, "y": metric},
            "rationale": "Preserves time context while identifying the group with the largest absolute change.",
        })
    return out


def group_mean_candidates(rows: list[dict[str, Any]], category: str, nums: list[str], repeated_time: bool) -> list[dict[str, Any]]:
    out = []
    for metric in nums[:8]:
        usable = complete_rows(rows, [category, metric])
        grouped: dict[str, list[float]] = defaultdict(list)
        for row in usable:
            value = parse_number(str(row[metric]))
            if value is not None:
                grouped[str(row[category])].append(value)
        summary = sorted([(statistics.fmean(v), name, len(v)) for name, v in grouped.items() if v], reverse=True)
        if len(summary) < 2:
            continue
        hi, lo = summary[0], summary[-1]
        values = [v for v, _, _ in summary]
        spread = max(values) - min(values)
        second = summary[1][0]
        distinct = 100.0 * max(0.0, hi[0] - second) / max(spread, 1e-9)
        penalty = 10 if repeated_time else 0
        out.append({
            "id": candidate_id("group-mean", metric),
            "pattern": "group_mean",
            "claim": f"{hi[1]} has the highest average {metric} ({fmt(hi[0])}), {fmt(hi[0] - lo[0])} above {lo[1]}.",
            "question": f"How does {metric} differ across {category}?",
            "n": len(usable),
            "effect": clamp(60 + 40 * (hi[0] - lo[0]) / max(abs(hi[0]), abs(lo[0]), 1e-9)),
            "distinctiveness": distinct,
            "visual_fit": 94,
            "transformations": 1,
            "risk_penalty": penalty,
            "fields_used": [category, metric],
            "visual": "bar",
            "production_mode": "annotated-static",
            "evidence": {"kind": "group_mean", "metric": metric, "group_field": category, "group": hi[1], "value": hi[0], "n": hi[2], "lowest_group": lo[1], "lowest_value": lo[0]},
            "fields": {"category": category, "y": metric, "aggregate": "mean"},
            "rationale": "Makes rank and magnitude easy to compare across categories.",
            "caveat": "Averages pool repeated time periods; inspect time structure before publication." if repeated_time else None,
        })
    return out


def correlation_candidates(rows: list[dict[str, Any]], nums: list[str], structured_time: bool) -> list[dict[str, Any]]:
    out = []
    for x_field, y_field in itertools.combinations(nums[:8], 2):
        pairs = []
        for row in rows:
            x = parse_number(str(row.get(x_field, "")))
            y = parse_number(str(row.get(y_field, "")))
            if x is not None and y is not None:
                pairs.append((x, y))
        if len(pairs) < 3:
            continue
        xs, ys = zip(*pairs)
        r = pearson(list(xs), list(ys))
        if r is None:
            continue
        strength = "strong" if abs(r) >= 0.7 else "moderate" if abs(r) >= 0.4 else "weak"
        direction = "positive" if r >= 0 else "negative"
        penalty = 8 + (10 if structured_time else 0)
        out.append({
            "id": candidate_id("correlation", x_field, y_field),
            "pattern": "correlation",
            "claim": f"{x_field} and {y_field} show a {strength} {direction} association (r={r:.2f}) in these observations.",
            "question": f"How are {x_field} and {y_field} related?",
            "n": len(pairs),
            "effect": abs(r) * 100,
            "distinctiveness": 55,
            "visual_fit": 90,
            "transformations": 1,
            "risk_penalty": penalty,
            "fields_used": [x_field, y_field],
            "visual": "scatter",
            "production_mode": "annotated-static",
            "evidence": {"kind": "correlation", "x": x_field, "y": y_field, "r": r, "n": len(pairs)},
            "fields": {"x": x_field, "y": y_field},
            "rationale": "Tests whether two quantitative measures move together, while explicitly avoiding causal language.",
            "caveat": "Correlation does not establish causation; repeated measures or shared trends may inflate association." if structured_time else "Correlation does not establish causation.",
        })
    return out


def distribution_candidates(rows: list[dict[str, Any]], nums: list[str]) -> list[dict[str, Any]]:
    out = []
    for metric in nums[:8]:
        vals = [parse_number(str(row.get(metric, ""))) for row in rows]
        values = [v for v in vals if v is not None]
        if len(values) < 3:
            continue
        med = statistics.median(values)
        lo, hi = min(values), max(values)
        mean = statistics.fmean(values)
        sd = statistics.pstdev(values) if len(values) > 1 else 0
        effect = 100.0 * sd / max(abs(mean), sd, 1e-9)
        out.append({
            "id": candidate_id("distribution", metric),
            "pattern": "distribution",
            "claim": f"The median {metric} is {fmt(med)}, spanning {fmt(lo)} to {fmt(hi)}.",
            "question": f"What is the distribution of {metric}?",
            "n": len(values),
            "effect": effect,
            "distinctiveness": 45,
            "visual_fit": 82,
            "transformations": 1,
            "risk_penalty": 0,
            "fields_used": [metric],
            "visual": "histogram",
            "production_mode": "annotated-static",
            "evidence": {"kind": "distribution", "metric": metric, "min": lo, "median": med, "max": hi, "n": len(values)},
            "fields": {"y": metric},
            "rationale": "Shows shape, center, spread, and potential extremes without asserting a causal explanation.",
        })
    return out


def decorate_semantics(candidate: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    if not contract or not contract.get("fields"):
        return candidate
    replacements = [(field, label_for(contract, field)) for field in candidate.get("fields_used", [])]
    replacements.sort(key=lambda item: len(item[0]), reverse=True)
    for key in ("claim", "question", "rationale"):
        text = str(candidate.get(key, ""))
        for raw, label in replacements:
            text = text.replace(raw, label)
        candidate[key] = text
    metadata = {field: field_meta(contract, field) for field in candidate.get("fields_used", [])}
    candidate["field_metadata"] = {field: meta for field, meta in metadata.items() if meta}
    if contract.get("notes"):
        candidate["data_notes"] = list(contract["notes"])
    return candidate


def build_candidates(path: Path, question: str | None = None, limit: int = 12, contract: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = contract or {"fields": {}, "notes": []}
    rows, dates, cats, nums = numeric_types(path, contract)
    candidates: list[dict[str, Any]] = []
    if dates and cats and len(nums) >= 2:
        candidates.extend(change_gap_candidates(rows, dates[0], cats[0], nums))
    if dates and cats and nums:
        candidates.extend(group_change_candidates(rows, dates[0], cats[0], nums))
    if cats and nums:
        candidates.extend(group_mean_candidates(rows, cats[0], nums, repeated_time=bool(dates)))
    if len(nums) >= 2:
        candidates.extend(correlation_candidates(rows, nums, structured_time=bool(dates or cats)))
    if nums:
        candidates.extend(distribution_candidates(rows, nums))

    for candidate in candidates:
        decorate_semantics(candidate, contract)
        score_candidate(candidate, len(rows), question)
    candidates.sort(key=lambda c: (-c["score"], c["id"]))
    candidates = candidates[: max(1, limit)]
    for rank, candidate in enumerate(candidates, start=1):
        candidate["rank"] = rank

    return {
        "source_file": path.name,
        "row_count": len(rows),
        "question": question,
        "candidate_count": len(candidates),
        "scoring_note": "Scores rank evidence-backed directions using deterministic proxies; they do not measure real-world newsworthiness or cultural significance.",
        "data_contract_applied": bool(contract.get("fields")),
        "data_notes": list(contract.get("notes", [])),
        "candidates": candidates,
    }


def candidate_to_spec(candidate: dict[str, Any], source_path: Path, question: str | None = None, audience: str = "general audience") -> dict[str, Any]:
    pattern = candidate["pattern"]
    evidence = dict(candidate["evidence"])
    fields = dict(candidate["fields"])
    visual = candidate["visual"]
    caveats = ["This direction was selected by deterministic scoring and requires editorial review before publication."]
    if candidate.get("caveat"):
        caveats.append(candidate["caveat"])

    if pattern == "change_gap":
        e = evidence
        beats = [
            {"operation": "establish", "purpose": f"Establish the shared time frame for {e['metric_a']} and {e['metric_b']}."},
            {"operation": "reveal", "purpose": "Reveal how the two measures separate over time."},
            {"operation": "reorder", "purpose": "Rank groups by the difference between their start-to-end changes."},
            {"operation": "highlight", "purpose": f"Highlight {e['group']} as the largest absolute divergence."},
        ]
        purpose, operation = "Rank groups by the divergence between two changes.", "compare"
    elif pattern == "group_change":
        e = evidence
        beats = [
            {"operation": "establish", "purpose": f"Establish starting levels of {e['metric']} across groups."},
            {"operation": "reveal", "purpose": "Reveal change over time while preserving group context."},
            {"operation": "highlight", "purpose": f"Highlight {e['group']} as the largest absolute change."},
            {"operation": "annotate", "purpose": "State the measured change and its scope."},
        ]
        purpose, operation = "Compare group trajectories over time.", "reveal"
    elif pattern == "group_mean":
        e = evidence
        beats = [
            {"operation": "establish", "purpose": f"Show average {e['metric']} across groups."},
            {"operation": "reorder", "purpose": "Sort groups to make rank immediately legible."},
            {"operation": "highlight", "purpose": f"Highlight {e['group']} and the gap to the lowest group."},
        ]
        purpose, operation = "Compare ranked group averages.", "compare"
    elif pattern == "correlation":
        beats = [
            {"operation": "establish", "purpose": "Show the full set of paired observations."},
            {"operation": "reveal", "purpose": "Reveal the direction and strength of association."},
            {"operation": "annotate", "purpose": "State the correlation without implying causation."},
        ]
        purpose, operation = "Show the relationship between two quantitative variables.", "compare"
    elif pattern == "distribution":
        beats = [
            {"operation": "establish", "purpose": "Show the overall distribution."},
            {"operation": "annotate", "purpose": "Mark the center and range."},
            {"operation": "highlight", "purpose": "Call out extremes for editorial review."},
        ]
        purpose, operation = "Show distribution shape and spread.", "establish"
    else:
        raise ValueError(f"Unsupported candidate pattern: {pattern}")

    return {
        "question": question or candidate["question"],
        "audience": audience,
        "primary_insight": candidate["claim"],
        "evidence": [evidence],
        "beats": beats,
        "visuals": [{"type": visual, "purpose": purpose, "operation": operation}],
        "production_mode": candidate["production_mode"],
        "fields": fields,
        "field_metadata": candidate.get("field_metadata", {}),
        "data_notes": candidate.get("data_notes", []),
        "sources": [{"label": source_path.name, "path": str(source_path)}],
        "caveats": caveats,
        "selection": {
            "candidate_id": candidate["id"],
            "rank": candidate.get("rank"),
            "score": candidate.get("score"),
            "score_components": candidate.get("score_components", {}),
            "risk_penalty": candidate.get("risk_penalty", 0),
            "rationale": candidate.get("rationale", ""),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--question")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--schema", type=Path, help="Optional JSON data contract with roles, labels, units, and descriptions")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    contract = load_contract(args.schema)
    result = build_candidates(args.path, args.question, args.limit, contract)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote {args.output} with {result['candidate_count']} candidates")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
