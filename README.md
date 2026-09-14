# pudding-skill

A **Pudding-inspired editorial data-storytelling Agent Skill + SvelteKit starter** that turns structured data into an auditable set of story directions before it renders anything.

This project is not a visual clone of [The Pudding](https://pudding.cool/). It borrows the more useful editorial idea: start with a question and evidence, compare what the data can support, choose the right narrative/visual form, and verify the result before publishing.

> The Svelte starter is derived from [`the-pudding/svelte-starter`](https://github.com/the-pudding/svelte-starter) under the MIT License. This project is not affiliated with The Pudding and does not ship or hotlink The Pudding logos or proprietary fonts.

## Research dossier mode: from a question to auditable evidence

`pudding-skill` no longer has to start with a ready-made CSV. When a project starts with an industry/domain question, use the research dossier workflow to map definitions, papers, official reports, white papers, manuals, source conflicts, numeric claims, licensing constraints, and concrete data-acquisition steps before entering the story pipeline.

```bash
python scripts/pudding.py research init --topic "Global mental health" --question "Where does treatment capacity lag behind need?"
python scripts/pudding.py research validate generated/research/research-dossier.json
python scripts/pudding.py research compile generated/research/research-dossier.json
```

Compilation produces an executable research package: `research-report.md`, `source-ledger.json`, `numeric-evidence.csv`, and `data-acquisition-plan.md`. Material numbers retain source and scope metadata; unresolved conflicts and discovery-only figures are kept out of story-ready numeric evidence. See `references/research-dossier.md`.

## v2.6: editorial benchmark and regression corpus

v2.6 adds a curated regression suite so changes to scoring, selection, claim verification, visual grammar, or provenance can be measured across multiple data/story shapes rather than a single demo.

```bash
npm run benchmark
# or
python scripts/pudding.py benchmark
```

The initial corpus contains 12 self-contained cases across CSV, TSV, JSON, JSONL, and NDJSON. It covers divergence, grouped change, ranked means, correlation, distribution, missing values, percentage parsing, ignored identifiers, and explicit semantic contracts. Each case separately scores story selection (35), visual grammar (20), independent claim audit (25), editorial/renderer gate (10), and first-draft provenance (10).

The committed regression floor is intentionally strict: 100/100 overall, 100% case pass rate, zero hard failures, and 100% pass in every dimension. A claim-audit regression cannot be hidden by a good average. Reports are written to `.qa/benchmark-report.json` and `.qa/benchmark-report.md` and uploaded with CI evidence.

Use `/benchmark` to inspect the corpus and scoring contract. The benchmark is a deterministic regression instrument, **not** a score for newsworthiness, prose craft, causal validity, or visual taste. See `references/benchmark.md`.

## v2.5: screenshot-driven visual refinement

v2.5 extends the data/claim/browser pipeline into a bounded visual self-review loop. It deliberately keeps mechanical browser health, deterministic visual diagnostics, agent screenshot judgment, and automatic refinement as separate evidence layers.

After a production build and browser QA, run:

```bash
npm run qa:visual-probe -- --base-url http://127.0.0.1:4173 --out .qa/visual-probe.json
python scripts/pudding.py review .qa/visual-probe.json
```

The visual probe evaluates `/`, `/generated`, and `/lab` at desktop and mobile widths and captures both top-of-page and mid-page states, producing **12 screenshots** plus structured metrics. The critic checks measurable properties such as long-form copy measure, leading, heading hierarchy, touch targets, clipping, contrast, visual aspect, and sticky density.

A deterministic `100/100` is still **not** aesthetic approval. `agent_review.status` remains pending until an agent/editor explicitly inspects every required screenshot. `python scripts/pudding.py review-check agent-visual-review.json` verifies screenshot coverage and prevents an agent PASS from overriding a deterministic hard failure.

If review identifies a low-risk issue, `pudding refine` can only apply three allowlisted changes: readable copy width, text leading, and coarse-pointer target height. It never changes data, claims, chart transforms, arbitrary colors, or Svelte structure, and the automatic loop stops after two passes. Every applied change requires a fresh build, browser QA, visual probe, and before/after screenshot comparison.

The v2.5 baseline is validated with 21 regression tests, 6/6 browser-delivery cases, 6 visual-probe route/viewport cases, 12 reviewed screenshots, a deterministic visual score of 100/100 with zero findings, and the existing high/critical dependency-audit gate.

## v2.4: arbitrary data to publication-ready first draft

v2.4 extends the evidence-audited v2.3 pipeline through an editable first-draft layer. The preferred entry point is now:

```bash
python scripts/pudding.py story data.csv --question "What changed?" --schema data-schema.json
```

New in v2.4:

- accepts CSV, TSV, row-oriented JSON, JSONL, and NDJSON;
- emits `visual-plan.json` with a richer editorial recommendation while preserving a deterministic baseline renderer;
- emits `story-draft.json` and `story-draft.md` with headline, dek, narrative sections, annotations, methodology, caveats, sources, field glossary, and claim provenance;
- maps quantitative copy back to verified structured evidence through `claim_ref` / `evidence_index`;
- adds a unified `pudding.py` CLI for data inspection, candidate ranking, and full story generation;
- expands regression coverage to 13 tests while retaining production build, dependency-audit, and 6/6 real-browser delivery gates.

Generated copy remains `EDITORIAL_REVIEW_REQUIRED`. A richer visual recommendation never silently replaces the tested baseline renderer, and changing the numerical meaning of prose requires claim re-verification.

## v2.3: evidence-to-browser delivery gates

v2.3 keeps the v2.2 editorial decision system and closes the delivery gap between “the numbers are defensible” and “the published experience actually works.”

New release gates:

- real Chromium QA for `/`, `/generated`, and `/lab` at desktop and mobile widths;
- console/exception/network, horizontal-overflow, keyboard, accessible-name, duplicate-ID, image-alt, and reduced-motion checks;
- six screenshot artifacts plus a machine-readable browser QA report for review;
- dependency-audit evidence in CI, with **high or critical advisories failing the build**;
- compatible dependency remediation without destructive `npm audit fix --force`;
- Svelte 5 reactive renderer cleanup so production builds are free of the prior project-level state warnings.

The current compatible dependency set has **0 critical, 0 high, 0 moderate, and 7 low** audit findings. The remaining lows stay visible in CI evidence because npm's only automated remediation path is breaking and would downgrade SvelteKit.

## v2.2: from chart heuristic to editorial decision system

v2.1 established a deterministic data → story → Svelte baseline. v2.2 removes the biggest remaining shortcut: **the first matching analytical pattern no longer automatically becomes the story.**

The pipeline now:

1. profiles the data;
2. optionally applies an explicit data contract for roles, labels, units, and definitions;
3. generates multiple defensible story candidates;
4. scores them with transparent editorial-priority proxies;
5. selects the highest-ranked candidate that passes quality + renderer gates, with automatic fallback;
6. creates a story spec and render bundle;
7. independently recomputes the selected quantitative evidence from raw data;
8. exposes the candidate board and audit trail in `/lab`;
9. renders the selected baseline at `/generated`;
10. runs the same gates in CI.

## Pipeline

```text
research question + structured data
              │
              ├──── optional data contract
              ▼
          DATA AUDIT
              ▼
      CANDIDATE GENERATION
              │
      ┌───────┼────────┬───────────┐
      ▼       ▼        ▼           ▼
   change   divergence relation distribution ...
      └───────┬────────┴───────────┘
              ▼
       TRANSPARENT SCORING
              ▼
     QUALITY / RENDERER GATES
          fail │  pass
               ├──► try next
               ▼
          STORY SPEC
              ▼
       INDEPENDENT CLAIM AUDIT
              ▼
       BASELINE RENDER BUNDLE
          ┌───┴────┐
          ▼        ▼
        /lab   /generated
              ▼
       BESPOKE EDITORIAL BUILD
```

The score is **not newsworthiness**. It ranks evidence-backed directions using computable proxies such as coverage, effect size, distinctiveness, visual fit, simplicity, question alignment, and risk penalties. Domain meaning and editorial significance still require judgment.

## Quick start

```bash
git clone https://github.com/CochraneK/pudding-skill.git
cd pudding-skill
npm install
npm run dev
```

Useful routes:

- `/` — Pudding-inspired scrollytelling design demo;
- `/lab` — ranked story candidates, score breakdown, fallback attempts, quality gates, and claim audit;
- `/generated` — the selected deterministic baseline story;
- `/benchmark` — the v2.6 regression corpus and scoring contract.

## Run the full editorial pipeline

```bash
python scripts/pipeline.py examples/sample-data.csv \
  --question "Which fictional cities saw housing costs separate most sharply from income after 2019?" \
  --schema examples/data-schema.example.json
```

Outputs:

```text
generated/profile.json
generated/candidates.json
generated/story-spec.json
generated/selection-report.json
generated/evaluation.json
generated/claim-audit.json
src/data/story-candidates.json
src/data/story-selection.json
src/data/story-evaluation.json
src/data/story-claim-audit.json
src/data/auto-story.json
```

## Why the data contract matters

Field names are not enough to establish semantics. An optional JSON contract can identify time/category/measure roles and provide publication labels, units, and definitions:

```json
{
  "fields": {
    "year": { "role": "time", "label": "Year" },
    "city": { "role": "category", "label": "City" },
    "income_index": {
      "role": "measure",
      "label": "Income index",
      "unit": "index, 2019 = 100"
    }
  }
}
```

Validate one with:

```bash
python scripts/data_contract.py examples/data-schema.example.json
```

## Candidate generation and selection

Inspect candidates directly:

```bash
python scripts/candidate_story.py data.csv \
  --question "What changed?" \
  --schema data-schema.json \
  --output candidates.json
```

Select with automatic fallback:

```bash
python scripts/select_story.py data.csv \
  --question "What changed?" \
  --schema data-schema.json
```

Current baseline patterns include:

- time + category + two measures → divergence in start-to-end change;
- time + category + measure → group change over time;
- category + measure → ranked group mean comparison;
- two numeric measures → correlation/scatter;
- numeric measure → distribution.

## Independent claim verification

The story spec does not get to “trust itself.” `verify_claims.py` reads raw rows again and recomputes structured evidence:

```bash
python scripts/verify_claims.py generated/story-spec.json examples/sample-data.csv
```

A mismatch is a hard failure. Tests include a tampering case where a correct gap of `31` is changed to `999`; the audit must reject it.

The audit verifies numbers, not interpretation. It cannot decide whether a denominator is meaningful, a causal story is valid, or a metric is ethically appropriate.

## Main scripts

| Script | Purpose |
|---|---|
| `profile_data.py` | schema/type/missingness/range audit |
| `data_contract.py` | validates explicit roles, labels, units, descriptions |
| `candidate_story.py` | generates and scores multiple story directions |
| `select_story.py` | applies quality/renderer gates and falls back when needed |
| `validate_story.py` | validates story-spec structure |
| `evaluate_story.py` | deterministic editorial quality gates |
| `verify_claims.py` | independently recomputes quantitative evidence |
| `generate_story.py` | creates normalized renderer data |
| `pipeline.py` | orchestrates the full v2.2 chain |
| `qa_story.py` | repository/static/brand preflight |

`derive_story.py` remains as the v2.1 single-direction baseline for compatibility and simple experiments; the preferred workflow is now `pipeline.py`.

## Repository structure

```text
pudding-skill/
├── SKILL.md
├── references/
│   ├── editorial-workflow.md
│   ├── editorial-scoring.md
│   ├── data-contract.md
│   ├── visual-grammar.md
│   ├── story-spec.md
│   ├── claim-audit.md
│   └── quality-rubric.md
├── scripts/
│   ├── profile_data.py
│   ├── data_contract.py
│   ├── candidate_story.py
│   ├── select_story.py
│   ├── derive_story.py
│   ├── validate_story.py
│   ├── evaluate_story.py
│   ├── verify_claims.py
│   ├── generate_story.py
│   ├── pipeline.py
│   └── qa_story.py
├── examples/
│   ├── sample-data.csv
│   ├── data-schema.example.json
│   └── story-spec.example.json
├── src/routes/
│   ├── +page.svelte
│   ├── generated/+page.svelte
│   └── lab/+page.svelte
├── tests/test_pipeline.py
└── .github/workflows/ci.yml
```

## Checks

```bash
npm run check:skill
npm run benchmark
npm run build
npm run qa:browser
npm audit --audit-level=high
```

`check:skill` validates the example contract/spec, runs the full candidate-selection pipeline, independently audits the selected quantitative evidence, runs unit tests, and performs static preflight checks. CI then runs the editorial benchmark gate, builds the Svelte app, validates four routes at desktop/mobile widths (8 browser cases), stores benchmark/browser/visual evidence, and fails on high-or-critical npm advisories.

## Editorial principles

1. **Evidence before aesthetics.**
2. **Competing hypotheses before commitment.** Do not stop at the first chartable pattern.
3. **Explicit semantics before inference.** Units and roles should be stated when ambiguous.
4. **One primary argument.** Supporting facts should reinforce it.
5. **Narrative operations before chart names.**
6. **Use scroll only when sequence matters.**
7. **Numeric claims must be reproducible from source data.**
8. **Mobile and accessibility are correctness concerns, not polish.**
9. **Scores assist judgment; they do not replace it.**

## Licensing and attribution

- Upstream starter: [`the-pudding/svelte-starter`](https://github.com/the-pudding/svelte-starter), MIT License.
- Skill instructions, scripts, examples, and demo additions: MIT License under this repository.
- The Pudding name is used only for attribution and to describe editorial inspiration. No affiliation is implied.
