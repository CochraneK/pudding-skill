# Global mental health field story

Working title: **The world's invisible burden**

This is the first full-scale field story built on top of `pudding-skill` rather than a demo fixture. v0.2 is now driven by a compiled Research Dossier instead of waiting for one large external dataset.

## Editorial question

**A billion people live with mental disorders. How unequal is the capacity to care for them?**

The story deliberately avoids treating modeled prevalence as a national league table. Burden estimates, treatment evidence, financing, workforce, service-system measurements, and interpretation remain separate evidence layers.

Route: `/stories/global-mental-health`

## Current v0.2 sequence

1. **1.095 billion / 13.6%** — establish the 2021 global burden using WHO's latest synthesis of GBD 2021 estimates.
2. **359 million anxiety / 332 million depression** — show the largest disorder groups inside the aggregate.
3. **155 million DALYs / 5.4% of global DALYs** — explain why mental-health burden is primarily nonfatal disability rather than mortality.
4. **The turn** — move from burden to the capacity to provide care.
5. **Financing gap** — 2.1% median government-health-budget share; US$0.04 per capita in low-income countries versus US$65.89 in high-income countries among reporting countries.
6. **Workforce gap** — about 1.1–2.4 specialized mental-health workers per 100,000 in low/lower-middle-income settings versus 67.2 in high-income settings; global median 13.5.
7. **Treatment gap** — systematic-review evidence for major depressive disorder, with uncertainty and sparse low-resource evidence kept explicit.
8. **Service-model transition** — fewer than 10% of responding countries fully transitioned to community-based care; 52.9% remained at an early stage.
9. **Country data next layer** — build WHO capacity maps first; add country-level IHME prevalence/YLD trends only if the final editorial question still requires them.
10. **Method boundary** — explain modeled prevalence, response denominators, uncertainty, non-comparable coverage estimates, and why missing country observations are never zero.

## Research Dossier

The research-first evidence package lives in:

```text
stories/global-mental-health/research/
├── research-dossier.json
└── compiled/
    ├── research-report.md
    ├── source-ledger.json
    ├── numeric-evidence.csv
    ├── data-acquisition-plan.md
    └── research-dossier.json
```

`numeric-evidence.csv` contains only `VERIFIED` and `QUALIFIED` numeric claims. Discovery-only, conflicting, or rejected figures remain outside story-ready evidence.

The dossier currently covers WHO's *World mental health today* (2025), WHO *Mental Health Atlas 2024*, WHO GHO workforce indicators, IHME GBD 2021 mental-disorder burden summaries and tools documentation, and a PLOS Medicine systematic review/meta-regression of major-depression treatment coverage.

A recorded non-comparability rule prevents the WHO fact-sheet psychosis-care figure based on Mental Health Atlas 2020 from being plotted as a time trend against the Atlas 2024 estimate, because definitions, samples and reference periods differ.

## Primary next data target: WHO country capacity

The story no longer depends on a giant GBD export. WHO's Global Health Observatory exposes country-level workforce indicators through its public API:

```bash
python scripts/mental_health_story.py who
```

Default output:

```text
generated/global-mental-health/who-workforce.json
```

The helper currently fetches total mental-health workforce, psychiatrists, nurses and psychologists per 100,000. Before mapping, audit country/year coverage and choose a defensible common comparison rule rather than silently mixing years.

The next extraction target is the standardized **Mental Health Atlas 2024 country profiles**, especially:

- government mental-health expenditure per capita;
- mental-health expenditure as a share of government health expenditure;
- total mental-health workforce and professional groups per 100,000;
- community-service / primary-care integration indicators;
- financial-protection indicators;
- profile/reference year and explicit missingness.

Missing or nonreported values must remain missing and must never be encoded as zero.

## Optional IHME burden layer

Country-level GBD data remains useful for an eventual burden × capacity analysis, but it is now an optional enhancement rather than a blocker.

If needed, request/export a narrower IHME result using:

```text
GBD Estimate = Cause of death or injury
Cause        = Mental disorders
Measure      = Prevalence (or YLDs for the nonfatal-burden layer)
Metric       = Rate
Age          = Age-standardized
Sex          = Both
Years        = 1990–2023
Locations    = countries
```

Keep the raw file local and normalize it with:

```bash
python scripts/mental_health_story.py ihme-import path/to/your-gbd-export.csv
```

Default output:

```text
generated/global-mental-health/ihme-burden.json
```

Do not assume requested/exported GBD files can be mirrored publicly. Preserve the applicable IHME terms and commit only the derived values needed for the story when redistribution rights are unclear.

## Editorial guardrails

- A modeled prevalence estimate is not a national scorecard of subjective wellbeing.
- Counts, age-standardized rates, DALYs, budget shares, per-capita spending, workforce rates and treatment coverage are different measures and must not be collapsed into an opaque composite index.
- Mental Health Atlas medians describe reporting countries and are not population-weighted global averages.
- Atlas indicator denominators vary because response completeness differs by question.
- Treatment-gap estimates carry wide uncertainty, especially in low-resource settings.
- Country nonresponse is missing data, never zero.

See `source-manifest.json` and the Research Dossier for URLs, licensing notes, claim locators, uncertainty, source conflicts and acquisition plans.