# pudding-skill

A **Pudding-inspired editorial data-storytelling Agent Skill + SvelteKit starter**.

This project is deliberately not a visual clone of [The Pudding](https://pudding.cool/). It borrows the more useful idea: start with an editorial question and evidence, design a narrative around what the data can actually support, choose the visual form that serves that narrative, and validate the result before publishing.

> The Svelte starter is derived from [`the-pudding/svelte-starter`](https://github.com/the-pudding/svelte-starter) under the MIT License. This project is not affiliated with The Pudding and does not ship or hotlink The Pudding logos or proprietary fonts.

## What changed in v2.1

The old repository described a six-stage AI workflow in the README but did not actually implement the skill layer. v2 makes that workflow executable:

- `SKILL.md` — agent instructions, trigger conditions, decision rules, and delivery checks
- `scripts/profile_data.py` — CSV/TSV/JSON data audit for story planning
- `scripts/validate_story.py` — validates the editorial story specification before implementation
- `scripts/derive_story.py` — deterministic heuristic baseline that selects a defensible first story pattern from common tabular data
- `scripts/generate_story.py` — turns a valid story spec + source data into a normalized render bundle
- `scripts/pipeline.py` — profile → derive → validate → render in one command
- `scripts/qa_story.py` — static preflight for generated data and Pudding brand/hotlink leakage
- `references/editorial-workflow.md` — question → evidence → insight → beats → production mode
- `references/visual-grammar.md` — analytical task + narrative operation → visual treatment
- `references/quality-rubric.md` — pre-delivery scoring and rejection conditions
- `references/story-spec.md` — contract between editorial analysis and the renderer
- `examples/` — a valid story spec and synthetic dataset
- a real scrollytelling demo on the root route
- a generated baseline story at `/generated` powered by `src/data/auto-story.json`
- Python unit tests covering change-gap, group comparison, correlation, and bundle generation
- generic metadata and system font stacks instead of Pudding-specific brand defaults
- CI that validates the skill example and builds the Svelte project

## Workflow

```text
research question / data
          ↓
      DATA AUDIT
          ↓
  defensible insight?
      ↙         ↘
    no           yes
 explain gap       ↓
              STORY SPEC
                  ↓
          NARRATIVE BEATS
                  ↓
         PRODUCTION MODE
        ↙    ↓    ↓    ↘
     static small scroll explore
            multiples
                  ↓
             IMPLEMENT
                  ↓
      DATA + VISUAL + MOBILE QA
                  ↓
               DELIVER
```

The important rule is that **scrollytelling is not the default**. If an annotated static chart, small multiples, stepper, map, or explorable communicates the evidence better, use that instead.

## Quick start

```bash
git clone https://github.com/CochraneK/pudding-skill.git
cd pudding-skill
npm install
npm run dev
```

Open the local Vite URL to see the demo.

## Validate the skill layer

```bash
npm run check:skill
```

Or run the tools directly:

```bash
python scripts/profile_data.py examples/sample-data.csv
python scripts/validate_story.py examples/story-spec.example.json
```

Profile your own data:

```bash
python scripts/profile_data.py path/to/data.csv --output profile.json
```

## End-to-end baseline

Run the full deterministic pipeline on any CSV/TSV/row-oriented JSON:

```bash
python scripts/pipeline.py data.csv --question "What changed, where, and by how much?"
```

It produces:

```text
generated/profile.json
generated/story-spec.json
src/data/auto-story.json
```

Then open `/generated` in the Svelte app. The baseline currently detects common patterns such as:

- time + category + two measures → divergence in start-to-end change;
- time + category + one measure → group time trend;
- time + one measure → trend;
- category + measure → ranked group comparison;
- two numeric measures → correlation/scatter;
- one numeric measure → distribution.

This is deliberately conservative. The point is to establish a reproducible evidence chain before an agent invests in a bespoke visual treatment.

## Story spec

The story spec is the contract between analysis and implementation. At minimum it contains:

```json
{
  "question": "What are we trying to explain?",
  "audience": "Who is this for?",
  "primary_insight": "What does the evidence support?",
  "evidence": [],
  "beats": [],
  "visuals": [],
  "sources": [],
  "caveats": []
}
```

See `examples/story-spec.example.json` for a complete example.

## Repository structure

```text
pudding-skill/
├── SKILL.md
├── references/
│   ├── editorial-workflow.md
│   ├── visual-grammar.md
│   ├── story-spec.md
│   └── quality-rubric.md
├── scripts/
│   ├── profile_data.py
│   ├── derive_story.py
│   ├── validate_story.py
│   ├── generate_story.py
│   ├── pipeline.py
│   └── qa_story.py
├── examples/
│   ├── sample-data.csv
│   └── story-spec.example.json
├── src/
│   ├── actions/
│   ├── components/
│   ├── data/
│   ├── routes/
│   ├── styles/
│   └── utils/
├── tests/test_pipeline.py
├── .github/workflows/ci.yml
└── package.json
```

## Editorial principles

1. **Evidence before aesthetics.** Do not make the visual more confident than the data.
2. **One primary argument.** Supporting facts should reinforce it, not compete with it.
3. **Narrative operations before chart names.** Establish, compare, reveal, highlight, filter, reorder, zoom, annotate, accumulate, or morph.
4. **Use scroll only when sequence matters.** Sticky graphics are a storytelling mechanism, not a house style.
5. **Render, inspect, revise.** Visual QA is part of editing.
6. **Mobile is its own editorial layout.** Do not merely shrink desktop.
7. **Accessibility is part of correctness.** Essential conclusions cannot depend on hover or motion alone.

## Checks and build

```bash
npm run check:skill
npm run build
npm run preview
```

`check:skill` runs the sample pipeline, validation, unit tests, and static preflight.

The project uses Svelte 5, SvelteKit, Vite, and D3-compatible tooling inherited from the upstream starter.

## Licensing and attribution

- Upstream starter: [`the-pudding/svelte-starter`](https://github.com/the-pudding/svelte-starter), MIT License.
- v2 skill instructions, scripts, examples, and demo additions: MIT License under this repository.
- The Pudding name is used only for attribution and to describe the editorial inspiration. No affiliation is implied.
