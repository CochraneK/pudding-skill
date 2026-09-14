#!/usr/bin/env python3
"""Validate that an agent/editor actually reviewed every required visual-QA screenshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VERDICTS = {"pass", "revise"}
VIEWPORTS = {"desktop", "mobile"}
POSITIONS = {"top", "mid"}
SEVERITIES = {"info", "warning", "error"}
CATEGORIES = {"hierarchy", "spacing", "density", "chart", "annotation", "typography", "mobile", "other"}
ACTIONS = {"tighten_copy_measure", "increase_text_leading", "increase_touch_targets", "manual"}


def validate(review_contract: dict[str, Any], agent_review: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_items = (review_contract.get("agent_review") or {}).get("screenshots") or []
    expected = {str(item.get("path")) for item in expected_items if item.get("path")}

    verdict = agent_review.get("verdict")
    if verdict not in VERDICTS:
        errors.append("verdict must be 'pass' or 'revise'.")

    reviewed_raw = agent_review.get("reviewed_screenshots")
    if not isinstance(reviewed_raw, list):
        errors.append("reviewed_screenshots must be a list.")
        reviewed: set[str] = set()
    else:
        reviewed = {str(item) for item in reviewed_raw}
        missing = sorted(expected - reviewed)
        unknown = sorted(reviewed - expected)
        if missing:
            errors.append("missing required screenshots: " + ", ".join(missing))
        if unknown:
            errors.append("reviewed_screenshots contains unknown paths: " + ", ".join(unknown))
        if len(reviewed_raw) != len(reviewed):
            errors.append("reviewed_screenshots must not contain duplicates.")

    observations = agent_review.get("observations")
    if not isinstance(observations, list):
        errors.append("observations must be a list.")
        observations = []

    route_view_positions = {
        (str(item.get("route")), str(item.get("viewport")), str(item.get("position")))
        for item in expected_items
    }
    for index, item in enumerate(observations):
        prefix = f"observations[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        route = str(item.get("route", ""))
        viewport = str(item.get("viewport", ""))
        position = str(item.get("position", ""))
        if (route, viewport, position) not in route_view_positions:
            errors.append(f"{prefix} route/viewport/position does not match a required screenshot.")
        if viewport not in VIEWPORTS:
            errors.append(f"{prefix}.viewport must be desktop or mobile.")
        if position not in POSITIONS:
            errors.append(f"{prefix}.position must be top or mid.")
        if item.get("severity") not in SEVERITIES:
            errors.append(f"{prefix}.severity is invalid.")
        if item.get("category") not in CATEGORIES:
            errors.append(f"{prefix}.category is invalid.")
        if item.get("proposed_action") not in ACTIONS:
            errors.append(f"{prefix}.proposed_action is invalid.")
        for key in ("note", "evidence"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f"{prefix}.{key} must be a non-empty string.")

    if verdict == "pass" and any(item.get("severity") == "error" for item in observations if isinstance(item, dict)):
        errors.append("verdict cannot be pass while an error-severity observation remains.")
    if verdict == "revise" and not observations:
        errors.append("revise verdict requires at least one observation.")

    deterministic_status = review_contract.get("status")
    if deterministic_status == "FAIL" and verdict == "pass":
        errors.append("agent verdict cannot override a deterministic FAIL; fix the hard failure first.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="visual-review.json produced by visual_critic.py")
    parser.add_argument("agent_review", type=Path, help="agent/editor screenshot review JSON")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    agent_review = json.loads(args.agent_review.read_text(encoding="utf-8"))
    errors = validate(contract, agent_review)
    if errors:
        print("FAIL: agent visual review is incomplete or invalid.")
        for error in errors:
            print(f"- {error}")
        return 1
    expected = len((contract.get("agent_review") or {}).get("screenshots") or [])
    print(f"PASS: agent visual review covers all {expected} required screenshots with verdict {agent_review['verdict']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
