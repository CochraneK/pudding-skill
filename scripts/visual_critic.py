#!/usr/bin/env python3
"""Turn browser visual-probe metrics into a scored editorial visual review.

This critic intentionally separates deterministic layout/accessibility evidence from
subjective art direction. It produces an agent-review contract that points to the
captured screenshots but does not pretend that numeric heuristics can judge taste.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SEVERITY_WEIGHT = {"error": 18, "warning": 7, "info": 2}


def finding(code: str, severity: str, route: str, viewport: str, summary: str, evidence: Any, *, action: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "route": route,
        "viewport": viewport,
        "summary": summary,
        "evidence": evidence,
    }
    if action:
        item["auto_action"] = action
    return item


def critique_case(case: dict[str, Any]) -> list[dict[str, Any]]:
    route = str(case.get("route", "?"))
    viewport = str(case.get("viewport", "?"))
    m = case.get("metrics") or {}
    out: list[dict[str, Any]] = []

    clipping = m.get("clipping") or {}
    if int(clipping.get("count", 0)):
        out.append(finding(
            "text_clipping", "error", route, viewport,
            "Visible text appears clipped inside its box.", clipping.get("samples", []),
        ))

    contrast = m.get("contrast") or {}
    if int(contrast.get("severeCount", 0)):
        out.append(finding(
            "contrast_severe", "error", route, viewport,
            "Some visible text has contrast below 3:1.", contrast.get("severeSamples", []),
        ))
    elif int(contrast.get("lowCount", 0)):
        out.append(finding(
            "contrast_borderline", "warning", route, viewport,
            "Some visible text is below the WCAG contrast target for its computed size/weight.", contrast.get("lowSamples", []),
        ))

    controls = m.get("controls") or {}
    if viewport == "mobile" and int(controls.get("smallTargetCount", 0)):
        out.append(finding(
            "small_touch_targets", "warning", route, viewport,
            "Interactive targets smaller than 44×44 px were detected on the mobile viewport.",
            controls.get("smallTargets", []), action="increase_touch_targets",
        ))

    copy = m.get("copy") or {}
    max_measure = float(copy.get("maxMeasureEm") or 0)
    if max_measure > 82:
        out.append(finding(
            "copy_measure_too_wide", "warning", route, viewport,
            f"The widest copy block is about {max_measure:.1f}em; long-form reading is likely too wide.",
            copy.get("samples", []), action="tighten_copy_measure",
        ))
    min_font = float(copy.get("minFontPx") or 0)
    if copy.get("blockCount") and min_font and min_font < 14:
        out.append(finding(
            "copy_too_small", "warning", route, viewport,
            f"Body copy drops to {min_font:.1f}px.", {"minFontPx": min_font},
        ))
    min_leading = float(copy.get("minLineHeightRatio") or 0)
    if copy.get("blockCount") and min_leading and min_leading < 1.32:
        out.append(finding(
            "leading_too_tight", "warning", route, viewport,
            f"The tightest copy line-height ratio is {min_leading:.2f}.",
            {"minLineHeightRatio": min_leading}, action="increase_text_leading",
        ))

    headings = m.get("headings") or {}
    jumps = headings.get("jumps") or []
    if jumps:
        out.append(finding(
            "heading_hierarchy_jump", "warning", route, viewport,
            "Heading levels skip one or more semantic levels.", jumps,
        ))

    visuals = m.get("visuals") or {}
    if viewport == "mobile" and int(visuals.get("wideMobileCount", 0)):
        out.append(finding(
            "mobile_visual_aspect", "warning", route, viewport,
            "A very wide visual may be difficult to read on mobile even without horizontal overflow.",
            visuals.get("items", []),
        ))

    composition = m.get("composition") or {}
    first_visual = composition.get("firstVisualTop")
    vh = (m.get("viewport") or {}).get("height")
    if first_visual is not None and vh and float(first_visual) > float(vh) * 2.6:
        out.append(finding(
            "visual_arrives_late", "info", route, viewport,
            "The first visual appears more than 2.6 viewports below the top of the page.",
            {"firstVisualTop": first_visual, "viewportHeight": vh},
        ))
    if int(composition.get("stickyCount", 0)) > 2 and viewport == "mobile":
        out.append(finding(
            "many_sticky_elements", "info", route, viewport,
            "Several sticky/fixed elements are active on mobile; inspect for viewport crowding.",
            {"stickyCount": composition.get("stickyCount")},
        ))

    return out


def build_review(probe: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    screenshots = []
    for case in probe.get("results") or []:
        findings.extend(critique_case(case))
        case_shots = case.get("screenshots") or ([{"position": "mid", "path": case.get("screenshot")}] if case.get("screenshot") else [])
        for shot in case_shots:
            if shot.get("path"):
                screenshots.append({
                    "route": case.get("route"),
                    "viewport": case.get("viewport"),
                    "position": shot.get("position", "unknown"),
                    "path": shot.get("path"),
                })

    unique_penalties = {}
    for item in findings:
        unique_penalties[item["code"]] = max(unique_penalties.get(item["code"], 0), SEVERITY_WEIGHT.get(item["severity"], 0))
    penalty = sum(unique_penalties.values())
    score = max(0, 100 - penalty)
    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    status = "FAIL" if errors else ("REVIEW" if warnings else "PASS")
    auto_actions = sorted({item["auto_action"] for item in findings if item.get("auto_action")})

    return {
        "status": status,
        "score": score,
        "summary": {"errors": errors, "warnings": warnings, "info": len(findings) - errors - warnings},
        "findings": findings,
        "safe_auto_actions": auto_actions,
        "agent_review": {
            "status": "PENDING",
            "screenshots": screenshots,
            "instructions": [
                "Inspect every desktop/mobile screenshot; do not infer visual quality from the numeric score alone.",
                "Check hierarchy, pacing, whitespace, annotation collisions, chart legibility, first-screen effectiveness, and mobile composition.",
                "Record only observations visible in the screenshots. Distinguish aesthetic preference from a concrete usability problem.",
                "If proposing an automatic refinement, use only an allowlisted action; otherwise mark the change as manual.",
                "After any change, rebuild and rerun browser QA + visual probe; compare before/after evidence before accepting the iteration.",
            ],
            "schema": {
                "verdict": "pass | revise",
                "observations": [{
                    "route": "/generated",
                    "viewport": "mobile",
                    "severity": "info | warning | error",
                    "category": "hierarchy | spacing | density | chart | annotation | typography | mobile | other",
                    "note": "What is visibly wrong or notably strong",
                    "evidence": "Specific visible evidence from the screenshot",
                    "proposed_action": "tighten_copy_measure | increase_text_leading | increase_touch_targets | manual",
                }],
            },
        },
        "note": "The numeric score is a deterministic triage aid. Publication-quality art direction still requires screenshot inspection by an agent/editor.",
    }


def to_markdown(review: dict[str, Any]) -> str:
    lines = [
        "# Visual review",
        "",
        f"**Status:** {review['status']}  ",
        f"**Score:** {review['score']}/100  ",
        f"**Findings:** {review['summary']['errors']} errors · {review['summary']['warnings']} warnings · {review['summary']['info']} info",
        "",
    ]
    if review["findings"]:
        lines += ["## Deterministic findings", ""]
        for item in review["findings"]:
            lines.append(f"- **{item['severity'].upper()} · {item['code']} · {item['route']} {item['viewport']}** — {item['summary']}")
        lines.append("")
    else:
        lines += ["No deterministic visual findings at the configured thresholds.", ""]
    lines += [
        "## Agent screenshot review",
        "",
        "This step is still required even when the deterministic score is 100.",
        "",
    ]
    for shot in review["agent_review"]["screenshots"]:
        lines.append(f"- `{shot['route']}` · `{shot['viewport']}` → `{shot['path']}`")
    lines += ["", "## Safe auto-actions", ""]
    if review["safe_auto_actions"]:
        lines.extend(f"- `{action}`" for action in review["safe_auto_actions"])
    else:
        lines.append("- none proposed by deterministic checks")
    lines += ["", "_A passing mechanical review is not an aesthetic approval._", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("probe", type=Path, help="visual-probe.json")
    parser.add_argument("--output", type=Path, default=Path(".qa/visual-review.json"))
    parser.add_argument("--markdown", type=Path, default=Path(".qa/visual-review.md"))
    parser.add_argument("--fail-on", choices=["never", "error", "warning"], default="error")
    args = parser.parse_args()

    probe = json.loads(args.probe.read_text(encoding="utf-8"))
    review = build_review(probe)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(to_markdown(review), encoding="utf-8")
    print(f"Visual review: {review['status']} · {review['score']}/100 · {len(review['findings'])} findings")
    print(f"JSON: {args.output}")
    print(f"Markdown: {args.markdown}")

    if args.fail_on == "error" and review["summary"]["errors"]:
        return 1
    if args.fail_on == "warning" and (review["summary"]["errors"] or review["summary"]["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
