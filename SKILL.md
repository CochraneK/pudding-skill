---
name: pudding-scrolly
description: Turn a research question and dataset into an editorial, data-driven web story. Use when the user asks for Pudding-inspired scrollytelling, interactive data journalism, annotated charts, visual explainers, or a narrative visualization built with Svelte.
---

# Pudding Scrolly

Build **Pudding-inspired editorial data stories**, not visual clones of The Pudding. Reproduce the editorial reasoning: a clear question, defensible evidence, purposeful visual encodings, progressive disclosure, restrained annotation, and strong mobile behavior.

## Core rule

Do not start by choosing a chart or generating Svelte. First establish the claim the data can support.

Use this sequence:

1. **Audit the input** — inspect files, fields, types, missingness, ranges, duplicates, units, and analytical grain.
2. **Find the story** — identify the strongest defensible insight and its supporting evidence. If no insight is supported, say so rather than fabricating one.
3. **Design narrative beats** — turn the insight into a short progression: hook → baseline → reveal → comparison/explanation → conclusion.
4. **Choose the visual grammar** — select a visual and interaction because it serves a narrative operation, not because it looks impressive.
5. **Implement** — build the smallest Svelte experience that communicates the story well.
6. **Validate** — check data claims, rendering, mobile layout, accessibility, reduced motion, and source/annotation clarity.

Read `references/editorial-workflow.md` for the full decision process, `references/visual-grammar.md` for chart/interaction selection, `references/story-spec.md` for the analysis/rendering contract, and `references/quality-rubric.md` before delivery.

## Inputs

Accept any combination of:

- CSV/TSV/JSON data
- a research question or hypothesis
- prose notes or an article draft
- an existing chart or page to redesign
- links/sources supplied by the user

When structured data is available, begin with the deterministic baseline:

```bash
python scripts/profile_data.py path/to/data.csv
python scripts/derive_story.py path/to/data.csv --question "Your research question" --output generated/story-spec.json
python scripts/validate_story.py generated/story-spec.json
```

Or run the full baseline pipeline:

```bash
python scripts/pipeline.py path/to/data.csv --question "Your research question"
```

The pipeline writes a profile, a story spec, and `src/data/auto-story.json` for the generic `/generated` renderer. Treat the derived spec as a grounded starting point, **not** as finished editorial judgment. Review field semantics, units, denominators, and whether the heuristic insight is actually meaningful. Never infer column meaning solely from a field name when units or semantics are ambiguous.

## Story specification

Before implementation, create a compact story spec. Use `examples/story-spec.example.json` as a schema-by-example. The spec must contain:

- `question`
- `audience`
- `primary_insight`
- `evidence`
- `beats`
- `visuals`
- `sources`
- `caveats`

Validate it with:

```bash
python scripts/validate_story.py path/to/story.json
```

If validation fails, fix the story spec before generating the page.

## Narrative operations

Think in operations before chart names:

- **establish** — give the reader a baseline
- **compare** — show meaningful differences
- **reveal** — introduce the central change or surprise
- **highlight** — direct attention to a subset or outlier
- **filter** — remove irrelevant marks or categories
- **reorder** — make rank or structure legible
- **zoom** — move from overview to detail
- **annotate** — attach interpretation to evidence
- **accumulate** — show a quantity building over time
- **morph** — change representation only when the transition teaches something

Do not default to scrollytelling. A static annotated chart, small multiples, stepper, map, or explorable can be the better editorial form.

## Scrollytelling decision

Use sticky scroll only when at least one is true:

- the same visual needs several sequential transformations;
- the reader must preserve spatial context while the argument advances;
- staged annotation materially reduces cognitive load;
- the story depends on a meaningful reveal.

Avoid scrollytelling when the reader mainly needs comparison, lookup, or free exploration.

## Implementation constraints

- Prefer semantic HTML and lightweight Svelte state.
- Use SVG for modest vector charts; Canvas only when mark count requires it.
- Keep chart state derivable from data + active narrative beat.
- Separate data transforms from rendering code.
- Label important values directly when practical.
- Provide textual equivalents for essential visual conclusions.
- Support keyboard focus and `prefers-reduced-motion`.
- Design mobile intentionally; do not merely shrink the desktop layout.
- Do not hotlink proprietary Pudding fonts, logos, or brand assets.
- Attribute upstream code when derived from third-party starters.

## Visual restraint

A Pudding-inspired page is not defined by a serif font or a sticky panel. Favor:

- one strong visual idea per section;
- generous whitespace;
- high information hierarchy;
- muted context with selective emphasis;
- annotations near the marks they explain;
- short prose steps;
- transitions that encode meaning rather than decoration.

## Baseline renderer

The generic renderer exists to prove the pipeline end to end. It currently supports bar charts (including derived change-gap comparisons), line charts, scatterplots, and histograms. Use `/generated` to inspect the output.

Do **not** confuse baseline rendering with final design. Once the story spec is validated, replace the generic chart with bespoke Svelte when the editorial idea benefits from a stronger visual metaphor, richer annotation, small multiples, meaningful scroll transformations, or reader exploration. Keep the story spec as the source of truth.

## Delivery checklist

Before declaring the story complete:

1. Re-run `scripts/validate_story.py`.
2. Run `python scripts/qa_story.py --root .`.
3. Run the Python unit tests (`npm run test:skill`).
4. Build the Svelte project with `npm run build`.
5. Inspect desktop and mobile widths.
6. Verify every quantitative sentence against the transformed data.
7. Test the first screen without scrolling: the topic and reading direction should be obvious.
8. Test with reduced motion.
9. Confirm there are no Pudding logos, proprietary fonts, or misleading claims of affiliation.

If any check fails, revise before delivery.
