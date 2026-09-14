#!/usr/bin/env python3
"""Prototype tournament manifest, scoring, and decision validator.

This stage sits after a contrastive concept board and before bespoke implementation.
It makes low-cost prototypes comparable without rewarding interaction for its own sake.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CRITERIA = (
    ("reader_realization", 20, "Can a reader state the intended insight from the prototype?"),
    ("evidence_fidelity", 20, "Does the prototype preserve units, caveats, missingness, and provenance?"),
    ("visual_necessity", 15, "Does the visual treatment materially improve understanding over prose alone?"),
    ("interaction_economy", 15, "Does the chosen interaction level, including none, earn its complexity?"),
    ("reader_effort", 10, "Can the reader understand the claim without avoidable work or controls?"),
    ("mobile_viability", 10, "Does the same conclusion survive a narrow viewport and touch input?"),
    ("accessibility_equivalence", 10, "Is the same evidence and conclusion available without hover, motion, or vision-only cues?"),
)
CRITERION_IDS = {item[0] for item in CRITERIA}
HARD_GATE_CRITERIA = {"evidence_fidelity", "mobile_viability", "accessibility_equivalence"}
OUTCOMES = {"PENDING", "SELECT", "COMBINE", "PIVOT", "PUT_DOWN"}
VERDICTS = {"PENDING", "SURVIVE", "ELIMINATE"}
PASSING_SCORE = 70.0


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _criteria_payload() -> list[dict[str, Any]]:
    return [
        {"id": cid, "weight": weight, "question": question, "scale": "1-5"}
        for cid, weight, question in CRITERIA
    ]


def screenshot_name(route: str, alias: str, viewport: str) -> str:
    route_with_focus = f"{route}?focus={alias}"
    slug = route_with_focus.strip("/")
    out = []
    last_dash = False
    for char in slug:
        if char.isalnum():
            out.append(char)
            last_dash = False
        elif not last_dash:
            out.append("-")
            last_dash = True
    return f".qa/{''.join(out).strip('-')}-{viewport}.png"


def scaffold(board: dict[str, Any], board_path: str, route: str) -> dict[str, Any]:
    concepts = board.get("concepts")
    if not isinstance(concepts, list) or not (3 <= len(concepts) <= 6):
        raise ValueError("Concept board must contain 3–6 concepts before a tournament can be created.")

    prototypes = []
    for index, concept in enumerate(concepts):
        if not isinstance(concept, dict) or not _text(concept.get("id")):
            raise ValueError(f"Concept {index + 1} needs a non-empty id.")
        alias = chr(ord("A") + index)
        prototypes.append(
            {
                "alias": alias,
                "concept_id": concept["id"],
                "form": concept.get("form", ""),
                "interaction_job": concept.get("interaction_job", ""),
                "prototype_route": f"{route}?focus={alias}",
                "desktop_screenshot": screenshot_name(route, alias, "desktop"),
                "mobile_screenshot": screenshot_name(route, alias, "mobile"),
                "judge": {
                    "scores": {},
                    "hard_failures": [],
                    "verdict": "PENDING",
                    "notes": "",
                },
            }
        )

    return {
        "status": "PROTOTYPES_REQUIRED",
        "story_id": board.get("story_id", ""),
        "question": board.get("question", ""),
        "argument": board.get("argument", ""),
        "concept_board": board_path,
        "comparison_route": route,
        "instructions": (
            "Build only the hardest claim-bearing moment for every concept. Capture the same desktop and mobile viewports, "
            "score the screenshots independently, eliminate hard-gate failures, then select, combine, pivot, or put the story down."
        ),
        "criteria": _criteria_payload(),
        "prototypes": prototypes,
        "decision": {
            "outcome": "PENDING",
            "winner_concept_ids": [],
            "reason": "",
            "implementation_handoff": [],
            "discarded_lessons": [],
        },
    }


def _score_prototype(row: dict[str, Any]) -> tuple[float | None, list[str], str]:
    judge = row.get("judge")
    if not isinstance(judge, dict):
        return None, ["judge must be an object"], "PENDING"
    scores = judge.get("scores")
    if not isinstance(scores, dict):
        return None, ["judge.scores must be an object"], "PENDING"
    if set(scores) != CRITERION_IDS:
        missing = sorted(CRITERION_IDS - set(scores))
        extra = sorted(set(scores) - CRITERION_IDS)
        problems = []
        if missing:
            problems.append(f"missing scores: {', '.join(missing)}")
        if extra:
            problems.append(f"unknown scores: {', '.join(extra)}")
        return None, problems, "PENDING"

    invalid = []
    total = 0.0
    for cid, weight, _ in CRITERIA:
        value = scores.get(cid)
        if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 5:
            invalid.append(f"{cid} must be an integer from 1 to 5")
            continue
        total += (value / 5) * weight
    if invalid:
        return None, invalid, "PENDING"

    hard_failures = judge.get("hard_failures")
    if not isinstance(hard_failures, list) or any(not _text(item) for item in hard_failures):
        return None, ["judge.hard_failures must be a list of non-empty strings"], "PENDING"

    hard_gate_failed = any(scores[cid] < 3 for cid in HARD_GATE_CRITERIA)
    verdict = "SURVIVE" if not hard_failures and not hard_gate_failed and total >= PASSING_SCORE else "ELIMINATE"
    return round(total, 1), [], verdict


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    ranking = []
    for row in data.get("prototypes", []) if isinstance(data.get("prototypes"), list) else []:
        if not isinstance(row, dict):
            continue
        total, problems, verdict = _score_prototype(row)
        ranking.append(
            {
                "alias": row.get("alias"),
                "concept_id": row.get("concept_id"),
                "score": total,
                "verdict": verdict,
                "problems": problems,
            }
        )
    ranking.sort(key=lambda item: (-1 if item["score"] is None else -item["score"], str(item.get("alias"))))
    return {"ranking": ranking, "survivors": [item["concept_id"] for item in ranking if item["verdict"] == "SURVIVE"]}


def validate(data: dict[str, Any], stage: str = "manifest", evidence_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    prototypes = data.get("prototypes")
    if not isinstance(prototypes, list):
        return {"status": "REVISE", "errors": ["prototypes must be a list"], "warnings": [], "ranking": []}
    if not 3 <= len(prototypes) <= 6:
        errors.append("Tournament must contain 3–6 prototypes from the validated concept board.")

    aliases: set[str] = set()
    concepts: set[str] = set()
    screenshot_paths: set[str] = set()
    for index, row in enumerate(prototypes):
        label = f"prototype-{index + 1}"
        if not isinstance(row, dict):
            errors.append(f"{label}: prototype must be an object")
            continue
        alias = _text(row.get("alias"))
        concept_id = _text(row.get("concept_id"))
        route = _text(row.get("prototype_route"))
        if not alias:
            errors.append(f"{label}: alias is empty")
        elif alias in aliases:
            errors.append(f"{label}: duplicate alias {alias}")
        aliases.add(alias)
        if not concept_id:
            errors.append(f"{label}: concept_id is empty")
        elif concept_id in concepts:
            errors.append(f"{label}: duplicate concept_id {concept_id}")
        concepts.add(concept_id)
        if not route:
            errors.append(f"{label}: prototype_route is empty")

        for field in ("desktop_screenshot", "mobile_screenshot"):
            path = _text(row.get(field))
            if not path:
                errors.append(f"{label}: {field} is empty")
                continue
            if path in screenshot_paths:
                warnings.append(f"{label}: {field} reuses screenshot path {path}; prefer one capture per prototype/viewport")
            screenshot_paths.add(path)
            if stage == "evidence" and evidence_root is not None and not (evidence_root / path).is_file():
                errors.append(f"{label}: missing screenshot evidence {path}")

    criteria = data.get("criteria")
    criterion_ids = {row.get("id") for row in criteria} if isinstance(criteria, list) else set()
    if criterion_ids != CRITERION_IDS:
        errors.append("criteria must use the canonical seven tournament dimensions; do not change weights to favor a concept.")
    elif sum(int(row.get("weight", 0)) for row in criteria if isinstance(row, dict)) != 100:
        errors.append("criteria weights must sum to 100.")

    assessment = evaluate(data)
    ranking = assessment["ranking"]

    if stage in {"decision", "evidence"}:
        for item in ranking:
            if item["score"] is None:
                errors.append(f"{item['concept_id'] or item['alias']}: incomplete or invalid judging scores ({'; '.join(item['problems'])})")
                continue
            source = next((row for row in prototypes if isinstance(row, dict) and row.get("concept_id") == item["concept_id"]), None)
            judge = source.get("judge", {}) if source else {}
            if _text(judge.get("verdict")) not in VERDICTS:
                errors.append(f"{item['concept_id']}: judge.verdict must be PENDING, SURVIVE, or ELIMINATE")
            elif judge.get("verdict") != item["verdict"]:
                errors.append(f"{item['concept_id']}: recorded verdict {judge.get('verdict')} disagrees with computed {item['verdict']}")
            if len(_text(judge.get("notes"))) < 40:
                errors.append(f"{item['concept_id']}: judge.notes must explain the screenshot-based decision")

        decision = data.get("decision")
        if not isinstance(decision, dict):
            errors.append("decision must be an object")
        else:
            outcome = _text(decision.get("outcome"))
            winners = decision.get("winner_concept_ids")
            reason = _text(decision.get("reason"))
            handoff = decision.get("implementation_handoff")
            if outcome not in OUTCOMES - {"PENDING"}:
                errors.append("decision.outcome must be SELECT, COMBINE, PIVOT, or PUT_DOWN once judging is complete")
            if not isinstance(winners, list) or any(not _text(item) for item in winners):
                errors.append("decision.winner_concept_ids must be a list of non-empty ids")
                winners = []
            survivor_set = set(assessment["survivors"])
            if any(item not in survivor_set for item in winners):
                errors.append("A selected winner must survive deterministic score and hard gates.")
            if outcome == "SELECT" and len(winners) != 1:
                errors.append("SELECT requires exactly one winning concept.")
            if outcome == "COMBINE" and len(winners) < 2:
                errors.append("COMBINE requires at least two surviving concepts.")
            if outcome in {"PIVOT", "PUT_DOWN"} and winners:
                errors.append(f"{outcome} cannot name a winning concept.")
            if outcome in {"SELECT", "COMBINE"} and not survivor_set:
                errors.append("No prototype survived; select PIVOT or PUT_DOWN instead of forcing a winner.")
            if len(reason) < 60:
                errors.append("decision.reason must state why the result beats the alternatives, not just name a favorite.")
            if outcome in {"SELECT", "COMBINE"}:
                if not isinstance(handoff, list) or len([item for item in handoff if _text(item)]) < 2:
                    errors.append("Selected outcomes need at least two implementation_handoff constraints from the tournament.")

    if errors:
        status = "REVISE"
    elif stage == "manifest":
        status = "READY_FOR_PROTOTYPE"
    elif stage == "decision":
        status = "WINNER_SELECTED"
    else:
        status = "EVIDENCE_VERIFIED"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "ranking": ranking,
        "survivors": assessment["survivors"],
        "disclaimer": (
            "Scores structure the comparison; they do not prove aesthetic quality. Evidence, mobile, and accessibility hard gates cannot be traded away for visual novelty."
        ),
    }


def render_markdown(data: dict[str, Any], report: dict[str, Any]) -> str:
    lines = [
        "# Prototype tournament",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Question: {data.get('question', '')}",
        "",
        f"Argument: {data.get('argument', '')}",
        "",
        "## Screenshot matrix",
        "",
        "| Prototype | Concept | Desktop | Mobile | Score | Verdict |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    by_id = {row.get("concept_id"): row for row in data.get("prototypes", []) if isinstance(row, dict)}
    for item in report.get("ranking", []):
        row = by_id.get(item.get("concept_id"), {})
        score = "—" if item.get("score") is None else f"{item['score']:.1f}"
        lines.append(
            f"| {row.get('alias', '')} | `{item.get('concept_id', '')}` | `{row.get('desktop_screenshot', '')}` | "
            f"`{row.get('mobile_screenshot', '')}` | {score} | {item.get('verdict', '')} |"
        )
    lines += ["", "## Decision", "", f"Outcome: **{data.get('decision', {}).get('outcome', 'PENDING')}**", ""]
    reason = _text(data.get("decision", {}).get("reason"))
    if reason:
        lines.append(reason)
        lines.append("")
    if report.get("errors"):
        lines += ["## Required revisions", ""] + [f"- {item}" for item in report["errors"]] + [""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and validate a screenshot-based prototype tournament")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("board", type=Path)
    init.add_argument("--route", required=True)
    init.add_argument("--output", type=Path, default=Path("generated/prototype-tournament.json"))

    check = sub.add_parser("validate")
    check.add_argument("tournament", type=Path)
    check.add_argument("--stage", choices=["manifest", "decision", "evidence"], default="manifest")
    check.add_argument("--evidence-root", type=Path, default=Path("."))
    check.add_argument("--output", type=Path, default=Path(".qa/prototype-tournament-review.json"))
    check.add_argument("--markdown", type=Path, default=Path(".qa/prototype-tournament-review.md"))

    args = parser.parse_args()
    if args.command == "init":
        board = _load(args.board)
        result = scaffold(board, str(args.board), args.route)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Prototype tournament scaffold: {args.output}")
        return 0

    data = _load(args.tournament)
    report = validate(data, args.stage, args.evidence_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(render_markdown(data, report), encoding="utf-8")
    print(f"Prototype tournament: {report['status']} · {len(report['ranking'])} prototypes · {len(report['survivors'])} survivor(s)")
    for item in report["errors"]:
        print(f"- ERROR: {item}")
    return 0 if report["status"] != "REVISE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
