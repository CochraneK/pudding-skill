#!/usr/bin/env python3
"""Editorial triage for Pudding-inspired story pitches.

This is an operational approximation built from public Pudding pitch/process guidance.
It is deliberately *not* an official Pudding rubric, a truth score, an aesthetic score,
or a guarantee that a story is worth publishing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


OUTCOMES = {"CONTINUE", "PIVOT", "PIVOT_NONVISUAL", "PUT_DOWN"}


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _meaningful(value: Any, minimum: int = 30) -> bool:
    return len(_text(value)) >= minimum


def score_pitch(pitch: dict[str, Any]) -> dict[str, Any]:
    """Score a pitch for deterministic triage and return an editorial decision."""
    scores: dict[str, int] = {}
    notes: list[str] = []

    argument = _text(pitch.get("argument"))
    if not argument:
        argument_score = 0
        notes.append("No declarative argument is stated; the pitch is still a topic or question.")
    else:
        argument_score = 8
        if len(argument) >= 45:
            argument_score += 7
        if not argument.endswith("?") and not argument.endswith("？"):
            argument_score += 5
    scores["argument"] = min(argument_score, 20)

    soul = 0
    if _meaningful(pitch.get("why_you"), 25):
        soul += 6
    if _meaningful(pitch.get("human_angle"), 25):
        soul += 6
    if _meaningful(pitch.get("tone_or_obsession"), 12):
        soul += 3
    scores["soul_human_angle"] = soul
    if soul < 8:
        notes.append("The human stake/obsession is thin; add why this story matters to a person, not only to a dataset.")

    data_plan = pitch.get("data_plan") if isinstance(pitch.get("data_plan"), dict) else {}
    data_status = _text(data_plan.get("status")).lower()
    data_scores = {"verified": 20, "obtainable": 17, "speculative": 8, "blocked": 0}
    data_score = data_scores.get(data_status, 0)
    fallback = _text(data_plan.get("fallback"))
    sources = _list(data_plan.get("sources"))
    method = _text(data_plan.get("method"))
    if data_status == "blocked" and fallback:
        data_score = 5
    elif data_status in {"verified", "obtainable"} and not sources:
        data_score = max(0, data_score - 4)
    if data_status in {"verified", "obtainable"} and len(method) < 20:
        data_score = max(0, data_score - 3)
    scores["data_pathway"] = data_score
    if data_score < 12:
        notes.append("The data path is not yet publication-safe; verify access, method, and a fallback before production.")

    visual_case = pitch.get("visual_case") if isinstance(pitch.get("visual_case"), dict) else {}
    visual_score = 0
    if _meaningful(visual_case.get("why_visual"), 40):
        visual_score += 8
    elif _meaningful(visual_case.get("why_visual"), 20):
        visual_score += 4
    if _meaningful(visual_case.get("first_whiteboard"), 20):
        visual_score += 4
    visual_concepts = _list(visual_case.get("visual_concepts"))
    if len(visual_concepts) >= 2:
        visual_score += 3
    scores["visual_necessity"] = min(visual_score, 15)
    if visual_score < 8:
        notes.append("The pitch has not shown why it must be visual; do not force charts or scrollytelling onto a text-first argument.")

    distinctive_score = 0
    if _meaningful(pitch.get("aha"), 25):
        distinctive_score += 5
    if _meaningful(pitch.get("distinctive_entry_point"), 25):
        distinctive_score += 5
    scores["aha_distinctiveness"] = distinctive_score
    if distinctive_score < 5:
        notes.append("The surprise or distinctive entry point is weak; identify what a reader should learn that is not already obvious from the topic.")

    interaction = pitch.get("interaction") if isinstance(pitch.get("interaction"), dict) else {}
    interaction_job = _text(interaction.get("job")).lower()
    interaction_rationale = _text(interaction.get("rationale"))
    if interaction_job in {"", "none", "not_needed", "not-needed"}:
        interaction_score = 5
    elif interaction_job in {
        "compare", "reveal", "highlight", "zoom", "annotate", "accumulate", "morph", "explore", "lookup", "simulate", "play", "personalize"
    } and len(interaction_rationale) >= 25:
        interaction_score = 5
    else:
        interaction_score = 0
        notes.append("Interaction is present without a clear cognitive/editorial job; remove it or state what understanding it enables.")
    scores["interaction_earned"] = interaction_score

    iteration_score = 0
    if len(visual_concepts) >= 3:
        iteration_score += 4
    elif len(visual_concepts) >= 2:
        iteration_score += 3
    if _meaningful(pitch.get("prototype_plan"), 25):
        iteration_score += 3
    if _meaningful(pitch.get("iteration_plan"), 25):
        iteration_score += 3
    scores["iteration"] = iteration_score
    if iteration_score < 6:
        notes.append("The pitch jumps too quickly from idea to implementation; storyboard and compare multiple visual concepts first.")

    kill_conditions = [x for x in _list(pitch.get("kill_conditions")) if _text(x)]
    kill_score = 5 if len(kill_conditions) >= 2 else 3 if len(kill_conditions) == 1 else 0
    scores["killability"] = kill_score
    if kill_score < 3:
        notes.append("No explicit kill/pivot conditions are defined; the workflow currently assumes the story must ship.")

    total = sum(scores.values())

    hard_block = data_status == "blocked" and not fallback
    if hard_block:
        decision = "PUT_DOWN"
        notes.insert(0, "The required data is blocked and no viable fallback is defined.")
    elif scores["argument"] < 8:
        decision = "PIVOT"
    elif scores["visual_necessity"] < 8 and scores["argument"] >= 15 and scores["data_pathway"] >= 15:
        decision = "PIVOT_NONVISUAL"
    elif total >= 75:
        decision = "CONTINUE"
    elif total >= 50:
        decision = "PIVOT"
    else:
        decision = "PUT_DOWN"

    return {
        "status": "EDITORIAL_TRIAGE_ONLY",
        "decision": decision,
        "score": total,
        "score_max": 100,
        "dimensions": scores,
        "notes": notes,
        "disclaimer": "Operational Pudding-inspired gate; not an official Pudding rubric, publication approval, truth score, or aesthetic judgment.",
    }


def evaluate_file(path: Path, output: Path | None = None) -> dict[str, Any]:
    pitch = json.loads(path.read_text(encoding="utf-8"))
    report = score_pitch(pitch)
    report["pitch_id"] = pitch.get("id") or path.stem
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def benchmark(corpus_path: Path, output: Path | None = None) -> dict[str, Any]:
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    cases = corpus.get("cases", [])
    results = []
    for case in cases:
        report = score_pitch(case["pitch"])
        expected = case["expected_decision"]
        ok = report["decision"] == expected
        results.append({
            "id": case["id"],
            "split": case.get("split", "calibration"),
            "kind": case.get("kind", "unknown"),
            "expected": expected,
            "actual": report["decision"],
            "score": report["score"],
            "ok": ok,
        })
    holdout = [r for r in results if r["split"] == "holdout"]
    anti = [r for r in results if r["kind"] == "anti_pattern"]
    report = {
        "status": "PASS" if all(r["ok"] for r in results) else "FAIL",
        "passed": sum(1 for r in results if r["ok"]),
        "total": len(results),
        "holdout_passed": sum(1 for r in holdout if r["ok"]),
        "holdout_total": len(holdout),
        "anti_pattern_passed": sum(1 for r in anti if r["ok"]),
        "anti_pattern_total": len(anti),
        "results": results,
        "disclaimer": "This corpus checks internal decision consistency, not whether the model has learned Pudding's taste.",
    }
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Pudding-inspired editorial pitch triage")
    sub = parser.add_subparsers(dest="command", required=True)

    evaluate = sub.add_parser("evaluate", help="evaluate one story concept")
    evaluate.add_argument("pitch", type=Path)
    evaluate.add_argument("--output", type=Path, default=Path(".qa/pudding-gate.json"))

    bench = sub.add_parser("benchmark", help="run the Pudding DNA calibration/holdout corpus")
    bench.add_argument("--corpus", type=Path, default=Path("benchmarks/pudding-dna-corpus.json"))
    bench.add_argument("--output", type=Path, default=Path(".qa/pudding-dna-report.json"))

    args = parser.parse_args()
    if args.command == "evaluate":
        report = evaluate_file(args.pitch, args.output)
        print(f"Pudding gate: {report['decision']} · {report['score']}/100")
        for note in report["notes"]:
            print(f"- {note}")
        return 0

    report = benchmark(args.corpus, args.output)
    print(
        f"Pudding DNA benchmark: {report['status']} · {report['passed']}/{report['total']} cases · "
        f"holdout {report['holdout_passed']}/{report['holdout_total']} · "
        f"anti-pattern {report['anti_pattern_passed']}/{report['anti_pattern_total']}"
    )
    for row in report["results"]:
        marker = "PASS" if row["ok"] else "FAIL"
        print(f"- {marker} {row['id']}: expected {row['expected']}, got {row['actual']} ({row['score']}/100)")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
