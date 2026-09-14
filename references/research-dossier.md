# Research dossier workflow

Use this mode when the user has a **topic or industry question but not yet a trustworthy dataset**. The goal is not to produce a generic literature summary. The goal is to leave behind a reproducible evidence package that can support quantitative editorial work and data acquisition.

## State machine

```text
QUESTION ONLY
  ↓
research framing
  ↓
definitions / standards
  ↓
source map
  ↓
primary evidence harvest
  ↓
numeric claim extraction
  ↓
triangulation / conflict resolution
  ↓
data acquisition plan
  ↓
RESEARCH DOSSIER
  ├── research-report.md
  ├── source-ledger.json
  ├── numeric-evidence.csv
  └── data-acquisition-plan.md
  ↓
structured dataset when available
  ↓
pudding story
```

## What counts as successful research

A research pass is successful when it can answer, with citations and boundaries:

1. What exactly is being measured?
2. Which sources are authoritative for definitions and which for numeric estimates?
3. Which numbers are directly verified, which are qualified/modelled, and which are only leads?
4. Which figures conflict because of population, geography, period, definition, denominator, model version, or methodology?
5. Which downloadable/API/request-only datasets can answer the remaining questions?
6. What are the licensing and redistribution constraints?
7. Which evidence is safe to hand to the story pipeline?

A long list of URLs is not a successful research pass.

## Source ladder

Use source tiers as a priority system, not a prestige score.

- **T0 — definitions and standards.** Classification systems, technical manuals, methodology documents, indicator definitions. Use these first to avoid comparing unlike measures.
- **T1 — primary evidence.** Official datasets/statistical releases, peer-reviewed primary studies, systematic reviews. Prefer these for material numbers and reproducible data.
- **T2 — authoritative synthesis.** Government/IGO reports, major white papers, professional guidelines. Useful for synthesis and cited tables, but follow material numbers to the primary source when possible.
- **T3 — industry evidence.** Trade bodies, commercial reports, vendor research with disclosed methods. Useful for market structure and operational detail; record incentives and methods.
- **T4 — discovery only.** Journalism, blogs, aggregators, search snippets. Use to discover primary sources, not as the final provenance for a key number when a better source exists.

Do not promote a T4 number to VERIFIED merely because many websites repeat it.

## Research sequence

### 1. Frame the question

Write down the decision the research must support. Break vague topics into measurable dimensions such as size, prevalence, burden, growth, workforce, cost, access, outcomes, demographics, geography, or regulation.

Record scope explicitly: geography, population, period, exclusions, and required granularity.

### 2. Fix semantics before numbers

Locate definitions, manuals, classifications, or methodology notes before comparing figures. Capture:

- numerator and denominator;
- unit and scale;
- population universe;
- age/sex standardization;
- geography and aggregation level;
- reference period;
- nominal vs real currency;
- observed vs modelled estimate;
- uncertainty interval;
- revisions / model version.

If two numbers use different semantics, mark them non-comparable rather than averaging them.

### 3. Search broadly, cite narrowly

Search papers, white papers, manuals, reports, data portals, technical appendices, and official release pages. Use broad discovery to find the evidence graph, then cite the narrowest primary artifact that actually supports the claim.

A useful pattern is:

```text
journalism / search result
  → report
  → technical appendix
  → primary dataset / table
```

The final ledger should point as far down this chain as practical.

### 4. Extract claims atomically

One claim record should represent one checkable proposition. For a numeric claim, record at minimum:

- statement;
- numeric value;
- unit;
- geography;
- period;
- population / denominator;
- source IDs;
- locator: page, table, figure, worksheet, API endpoint, or query parameters;
- definition / method note;
- uncertainty when supplied;
- license / redistribution note when relevant;
- status and confidence.

Do not store a paragraph containing four unrelated numbers as one claim.

### 5. Verify material numbers

For a central number, prefer one of these:

