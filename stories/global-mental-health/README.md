# Global mental health field story

Working title: **The world's invisible burden**

This is the first full-scale field story built on top of pudding-skill rather than a demo fixture.

## Editorial question

How is the global burden of mental disorders distributed, how has it changed since 1990, and does treatment capacity exist where the burden is greatest?

The story deliberately avoids treating modeled prevalence as a national league table. Burden estimates, service-system measurements, and interpretation remain separate evidence layers.

## Current v0.1 sequence

1. **1.1 billion** — establish the scale using WHO's 2021 global estimate.
2. **The turn** — shift from prevalence to the capacity to provide care.
3. **Workforce gap** — WHO Mental Health Atlas 2024 financing/workforce/service-system facts.
4. **1990–2023 burden layer** — reserved for a user-supplied IHME/GBD export.
5. **Method boundary** — explain modeling, diagnosis, survey coverage and why country rankings are not a mental-health scorecard.

Route: `/stories/global-mental-health`

## Fetch WHO workforce data

WHO's Global Health Observatory exposes country-level workforce indicators through its public API:

```bash
python scripts/mental_health_story.py who
```

Default output:

```text
generated/global-mental-health/who-workforce.json
```

The helper currently fetches total mental-health workforce, psychiatrists, nurses and psychologists per 100,000.

## Add the latest IHME burden layer

The latest GBD mental-health estimates cover 1990–2023. The source data is not committed to this repository because the IHME redistribution terms do not permit us to simply mirror the dataset from an OWID chart.

Export the required mental-disorder result from the IHME GBD Results tool, keep the raw file local, then normalize it:

```bash
python scripts/mental_health_story.py ihme-import path/to/your-gbd-export.csv
```

Default output:

```text
generated/global-mental-health/ihme-burden.json
```

For cross-country comparison prefer age-standardized prevalence/rates and retain sex/age/measure/cause dimensions in the export whenever available.

## Planned analytical join

The main story join will be:

```text
IHME country burden / trend
        ×
WHO country mental-health workforce
        ↓
burden-capacity mismatch
```

That join should never be described as causation. Missing workforce observations must remain visible rather than being imputed silently.

## Sources

See `source-manifest.json` for URLs, licensing notes and editorial guardrails.
