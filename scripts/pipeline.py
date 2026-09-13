#!/usr/bin/env python3
"""Run the v2.2 editorial pipeline: profile -> candidates -> selection -> validation -> render -> evaluation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from data_contract import load_contract
from evaluate_story import evaluate
from generate_story import generate
from profile_data import profile
from select_story import select
from validate_story import validate
from verify_claims import verify


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("--question")
    parser.add_argument("--audience", default="general audience")
    parser.add_argument("--schema", type=Path, help="Optional JSON data contract with roles, labels, units, and descriptions")
    parser.add_argument("--workdir", type=Path, default=Path("generated"))
    parser.add_argument("--render-output", type=Path, default=Path("src/data/auto-story.json"))
    parser.add_argument("--candidate-output", type=Path, default=Path("src/data/story-candidates.json"))
    parser.add_argument("--selection-output", type=Path, default=Path("src/data/story-selection.json"))
    parser.add_argument("--evaluation-output", type=Path, default=Path("src/data/story-evaluation.json"))
    parser.add_argument("--claim-audit-output", type=Path, default=Path("src/data/story-claim-audit.json"))
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    args.workdir.mkdir(parents=True, exist_ok=True)
    profile_path = args.workdir / "profile.json"
    candidate_path = args.workdir / "candidates.json"
    spec_path = args.workdir / "story-spec.json"
    selection_path = args.workdir / "selection-report.json"
    evaluation_path = args.workdir / "evaluation.json"
    claim_audit_path = args.workdir / "claim-audit.json"

    prof = profile(args.data)
    contract = load_contract(args.schema)
    spec, pool, selection = select(args.data, args.question, args.audience, args.limit, contract)
    errors = validate(spec)
    if errors:
        raise SystemExit("Selected story spec failed validation:\n- " + "\n- ".join(errors))
    evaluation = evaluate(spec)
    if evaluation["status"] == "FAIL":
        raise SystemExit("Selected story failed deterministic editorial quality gates.")
    claim_audit = verify(spec, args.data)
    if claim_audit["status"] != "PASS":
        raise SystemExit("Selected story failed independent quantitative claim verification.")

    write_json(profile_path, prof)
    write_json(candidate_path, pool)
    write_json(spec_path, spec)
    write_json(selection_path, selection)
    write_json(evaluation_path, evaluation)
    write_json(claim_audit_path, claim_audit)
    write_json(args.candidate_output, pool)
    write_json(args.selection_output, selection)
    write_json(args.evaluation_output, evaluation)
    write_json(args.claim_audit_output, claim_audit)
    bundle = generate(spec_path, args.data, args.render_output)

    print(f"Profile: {profile_path}")
    print(f"Candidates: {candidate_path} ({pool['candidate_count']} ranked directions)")
    print(f"Story spec: {spec_path}")
    print(f"Selection report: {selection_path}")
    print(f"Evaluation: {evaluation_path} ({evaluation['status']})")
    print(f"Claim audit: {claim_audit_path} ({claim_audit['status']})")
    print(f"Render bundle: {args.render_output} ({bundle['chart']['type']})")
    print(f"Selected: #{selection['selected_rank']} {selection['selected_candidate_id']} · score {selection['selected_score']}")
    print(f"Insight: {spec['primary_insight']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
