# Story spec contract

The story spec is the boundary between **analysis/editorial reasoning** and **rendering**. Keep it small enough to inspect in code review and structured enough to audit.

## Required fields

- `question`: the answerable research question.
- `audience`: who the story is for.
- `primary_insight`: one defensible sentence supported by evidence.
- `evidence`: structured facts or concise evidence statements.
- `beats`: at least three narrative steps with `operation` and `purpose`.
- `visuals`: selected visual forms with `type`, `purpose`, and `operation`.
- `sources`: source labels/paths/URLs as appropriate.
- `caveats`: limitations the reader should know.

## Optional machine-generated fields

- `production_mode`: `annotated-static`, `small-multiples`, `scrollytelling`, or `explorable`.
- `fields`: raw rendering keys such as x/y/category/series or a named derived calculation.
- `field_metadata`: human labels, roles, units, and descriptions from the data contract.
- `data_notes`: dataset-level semantic notes.
- `selection`: candidate id, rank, score components, risk penalty, and deterministic rationale.

## Evidence objects

Prefer structured evidence so calculations can be audited. Current baseline kinds include:

- `change`
- `change_gap`
- `group_mean`
- `correlation`
- `distribution`

`scripts/verify_claims.py` recomputes these values from raw data. A quantitative spec that fails the claim audit must not be delivered.

## Renderer contract

`scripts/generate_story.py` turns a valid story spec + source data into `src/data/auto-story.json`. `src/components/AutoStory.svelte` renders the baseline bundle.

The generic renderer currently supports bar/change-gap bars, line charts, scatterplots, and histograms. It is intentionally conservative. Once the baseline is correct, an agent may replace it with a bespoke editorial visualization while preserving the story spec and claim audit as sources of truth.
