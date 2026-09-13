#!/usr/bin/env python3
"""Evaluate a selected story spec against deterministic editorial quality gates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_story import validate

SUPPORTED_VISUALS = {"bar", "line", "scatter", "histogram"}


def evaluate(spec: dict[str, Any]) -> dict[str, Any]:
    structural_errors = validate(spec)
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str, severity: str = "error") -> None:
        checks.append({"name": name, "ok": bool(ok), "severity": severity, "detail": detail})

    add("story_spec_structure", not structural_errors, "Valid story spec." if not structural_errors else "; ".join(structural_errors))
    selection = spec.get("selection", {}) if isinstance(spec.get("selection"), dict) else {}
    score = selection.get("score")
    score_ok = isinstance(score, (int, float)) and score >= 55
    add("candidate_score", score_ok, f"Selected candidate score: {score if score is not None else 'missing'} (minimum 55).")

    evidence = spec.get("evidence", [])
    first = evidence[0] if isinstance(evidence, list) and evidence and isinstance(evidence[0], dict) else {}
    n = first.get("n")
    if n is None and first.get("kind") in {"change", "change_gap"}:
        # Start/end comparisons can be valid without an explicit row count in evidence.
        n_ok = True
        n_detail = "Start/end comparison evidence present."
    else:
        n_ok = isinstance(n, (int, float)) and n >= 3
        n_detail = f"Evidence observation count: {n if n is not None else 'missing'}."
    add("minimum_evidence", n_ok, n_detail, severity="warning" if not n_ok else "error")

    visuals = spec.get("visuals", [])
    visual_type = visuals[0].get("type") if visuals and isinstance(visuals[0], dict) else None
    add("baseline_renderer_support", visual_type in SUPPORTED_VISUALS, f"Visual type: {visual_type}; supported baseline types: {', '.join(sorted(SUPPORTED_VISUALS))}.")

    caveats = spec.get("caveats")
    add("caveats_present", isinstance(caveats, list) and bool(caveats), "At least one limitation/caveat is stated.")
    sources = spec.get("sources")
    add("sources_present", isinstance(sources, list) and bool(sources), "At least one source is attached.")

    claim = spec.get("primary_insight", "")
    claim_ok = isinstance(claim, str) and 20 <= len(claim.strip()) <= 240
    add("claim_length", claim_ok, f"Primary insight length: {len(claim.strip()) if isinstance(claim, str) else 0} characters.", severity="warning")

    mode = spec.get("production_mode", "annotated-static")
    beats = spec.get("beats", [])
    if mode == "scrollytelling":
        operations = {b.get("operation") for b in beats if isinstance(b, dict)}
        scrolly_ok = bool(operations & {"reveal", "filter", "zoom", "morph", "reorder"}) and len(beats) >= 4
        add("scrolly_justification", scrolly_ok, "Scrollytelling requires at least four beats and a meaningful transformation operation.", severity="warning")

    hard_fail = any((not c["ok"]) and c["severity"] == "error" for c in checks)
    warnings = [c for c in checks if (not c["ok"]) and c["severity"] == "warning"]
    status = "FAIL" if hard_fail else "WARN" if warnings else "PASS"
    return {
        "status": status,
        "candidate_id": selection.get("candidate_id"),
        "candidate_score": score,
        "checks": checks,
        "warnings": len(warnings),
        "errors": sum(1 for c in checks if (not c["ok"]) and c["severity"] == "error"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.spec.read_text(encoding="utf-8"))
    report = evaluate(data)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(f"{report['status']}: candidate={report.get('candidate_id')} score={report.get('candidate_score')}")
    for check in report["checks"]:
        marker = "✓" if check["ok"] else "!" if check["severity"] == "warning" else "✗"
        print(f"{marker} {check['name']}: {check['detail']}")
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
