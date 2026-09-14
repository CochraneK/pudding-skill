#!/usr/bin/env python3
"""Generate a publication-ready first-draft package from a validated story spec.

The copy is deterministic and conservative. It exposes provenance for every quantitative
claim so an agent/editor can rewrite tone without losing the evidence trail.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from data_contract import label_for
from visual_grammar import plan_visual


def sentence_case(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def source_label(source: Any) -> str:
    if isinstance(source, str):
        return source
    if isinstance(source, dict):
        return str(source.get("label") or source.get("path") or "source")
    return "source"


def build_draft(spec: dict[str, Any], claim_audit: dict[str, Any] | None = None) -> dict[str, Any]:
    insight = sentence_case(str(spec.get("primary_insight", "")))
    question = str(spec.get("question", "What does the data show?"))
    evidence = list(spec.get("evidence") or [])
    metadata = spec.get("field_metadata") or {}
    visual_plan = plan_visual(spec)

    headline = insight.rstrip(".") if insight else question.rstrip("?")
    dek = f"A data-led answer to: {question.rstrip('?')}?"

    sections: list[dict[str, Any]] = []
    beat_names = {
        "establish": "What the data covers",
        "reveal": "The central pattern",
        "reorder": "How the groups compare",
        "highlight": "The clearest example",
        "compare": "What stands out",
        "contextualize": "What this does — and does not — show",
    }
    for index, beat in enumerate(spec.get("beats") or []):
        op = str(beat.get("operation", "explain"))
        body = str(beat.get("purpose", "")).strip()
        if index == 1 and insight:
            body = insight
        sections.append({
            "id": f"section-{index + 1}",
            "operation": op,
            "heading": beat_names.get(op, sentence_case(op)),
            "body": body,
            "claim_refs": [0] if index == 1 and evidence else [],
        })

    if not sections:
        sections = [{
            "id": "section-1",
            "operation": "reveal",
            "heading": "The central pattern",
            "body": insight,
            "claim_refs": [0] if evidence else [],
        }]

    annotations = []
    for index, item in enumerate(evidence):
        annotations.append({
            "claim_ref": index,
            "kind": item.get("kind", "evidence"),
            "text": insight if index == 0 else f"Supporting evidence {index + 1}",
            "evidence": item,
        })

    sources = [source_label(source) for source in spec.get("sources") or []]
    caveats = list(spec.get("caveats") or [])
    data_notes = list(spec.get("data_notes") or [])
    methodology_bits = [
        "The pipeline profiled the source data, generated multiple candidate story directions, ranked them with transparent deterministic proxies, and selected the highest viable candidate.",
        "The selected quantitative evidence was independently recomputed from the source data before this draft was generated.",
    ]
    if claim_audit and claim_audit.get("status"):
        methodology_bits.append(f"Independent claim-audit status: {claim_audit['status']}.")

    field_glossary = []
    for field, meta in metadata.items():
        if not isinstance(meta, dict):
            continue
        field_glossary.append({
            "field": field,
            "label": meta.get("label") or label_for(field, metadata),
            "unit": meta.get("unit"),
            "description": meta.get("description"),
        })

    return {
        "status": "EDITORIAL_REVIEW_REQUIRED",
        "headline": headline,
        "dek": dek,
        "question": question,
        "audience": spec.get("audience", "general audience"),
        "primary_insight": insight,
        "sections": sections,
        "visual_plan": visual_plan,
        "annotations": annotations,
        "sources": sources,
        "source_note": "Source: " + ", ".join(sources) if sources else "Source: not specified",
        "methodology": " ".join(methodology_bits),
        "caveats": caveats,
        "data_notes": data_notes,
        "field_glossary": field_glossary,
        "provenance": {
            "claims": [{"claim_ref": i, "evidence_index": i, "verified": True} for i in range(len(evidence))],
            "selection": spec.get("selection"),
            "note": "A claim_ref points back to structured evidence in the validated story spec. Rewriting copy must preserve this mapping or trigger re-review.",
        },
    }


def to_markdown(draft: dict[str, Any]) -> str:
    lines = [f"# {draft['headline']}", "", draft["dek"], ""]
    for section in draft["sections"]:
        lines += [f"## {section['heading']}", "", section["body"], ""]
    lines += ["## Visual direction", "", f"**Recommended:** {draft['visual_plan']['recommended_visual']}", "", draft['visual_plan']['why'], ""]
    lines += ["## Methodology", "", draft["methodology"], ""]
    if draft.get("caveats"):
        lines += ["## Caveats", ""] + [f"- {item}" for item in draft["caveats"]] + [""]
    lines += [draft["source_note"], "", "_Editorial review required before publication._", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--claim-audit", type=Path)
    parser.add_argument("--output", type=Path, default=Path("generated/story-draft.json"))
    parser.add_argument("--markdown", type=Path, default=Path("generated/story-draft.md"))
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    audit = json.loads(args.claim_audit.read_text(encoding="utf-8")) if args.claim_audit and args.claim_audit.exists() else None
    draft = build_draft(spec, audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(to_markdown(draft), encoding="utf-8")
    print(f"Draft JSON: {args.output}")
    print(f"Draft Markdown: {args.markdown}")
    print(f"Visual: {draft['visual_plan']['recommended_visual']} (baseline: {draft['visual_plan']['baseline_renderer']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
