# Editorial benchmark contract

v2.6 adds a deterministic regression corpus after the existing data/claim/browser/visual gates.

The benchmark answers a narrow question: **when the pipeline sees a curated data task whose supported story operation is known, does it still choose and verify the expected path?**

It is not a proxy for newsworthiness, cultural importance, prose quality, causal validity, or visual taste.

## Corpus

`benchmarks/corpus.json` stores self-contained cases. Each case declares:

- an input format (`csv`, `tsv`, `json`, `jsonl`, or `ndjson`);
- source rows;
- a research question;
- an optional semantic data contract;
- the expected evidence pattern;
- the expected richer visual grammar;
- fixture-specific text that should remain in the selected quantitative claim.

The initial corpus intentionally mixes story operations and data conditions rather than cloning one sample:

- divergence between two changes;
- grouped change over time;
- ranked group means;
- positive and negative correlation;
- distributions;
- missing values;
- percentage-like numeric strings;
- identifier fields that must be ignored;
- opaque field names that require an explicit semantic contract;
- all five supported structured-data formats.

## Score

Each case is scored out of 100 with separate dimensions:

| Dimension | Weight | What it establishes |
|---|---:|---|
| story selection | 35 | selected evidence kind and fixture-specific claim signal match the expectation |
| visual grammar | 20 | recommended publication visual matches the evidence operation |
| claim audit | 25 | quantitative evidence independently recomputes from raw rows |
| editorial gate | 10 | story validation, editorial evaluation, and renderer-selection gate remain viable |
| provenance | 10 | first-draft `claim_ref` → `evidence_index` mappings remain complete and verified |

A full case pass requires 100/100. This is intentional: an average must not hide a broken claim audit or a changed story operation.

## Regression floor

`benchmarks/baseline.json` defines the release floor. The v2.6 baseline requires:

- overall score: 100/100;
- full case pass rate: 100%;
- hard failures: 0;
- every dimension pass rate: 100%.

Do not lower the baseline in the same patch merely to make a regression green. If product behavior is intentionally changing, update the corpus expectation with an explicit explanation of why the new behavior is more correct.

## Run it

```bash
npm run benchmark
# or
python scripts/pudding.py benchmark
```

Outputs:

```text
.qa/benchmark-report.json
.qa/benchmark-report.md
```

CI runs the benchmark before the production build. The reports are uploaded with the normal QA evidence artifact.

Use `--no-gate` only for exploratory comparison; it writes the same report without failing the process on baseline regression.

## Reading failures

A benchmark failure is evidence of changed deterministic behavior, not automatically evidence that the new code is bad. Inspect the exact dimension and case:

- **selection**: did scoring/question relevance choose a different analytical operation?
- **visual grammar**: did the evidence kind map to a different publication form?
- **claim audit**: stop; raw-data recomputation failed and the release should not proceed.
- **editorial gate**: inspect validation/evaluation/renderer compatibility.
- **provenance**: the draft lost or corrupted a structured evidence reference.

Only after explaining the change should the implementation or benchmark expectation move.

## Self-improvement use

The benchmark report is designed to be compared across future versions. A useful improvement cycle is:

```text
new candidate/scoring/rendering idea
        ↓
run corpus
        ↓
inspect per-case + per-dimension changes
        ↓
keep gains that do not regress hard evidence gates
        ↓
add a new fixture for the newly learned failure mode
```

That turns discovered mistakes into permanent regression cases instead of one-off fixes.
