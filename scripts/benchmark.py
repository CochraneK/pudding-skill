#!/usr/bin/env python3
"""Run the v2.6 editorial benchmark corpus and gate measurable regressions.

The benchmark measures whether the deterministic pipeline selects the expected story
operation, recommends the expected visual grammar, independently verifies claims,
passes editorial/renderer gates, and preserves claim provenance. It does not claim to
measure real-world newsworthiness, writing quality, or aesthetic taste.
"""
from __future__ import annotations

import argparse
import csv
import json
import tempfile
from pathlib import Path
from typing import Any

from draft_story import build_draft
from evaluate_story import evaluate
from select_story import select
from validate_story import validate
from verify_claims import verify
from visual_grammar import plan_visual

DIMENSIONS = {
    "selection": 35,
    "visual_grammar": 20,
    "claim_audit": 25,
    "editorial_gate": 10,
    "provenance": 10,
}
SUPPORTED_FORMATS = {"csv", "tsv", "json", "jsonl", "ndjson"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def all_fields(rows: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(key for row in rows for key in row.keys()))


def materialize_case(case: dict[str, Any], root: Path) -> Path:
    fmt = str(case.get("format", "csv")).lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported benchmark format {fmt!r} in {case.get('id')}")
    rows = case.get("rows") or []
    if not isinstance(rows, list) or not rows or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"Benchmark case {case.get('id')} must contain a non-empty rows list")
    path = root / f"{case['id']}.{fmt}"
    if fmt in {"csv", "tsv"}:
        delimiter = "\t" if fmt == "tsv" else ","
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=all_fields(rows), delimiter=delimiter)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: "" if value is None else value for key, value in row.items()})
    elif fmt == "json":
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    return path


