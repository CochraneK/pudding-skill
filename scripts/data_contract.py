#!/usr/bin/env python3
"""Load and validate optional field semantics for the editorial pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_ROLES = {"time", "category", "measure", "identifier", "ignore"}


def validate_contract(contract: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(contract, dict):
        return ["Data contract must be a JSON object."]
    fields = contract.get("fields")
    if not isinstance(fields, dict) or not fields:
        return ["Data contract must contain a non-empty 'fields' object."]
    for name, meta in fields.items():
        if not isinstance(name, str) or not name.strip():
            errors.append("Field names must be non-empty strings.")
            continue
        if not isinstance(meta, dict):
            errors.append(f"fields.{name} must be an object.")
            continue
        role = meta.get("role")
        if role is not None and role not in ALLOWED_ROLES:
            errors.append(f"fields.{name}.role must be one of: {', '.join(sorted(ALLOWED_ROLES))}.")
        for key in ("label", "unit", "description"):
            value = meta.get(key)
            if value is not None and not isinstance(value, str):
                errors.append(f"fields.{name}.{key} must be a string when present.")
    notes = contract.get("notes")
    if notes is not None and not isinstance(notes, list):
        errors.append("notes must be a list when present.")
    return errors


def load_contract(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"fields": {}, "notes": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_contract(data)
    if errors:
        raise ValueError("Invalid data contract:\n- " + "\n- ".join(errors))
    return data


def label_for(contract: dict[str, Any], field: str) -> str:
    meta = contract.get("fields", {}).get(field, {})
    return str(meta.get("label") or field.replace("_", " "))


def field_meta(contract: dict[str, Any], field: str) -> dict[str, Any]:
    meta = contract.get("fields", {}).get(field, {})
    return {key: meta[key] for key in ("role", "label", "unit", "description") if key in meta}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        contract = json.loads(args.path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    errors = validate_contract(contract)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {len(contract['fields'])} field definitions are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
