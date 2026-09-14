# Research waste / paper flood — research dossier

## Editorial question

How fast is the scholarly literature growing relative to one human's reading capacity, and what do retractions, irreproducibility, paper mills, post-retraction citations, peer-review labor, and research spending tell us about the cost of weak correction and filtering?

The story **must not** collapse those categories into a single "junk science" percentage.

## Evidence classes

### Observed / database counts

- NCSES / National Science Board: worldwide Scopus-indexed S&E output was 2,000,000 in 2010, 3,117,036 in 2021, and 3,275,079 in 2023.
- Nature: more than 10,000 research-paper retractions were issued in 2023. The article notes that the bulk of that exceptional year came from Hindawi cleanup.
- Retraction Watch: the database contains more than 65,000 retractions in 2026.

### Published estimates

- Oransky (Nature, 2022): around 45 retractions/month in 2010 and nearly 300/month in 2021; an estimate that roughly 1 in 50 papers could meet at least one COPE retraction criterion. This does **not** mean 2% of papers are fraudulent.
- Aczel et al. (2021): more than 100 million hours spent on journal peer review globally in 2020. Their method is designed to be conservative.
- Freedman, Cockburn & Simcoe (2015): more than 50% cumulative irreproducibility in US preclinical life-science research, associated with about $28B/year in direct spending. Do not globalize this number to all scholarship.
- Hsiao & Schneider (2021): 13,252 post-retraction citation contexts; 722 (5.4%) explicitly acknowledged the retraction.
- Fanelli (2009): 1.97% pooled self-report of fabrication/falsification/modification at least once; up to 33.7% self-report of other questionable practices. These are researcher-level survey estimates, not paper-level rates.
- Nature (2025) cites an estimate of at least 400,000 papers published from 2000–2022 with paper-mill hallmarks.
- Porter & McIntosh (2024) report an estimate that roughly 2% of journal submissions across disciplines originate from paper mills.

## Derived calculations

### Publication pace

Use 2023 as the latest observed annual output baseline in the report data:

`3,275,079 / 365.2425 / 24 / 60 / 60 ≈ 0.104 papers/second`

For the live "today / this year / since page open" counters, continue the observed 2010–2023 publication CAGR into the user's current year:

`publication CAGR = (3,275,079 / 2,000,000)^(1/13) - 1 ≈ 3.87%`

These live counters are a **pace model**, not a live Crossref/Scopus query, and the UI must say so.

### Reading capacity

For `N` full papers/day over `Y` years:

- annual reading = `N × 365.2425`
- share of modeled current-year output = `annual reading / modeled annual publication output`
- lifetime reading = `annual reading × Y`

Do not imply that "read" means deeply understood or that all papers are equally long.

### Hidden retraction-criterion reservoir

For scale only:

`3,275,079 × 2% ≈ 65,502`

This is the mechanical application of Oransky's "1 in 50" estimate to one publication year. It cannot be directly compared by subtraction with 2023's >10,000 retractions because retractions come from mixed publication cohorts and 2023 was an abnormal cleanup spike.

### Retraction/publication crossover — scenario, not forecast

Publication growth baseline: 2010→2023 CAGR ≈ 3.87%.

Scenario A — avoid the 2023 cleanup spike:

- retractions: ~540/year in 2010 (45/month) → ~3,600/year in 2021 (300/month)
- retraction CAGR ≈ 18.82%
- mechanically extending both exponentials yields a crossover around **2071**.

Scenario B — treat the 2023 spike as durable:

- ~540/year in 2010 → 10,000/year in 2023
- retraction CAGR ≈ 25.17%
- mechanically extending both exponentials yields a crossover around **2054**.

The 17-year gap is the editorial point: dramatic crossover dates are extremely sensitive to window choice and should not be presented as predictions.

## Resource / opportunity-cost rules

- `100M peer-review hours / 2,000 working hours ≈ 50,000 FTE-years` is a capacity equivalence, not a claim that all peer review is waste.
- `$28B / $1M ≈ 28,000 hypothetical $1M projects` is a budget-capacity equivalence, not a forecast of social value created.
- Paper and electricity are shown only in an editable assumption sandbox. Default paper mass uses ~5g per A4 80gsm sheet. The result must never be called total environmental cost.

## Anti-misleading rules

1. Retraction ≠ misconduct.
2. Misconduct ≠ irreproducibility.
3. Irreproducibility ≠ uselessness.
4. A paper-mill estimate ≠ a proven count of fabricated published papers.
5. Retraction growth can partly reflect better detection and publisher cleanup.
6. A 2023 retraction count cannot be divided by 2023 publication output and called a cohort retraction rate.
7. "1 in 50" is an estimate of meeting at least one retraction criterion, not a fraud rate.
8. The crossover year is a scenario result and must display its growth assumptions.

## Sources

- https://ncses.nsf.gov/pubs/nsb20257/publication-output-by-geography-and-scientific-field
- https://www.nature.com/articles/d41586-023-03974-8
- https://www.nature.com/articles/d41586-022-02071-6
- https://retractionwatch.com/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8591820/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4461318/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9520488/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2685008/
- https://www.nature.com/articles/d41586-025-00212-1
- https://www.nature.com/articles/s41598-024-71230-8