def validate_provenance(spec: dict[str, Any], draft: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    evidence = list(spec.get("evidence") or [])
    claims = list((draft.get("provenance") or {}).get("claims") or [])
    if draft.get("status") != "EDITORIAL_REVIEW_REQUIRED":
        errors.append("draft status must remain EDITORIAL_REVIEW_REQUIRED")
    if len(claims) != len(evidence):
        errors.append(f"expected {len(evidence)} provenance claim(s), found {len(claims)}")
    for index, claim in enumerate(claims):
        if claim.get("claim_ref") != index or claim.get("evidence_index") != index or claim.get("verified") is not True:
            errors.append(f"claim {index} does not preserve claim_ref/evidence_index/verified mapping")
    for section in draft.get("sections") or []:
        for ref in section.get("claim_refs") or []:
            if not isinstance(ref, int) or ref < 0 or ref >= len(evidence):
                errors.append(f"section {section.get('id')} references missing evidence index {ref!r}")
    return not errors, errors


def run_case(case: dict[str, Any], temp_root: Path) -> dict[str, Any]:
    data_path = materialize_case(case, temp_root)
    question = case.get("question")
    contract = case.get("contract") or {"fields": {}, "notes": []}
    expected = case.get("expect") or {}
    result: dict[str, Any] = {
        "id": case.get("id"),
        "format": case.get("format"),
        "question": question,
        "expected": expected,
        "hard_failure": None,
        "checks": {},
    }
    try:
        spec, pool, selection = select(data_path, question, "general audience", 12, contract)
        validation_errors = validate(spec)
        evaluation = evaluate(spec)
        audit = verify(spec, data_path)
        visual = plan_visual(spec)
        draft = build_draft(spec, audit)
        provenance_ok, provenance_errors = validate_provenance(spec, draft)

        evidence = list(spec.get("evidence") or [])
        actual_pattern = str(evidence[0].get("kind")) if evidence else "unknown"
        insight = str(spec.get("primary_insight", ""))
        claim_tokens = [str(token) for token in expected.get("claim_contains") or []]
        selection_ok = actual_pattern == expected.get("pattern") and all(token.lower() in insight.lower() for token in claim_tokens)
        visual_ok = visual.get("recommended_visual") == expected.get("visual")
        audit_ok = audit.get("status") == "PASS"
        editorial_ok = not validation_errors and evaluation.get("status") == "PASS" and selection.get("status") == "PASS"

        result.update({
            "actual": {
                "pattern": actual_pattern,
                "selected_candidate_id": selection.get("selected_candidate_id"),
                "selected_rank": selection.get("selected_rank"),
                "selected_score": selection.get("selected_score"),
                "candidate_count": pool.get("candidate_count"),
                "visual": visual.get("recommended_visual"),
                "baseline_renderer": visual.get("baseline_renderer"),
                "insight": insight,
                "claim_audit": audit.get("status"),
                "editorial_status": evaluation.get("status"),
                "selection_status": selection.get("status"),
            },
            "checks": {
                "selection": {"ok": selection_ok, "weight": DIMENSIONS["selection"], "detail": f"expected {expected.get('pattern')} + tokens {claim_tokens}; got {actual_pattern}"},
                "visual_grammar": {"ok": visual_ok, "weight": DIMENSIONS["visual_grammar"], "detail": f"expected {expected.get('visual')}; got {visual.get('recommended_visual')}"},
                "claim_audit": {"ok": audit_ok, "weight": DIMENSIONS["claim_audit"], "detail": str(audit.get("status"))},
                "editorial_gate": {"ok": editorial_ok, "weight": DIMENSIONS["editorial_gate"], "detail": f"validate={len(validation_errors)} errors, evaluate={evaluation.get('status')}, selection={selection.get('status')}"},
                "provenance": {"ok": provenance_ok, "weight": DIMENSIONS["provenance"], "detail": "PASS" if provenance_ok else "; ".join(provenance_errors)},
            },
        })
    except Exception as exc:
        result["hard_failure"] = f"{type(exc).__name__}: {exc}"
        result["checks"] = {
            name: {"ok": False, "weight": weight, "detail": result["hard_failure"]}
            for name, weight in DIMENSIONS.items()
        }

    result["score"] = sum(item["weight"] for item in result["checks"].values() if item["ok"])
    result["passed"] = result["score"] == 100 and result["hard_failure"] is None
    return result


def aggregate(corpus: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(cases)
    dimensions: dict[str, Any] = {}
    for name, weight in DIMENSIONS.items():
        passed = sum(bool(case["checks"][name]["ok"]) for case in cases)
        dimensions[name] = {
            "weight": weight,
            "passed": passed,
            "total": count,
            "pass_rate": round(passed / count, 4) if count else 0.0,
        }
    overall = round(sum(case["score"] for case in cases) / count, 2) if count else 0.0
    passed_cases = sum(bool(case["passed"]) for case in cases)
    hard_failures = sum(case.get("hard_failure") is not None for case in cases)
    return {
        "schema_version": 1,
        "corpus_schema_version": corpus.get("schema_version"),
        "case_count": count,
        "passed_cases": passed_cases,
        "case_pass_rate": round(passed_cases / count, 4) if count else 0.0,
        "hard_failures": hard_failures,
        "overall_score": overall,
        "dimensions": dimensions,
        "cases": cases,
        "note": "This benchmark measures deterministic pipeline behavior on curated fixtures. It does not measure real-world newsworthiness, factual completeness outside the fixture, prose craft, or aesthetic taste.",
    }


def gate(report: dict[str, Any], baseline: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    minimum_score = float(baseline.get("minimum_overall_score", 0))
    if float(report.get("overall_score", 0)) < minimum_score:
        failures.append(f"overall score {report['overall_score']} < baseline {minimum_score}")
    minimum_case_rate = float(baseline.get("minimum_case_pass_rate", 0))
    if float(report.get("case_pass_rate", 0)) < minimum_case_rate:
        failures.append(f"case pass rate {report['case_pass_rate']:.1%} < baseline {minimum_case_rate:.1%}")
    max_hard = int(baseline.get("max_hard_failures", 0))
    if int(report.get("hard_failures", 0)) > max_hard:
        failures.append(f"hard failures {report['hard_failures']} > baseline {max_hard}")
    minimum_dimensions = baseline.get("minimum_dimension_pass_rates") or {}
    for name, minimum in minimum_dimensions.items():
        actual = float((report.get("dimensions") or {}).get(name, {}).get("pass_rate", 0))
        if actual < float(minimum):
            failures.append(f"dimension {name} pass rate {actual:.1%} < baseline {float(minimum):.1%}")
    return failures


def to_markdown(report: dict[str, Any], gate_failures: list[str]) -> str:
    lines = [
        "# Editorial benchmark report",
        "",
        f"**Overall:** {report['overall_score']}/100  ",
        f"**Cases:** {report['passed_cases']}/{report['case_count']} full passes  ",
        f"**Hard failures:** {report['hard_failures']}  ",
        f"**Regression gate:** {'FAIL' if gate_failures else 'PASS'}",
        "",
        "## Dimensions",
        "",
        "| Dimension | Weight | Pass rate |",
        "|---|---:|---:|",
    ]
    for name, item in report["dimensions"].items():
        lines.append(f"| `{name}` | {item['weight']} | {item['passed']}/{item['total']} ({item['pass_rate']:.0%}) |")
    lines += ["", "## Cases", ""]
    for case in report["cases"]:
        actual = case.get("actual") or {}
        marker = "PASS" if case["passed"] else "FAIL"
        lines.append(f"- **{marker} · `{case['id']}` · {case['score']}/100** — `{actual.get('pattern', 'n/a')}` → `{actual.get('visual', 'n/a')}`")
        if case.get("hard_failure"):
            lines.append(f"  - hard failure: `{case['hard_failure']}`")
        for name, check in case["checks"].items():
            if not check["ok"]:
                lines.append(f"  - {name}: {check['detail']}")
    if gate_failures:
        lines += ["", "## Regression gate failures", ""] + [f"- {failure}" for failure in gate_failures]
    lines += ["", "_The benchmark is a regression instrument, not a substitute for editorial judgment._", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path("benchmarks/corpus.json"))
    parser.add_argument("--baseline", type=Path, default=Path("benchmarks/baseline.json"))
    parser.add_argument("--output", type=Path, default=Path(".qa/benchmark-report.json"))
    parser.add_argument("--markdown", type=Path, default=Path(".qa/benchmark-report.md"))
    parser.add_argument("--no-gate", action="store_true", help="Write the report without failing on baseline regression")
    args = parser.parse_args()

    corpus = load_json(args.corpus)
    baseline = load_json(args.baseline) if args.baseline.exists() else {}
    raw_cases = corpus.get("cases") or []
    ids = [case.get("id") for case in raw_cases]
    if not raw_cases or any(not case_id for case_id in ids) or len(ids) != len(set(ids)):
        parser.error("benchmark corpus must contain unique non-empty case ids")

    with tempfile.TemporaryDirectory(prefix="pudding-benchmark-") as temp:
        root = Path(temp)
        cases = [run_case(case, root) for case in raw_cases]
    report = aggregate(corpus, cases)
    failures = [] if args.no_gate else gate(report, baseline)
    report["gate"] = {"status": "FAIL" if failures else "PASS", "failures": failures, "baseline": str(args.baseline)}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(to_markdown(report, failures), encoding="utf-8")

    print(f"Benchmark: {report['overall_score']}/100 · {report['passed_cases']}/{report['case_count']} cases · gate {report['gate']['status']}")
    for case in cases:
        actual = case.get("actual") or {}
        print(f"- {'PASS' if case['passed'] else 'FAIL'} {case['id']}: {case['score']}/100 · {actual.get('pattern', 'n/a')} · {actual.get('visual', 'n/a')}")
    if failures:
        for failure in failures:
            print(f"REGRESSION: {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
