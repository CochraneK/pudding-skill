#!/usr/bin/env python3
"""Map an evidence-backed story spec to a recommended editorial visual grammar.

The recommendation is intentionally separate from the conservative baseline renderer.
This lets the agent suggest a richer publication form without breaking deterministic build support.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GRAMMAR: dict[str, dict[str, Any]] = {
    "change_gap": {
        "recommended_visual": "slopegraph",
        "baseline_renderer": "bar",
        "operation": "compare divergence",
        "production_mode": "annotated-static",
        "why": "Two measures change over the same interval; a slopegraph makes their separation legible while a ranked bar remains a robust baseline.",
    },
    "group_change": {
        "recommended_visual": "small-multiple line chart",
        "baseline_renderer": "line",
        "operation": "trace trajectories",
        "production_mode": "small-multiples",
        "why": "The evidence is temporal and grouped, so preserving shape over time matters more than collapsing to one endpoint.",
    },
    "group_mean": {
        "recommended_visual": "annotated dot plot",
        "baseline_renderer": "bar",
        "operation": "rank groups",
        "production_mode": "annotated-static",
        "why": "A dot plot emphasizes relative position and avoids implying that bar area carries meaning beyond the ranked values.",
    },
    "correlation": {
        "recommended_visual": "annotated scatterplot",
        "baseline_renderer": "scatter",
        "operation": "show relationship",
        "production_mode": "annotated-static",
        "why": "The claim concerns association between two measures, which should remain visible as individual paired observations.",
    },
    "distribution": {
        "recommended_visual": "histogram + reference annotations",
        "baseline_renderer": "histogram",
        "operation": "show distribution",
        "production_mode": "annotated-static",
        "why": "The shape, center, and spread of a continuous measure are the story rather than individual categories.",
    },
}


def plan_visual(spec: dict[str, Any]) -> dict[str, Any]:
    evidence = spec.get("evidence") or []
    kind = evidence[0].get("kind") if evidence and isinstance(evidence[0], dict) else None
    fallback = {
        "recommended_visual": (spec.get("visuals") or [{"type": "bar"}])[0].get("type", "bar"),
        "baseline_renderer": (spec.get("visuals") or [{"type": "bar"}])[0].get("type", "bar"),
        "operation": "explain evidence",
        "production_mode": spec.get("production_mode", "annotated-static"),
        "why": "No richer deterministic grammar rule matched this evidence type; preserve the validated baseline form.",
    }
    chosen = dict(GRAMMAR.get(str(kind), fallback))
    chosen["evidence_kind"] = kind or "unknown"
    chosen["editorial_constraints"] = [
        "Lead with the claim, not the chart type.",
        "Annotate the evidence that directly supports the primary insight.",
        "Keep the baseline renderer available as a safe fallback.",
        "Do not use scrollytelling unless sequence materially improves comprehension.",
    ]
    return chosen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    result = plan_visual(spec)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
