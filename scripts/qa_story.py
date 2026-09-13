#!/usr/bin/env python3
"""Static preflight QA for generated editorial artifacts, renderer data, and brand hygiene."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from validate_story import validate

FORBIDDEN = (
    "pudding.cool/assets/fonts",
    'og:site_name" content="The Pudding',
    "@puddingviz",
)


def walk_text(root: Path):
    for pattern in ("*.svelte", "*.css", "*.html", "*.js", "*.ts"):
        for path in root.rglob(pattern):
            try:
                yield path, path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pass


def finite_numbers(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from finite_numbers(child)
    elif isinstance(value, list):
        for child in value:
            yield from finite_numbers(child)
    elif isinstance(value, float):
        yield math.isfinite(value)


def load_required(root: Path, relative: str, errors: list[str]):
    path = root / relative
    if not path.exists():
        errors.append(f"Missing generated artifact: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {path}: {exc}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--bundle", default="src/data/auto-story.json")
    parser.add_argument("--candidates", default="src/data/story-candidates.json")
    parser.add_argument("--selection", default="src/data/story-selection.json")
    parser.add_argument("--evaluation", default="src/data/story-evaluation.json")
    parser.add_argument("--claim-audit", default="src/data/story-claim-audit.json")
    args = parser.parse_args()

    errors: list[str] = []
    bundle = load_required(args.root, args.bundle, errors)
    candidates = load_required(args.root, args.candidates, errors)
    selection = load_required(args.root, args.selection, errors)
    evaluation = load_required(args.root, args.evaluation, errors)
    claim_audit = load_required(args.root, args.claim_audit, errors)

    if bundle:
        errors.extend(validate(bundle.get("spec")))
        chart = bundle.get("chart", {})
        if not chart.get("type") or not isinstance(chart.get("data"), list) or not chart.get("data"):
            errors.append("Generated chart must contain a type and non-empty data list.")
        if not all(finite_numbers(bundle)):
            errors.append("Generated bundle contains NaN or infinite numbers.")

    candidate_ids: set[str] = set()
    if candidates:
        items = candidates.get("candidates")
        if not isinstance(items, list) or not items:
            errors.append("Candidate board must contain at least one candidate.")
        else:
            ids = [item.get("id") for item in items if isinstance(item, dict)]
            candidate_ids = {value for value in ids if isinstance(value, str)}
            if len(candidate_ids) != len(items):
                errors.append("Candidate ids must be non-empty and unique.")
            scores = [item.get("score") for item in items]
            if any(not isinstance(score, (int, float)) for score in scores):
                errors.append("Every candidate must contain a numeric score.")
            elif scores != sorted(scores, reverse=True):
                errors.append("Candidates must be sorted by descending score.")

    if selection:
        selected = selection.get("selected_candidate_id")
        if candidate_ids and selected not in candidate_ids:
            errors.append("Selection report references a candidate that is not in the candidate board.")
        if selection.get("status") == "FAIL":
            errors.append("Committed selection report is in FAIL state.")

    if evaluation and evaluation.get("status") == "FAIL":
        errors.append("Committed editorial evaluation is in FAIL state.")

    if claim_audit and claim_audit.get("status") != "PASS":
        errors.append("Committed claim audit must be PASS.")

    src = args.root / "src"
    if src.exists():
        for path, text in walk_text(src):
            for token in FORBIDDEN:
                if token in text:
                    errors.append(f"Forbidden brand/hotlink token in {path}: {token}")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS: candidate board, selection, claim audit, story bundle, and static preflight checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
