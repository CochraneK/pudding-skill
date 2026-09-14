# Global mental health field story

Working title: **The world's invisible burden**

This is the first full-scale field story built on top of `pudding-skill` rather than a demo fixture. The story now combines a compiled Research Dossier with a country-level WHO capacity atlas instead of waiting for one large external dataset.

## Editorial question

**A billion people live with mental disorders. How unequal is the capacity to care for them?**

The project deliberately avoids treating modeled prevalence as a national league table. Burden estimates, treatment evidence, financing, workforce, service-system measurements, and interpretation remain separate evidence layers.

Routes:

```text
/stories/global-mental-health        research-backed narrative
/stories/global-mental-health/atlas  country capacity atlas + historical mismatch lens
```

## Current sequence

1. **1.095 billion / 13.6%** — establish the 2021 global burden using WHO's synthesis of GBD 2021 estimates.
2. **359 million anxiety / 332 million depression** — show the largest disorder groups inside the aggregate.
3. **155 million DALYs / 5.4% of global DALYs** — explain why mental-health burden is primarily nonfatal disability rather than mortality.
4. **The turn** — move from burden to the capacity to provide care.
5. **Financing gap** — 2.1% median government-health-budget share; US$0.04 per capita in low-income countries versus US$65.89 in high-income countries among reporting countries.
6. **Workforce gap** — about 1.1–2.4 specialized mental-health workers per 100,000 in low/lower-middle-income settings versus 67.2 in high-income settings; global median 13.5.
7. **Treatment and service-model gaps** — systematic-review evidence plus Mental Health Atlas community-care transition indicators.
8. **Country capacity atlas** — map reported psychiatrist, nurse, psychologist, outpatient-facility and government-spending indicators while showing the observation year and missingness.
9. **Historical need × capacity lens** — pair WHO's 2015 modeled depression prevalence with the latest available psychiatrist-density observation for countries with both measures. This is descriptive context only, not a current need score or causal estimate.
10. **Method boundary** — explain modeled prevalence, response denominators, uncertainty, data age and why missing country observations are never zero.

## Country capacity data

Run:

```bash
python scripts/mental_health_story.py capacity
```

Default outputs:

```text
generated/global-mental-health/country-capacity.json
generated/global-mental-health/capacity-audit.json
```

The committed atlas data is generated from WHO Global Health Observatory OData indicators and Natural Earth public-domain 1:110m country geometry. The compiler retains the latest non-missing observation per country and indicator and preserves its year.

Current audited coverage across the 234 WHO country/area dimension entries:

- psychiatrists per 100,000: **146** observations, mostly 2013–2017;
- mental-health nurses per 100,000: **127**;
- psychologists per 100,000: **120**;
- mental-health outpatient facilities per 100,000: **139**;
- government mental-health spending share: **78**, all from the 2011 indicator table;
- WHO 2015 modeled depression prevalence: **183**;
- depression × psychiatrist-density historical overlap: **142** countries.

The GHO code `MH_21` currently yields no usable total-workforce values through this public endpoint, so the atlas does not fabricate a total-workforce layer from professional subgroups.

## Research Dossier

The research-first evidence package lives in:

```text
stories/global-mental-health/research/
├── research-dossier.json
├── capacity-atlas.md
├── capacity-audit.json
├── capacity-data-manifest.json
└── compiled/
    ├── research-report.md
    ├── source-ledger.json
    ├── numeric-evidence.csv
    ├── data-acquisition-plan.md
    └── research-dossier.json
```

`numeric-evidence.csv` contains only `VERIFIED` and `QUALIFIED` numeric claims. Discovery-only, conflicting, or rejected figures remain outside story-ready evidence.

The dossier covers WHO's *World mental health today* (2025), WHO *Mental Health Atlas 2024*, WHO GHO indicators, IHME GBD mental-disorder burden summaries/tools documentation, and a PLOS Medicine systematic review/meta-regression of major-depression treatment coverage.

## Optional IHME burden layer

Country-level GBD prevalence/YLD data remains an optional enhancement, not a blocker. If needed, request/export a narrow IHME result, keep the raw file local, and normalize it with:

```bash
python scripts/mental_health_story.py ihme-import path/to/your-gbd-export.csv
```

Do not mirror restricted GBD exports or scrape values from a visualization when redistribution rights are unclear.

## Editorial guardrails

- A modeled prevalence estimate is not a national scorecard of subjective wellbeing.
- Counts, age-standardized rates, DALYs, budget shares, per-capita spending, workforce rates and treatment coverage are different measures and must not be collapsed into an opaque composite index.
- Mental Health Atlas medians describe reporting countries and are not population-weighted global averages.
- Country observations come from different reporting years; every country value must retain its year.
- Workforce and facility rates measure reported system capacity, not quality of care or actual access by themselves.
- The 2015 depression estimate is historical and cannot stand in for current total mental-disorder burden.
- Country nonresponse is missing data, never zero.

See `source-manifest.json`, `research/capacity-data-manifest.json`, and the Research Dossier for URLs, licensing notes, claim locators, uncertainty, conflicts and acquisition plans.
