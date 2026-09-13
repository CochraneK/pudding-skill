# Story spec contract

The story spec is the boundary between **analysis/editorial reasoning** and **rendering**. Keep it small enough to inspect in a code review.

## Required fields

- `question`: the answerable research question.
- `audience`: who the story is for.
- `primary_insight`: one defensible sentence supported by evidence.
- `evidence`: structured facts or concise evidence statements.
- `beats`: at least three narrative steps. Generated specs should include `operation` and `purpose`.
- `visuals`: candidate or selected visual forms with `type`, `purpose`, and `operation`.
- `sources`: source labels/paths/URLs as appropriate.
- `caveats`: limitations the reader should know.

## Optional implementation fields

- `production_mode`: `annotated-static`, `small-multiples`, `scrollytelling`, or `explorable`.
- `fields`: rendering hints such as x/y/category/series fields or a named derived calculation.

## Evidence objects

Prefer structured evidence for generated stories so calculations can be audited. Current baseline kinds include:

- `change`
- `change_gap`
- `group_mean`
- `correlation`
- `distribution`

Do not treat these as an exhaustive schema. Agent-authored stories can use richer evidence, but quantitative claims should remain traceable to a data transformation.

## Renderer contract

`scripts/generate_story.py` turns a valid story spec + source data into `src/data/auto-story.json`. `src/components/AutoStory.svelte` renders the baseline bundle.

The generic renderer currently supports:

- bar / derived change-gap bars;
- line;
- scatter;
- histogram.

It is intentionally conservative. Once the baseline builds and communicates the evidence correctly, an agent may replace the generic component with a bespoke editorial visualization while preserving the story spec as the source of truth.
