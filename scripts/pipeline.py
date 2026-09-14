#!/usr/bin/env python3
"""Run the v2.4 editorial pipeline: data audit -> candidates -> selection -> claim audit -> visual plan -> first draft -> render."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from data_contract import load_contract
from draft_story import build_draft, to_markdown
from evaluate_story import evaluate
from generate_story import generate
from profile_data import profile
from select_story import select
from validate_story import validate
from verify_claims import verify
from visual_grammar import plan_visual


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_pipeline(
    data: Path,
    question: str | None = None,
    audience: str = "general audience",
    schema: Path | None = None,
    workdir: Path = Path("generated"),
    render_output: Path = Path("src/data/auto-story.json"),
    candidate_output: Path = Path("src/data/story-candidates.json"),
    selection_output: Path = Path("src/data/story-selection.json"),
    evaluation_output: Path = Path("src/data/story-evaluation.json"),
    claim_audit_output: Path = Path("src/data/story-claim-audit.json"),
    draft_output: Path = Path("src/data/story-draft.json"),
    limit: int = 12,
) -> dict[str, Any]:
    workdir.mkdir(parents=True, exist_ok=True)
    profile_path = workdir / "profile.json"
    candidate_path = workdir / "candidates.json"
    spec_path = workdir / "story-spec.json"
    selection_path = workdir / "selection-report.json"
    evaluation_path = workdir / "evaluation.json"
    claim_audit_path = workdir / "claim-audit.json"
    visual_plan_path = workdir / "visual-plan.json"
    draft_path = workdir / "story-draft.json"
    markdown_path = workdir / "story-draft.md"

    prof = profile(data)
    contract = load_contract(schema)
    spec, pool, selection = select(data, question, audience, limit, contract)
    errors = validate(spec)
    if errors:
        raise ValueError("Selected story spec failed validation:\n- " + "\n- ".join(errors))
    evaluation = evaluate(spec)
    if evaluation["status"] == "FAIL":
        raise ValueError("Selected story failed deterministic editorial quality gates.")
    claim_audit = verify(spec, data)
    if claim_audit["status"] != "PASS":
        raise ValueError("Selected story failed independent quantitative claim verification.")

    visual_plan = plan_visual(spec)
    spec["visual_plan"] = visual_plan
    draft = build_draft(spec, claim_audit)

    write_json(profile_path, prof)
    write_json(candidate_path, pool)
    write_json(spec_path, spec)
    write_json(selection_path, selection)
    write_json(evaluation_path, evaluation)
    write_json(claim_audit_path, claim_audit)
    write_json(visual_plan_path, visual_plan)
    write_json(draft_path, draft)
    markdown_path.write_text(to_markdown(draft), encoding="utf-8")

    write_json(candidate_output, pool)
    write_json(selection_output, selection)
    write_json(evaluation_output, evaluation)
    write_json(claim_audit_output, claim_audit)
    write_json(draft_output, draft)
    bundle = generate(spec_path, data, render_output)

    return {
        "profile": profile_path,
        "candidates": candidate_path,
        "story_spec": spec_path,
        "selection": selection_path,
        "evaluation": evaluation_path,
        "claim_audit": claim_audit_path,
        "visual_plan": visual_plan_path,
        "draft_json": draft_path,
        "draft_markdown": markdown_path,
        "render_output": render_output,
        "bundle": bundle,
        "pool": pool,
        "spec": spec,
        "selection_report": selection,
        "evaluation_report": evaluation,
        "claim_audit_report": claim_audit,
        "draft": draft,
    }


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
    parser.add_argument("--draft-output", type=Path, default=Path("src/data/story-draft.json"))
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    result = run_pipeline(
        args.data, args.question, args.audience, args.schema, args.workdir,
        args.render_output, args.candidate_output, args.selection_output,
        args.evaluation_output, args.claim_audit_output, args.draft_output, args.limit,
    )
    pool = result["pool"]
    spec = result["spec"]
    selection = result["selection_report"]
    evaluation = result["evaluation_report"]
    claim_audit = result["claim_audit_report"]
    draft = result["draft"]
    bundle = result["bundle"]

    print(f"Profile: {result['profile']}")
    print(f"Candidates: {result['candidates']} ({pool['candidate_count']} ranked directions)")
    print(f"Story spec: {result['story_spec']}")
    print(f"Selection report: {result['selection']}")
    print(f"Evaluation: {result['evaluation']} ({evaluation['status']})")
    print(f"Claim audit: {result['claim_audit']} ({claim_audit['status']})")
    print(f"Visual plan: {result['visual_plan']} ({draft['visual_plan']['recommended_visual']})")
    print(f"Draft: {result['draft_markdown']}")
    print(f"Render bundle: {result['render_output']} ({bundle['chart']['type']})")
    print(f"Selected: #{selection['selected_rank']} {selection['selected_candidate_id']} · score {selection['selected_score']}")
    print(f"Headline: {draft['headline']}")
    print(f"Insight: {spec['primary_insight']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
