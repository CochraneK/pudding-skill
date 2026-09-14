from __future__ import annotations

import argparse
import csv
import json
import urllib.request
from pathlib import Path

WHO_GHO_BASE = "https://ghoapi.azureedge.net/api"
WHO_INDICATORS = {
    "MH_21": "total_mental_health_workforce_per_100k",
    "MH_6": "psychiatrists_per_100k",
    "MH_7": "mental_health_nurses_per_100k",
    "MH_9": "psychologists_per_100k",
}


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "pudding-skill/2.6 global-mental-health"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def normalize_gho_record(record: dict, metric: str) -> dict:
    value = record.get("NumericValue")
    if value is None:
        value = record.get("Value")
    return {
        "country_code": record.get("SpatialDim"),
        "year": record.get("TimeDim"),
        "metric": metric,
        "value": value,
        "low": record.get("Low"),
        "high": record.get("High"),
        "source": "WHO Global Health Observatory",
    }


def fetch_who_workforce(output: Path) -> None:
    rows: list[dict] = []
    for code, metric in WHO_INDICATORS.items():
        # Indicator endpoints already return JSON. Avoid filtering on optional OData fields
        # that differ across older mental-health indicator tables.
        payload = fetch_json(f"{WHO_GHO_BASE}/{code}?$top=10000")
        for record in payload.get("value", []):
            normalized = normalize_gho_record(record, metric)
            if normalized["country_code"] and normalized["value"] is not None:
                rows.append(normalized)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} WHO workforce rows to {output}")


def first_present(row: dict[str, str], names: tuple[str, ...]) -> str | None:
    lowered = {key.lower().strip(): value for key, value in row.items()}
    for name in names:
        if name in lowered and lowered[name] not in (None, ""):
            return lowered[name]
    return None


def import_ihme(input_path: Path, output: Path) -> None:
    """Normalize a user-supplied IHME/GBD CSV without redistributing the source data.

    The exporter has changed column labels across releases, so this importer accepts common
    country/year/value aliases while retaining the dimensions needed for later filtering.
    """
    with input_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    normalized: list[dict] = []
    for row in rows:
        country = first_present(row, ("location", "entity", "country", "location_name"))
        year = first_present(row, ("year", "year_id"))
        value = first_present(row, ("value", "val", "mean", "estimate"))
        measure = first_present(row, ("measure", "measure_name"))
        cause = first_present(row, ("cause", "cause_name", "rei"))
        metric = first_present(row, ("metric", "metric_name"))
        sex = first_present(row, ("sex", "sex_name"))
        age = first_present(row, ("age", "age_name"))

        if not country or not year or value is None:
            continue
        try:
            numeric_value = float(str(value).replace(",", ""))
        except ValueError:
            continue

        normalized.append(
            {
                "country": country,
                "year": int(float(year)),
                "value": numeric_value,
                "measure": measure,
                "cause": cause,
                "metric": metric,
                "sex": sex,
                "age": age,
                "source": "IHME Global Burden of Disease — user-supplied export",
            }
        )

    if not normalized:
        raise SystemExit("No usable IHME rows found. Expected country/location, year and numeric value columns.")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(normalized)} normalized IHME rows to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Data helpers for the global mental-health story")
    sub = parser.add_subparsers(dest="command", required=True)

    who = sub.add_parser("who", help="Fetch country-level WHO mental-health workforce indicators")
    who.add_argument("--output", type=Path, default=Path("generated/global-mental-health/who-workforce.json"))

    ihme = sub.add_parser("ihme-import", help="Normalize a local IHME/GBD CSV export")
    ihme.add_argument("input", type=Path)
    ihme.add_argument("--output", type=Path, default=Path("generated/global-mental-health/ihme-burden.json"))

    args = parser.parse_args()
    if args.command == "who":
        fetch_who_workforce(args.output)
    elif args.command == "ihme-import":
        import_ihme(args.input, args.output)


if __name__ == "__main__":
    main()
