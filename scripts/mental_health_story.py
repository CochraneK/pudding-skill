from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

WHO_GHO_BASE = "https://ghoapi.azureedge.net/api"
WHO_COUNTRY_DIMENSION = f"{WHO_GHO_BASE}/Dimension/COUNTRY/DimensionValues"

WHO_CAPACITY_INDICATORS: dict[str, dict[str, str]] = {
    "MH_21": {
        "metric": "total_mental_health_workforce_per_100k",
        "label": "Total mental-health workforce",
        "unit": "per 100,000",
    },
    "MH_6": {
        "metric": "psychiatrists_per_100k",
        "label": "Psychiatrists",
        "unit": "per 100,000",
    },
    "MH_7": {
        "metric": "mental_health_nurses_per_100k",
        "label": "Mental-health nurses",
        "unit": "per 100,000",
    },
    "MH_9": {
        "metric": "psychologists_per_100k",
        "label": "Psychologists",
        "unit": "per 100,000",
    },
    "MH_4": {
        "metric": "government_mental_health_spending_share",
        "label": "Government mental-health spending share",
        "unit": "% of government health expenditure",
    },
    "MH_10": {
        "metric": "mental_health_outpatient_facilities_per_100k",
        "label": "Mental-health outpatient facilities",
        "unit": "per 100,000",
    },
}

WHO_NEED_PROXY_INDICATORS: dict[str, dict[str, str]] = {
    "GDO_q35": {
        "metric": "depression_prevalence_2015",
        "label": "Depression prevalence estimate",
        "unit": "% of population",
    }
}

# Backward-compatible subset used by the original helper/tests.
WHO_INDICATORS = {
    code: meta["metric"]
    for code, meta in WHO_CAPACITY_INDICATORS.items()
    if code in {"MH_21", "MH_6", "MH_7", "MH_9"}
}


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "pudding-skill global-mental-health"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def fetch_odata_rows(url: str) -> list[dict[str, Any]]:
    """Fetch an OData collection, following continuation links when present."""
    rows: list[dict[str, Any]] = []
    next_url: str | None = url
    seen: set[str] = set()
    while next_url:
        if next_url in seen:
            raise RuntimeError(f"WHO OData pagination loop detected at {next_url}")
        seen.add(next_url)
        payload = fetch_json(next_url)
        rows.extend(payload.get("value", []))
        next_url = payload.get("@odata.nextLink") or payload.get("odata.nextLink")
    return rows


