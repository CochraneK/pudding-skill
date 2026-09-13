#!/usr/bin/env python3
"""Validate a compact editorial data-story specification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED = (
    "question",
    "audience",
    "primary_insight",
    "evidence",
    "beats",
    "visuals",
    "sources",
    "caveats",
)

ALLOWED_OPERATIONS = {
    "establish",
    "compare",
    "reveal",
    "highlight",
    "filter",
    "reorder",
    "zoom",
    "annotate",
    "accumulate",
    "morph",
}


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Story spec must be a JSON object."]

    for key in REQUIRED:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    for key in ("question", "audience", "primary_insight"):
        if key in data and not nonempty_string(data[key]):
            errors.append(f"{key} must be a non-empty string.")

    evidence = data.get("evidence")
    if evidence is not None and (not isinstance(evidence, list) or not evidence):
        errors.append("evidence must be a non-empty list.")

    beats = data.get("beats")
    if beats is not None:
        if not isinstance(beats, list) or len(beats) < 3:
            errors.append("beats must contain at least 3 narrative beats.")
        elif any(not isinstance(beat, dict) or not nonempty_string(beat.get("purpose")) for beat in beats):
            errors.append("Each beat must be an object with a non-empty purpose.")

    visuals = data.get("visuals")
    if visuals is not None:
        if not isinstance(visuals, list) or not visuals:
            errors.append("visuals must be a non-empty list.")
        else:
            for index, visual in enumerate(visuals):
                if not isinstance(visual, dict):
                    errors.append(f"visuals[{index}] must be an object.")
                    continue
                for key in ("type", "purpose", "operation"):
                    if not nonempty_string(visual.get(key)):
                        errors.append(f"visuals[{index}].{key} must be a non-empty string.")
                operation = visual.get("operation")
                if nonempty_string(operation) and operation not in ALLOWED_OPERATIONS:
                    errors.append(
                        f"visuals[{index}].operation '{operation}' is not one of: "
                        + ", ".join(sorted(ALLOWED_OPERATIONS))
                    )

    for key in ("sources", "caveats"):
        value = data.get(key)
        if value is not None and not isinstance(value, list):
            errors.append(f"{key} must be a list.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Story spec JSON")
    args = parser.parse_args()

    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        parser.error(f"file not found: {args.path}")
    except json.JSONDecodeError as exc:
        print(f"FAIL: invalid JSON: {exc}")
        return 1

    errors = validate(data)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS: story spec satisfies the required editorial structure.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
