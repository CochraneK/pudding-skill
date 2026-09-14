#!/usr/bin/env python3
"""Research dossier contract and compiler for evidence-first industry/domain research.

The agent does the browsing/retrieval. This module makes the resulting research auditable:
source provenance, numeric evidence, conflicts, acquisition plans, and story handoff.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SOURCE_TIERS = {"T0", "T1", "T2", "T3", "T4"}
SOURCE_TYPES = {
    "standard",
    "official_dataset",
    "official_report",
    "peer_reviewed",
    "systematic_review",
    "white_paper",
    "manual",
    "guideline",
    "industry_report",
    "secondary_analysis",
    "journalism",
    "other",
}
CLAIM_STATUSES = {"VERIFIED", "QUALIFIED", "CONFLICT", "LEAD_ONLY", "REJECTED"}
CONFIDENCE = {"high", "medium", "low"}
ACCESS_MODES = {"direct_download", "api", "query_tool", "request", "manual_extract", "not_available", "unknown"}

SOURCE_STRATEGY = [
    {
        "tier": "T0",
        "label": "Definitions and standards",
        "targets": ["classification standards", "technical manuals", "indicator definitions", "methodology documents"],
        "purpose": "Fix definitions, denominators, units, and comparability before extracting numbers.",
    },
    {
        "tier": "T1",
        "label": "Primary evidence",
        "targets": ["official datasets", "official statistical releases", "peer-reviewed primary studies", "systematic reviews"],
        "purpose": "Preferred source for publishable quantitative claims and downloadable data.",
    },
    {
        "tier": "T2",
        "label": "Authoritative synthesis",
        "targets": ["government/IGO reports", "major white papers", "professional guidelines"],
        "purpose": "Context, synthesis, and numbers when primary tables are clearly attributed.",
    },
    {
        "tier": "T3",
        "label": "Industry evidence",
        "targets": ["industry reports", "trade associations", "vendor research with disclosed methods"],
        "purpose": "Market structure and operational detail; treat incentives and methodology as explicit caveats.",
    },
    {
        "tier": "T4",
        "label": "Discovery only",
        "targets": ["journalism", "blogs", "aggregators", "search snippets"],
        "purpose": "Find leads. Do not use as the final source for a material numeric claim when a primary source exists.",
    },
]


@dataclass
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def scaffold(question: str, topic: str, audience: str = "general audience") -> dict[str, Any]:
    return {
        "version": 1,
        "status": "RESEARCH_REQUIRED",
        "topic": topic,
        "question": question,
        "audience": audience,
        "research_scope": {
            "geographies": [],
            "period": None,
            "population": None,
            "dimensions": [],
            "exclusions": [],
        },
        "source_strategy": SOURCE_STRATEGY,
        "sources": [],
        "claims": [],
        "conflicts": [],
        "data_targets": [],
        "recommendations": [],
        "story_handoff": {
            "candidate_questions": [],
            "recommended_question": question,
            "usable_claim_ids": [],
            "preferred_dataset_targets": [],
            "caveats": [],
        },
    }


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def validate_dossier(dossier: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    for key in ("topic", "question", "sources", "claims", "data_targets"):
        if key not in dossier:
            errors.append(f"missing top-level field: {key}")

    sources = dossier.get("sources") or []
    claims = dossier.get("claims") or []
    targets = dossier.get("data_targets") or []

    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        sid = _text(source.get("id"))
        prefix = f"sources[{index}]"
        if not sid:
            errors.append(f"{prefix}: id is required")
            continue
        if sid in source_ids:
            errors.append(f"{prefix}: duplicate source id {sid}")
        source_ids.add(sid)
        tier = _text(source.get("tier"))
        if tier not in SOURCE_TIERS:
            errors.append(f"{prefix}: tier must be one of {sorted(SOURCE_TIERS)}")
        source_type = _text(source.get("type"))
        if source_type not in SOURCE_TYPES:
            errors.append(f"{prefix}: type must be one of {sorted(SOURCE_TYPES)}")
        if not _text(source.get("title")):
            errors.append(f"{prefix}: title is required")
        if not _text(source.get("url")):
            errors.append(f"{prefix}: url is required")
        if tier in {"T0", "T1", "T2"} and not _text(source.get("publisher")):
            warnings.append(f"{prefix}: authoritative source should record publisher")
        if not _text(source.get("retrieved_at")):
            warnings.append(f"{prefix}: retrieved_at is recommended for reproducibility")

    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        cid = _text(claim.get("id"))
        prefix = f"claims[{index}]"
        if not cid:
            errors.append(f"{prefix}: id is required")
            continue
        if cid in claim_ids:
            errors.append(f"{prefix}: duplicate claim id {cid}")
        claim_ids.add(cid)
        status = _text(claim.get("status"))
        if status not in CLAIM_STATUSES:
            errors.append(f"{prefix}: status must be one of {sorted(CLAIM_STATUSES)}")
        confidence = _text(claim.get("confidence"))
        if confidence not in CONFIDENCE:
            errors.append(f"{prefix}: confidence must be one of {sorted(CONFIDENCE)}")
        if not _text(claim.get("statement")):
            errors.append(f"{prefix}: statement is required")
        refs = claim.get("source_ids") or []
        if not refs:
            errors.append(f"{prefix}: at least one source_id is required")
        for source_id in refs:
            if source_id not in source_ids:
                errors.append(f"{prefix}: unknown source_id {source_id}")
        if claim.get("kind") == "numeric":
            if claim.get("value") is None:
                errors.append(f"{prefix}: numeric claim requires value")
            for field in ("unit", "geography", "period", "population"):
                if not _text(claim.get(field)):
                    errors.append(f"{prefix}: numeric claim requires {field}")
            if not _text(claim.get("locator")):
                warnings.append(f"{prefix}: locator (page/table/figure/query) is strongly recommended")
            if status in {"VERIFIED", "QUALIFIED"} and confidence == "low":
                warnings.append(f"{prefix}: publishable numeric claim has low confidence")
        if status == "VERIFIED" and not _text(claim.get("verification_note")):
            warnings.append(f"{prefix}: VERIFIED claim should explain how it was checked")

    target_ids: set[str] = set()
    for index, target in enumerate(targets):
        prefix = f"data_targets[{index}]"
        tid = _text(target.get("id"))
        if not tid:
            errors.append(f"{prefix}: id is required")
            continue
        if tid in target_ids:
            errors.append(f"{prefix}: duplicate target id {tid}")
        target_ids.add(tid)
        if not _text(target.get("dataset")):
            errors.append(f"{prefix}: dataset is required")
        mode = _text(target.get("access_mode"))
        if mode not in ACCESS_MODES:
            errors.append(f"{prefix}: access_mode must be one of {sorted(ACCESS_MODES)}")
        if not _text(target.get("next_action")):
            errors.append(f"{prefix}: next_action is required")

    conflicts = dossier.get("conflicts") or []
    for index, conflict in enumerate(conflicts):
        refs = conflict.get("claim_ids") or []
        for claim_id in refs:
            if claim_id not in claim_ids:
                errors.append(f"conflicts[{index}]: unknown claim_id {claim_id}")
        if len(refs) < 2:
            warnings.append(f"conflicts[{index}]: conflict should normally reference at least two claims")

    return ValidationResult(errors=errors, warnings=warnings)


def _source_index(dossier: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(source["id"]): source for source in dossier.get("sources") or [] if source.get("id")}


def publishable_claims(dossier: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        claim
        for claim in (dossier.get("claims") or [])
        if claim.get("kind") == "numeric" and claim.get("status") in {"VERIFIED", "QUALIFIED"}
    ]


def write_numeric_csv(dossier: dict[str, Any], output: Path) -> None:
    sources = _source_index(dossier)
    fields = [
        "claim_id",
        "statement",
        "value",
        "unit",
        "geography",
        "period",
        "population",
        "lower",
        "upper",
        "status",
        "confidence",
        "source_ids",
        "source_titles",
        "locator",
        "definition",
        "method_note",
        "license_note",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for claim in publishable_claims(dossier):
            refs = [str(item) for item in claim.get("source_ids") or []]
            writer.writerow(
                {
                    "claim_id": claim.get("id"),
                    "statement": claim.get("statement"),
                    "value": claim.get("value"),
                    "unit": claim.get("unit"),
                    "geography": claim.get("geography"),
                    "period": claim.get("period"),
                    "population": claim.get("population"),
                    "lower": claim.get("lower"),
                    "upper": claim.get("upper"),
                    "status": claim.get("status"),
                    "confidence": claim.get("confidence"),
                    "source_ids": ";".join(refs),
                    "source_titles": ";".join(_text(sources.get(ref, {}).get("title")) for ref in refs),
                    "locator": claim.get("locator"),
                    "definition": claim.get("definition"),
                    "method_note": claim.get("method_note"),
                    "license_note": claim.get("license_note"),
                }
            )


def write_report(dossier: dict[str, Any], output: Path) -> None:
    claims = publishable_claims(dossier)
    conflicts = dossier.get("conflicts") or []
    recommendations = dossier.get("recommendations") or []
    handoff = dossier.get("story_handoff") or {}
    lines = [
        f"# Research dossier — {_text(dossier.get('topic'))}",
        "",
        f"**Question:** {_text(dossier.get('question'))}",
        f"**Audience:** {_text(dossier.get('audience'))}",
        f"**Status:** {_text(dossier.get('status'))}",
        "",
        "## Executive answer",
        "",
        _text(dossier.get("executive_answer")) or "EDITORIAL_REVIEW_REQUIRED — add a concise synthesis after reviewing the evidence ledger.",
        "",
        "## Verified / qualified numeric evidence",
        "",
    ]
    if claims:
        lines += ["| Claim | Value | Scope | Confidence | Sources |", "|---|---:|---|---|---|"]
        for claim in claims:
            value = f"{claim.get('value')} {claim.get('unit', '')}".strip()
            scope = " · ".join(filter(None, [_text(claim.get("geography")), _text(claim.get("period")), _text(claim.get("population"))]))
            source_ids = ", ".join(str(item) for item in claim.get("source_ids") or [])
            lines.append(f"| {claim.get('statement')} | {value} | {scope} | {claim.get('confidence')} | {source_ids} |")
    else:
        lines.append("No publishable numeric claims yet.")

    lines += ["", "## Conflicts and non-comparable figures", ""]
    if conflicts:
        for conflict in conflicts:
            lines.append(f"- **{_text(conflict.get('issue'))}** — claims: {', '.join(conflict.get('claim_ids') or [])}. {_text(conflict.get('resolution'))}")
    else:
        lines.append("No recorded conflicts.")

    lines += ["", "## Recommendations", ""]
    if recommendations:
        for item in recommendations:
            if isinstance(item, dict):
                lines.append(f"- **{_text(item.get('action'))}** — {_text(item.get('why'))}")
            else:
                lines.append(f"- {_text(item)}")
    else:
        lines.append("No recommendations recorded yet.")

    lines += ["", "## Story handoff", ""]
    lines.append(f"Recommended question: {_text(handoff.get('recommended_question')) or _text(dossier.get('question'))}")
    usable = handoff.get("usable_claim_ids") or [claim.get("id") for claim in claims]
    lines.append(f"Usable claim IDs: {', '.join(str(item) for item in usable if item)}")
    caveats = handoff.get("caveats") or []
    if caveats:
        lines.append("")
        lines.append("Caveats:")
        lines.extend(f"- {_text(item)}" for item in caveats)

    lines += ["", "## Research boundary", "", "This dossier is an evidence and acquisition instrument, not an oracle. Material claims still require editorial/domain review, and a secondary source should not replace an accessible primary source for a key number."]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_acquisition_plan(dossier: dict[str, Any], output: Path) -> None:
    lines = [
        f"# Data acquisition plan — {_text(dossier.get('topic'))}",
        "",
        "Prioritize reproducible primary data. Record query parameters, export filters, access constraints, and redistribution terms.",
        "",
    ]
    targets = dossier.get("data_targets") or []
    if not targets:
        lines.append("No data targets recorded yet.")
    for target in targets:
        lines += [
            f"## {_text(target.get('dataset'))}",
            "",
            f"- ID: `{_text(target.get('id'))}`",
            f"- Purpose: {_text(target.get('purpose'))}",
            f"- Preferred source: {_text(target.get('preferred_source'))}",
            f"- Access mode: `{_text(target.get('access_mode'))}`",
            f"- License / redistribution: {_text(target.get('license_note')) or 'REVIEW_REQUIRED'}",
            f"- Query / filters: {_text(target.get('query_spec')) or 'TO_DEFINE'}",
            f"- Next action: {_text(target.get('next_action'))}",
            "",
        ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compile_dossier(dossier: dict[str, Any], outdir: Path) -> ValidationResult:
    result = validate_dossier(dossier)
    if not result.ok:
        return result
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "source-ledger.json").write_text(
        json.dumps(dossier.get("sources") or [], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_numeric_csv(dossier, outdir / "numeric-evidence.csv")
    write_report(dossier, outdir / "research-report.md")
    write_acquisition_plan(dossier, outdir / "data-acquisition-plan.md")
    (outdir / "research-dossier.json").write_text(json.dumps(dossier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_init(args: argparse.Namespace) -> int:
    dossier = scaffold(args.question, args.topic, args.audience)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dossier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote research dossier scaffold to {args.output}")
    return 0


def _print_validation(result: ValidationResult) -> None:
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")


def cmd_validate(args: argparse.Namespace) -> int:
    result = validate_dossier(load(args.dossier))
    _print_validation(result)
    if result.ok:
        print("Research dossier validation PASS")
        return 0
    return 1


def cmd_compile(args: argparse.Namespace) -> int:
    result = compile_dossier(load(args.dossier), args.outdir)
    _print_validation(result)
    if result.ok:
        print(f"Research dossier compiled to {args.outdir}")
        return 0
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and validate an auditable research dossier")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a research dossier scaffold for an agent to populate")
    init.add_argument("--question", required=True)
    init.add_argument("--topic", required=True)
    init.add_argument("--audience", default="general audience")
    init.add_argument("--output", type=Path, default=Path("generated/research/research-dossier.json"))
    init.set_defaults(func=cmd_init)

    validate = sub.add_parser("validate", help="validate a populated research dossier")
    validate.add_argument("dossier", type=Path)
    validate.set_defaults(func=cmd_validate)

    compile_cmd = sub.add_parser("compile", help="compile a populated dossier into research artifacts")
    compile_cmd.add_argument("dossier", type=Path)
    compile_cmd.add_argument("--outdir", type=Path, default=Path("generated/research"))
    compile_cmd.set_defaults(func=cmd_compile)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
