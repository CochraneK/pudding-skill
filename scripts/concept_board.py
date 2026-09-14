#!/usr/bin/env python3
"""Contrastive concept-board scaffold and validator.

The board sits between a passing pitch and bespoke implementation. It forces multiple
structurally different ideas to exist before one visual form becomes sunk cost.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = (
    "id",
    "title",
    "form",
    "interaction_job",
    "reader_realization",
    "why_visual",
    "evidence_dependencies",
    "visual_metaphor",
    "mobile_strategy",
    "accessibility_equivalent",
    "prototype_test",
    "kill_condition",
    "inspiration",
)

STATIC_FORMS = {"static", "static_sequence", "annotated_static", "small_multiples", "print_like"}
NO_INTERACTION = {"none", "not_needed", "not-needed"}
FORBIDDEN_TRANSFER = ("copy the", "same style", "look like pudding", "pudding style", "clone")


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _corpus_ids(path: Path) -> set[str]:
    data = _load(path)
    return {str(row.get("id")) for row in data.get("stories", []) if row.get("id")}


def scaffold(story_id: str, question: str, argument: str) -> dict[str, Any]:
    def blank(cid: str, title: str, form: str, job: str) -> dict[str, Any]:
        return {
            "id": cid,
            "title": title,
            "form": form,
            "interaction_job": job,
            "reader_realization": "",
            "why_visual": "",
            "evidence_dependencies": [],
            "visual_metaphor": "",
            "mobile_strategy": "",
            "accessibility_equivalent": "",
            "prototype_test": "",
            "kill_condition": "",
            "inspiration": [],
        }

    return {
        "status": "IDEATION_REQUIRED",
        "story_id": story_id,
        "question": question,
        "argument": argument,
        "instructions": "Develop all three directions before selecting one. Replace forms when the story suggests better contrasts; keep at least one static/no-interaction alternative.",
        "concepts": [
            blank("static-alternative", "Static / annotated alternative", "annotated_static", "none"),
            blank("guided-alternative", "Guided transformation alternative", "guided_sequence", "reveal"),
            blank("agency-alternative", "Reader-agency alternative", "explorable", "explore"),
        ],
    }


def validate(board: dict[str, Any], corpus_ids: set[str]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    concepts = board.get("concepts")
    if not isinstance(concepts, list):
        return {"status": "REVISE", "errors": ["concepts must be a list"], "warnings": [], "metrics": {}}
    if len(concepts) < 3:
        errors.append("Create at least 3 concepts before prototyping; one idea is not a concept comparison.")
    if len(concepts) > 6:
        warnings.append("More than 6 concepts can turn ideation into paperwork; prune before prototyping.")

    ids: set[str] = set()
    forms: set[str] = set()
    jobs: set[str] = set()
    static_count = 0
    inspired_count = 0

    for index, concept in enumerate(concepts):
        label = concept.get("id") if isinstance(concept, dict) else f"concept-{index + 1}"
        if not isinstance(concept, dict):
            errors.append(f"{label}: concept must be an object")
            continue
        missing = [field for field in REQUIRED_FIELDS if field not in concept]
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(missing)}")
            continue

        cid = _text(concept.get("id"))
        if not cid:
            errors.append(f"concept-{index + 1}: id is empty")
        elif cid in ids:
            errors.append(f"{cid}: duplicate concept id")
        ids.add(cid)

        form = _text(concept.get("form")).lower()
        job = _text(concept.get("interaction_job")).lower()
        if not form:
            errors.append(f"{label}: form is empty")
        if not job:
            errors.append(f"{label}: interaction_job is empty; use 'none' when interaction is unnecessary")
        forms.add(form)
        jobs.add(job)
        if form in STATIC_FORMS or job in NO_INTERACTION:
            static_count += 1

        for field, minimum in (
            ("reader_realization", 30),
            ("why_visual", 35),
            ("visual_metaphor", 20),
            ("mobile_strategy", 25),
            ("accessibility_equivalent", 25),
            ("prototype_test", 25),
            ("kill_condition", 25),
        ):
            if len(_text(concept.get(field))) < minimum:
                errors.append(f"{label}: {field} is too thin")

        evidence = concept.get("evidence_dependencies")
        if not isinstance(evidence, list) or not any(_text(item) for item in evidence):
            errors.append(f"{label}: evidence_dependencies needs at least one concrete dependency")

        inspiration = concept.get("inspiration")
        if not isinstance(inspiration, list):
            errors.append(f"{label}: inspiration must be a list")
            continue
        if len(inspiration) > 2:
            errors.append(f"{label}: use at most 2 reference stories; the board is for contrast, not style retrieval")
        for ref in inspiration:
            if not isinstance(ref, dict):
                errors.append(f"{label}: each inspiration entry must be an object")
                continue
            story_ref = _text(ref.get("story_id"))
            transfer = _text(ref.get("transfer"))
            if story_ref not in corpus_ids:
                errors.append(f"{label}: unknown corpus story_id {story_ref!r}")
            if len(transfer) < 25:
                errors.append(f"{label}: inspiration transfer principle is too thin")
            if any(token in transfer.lower() for token in FORBIDDEN_TRANSFER):
                errors.append(f"{label}: inspiration describes surface imitation instead of a transferable operation")
            inspired_count += 1

    if len(forms) < 2:
        errors.append("Concept board needs at least 2 distinct forms; variations of one layout do not count as ideation.")
    if len(jobs) < 2:
        errors.append("Concept board needs at least 2 distinct interaction jobs, including 'none' when appropriate.")
    if static_count < 1:
        errors.append("Concept board must include a static/no-interaction alternative before choosing an interactive form.")

    metrics = {
        "concepts": len(concepts),
        "distinct_forms": len(forms),
        "distinct_interaction_jobs": len(jobs),
        "static_alternatives": static_count,
        "reference_links": inspired_count,
    }
    return {
        "status": "READY_FOR_PROTOTYPE" if not errors else "REVISE",
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
        "disclaimer": "A passing board proves concept diversity and completeness, not that any concept is good. Prototype and editorial review still decide.",
    }


def render_markdown(board: dict[str, Any], report: dict[str, Any]) -> str:
    lines = [
        "# Concept board",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Question: {board.get('question', '')}",
        "",
        f"Argument: {board.get('argument', '')}",
        "",
        "## Directions",
        "",
    ]
    for concept in board.get("concepts", []):
        lines += [
            f"### {concept.get('title') or concept.get('id')}",
            "",
            f"- Form: `{concept.get('form', '')}`",
            f"- Interaction job: `{concept.get('interaction_job', '')}`",
            f"- Reader realization: {concept.get('reader_realization', '')}",
            f"- Why visual: {concept.get('why_visual', '')}",
            f"- Visual metaphor: {concept.get('visual_metaphor', '')}",
            f"- Prototype test: {concept.get('prototype_test', '')}",
            f"- Kill condition: {concept.get('kill_condition', '')}",
            "",
        ]
    if report["errors"]:
        lines += ["## Required revisions", ""] + [f"- {item}" for item in report["errors"]] + [""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and validate a contrastive visual concept board")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--story-id", required=True)
    init.add_argument("--question", required=True)
    init.add_argument("--argument", required=True)
    init.add_argument("--output", type=Path, default=Path("generated/concept-board.json"))

    check = sub.add_parser("validate")
    check.add_argument("board", type=Path)
    check.add_argument("--corpus", type=Path, default=Path("benchmarks/pudding-study-corpus.json"))
    check.add_argument("--output", type=Path, default=Path(".qa/concept-board-review.json"))
    check.add_argument("--markdown", type=Path, default=Path(".qa/concept-board-review.md"))

    args = parser.parse_args()
    if args.command == "init":
        board = scaffold(args.story_id, args.question, args.argument)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Concept board scaffold: {args.output}")
        return 0

    board = _load(args.board)
    report = validate(board, _corpus_ids(args.corpus))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(render_markdown(board, report), encoding="utf-8")
    print(
        f"Concept board: {report['status']} · {report['metrics'].get('concepts', 0)} concepts · "
        f"{report['metrics'].get('distinct_forms', 0)} forms · "
        f"{report['metrics'].get('static_alternatives', 0)} static alternative(s)"
    )
    for item in report["errors"]:
        print(f"- ERROR: {item}")
    return 0 if report["status"] == "READY_FOR_PROTOTYPE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
