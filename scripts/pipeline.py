#!/usr/bin/env python3
"""Run the deterministic baseline: profile -> story spec -> validation -> render bundle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from derive_story import derive
from generate_story import generate
from profile_data import profile
from validate_story import validate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("--question")
    parser.add_argument("--audience", default="general audience")
    parser.add_argument("--workdir", type=Path, default=Path("generated"))
    parser.add_argument("--render-output", type=Path, default=Path("src/data/auto-story.json"))
    args = parser.parse_args()

    args.workdir.mkdir(parents=True, exist_ok=True)
    profile_path = args.workdir / "profile.json"
    spec_path = args.workdir / "story-spec.json"

    profile_path.write_text(json.dumps(profile(args.data), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    spec = derive(args.data, args.question, args.audience)
    errors = validate(spec)
    if errors:
        raise SystemExit("Derived story spec failed validation:\n- " + "\n- ".join(errors))
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    generate(spec_path, args.data, args.render_output)

    print(f"Profile: {profile_path}")
    print(f"Story spec: {spec_path}")
    print(f"Render bundle: {args.render_output}")
    print(f"Mode: {spec.get('production_mode', 'unspecified')}")
    print(f"Insight: {spec['primary_insight']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
