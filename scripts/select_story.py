#!/usr/bin/env python3
"""Select the best viable candidate, falling back automatically when a candidate fails quality gates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from candidate_story import build_candidates, candidate_to_spec
from data_contract import load_contract
from evaluate_story import evaluate
from generate_story import prepare_chart
from profile_data import load_rows


def select(
    data_path: Path,
    question: str | None = None,
    audience: str = "general audience",
    limit: int = 12,
    contract: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    pool = build_candidates(data_path, question, limit, contract)
    rows = load_rows(data_path)
    attempts = []
    selected_spec: dict[str, Any] | None = None
    selected_report: dict[str, Any] | None = None

    for candidate in pool["candidates"]:
        spec = candidate_to_spec(candidate, data_path, question, audience)
        report = evaluate(spec)
        renderer_error = None
        if report["status"] != "FAIL":
            try:
                prepare_chart(spec, rows)
            except Exception as exc:  # renderer compatibility is a real fallback condition
                renderer_error = str(exc)
                report = dict(report)
                report["status"] = "FAIL"
                report["errors"] = int(report.get("errors", 0)) + 1
                report["checks"] = list(report.get("checks", [])) + [{
                    "name": "renderer_dry_run", "ok": False, "severity": "error", "detail": renderer_error
                }]
        attempts.append({
            "candidate_id": candidate["id"],
            "rank": candidate["rank"],
            "score": candidate["score"],
            "status": report["status"],
            "renderer_error": renderer_error,
        })
        if report["status"] == "PASS":
            selected_spec, selected_report = spec, report
            break
        if selected_spec is None and report["status"] == "WARN":
            # Keep the first warning-level candidate as a fallback but continue seeking PASS.
            selected_spec, selected_report = spec, report

    if selected_spec is None or selected_report is None:
        raise ValueError("No candidate passed the deterministic editorial and renderer gates. Write/review the story spec manually.")

    selection_report = {
        "status": selected_report["status"],
        "selected_candidate_id": selected_spec["selection"]["candidate_id"],
        "selected_rank": selected_spec["selection"]["rank"],
        "selected_score": selected_spec["selection"]["score"],
        "candidate_count": pool["candidate_count"],
        "attempt_count": len(attempts),
        "attempts": attempts,
        "quality": selected_report,
        "note": "Automatic fallback only checks deterministic evidence/renderer gates. Editorial meaning still requires review.",
    }
    return selected_spec, pool, selection_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("--question")
    parser.add_argument("--audience", default="general audience")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--schema", type=Path, help="Optional JSON data contract")
    parser.add_argument("--spec-output", type=Path, default=Path("generated/story-spec.json"))
    parser.add_argument("--candidates-output", type=Path, default=Path("generated/candidates.json"))
    parser.add_argument("--report-output", type=Path, default=Path("generated/selection-report.json"))
    args = parser.parse_args()

    contract = load_contract(args.schema)
    spec, pool, report = select(args.data, args.question, args.audience, args.limit, contract)
    for path, data in ((args.spec_output, spec), (args.candidates_output, pool), (args.report_output, report)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Selected #{report['selected_rank']} {report['selected_candidate_id']} (score {report['selected_score']}, {report['status']})")
    print(f"Candidates: {args.candidates_output}")
    print(f"Story spec: {args.spec_output}")
    print(f"Selection report: {args.report_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
