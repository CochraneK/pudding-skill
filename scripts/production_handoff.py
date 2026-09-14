#!/usr/bin/env python3
"""Compile and validate a machine-readable production handoff from a prototype tournament.

The tournament decides *which editorial job won*. This module prevents production from
silently drifting back to a losing interaction pattern after the prototype phase.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_CONTRACT_FIELDS = {
    "route",
    "primary_form",
    "primary_interaction_job",
    "required_sequence",
    "required_claims",
    "borrowed_lessons",
    "optional_depth",
    "forbidden_primary_interaction_jobs",
    "forbidden_source_tokens",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def tournament_fingerprint(tournament: dict[str, Any]) -> str:
    decision = tournament.get("decision") if isinstance(tournament.get("decision"), dict) else {}
    payload = {
        "story_id": tournament.get("story_id"),
        "outcome": decision.get("outcome"),
        "winner_concept_ids": decision.get("winner_concept_ids"),
        "production_contract": decision.get("production_contract"),
    }
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _prototype_by_id(tournament: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = tournament.get("prototypes") if isinstance(tournament.get("prototypes"), list) else []
    return {
        row.get("concept_id"): row
        for row in rows
        if isinstance(row, dict) and _text(row.get("concept_id"))
    }


def validate_tournament_contract(tournament: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    decision = tournament.get("decision")
    if not isinstance(decision, dict):
        return ["tournament.decision must be an object"]

    outcome = _text(decision.get("outcome"))
    if outcome not in {"SELECT", "COMBINE"}:
        errors.append("production handoff requires a SELECT or COMBINE tournament outcome")
        return errors

    winners = decision.get("winner_concept_ids")
    if not isinstance(winners, list) or not winners or any(not _text(item) for item in winners):
        errors.append("decision.winner_concept_ids must name at least one selected concept")
        winners = []

    contract = decision.get("production_contract")
    if not isinstance(contract, dict):
        errors.append("decision.production_contract must be an object")
        return errors

    missing_fields = sorted(REQUIRED_CONTRACT_FIELDS - set(contract))
    if missing_fields:
        errors.append(f"production_contract missing fields: {', '.join(missing_fields)}")

    prototypes = _prototype_by_id(tournament)
    for winner in winners:
        if winner not in prototypes:
            errors.append(f"winner {winner} is not present in tournament prototypes")

    if len(winners) == 1 and winners:
        winner = prototypes.get(winners[0], {})
        if _text(contract.get("primary_form")) != _text(winner.get("form")):
            errors.append("production_contract.primary_form must match the selected prototype form")
        if _text(contract.get("primary_interaction_job")) != _text(winner.get("interaction_job")):
            errors.append("production_contract.primary_interaction_job must match the selected prototype interaction job")

    if not _text(contract.get("route")) or not str(contract.get("route", "")).startswith("/"):
        errors.append("production_contract.route must be a site-relative route")

    sequence = contract.get("required_sequence")
    if not isinstance(sequence, list) or len(sequence) < 2 or any(not _text(item) for item in sequence):
        errors.append("production_contract.required_sequence needs at least two non-empty beat ids")

    claims = contract.get("required_claims")
    if not isinstance(claims, list) or not claims:
        errors.append("production_contract.required_claims must contain at least one claim")
    else:
        claim_ids: set[str] = set()
        for index, claim in enumerate(claims):
            label = f"required_claims[{index}]"
            if not isinstance(claim, dict):
                errors.append(f"{label} must be an object")
                continue
            cid = _text(claim.get("id"))
            tokens = claim.get("tokens")
            if not cid:
                errors.append(f"{label}.id is empty")
            elif cid in claim_ids:
                errors.append(f"duplicate required claim id: {cid}")
            claim_ids.add(cid)
            if not isinstance(tokens, list) or not tokens or any(not _text(token) for token in tokens):
                errors.append(f"{label}.tokens must contain visible evidence tokens")

    borrowed = contract.get("borrowed_lessons")
    if not isinstance(borrowed, list):
        errors.append("production_contract.borrowed_lessons must be a list")
    else:
        for index, item in enumerate(borrowed):
            if not isinstance(item, dict):
                errors.append(f"borrowed_lessons[{index}] must be an object")
                continue
            source_id = _text(item.get("from_concept_id"))
            if source_id not in prototypes:
                errors.append(f"borrowed lesson source {source_id or '(empty)'} is not a tournament concept")
            if source_id in winners:
                errors.append(f"borrowed lesson source {source_id} cannot also be a selected winner")
            if not _text(item.get("keep")) or not _text(item.get("reject_interaction_job")):
                errors.append(f"borrowed_lessons[{index}] must state keep and reject_interaction_job")

    optional = contract.get("optional_depth")
    if not isinstance(optional, list):
        errors.append("production_contract.optional_depth must be a list")
    else:
        for index, item in enumerate(optional):
            if not isinstance(item, dict):
                errors.append(f"optional_depth[{index}] must be an object")
                continue
            source_id = _text(item.get("from_concept_id"))
            if source_id not in prototypes:
                errors.append(f"optional depth source {source_id or '(empty)'} is not a tournament concept")
            if source_id in winners:
                errors.append(f"optional depth source {source_id} cannot also be a selected winner")
            if not _text(item.get("route")):
                errors.append(f"optional_depth[{index}].route is empty")

    forbidden_jobs = contract.get("forbidden_primary_interaction_jobs")
    if not isinstance(forbidden_jobs, list) or any(not _text(item) for item in forbidden_jobs):
        errors.append("production_contract.forbidden_primary_interaction_jobs must be a list of non-empty strings")
    elif _text(contract.get("primary_interaction_job")) in forbidden_jobs:
        errors.append("selected primary_interaction_job cannot also be forbidden")

    forbidden_tokens = contract.get("forbidden_source_tokens")
    if not isinstance(forbidden_tokens, list) or any(not _text(item) for item in forbidden_tokens):
        errors.append("production_contract.forbidden_source_tokens must be a list of non-empty strings")

    return errors


def compile_contract(tournament: dict[str, Any]) -> dict[str, Any]:
    errors = validate_tournament_contract(tournament)
    if errors:
        raise ValueError("; ".join(errors))

    decision = tournament["decision"]
    contract = decision["production_contract"]
    prototypes = _prototype_by_id(tournament)
    winners = decision["winner_concept_ids"]
    selected = [prototypes[item] for item in winners]

    return {
        "schema_version": 1,
        "status": "PRODUCTION_CONTRACT",
        "story_id": tournament.get("story_id"),
        "tournament_fingerprint": tournament_fingerprint(tournament),
        "decision": {
            "outcome": decision.get("outcome"),
            "winner_concept_ids": winners,
            "selected_forms": [row.get("form") for row in selected],
            "selected_interaction_jobs": [row.get("interaction_job") for row in selected],
        },
        "route": contract["route"],
        "primary_form": contract["primary_form"],
        "primary_interaction_job": contract["primary_interaction_job"],
        "required_sequence": contract["required_sequence"],
        "required_claims": contract["required_claims"],
        "borrowed_lessons": contract["borrowed_lessons"],
        "optional_depth": contract["optional_depth"],
        "forbidden_primary_interaction_jobs": contract["forbidden_primary_interaction_jobs"],
        "forbidden_source_tokens": contract["forbidden_source_tokens"],
    }


def validate_source(contract: dict[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    winners = contract.get("decision", {}).get("winner_concept_ids", [])
    for winner in winners:
        marker = f'data-production-winner="{winner}"'
        if marker not in source:
            errors.append(f"production source missing winner marker {marker}")

    interaction = _text(contract.get("primary_interaction_job"))
    marker = f'data-primary-interaction="{interaction}"'
    if marker not in source:
        errors.append(f"production source missing interaction marker {marker}")

    for beat in contract.get("required_sequence", []):
        marker = f'data-story-beat="{beat}"'
        if marker not in source:
            errors.append(f"production source missing required beat marker {marker}")

    for claim in contract.get("required_claims", []):
        cid = claim.get("id")
        marker = f'data-claim-id="{cid}"'
        if marker not in source:
            errors.append(f"production source missing claim marker {marker}")
        for token in claim.get("tokens", []):
            if str(token) not in source:
                errors.append(f"production source missing visible evidence token {token!r} for claim {cid}")

    for item in contract.get("borrowed_lessons", []):
        source_id = item.get("from_concept_id")
        marker = f'data-borrowed-from="{source_id}"'
        if marker not in source:
            errors.append(f"production source missing borrowed-lesson marker {marker}")

    for item in contract.get("optional_depth", []):
        source_id = item.get("from_concept_id")
        marker = f'data-optional-depth="{source_id}"'
        if marker not in source:
            errors.append(f"production source missing optional-depth marker {marker}")
        route = _text(item.get("route"))
        if route and route.strip("/") not in source:
            errors.append(f"production source does not expose optional-depth route {route}")

    for token in contract.get("forbidden_source_tokens", []):
        if str(token) in source:
            errors.append(f"production source contains forbidden token {token!r}")

    return errors


def validate(
    tournament: dict[str, Any],
    committed_contract: dict[str, Any],
    source_path: Path | None = None,
) -> dict[str, Any]:
    errors = validate_tournament_contract(tournament)
    expected: dict[str, Any] | None = None
    if not errors:
        expected = compile_contract(tournament)
        if committed_contract != expected:
            errors.append("committed production contract is stale or does not match the tournament decision")

    if expected is not None and source_path is not None:
        if not source_path.is_file():
            errors.append(f"production source not found: {source_path}")
        else:
            errors.extend(validate_source(expected, source_path.read_text(encoding="utf-8")))

    return {
        "status": "PRODUCTION_ALIGNED" if not errors else "REVISE",
        "errors": errors,
        "tournament_fingerprint": tournament_fingerprint(tournament),
        "winner_concept_ids": (
            tournament.get("decision", {}).get("winner_concept_ids", [])
            if isinstance(tournament.get("decision"), dict)
            else []
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile/validate a production handoff from a prototype tournament")
    sub = parser.add_subparsers(dest="command", required=True)

    compile_parser = sub.add_parser("compile")
    compile_parser.add_argument("tournament", type=Path)
    compile_parser.add_argument("--output", type=Path, required=True)

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("tournament", type=Path)
    validate_parser.add_argument("contract", type=Path)
    validate_parser.add_argument("--source", type=Path)
    validate_parser.add_argument("--output", type=Path, default=Path(".qa/production-handoff-review.json"))

    args = parser.parse_args()
    tournament = _load(args.tournament)

    if args.command == "compile":
        try:
            result = compile_contract(tournament)
        except ValueError as error:
            print(f"Production handoff: REVISE · {error}")
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Production handoff: COMPILED → {args.output}")
        return 0

    committed = _load(args.contract)
    report = validate(tournament, committed, args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Production handoff: {report['status']} · {len(report['winner_concept_ids'])} winner(s)")
    for error in report["errors"]:
        print(f"- ERROR: {error}")
    return 0 if report["status"] == "PRODUCTION_ALIGNED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
