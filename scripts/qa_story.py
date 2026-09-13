#!/usr/bin/env python3
"""Static preflight QA for the skill, generated bundle, and brand hygiene."""
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--bundle", type=Path, default=Path("src/data/auto-story.json"))
    args = parser.parse_args()

    errors = []
    bundle_path = args.root / args.bundle
    if not bundle_path.exists():
        errors.append(f"Missing generated bundle: {bundle_path}")
    else:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        errors.extend(validate(bundle.get("spec")))
        chart = bundle.get("chart", {})
        if not chart.get("type") or not isinstance(chart.get("data"), list) or not chart.get("data"):
            errors.append("Generated chart must contain a type and non-empty data list.")
        if not all(finite_numbers(bundle)):
            errors.append("Generated bundle contains NaN or infinite numbers.")

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

    print("PASS: story bundle and static preflight checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
