#!/usr/bin/env python3
"""Plan and optionally apply bounded visual refinements from review evidence.

Only a small allowlist of low-risk CSS adjustments can be applied automatically.
Everything else remains a manual/agent edit followed by a fresh build and QA pass.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_ACTIONS = {
    "tighten_copy_measure": {
        "description": "Limit long-form copy blocks to a more readable measure.",
        "css": "main :where(p, li) { max-inline-size: 68ch !important; }",
    },
    "increase_text_leading": {
        "description": "Increase paragraph/list line-height for readability.",
        "css": "main :where(p, li) { line-height: 1.55 !important; }",
    },
    "increase_touch_targets": {
        "description": "Ensure coarse-pointer form/button targets meet a 44px minimum height.",
        "css": "@media (pointer: coarse) { main :where(button, input, select, textarea, [role=\"button\"]) { min-block-size: 44px !important; } }",
    },
}


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def collect_actions(review: dict[str, Any], agent: dict[str, Any] | None = None) -> tuple[list[str], list[dict[str, Any]]]:
    requested: list[str] = []
    rejected: list[dict[str, Any]] = []
    for action in review.get("safe_auto_actions") or []:
        if action in ALLOWED_ACTIONS:
            requested.append(action)
        else:
            rejected.append({"source": "deterministic", "action": action, "reason": "not allowlisted"})

    for observation in (agent or {}).get("observations") or []:
        action = observation.get("proposed_action")
        if not action or action == "manual":
            continue
        if action in ALLOWED_ACTIONS:
            requested.append(action)
        else:
            rejected.append({"source": "agent", "action": action, "reason": "not allowlisted"})

    return sorted(set(requested)), rejected


def build_plan(review: dict[str, Any], agent: dict[str, Any] | None = None, iteration: int = 1) -> dict[str, Any]:
    actions, rejected = collect_actions(review, agent)
    return {
        "status": "READY" if actions else "NO_SAFE_AUTO_CHANGES",
        "iteration": iteration,
        "max_iterations": 2,
        "source_review_status": review.get("status"),
        "source_review_score": review.get("score"),
        "agent_verdict": (agent or {}).get("verdict"),
        "actions": [
            {
                "id": action,
                "description": ALLOWED_ACTIONS[action]["description"],
                "scope": "safe-css-override",
            }
            for action in actions
        ],
        "rejected_actions": rejected,
        "manual_findings": [
            item for item in review.get("findings") or [] if not item.get("auto_action")
        ],
        "next_gate": "Rebuild, rerun browser QA + visual probe, inspect before/after screenshots, and keep the change only if evidence improves without regressions.",
        "note": "The auto-refiner never changes data, claims, Svelte structure, chart transforms, or arbitrary colors. Non-allowlisted visual edits require an agent/editor patch and a fresh QA cycle.",
    }


def render_css(plan: dict[str, Any]) -> str:
    action_ids = [item["id"] for item in plan.get("actions") or []]
    lines = [
        "/*",
        " * Managed by scripts/refine_visual.py.",
        " * Bounded visual overrides only; regenerate instead of hand-editing.",
        " */",
        "",
    ]
    if not action_ids:
        lines.append("/* No active automatic refinements. */")
    else:
        for action in action_ids:
            lines += [f"/* {action}: {ALLOWED_ACTIONS[action]['description']} */", ALLOWED_ACTIONS[action]["css"], ""]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path, help="visual-review.json")
    parser.add_argument("--agent-review", type=Path, help="Optional screenshot observations written by an agent/editor")
    parser.add_argument("--output", type=Path, default=Path(".qa/refinement-plan.json"))
    parser.add_argument("--css", type=Path, default=Path("src/styles/refinement.css"))
    parser.add_argument("--iteration", type=int, default=1)
    parser.add_argument("--apply", action="store_true", help="Write the allowlisted CSS override file")
    args = parser.parse_args()

    if args.iteration < 1 or args.iteration > 2:
        parser.error("iteration must be 1 or 2; the bounded loop stops after two refinement passes")

    review = load_json(args.review)
    agent = load_json(args.agent_review) if args.agent_review else None
    plan = build_plan(review, agent, args.iteration)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Refinement plan: {plan['status']} · {len(plan['actions'])} safe action(s)")
    print(f"Plan: {args.output}")

    if args.apply:
        args.css.parent.mkdir(parents=True, exist_ok=True)
        args.css.write_text(render_css(plan), encoding="utf-8")
        print(f"Applied bounded CSS overrides: {args.css}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
