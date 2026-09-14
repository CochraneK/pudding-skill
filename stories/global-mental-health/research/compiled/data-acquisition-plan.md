# Data acquisition plan — Global mental health

Prioritize reproducible primary data. Record query parameters, export filters, access constraints, and redistribution terms.

## WHO Global Health Observatory mental-health workforce indicators

- ID: `who-gho-country-workforce`
- Purpose: Build reproducible country-level workforce comparisons without waiting for IHME burden exports.
- Preferred source: WHO GHO OData API
- Access mode: `api`
- License / redistribution: Preserve WHO indicator metadata and attribution; verify reuse terms for derived bulk files.
- Query / filters: Use indicator codes already supported by scripts/mental_health_story.py: MH_21 total workforce, MH_6 psychiatrists, MH_7 mental-health nurses, MH_9 psychologists; retain country code, year, numeric value and uncertainty fields when present.
- Next action: Run `python scripts/mental_health_story.py who` and audit indicator-year coverage before choosing a common comparison year.

## WHO Mental Health Atlas 2024 country profiles

- ID: `who-atlas-2024-country-profiles`
- Purpose: Extract comparable country-level financing, workforce, policy and service-system fields for the capacity side of the story.
- Preferred source: WHO Mental Health Atlas country-profile collection
- Access mode: `direct_download`
- License / redistribution: Profiles are WHO publications; derive only the fields needed, preserve source-profile URLs and do not imply nonresponding countries are zero.
- Query / filters: Country profile fields of interest: government mental-health expenditure per capita; mental-health expenditure as % of government health expenditure; total mental-health workers per 100k; psychiatrist/nurse/psychologist counts per 100k; community-service indicators; primary-care integration; public financial protection.
- Next action: Create a batch extractor for the standardized profile PDFs or manually seed a representative sample, recording missing/nonresponse explicitly.

## IHME Global Burden of Disease mental-disorder prevalence

- ID: `ihme-mental-disorders-prevalence`
- Purpose: Optional country-level need layer: age-standardized prevalence map and 1990–2023 trend.
- Preferred source: IHME GBD Results Tool / My Requests
- Access mode: `request`
- License / redistribution: GBD tools are available for non-commercial use under IHME terms. Do not assume a requested/exported file can be mirrored publicly; retain only the derived values needed for the story unless redistribution rights are clear.
- Query / filters: GBD Estimate=Cause of death or injury; Cause=Mental disorders; Measure=Prevalence; Metric=Rate; Age=Age-standardized; Sex=Both; Years=1990–2023; country locations.
- Next action: Only submit the large IHME request if the editorial story still needs country-level burden after the WHO capacity analysis. The story should not be blocked on this dataset.

## IHME Global Burden of Disease mental-disorder YLDs

- ID: `ihme-mental-disorders-ylds`
- Purpose: Optional country-level nonfatal burden layer, better aligned with how mental disorders contribute to health loss than deaths alone.
- Preferred source: IHME GBD Results Tool / My Requests
- Access mode: `request`
- License / redistribution: Same IHME terms and redistribution caution as prevalence exports.
- Query / filters: GBD Estimate=Cause of death or injury; Cause=Mental disorders; Measure=YLDs; Metric=Rate; Age=Age-standardized; Sex=Both; Years=1990–2023; country locations.
- Next action: Request only if a burden×capacity scatter/map is editorially necessary; otherwise use the published 2021 global burden estimate and focus country visuals on WHO system capacity.

## Supporting information for Moitra et al. 2022 MDD treatment-coverage systematic review

- ID: `plos-mdd-treatment-supporting-data`
- Purpose: Add treatment-gap evidence by income group or geography with transparent study provenance.
- Preferred source: PLOS Medicine supporting information
- Access mode: `direct_download`
- License / redistribution: Article and supporting information are CC BY.
- Query / filters: Use only variables with harmonized treatment-type definitions; preserve uncertainty intervals and study/sample metadata.
- Next action: Download S1 Appendix / supporting information only if treatment coverage becomes a main visual rather than an annotated supporting statistic.