- direct extraction from an authoritative primary dataset/table; or
- triangulation against a second independent authoritative source.

If a figure is modelled, label it modelled. If the source provides uncertainty intervals, carry them forward. If a number has been revised across releases, keep the release/version in provenance.

### 6. Record conflicts explicitly

Common conflict causes:

- different case definitions;
- all-age vs age-standardized rates;
- rate vs count vs percentage;
- different denominators;
- calendar year vs survey wave;
- modeled estimate vs observed survey;
- country vs region aggregation;
- current vs constant currency;
- different model/data release.

A conflict record should explain whether the figures can be reconciled, whether one should be preferred, or whether both should remain with caveats.

### 7. Treat data access as part of research

For each desired dataset, record an acquisition target:

- dataset name and publisher;
- question it answers;
- preferred source URL;
- access mode: direct download, API, query tool, request, manual extraction, unavailable;
- exact query/filter specification when known;
- license / redistribution terms;
- next action.

For restrictive tools such as large epidemiological query systems, the executable result may be a precise export/request recipe rather than a copied dataset.

### 8. Compile the handoff

The populated JSON dossier is the canonical research state. Validate and compile it:

```bash
python scripts/pudding.py research validate generated/research/research-dossier.json
python scripts/pudding.py research compile generated/research/research-dossier.json
```

The compiler writes:

```text
generated/research/research-dossier.json
generated/research/source-ledger.json
generated/research/numeric-evidence.csv
generated/research/research-report.md
generated/research/data-acquisition-plan.md
```

Only `VERIFIED` and `QUALIFIED` numeric claims enter `numeric-evidence.csv`. `CONFLICT`, `LEAD_ONLY`, and `REJECTED` claims stay visible in the dossier but do not silently become story input.

## Claim statuses

- **VERIFIED** — directly checked against strong evidence; semantics are clear enough for intended use.
- **QUALIFIED** — usable with an explicit limitation, modelling caveat, definition issue, or narrow scope.
- **CONFLICT** — materially disagrees with another figure and is not yet resolved.
- **LEAD_ONLY** — useful for discovery but not safe to publish as evidence.
- **REJECTED** — examined and intentionally excluded.

Confidence (`high`, `medium`, `low`) is separate from status. A verified number may still deserve medium confidence if the underlying estimate is uncertain.

## Agent behavior

When running as an Agent Skill, the agent should perform the web/library research itself. The Python module is deliberately **not** a web scraper: it enforces the evidence contract and compiles the research assets after retrieval. This separation makes browsing replaceable while provenance and QA stay deterministic.

The agent should:

1. search primary and secondary sources;
2. retrieve the relevant paper/report/manual/table, not just snippets;
3. populate source and claim ledgers while researching;
4. follow important secondary figures back to their primary source where possible;
5. preserve locators and query parameters;
6. flag access/paywall/licensing restrictions;
7. compile the dossier before starting the story pipeline.

## Research report is executable, not decorative

A useful report ends with concrete next actions, for example:

```text
1. Use WHO Atlas table X for country workforce baseline.
2. Submit an IHME request with Cause=Mental disorders, Measure=Prevalence,
   Metric=Rate, Age=Age-standardized, Sex=Both, Years=1990–2023,
   countries only.
3. Join by ISO3; keep estimate lower/upper bounds.
4. Build burden × workforce scatter only for years with comparable coverage.
5. Do not interpret modeled prevalence as a national diagnostic scorecard.
```

That is more useful than a prose conclusion that merely says “more research is needed.”

## Hard boundaries

- Never fabricate a number to fill a missing field.
- Never cite a search snippet as the source of a material number.
- Never collapse count, rate, percentage, and age-standardized rate into one metric.
- Never hide conflicting estimates by averaging them without a methodological basis.
- Never redistribute restricted source data merely because it can be downloaded or viewed.
- Never turn correlation or observational evidence into causal language without support.
- Never treat the research dossier as final editorial approval.
