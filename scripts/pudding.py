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

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