def _numeric(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        result = float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def normalize_gho_record(record: dict, metric: str) -> dict:
    value = _numeric(record.get("NumericValue"))
    if value is None:
        value = _numeric(record.get("Value"))
    year = record.get("TimeDim")
    try:
        year = int(year) if year is not None else None
    except (TypeError, ValueError):
        year = None
    return {
        "country_code": record.get("SpatialDim"),
        "year": year,
        "metric": metric,
        "value": value,
        "low": _numeric(record.get("Low")),
        "high": _numeric(record.get("High")),
        "region_code": record.get("ParentLocationCode"),
        "region": record.get("ParentLocation"),
        "indicator_code": record.get("IndicatorCode"),
        "source": "WHO Global Health Observatory",
    }


def latest_by_country(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Return the latest non-missing observation per country without imputing gaps."""
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        code = row.get("country_code")
        value = row.get("value")
        year = row.get("year")
        if not code or value is None or year is None:
            continue
        previous = latest.get(str(code))
        if previous is None or int(year) > int(previous["year"]):
            latest[str(code)] = row
    return latest


def _quantile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    fraction = pos - lo
    return ordered[lo] * (1 - fraction) + ordered[hi] * fraction


def _round(value: float | None, digits: int = 3) -> float | None:
    return None if value is None else round(float(value), digits)


def _metric_summary(countries: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    observations = [
        country["metrics"][metric]
        for country in countries
        if metric in country.get("metrics", {}) and country["metrics"][metric].get("value") is not None
    ]
    values = [float(item["value"]) for item in observations]
    years = [int(item["year"]) for item in observations if item.get("year") is not None]
    return {
        "n": len(values),
        "median": _round(statistics.median(values) if values else None),
        "q25": _round(_quantile(values, 0.25)),
        "q75": _round(_quantile(values, 0.75)),
        "min": _round(min(values) if values else None),
        "max": _round(max(values) if values else None),
        "year_min": min(years) if years else None,
        "year_max": max(years) if years else None,
        "year_median": int(round(statistics.median(years))) if years else None,
    }


def _region_summaries(countries: list[dict[str, Any]], metrics: list[str]) -> list[dict[str, Any]]:
    by_region: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for country in countries:
        region_code = country.get("region_code") or "UNK"
        region = country.get("region") or "Unknown"
        by_region[(region_code, region)].append(country)

    rows: list[dict[str, Any]] = []
    for (region_code, region), members in sorted(by_region.items(), key=lambda item: item[0][1]):
        metric_rows: dict[str, dict[str, Any]] = {}
        for metric in metrics:
            values = [
                float(member["metrics"][metric]["value"])
                for member in members
                if metric in member.get("metrics", {}) and member["metrics"][metric].get("value") is not None
            ]
            years = [
                int(member["metrics"][metric]["year"])
                for member in members
                if metric in member.get("metrics", {}) and member["metrics"][metric].get("year") is not None
            ]
            metric_rows[metric] = {
                "n": len(values),
                "median": _round(statistics.median(values) if values else None),
                "q25": _round(_quantile(values, 0.25)),
                "q75": _round(_quantile(values, 0.75)),
                "year_median": int(round(statistics.median(years))) if years else None,
            }
        rows.append(
            {
                "region_code": region_code,
                "region": region,
                "country_area_count": len(members),
                "metrics": metric_rows,
            }
        )
    return rows


def build_capacity_dataset(
    indicator_rows: dict[str, list[dict[str, Any]]],
    country_dimension: list[dict[str, Any]],
) -> dict[str, Any]:
    country_meta = {
        str(item.get("Code")): {
            "name": item.get("Title") or item.get("Code"),
            "region_code": item.get("ParentCode"),
            "region": item.get("ParentTitle"),
        }
        for item in country_dimension
        if item.get("Code")
    }

    metric_meta: dict[str, dict[str, str]] = {}
    latest_maps: dict[str, dict[str, dict[str, Any]]] = {}
    all_indicator_meta = {**WHO_CAPACITY_INDICATORS, **WHO_NEED_PROXY_INDICATORS}
    for indicator_code, meta in all_indicator_meta.items():
        metric = meta["metric"]
        metric_meta[metric] = {**meta, "indicator_code": indicator_code}
        normalized = [normalize_gho_record(row, metric) for row in indicator_rows.get(indicator_code, [])]
        latest_maps[metric] = latest_by_country(normalized)
        for row in normalized:
            code = row.get("country_code")
            if code and code not in country_meta:
                country_meta[str(code)] = {
                    "name": str(code),
                    "region_code": row.get("region_code"),
                    "region": row.get("region"),
                }

    countries: list[dict[str, Any]] = []
    for code, meta in sorted(country_meta.items(), key=lambda item: (str(item[1].get("name")), item[0])):
        metrics: dict[str, dict[str, Any]] = {}
        for metric, latest in latest_maps.items():
            row = latest.get(code)
            if not row:
                continue
            metrics[metric] = {
                "value": _round(row.get("value"), 5),
                "year": row.get("year"),
                "low": _round(row.get("low"), 5),
                "high": _round(row.get("high"), 5),
                "indicator_code": row.get("indicator_code") or metric_meta[metric]["indicator_code"],
            }
            if not meta.get("region_code") and row.get("region_code"):
                meta["region_code"] = row.get("region_code")
                meta["region"] = row.get("region")
        countries.append(
            {
                "code": code,
                "name": meta.get("name") or code,
                "region_code": meta.get("region_code"),
                "region": meta.get("region"),
                "metrics": metrics,
            }
        )

    capacity_metrics = [meta["metric"] for meta in WHO_CAPACITY_INDICATORS.values()]
    summaries = {metric: _metric_summary(countries, metric) for metric in metric_meta}

    depression_metric = "depression_prevalence_2015"
    capacity_candidates = ["total_mental_health_workforce_per_100k", "psychiatrists_per_100k"]
    overlap_counts: dict[str, int] = {}
    for metric in capacity_candidates:
        overlap_counts[metric] = sum(
            1
            for country in countries
            if depression_metric in country["metrics"] and metric in country["metrics"]
        )
    primary_capacity_metric = max(capacity_candidates, key=lambda metric: overlap_counts[metric])

    raw_pairs: list[dict[str, Any]] = []
    for country in countries:
        dep = country["metrics"].get(depression_metric)
        cap = country["metrics"].get(primary_capacity_metric)
        if not dep or not cap:
            continue
        raw_pairs.append(
            {
                "code": country["code"],
                "name": country["name"],
                "region": country.get("region"),
                "depression_prevalence": dep["value"],
                "depression_year": dep["year"],
                "capacity_value": cap["value"],
                "capacity_year": cap["year"],
            }
        )

    dep_values = [float(row["depression_prevalence"]) for row in raw_pairs]
    cap_values = [float(row["capacity_value"]) for row in raw_pairs]
    dep_median = statistics.median(dep_values) if dep_values else None
    cap_median = statistics.median(cap_values) if cap_values else None

    for row in raw_pairs:
        if dep_median is None or cap_median is None:
            row["quadrant"] = "unclassified"
        elif row["depression_prevalence"] >= dep_median and row["capacity_value"] < cap_median:
            row["quadrant"] = "higher_depression_lower_capacity"
        elif row["depression_prevalence"] >= dep_median and row["capacity_value"] >= cap_median:
            row["quadrant"] = "higher_depression_higher_capacity"
        elif row["depression_prevalence"] < dep_median and row["capacity_value"] < cap_median:
            row["quadrant"] = "lower_depression_lower_capacity"
        else:
            row["quadrant"] = "lower_depression_higher_capacity"

    return {
        "status": "EDITORIAL_REVIEW_REQUIRED",
        "source": "WHO Global Health Observatory",
        "source_base_url": WHO_GHO_BASE,
        "country_area_universe": len(countries),
        "metric_metadata": metric_meta,
        "summary": summaries,
        "region_summaries": _region_summaries(countries, capacity_metrics),
        "countries": countries,
        "historical_mismatch_lens": {
            "status": "DESCRIPTIVE_ONLY",
            "need_metric": depression_metric,
            "capacity_metric": primary_capacity_metric,
            "overlap_n": len(raw_pairs),
            "need_median": _round(dep_median),
            "capacity_median": _round(cap_median),
            "pairs": raw_pairs,
            "caveat": (
                "This pairs WHO's 2015 modeled depression-prevalence estimate with each country's latest available "
                "WHO capacity observation, which can come from a different year. It is a historical descriptive lens, "
                "not a current need score, causal estimate, or country ranking."
            ),
        },
        "editorial_guardrails": [
            "Missing observations remain missing and are never converted to zero.",
            "Country observations come from different reporting years; every displayed country value must show its year.",
            "A workforce or facility count measures reported system capacity, not quality of care or access by itself.",
            "The 2015 depression-prevalence estimate is historical and cannot stand in for total current mental-disorder burden.",
            "Do not combine heterogeneous indicators into a synthetic country score without a separately justified methodology.",
        ],
    }


def fetch_country_capacity(output: Path, audit_output: Path | None = None) -> dict[str, Any]:
    indicator_rows: dict[str, list[dict[str, Any]]] = {}
    for code in [*WHO_CAPACITY_INDICATORS, *WHO_NEED_PROXY_INDICATORS]:
        indicator_rows[code] = fetch_odata_rows(f"{WHO_GHO_BASE}/{code}?$top=100")
    country_dimension = fetch_odata_rows(WHO_COUNTRY_DIMENSION)
    dataset = build_capacity_dataset(indicator_rows, country_dimension)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")

    if audit_output:
        audit = {
            "source": dataset["source"],
            "country_area_universe": dataset["country_area_universe"],
            "metrics": dataset["summary"],
            "mismatch_overlap_n": dataset["historical_mismatch_lens"]["overlap_n"],
            "mismatch_capacity_metric": dataset["historical_mismatch_lens"]["capacity_metric"],
            "guardrails": dataset["editorial_guardrails"],
        }
        audit_output.parent.mkdir(parents=True, exist_ok=True)
        audit_output.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote WHO country capacity atlas data for {len(dataset['countries'])} countries/areas to {output}")
    return dataset


def fetch_who_workforce(output: Path) -> None:
    rows: list[dict] = []
    for code, metric in WHO_INDICATORS.items():
        for record in fetch_odata_rows(f"{WHO_GHO_BASE}/{code}?$top=100"):
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
    """Normalize a user-supplied IHME/GBD CSV without redistributing the source data."""
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

    capacity = sub.add_parser("capacity", help="Build a country-level WHO mental-health capacity atlas dataset")
    capacity.add_argument(
        "--output",
        type=Path,
        default=Path("generated/global-mental-health/country-capacity.json"),
    )
    capacity.add_argument(
        "--audit",
        type=Path,
        default=Path("generated/global-mental-health/capacity-audit.json"),
    )

    ihme = sub.add_parser("ihme-import", help="Normalize a local IHME/GBD CSV export")
    ihme.add_argument("input", type=Path)
    ihme.add_argument("--output", type=Path, default=Path("generated/global-mental-health/ihme-burden.json"))

    args = parser.parse_args()
    if args.command == "who":
        fetch_who_workforce(args.output)
    elif args.command == "capacity":
        fetch_country_capacity(args.output, args.audit)
    elif args.command == "ihme-import":
        import_ihme(args.input, args.output)


if __name__ == "__main__":
    main()
