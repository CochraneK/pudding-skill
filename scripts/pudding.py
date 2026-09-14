#!/usr/bin/env python3
"""Unified CLI for the editorial data-storytelling workflow."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> int:
    print("+", " ".join(command))
    return subprocess.call(command)


def story(args: argparse.Namespace) -> int:
    command = [sys.executable, "scripts/pipeline.py", str(args.data)]
    if args.question:
        command += ["--question", args.question]
    if args.audience:
        command += ["--audience", args.audience]
    if args.schema:
        command += ["--schema", str(args.schema)]
    if args.workdir:
        command += ["--workdir", str(args.workdir)]
    command += ["--limit", str(args.limit)]
    return run(command)


def inspect(args: argparse.Namespace) -> int:
    return run([sys.executable, "scripts/profile_data.py", str(args.data)])


def candidates(args: argparse.Namespace) -> int:
    command = [sys.executable, "scripts/candidate_story.py", str(args.data), "--limit", str(args.limit)]
    if args.question:
        command += ["--question", args.question]
    if args.schema:
        command += ["--schema", str(args.schema)]
    return run(command)


def benchmark(args: argparse.Namespace) -> int:
    command = [
        sys.executable,
        "scripts/benchmark.py",
        "--corpus",
        str(args.corpus),
        "--baseline",
        str(args.baseline),
        "--output",
        str(args.output),
        "--markdown",
        str(args.markdown),
    ]
    if args.no_gate:
        command.append("--no-gate")
    return run(command)


def review(args: argparse.Namespace) -> int:
    command = [
        sys.executable,
        "scripts/visual_critic.py",
        str(args.probe),
        "--output",
        str(args.output),
        "--markdown",
        str(args.markdown),
        "--fail-on",
        args.fail_on,
    ]
    return run(command)


def review_check(args: argparse.Namespace) -> int:
    return run([
        sys.executable,
        "scripts/validate_agent_visual_review.py",
        str(args.contract),
        str(args.agent_review),
    ])


def refine(args: argparse.Namespace) -> int:
    command = [
        sys.executable,
        "scripts/refine_visual.py",
        str(args.review),
        "--output",
        str(args.output),
        "--css",
        str(args.css),
        "--iteration",
        str(args.iteration),
    ]
    if args.agent_review:
        command += ["--agent-review", str(args.agent_review)]
    if args.apply:
        command.append("--apply")
    return run(command)


def main() -> int:
    parser = argparse.ArgumentParser(prog="pudding", description="Evidence-first editorial data-storytelling CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_parser = sub.add_parser("inspect", help="profile an arbitrary tabular dataset")
    inspect_parser.add_argument("data", type=Path)
    inspect_parser.set_defaults(func=inspect)

    candidate_parser = sub.add_parser("candidates", help="rank defensible story directions")
    candidate_parser.add_argument("data", type=Path)
    candidate_parser.add_argument("--question")
    candidate_parser.add_argument("--schema", type=Path)
    candidate_parser.add_argument("--limit", type=int, default=12)
    candidate_parser.set_defaults(func=candidates)

    story_parser = sub.add_parser("story", help="run data audit → candidates → claim audit → visual plan → first draft")
    story_parser.add_argument("data", type=Path)
    story_parser.add_argument("--question")
    story_parser.add_argument("--audience", default="general audience")
    story_parser.add_argument("--schema", type=Path)
    story_parser.add_argument("--workdir", type=Path, default=Path("generated"))
    story_parser.add_argument("--limit", type=int, default=12)
    story_parser.set_defaults(func=story)

    benchmark_parser = sub.add_parser("benchmark", help="run the curated editorial regression corpus")
    benchmark_parser.add_argument("--corpus", type=Path, default=Path("benchmarks/corpus.json"))
    benchmark_parser.add_argument("--baseline", type=Path, default=Path("benchmarks/baseline.json"))
    benchmark_parser.add_argument("--output", type=Path, default=Path(".qa/benchmark-report.json"))
    benchmark_parser.add_argument("--markdown", type=Path, default=Path(".qa/benchmark-report.md"))
    benchmark_parser.add_argument("--no-gate", action="store_true")
    benchmark_parser.set_defaults(func=benchmark)

    review_parser = sub.add_parser("review", help="turn visual-probe metrics into a screenshot review contract")
    review_parser.add_argument("probe", type=Path, nargs="?", default=Path(".qa/visual-probe.json"))
    review_parser.add_argument("--output", type=Path, default=Path(".qa/visual-review.json"))
    review_parser.add_argument("--markdown", type=Path, default=Path(".qa/visual-review.md"))
    review_parser.add_argument("--fail-on", choices=["never", "error", "warning"], default="error")
    review_parser.set_defaults(func=review)

    review_check_parser = sub.add_parser("review-check", help="validate that an agent/editor reviewed every required screenshot")
    review_check_parser.add_argument("agent_review", type=Path)
    review_check_parser.add_argument("--contract", type=Path, default=Path(".qa/visual-review.json"))
    review_check_parser.set_defaults(func=review_check)

    refine_parser = sub.add_parser("refine", help="plan/apply bounded visual refinements after screenshot review")
    refine_parser.add_argument("review", type=Path, nargs="?", default=Path(".qa/visual-review.json"))
    refine_parser.add_argument("--agent-review", type=Path)
    refine_parser.add_argument("--output", type=Path, default=Path(".qa/refinement-plan.json"))
    refine_parser.add_argument("--css", type=Path, default=Path("src/styles/refinement.css"))
    refine_parser.add_argument("--iteration", type=int, default=1)
    refine_parser.add_argument("--apply", action="store_true")
    refine_parser.set_defaults(func=refine)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
