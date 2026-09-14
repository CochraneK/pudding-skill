#!/usr/bin/env python3
"""Validate and summarize the qualitative Pudding public-story study corpus.

The corpus stores only links, coarse metadata, and original annotations about editorial
operations. It is not a scraper, a style-cloning dataset, or an official Pudding rubric.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {
    "id",
    "title",
    "url",
    "published_year",
    "story_family",
    "question",
    "argument_pattern",
    "human_angle",
    "data_strategy",
    "visual_necessity",
    "interaction_jobs",
    "interaction_mode",
    "design_move",
    "caveat_mode",
    "editorial_lesson",
    "anti_copy_note",
}

MIN_TEXT = {
    "question": 25,
    "argument_pattern": 45,
    "human_angle": 45,
    "visual_necessity": 45,
    "design_move": 35,
    "caveat_mode": 30,
    "editorial_lesson": 45,
    "anti_copy_note": 25,
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    stories = corpus.get("stories")
    if not isinstance(stories, list):
        return {"status": "FAIL", "errors": ["stories must be a list"], "warnings": [], "metrics": {}}

    ids: set[str] = set()
    urls: set[str] = set()
    families: Counter[str] = Counter()
    strategies: Counter[str] = Counter()
    jobs: Counter[str] = Counter()
    modes: Counter[str] = Counter()

    for index, story in enumerate(stories):
        label = story.get("id") if isinstance(story, dict) else f"row-{index}"
        if not isinstance(story, dict):
            errors.append(f"{label}: story must be an object")
            continue

        missing = sorted(REQUIRED_FIELDS - set(story))
        if missing:
            errors.append(f"{label}: missing required fields: {', '.join(missing)}")
            continue

        sid = str(story["id"]).strip()
        if not sid:
            errors.append(f"row-{index}: id is empty")
        elif sid in ids:
            errors.append(f"{sid}: duplicate id")
        ids.add(sid)

        url = str(story["url"]).strip()
        if not url.startswith("https://pudding.cool/"):
            errors.append(f"{sid}: url must point to a public pudding.cool page")
        if url in urls:
            errors.append(f"{sid}: duplicate url")
        urls.add(url)

        year = story["published_year"]
        if not isinstance(year, int) or year < 2010 or year > 2100:
            errors.append(f"{sid}: published_year must be a plausible integer")

        for field, minimum in MIN_TEXT.items():
            value = story.get(field)
            if not isinstance(value, str) or len(value.strip()) < minimum:
                errors.append(f"{sid}: {field} is too thin for qualitative study")

        interaction_jobs = story.get("interaction_jobs")
        if not isinstance(interaction_jobs, list) or not interaction_jobs:
            errors.append(f"{sid}: interaction_jobs must be a non-empty list")
        else:
            for job in interaction_jobs:
                if isinstance(job, str) and job.strip():
                    jobs[job.strip()] += 1
                else:
                    errors.append(f"{sid}: interaction job entries must be non-empty strings")

        family = str(story.get("story_family", "")).strip()
        strategy = str(story.get("data_strategy", "")).strip()
        mode = str(story.get("interaction_mode", "")).strip()
        if family:
            families[family] += 1
        if strategy:
            strategies[strategy] += 1
        if mode:
            modes[mode] += 1

        anti_copy = str(story.get("anti_copy_note", "")).lower()
        if not any(token in anti_copy for token in ("do not", "don't", "never", "not ")):
            warnings.append(f"{sid}: anti_copy_note should explicitly say what not to imitate")

    if len(stories) < 10:
        errors.append("corpus must contain at least 10 public story studies")
    if len(families) < 6:
        errors.append("corpus needs at least 6 distinct story families to avoid a scrollytelling monoculture")
    if len(strategies) < 6:
        errors.append("corpus needs at least 6 distinct data strategies")
    if len(jobs) < 6:
        errors.append("corpus needs at least 6 distinct interaction jobs")
    if len(modes) < 6:
        errors.append("corpus needs at least 6 distinct interaction modes")

    metrics = {
        "stories": len(stories),
        "story_families": len(families),
        "data_strategies": len(strategies),
        "interaction_jobs": len(jobs),
        "interaction_modes": len(modes),
        "family_counts": dict(sorted(families.items())),
        "strategy_counts": dict(sorted(strategies.items())),
        "job_counts": dict(sorted(jobs.items())),
        "mode_counts": dict(sorted(modes.items())),
    }
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
        "disclaimer": "Structural corpus validation only; it does not prove taste, quality, or similarity to The Pudding.",
    }


def render_markdown(corpus: dict[str, Any], report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    lines = [
        "# Pudding public-story study corpus",
        "",
        "> This is a qualitative learning set built from public story pages. It stores original annotations, not copied article prose or visual assets, and is not an official Pudding rubric.",
        "",
        f"Validation: **{report['status']}** · {metrics.get('stories', 0)} stories · {metrics.get('story_families', 0)} story families · {metrics.get('interaction_jobs', 0)} interaction jobs.",
        "",
        "## What the corpus is for",
        "",
        "Use the stories as counterexamples to chart-first thinking. Ask what created the author's curiosity, what the argument is, why the evidence needed a visual or interactive form, what the interaction makes the reader understand, and where caveats remain visible.",
        "",
        "The corpus should *increase* format diversity. A new project does not become more Pudding-like by copying sticky scroll, colors, type, layouts, jokes, or a famous chart from one of these examples.",
        "",
        "## Coverage",
        "",
        "### Story families",
        "",
    ]
    for name, count in metrics.get("family_counts", {}).items():
        lines.append(f"- `{name}`: {count}")
    lines += ["", "### Data strategies", ""]
    for name, count in metrics.get("strategy_counts", {}).items():
        lines.append(f"- `{name}`: {count}")
    lines += ["", "### Interaction jobs", ""]
    for name, count in metrics.get("job_counts", {}).items():
        lines.append(f"- `{name}`: {count}")

    lines += ["", "## Story studies", ""]
    for story in corpus.get("stories", []):
        jobs = ", ".join(f"`{job}`" for job in story["interaction_jobs"])
        lines += [
            f"### {story['title']}",
            "",
            f"- Source: {story['url']}",
            f"- Family: `{story['story_family']}` · data: `{story['data_strategy']}` · interaction: {jobs}",
            f"- Argument pattern: {story['argument_pattern']}",
            f"- Why visual: {story['visual_necessity']}",
            f"- Editorial lesson: {story['editorial_lesson']}",
            f"- Anti-copy guardrail: {story['anti_copy_note']}",
            "",
        ]

    lines += [
        "## Synthesis",
        "",
        "The recurring pattern is not a specific chart. Across the corpus, visual form is usually downstream of a distinctive question, a concrete human stake, and an evidence-gathering decision. Interaction is strongest when it changes the reader's cognitive state: committing to a guess, exposing model assumptions, revealing structure, comparing alternatives, looking up oneself, or exploring after a guided example.",
        "",
        "A future `pudding-skill` pitch should therefore be compared against multiple *operations* in this corpus, never against a single story's surface appearance.",
        "",
    ]
    return "\n".join(lines)


def write_report(corpus_path: Path, json_out: Path, markdown_out: Path) -> dict[str, Any]:
    corpus = _load(corpus_path)
    report = validate_corpus(corpus)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.write_text(render_markdown(corpus, report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and summarize the qualitative Pudding study corpus")
    parser.add_argument("command", choices=["validate", "report"])
    parser.add_argument("--corpus", type=Path, default=Path("benchmarks/pudding-study-corpus.json"))
    parser.add_argument("--output", type=Path, default=Path(".qa/pudding-study-corpus.json"))
    parser.add_argument("--markdown", type=Path, default=Path(".qa/pudding-study-corpus.md"))
    args = parser.parse_args()

    corpus = _load(args.corpus)
    report = validate_corpus(corpus)
    if args.command == "report":
        report = write_report(args.corpus, args.output, args.markdown)
    elif args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    metrics = report.get("metrics", {})
    print(
        f"Pudding study corpus: {report['status']} · {metrics.get('stories', 0)} stories · "
        f"{metrics.get('story_families', 0)} families · {metrics.get('interaction_jobs', 0)} interaction jobs"
    )
    for error in report["errors"]:
        print(f"- ERROR: {error}")
    for warning in report["warnings"]:
        print(f"- WARN: {warning}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
