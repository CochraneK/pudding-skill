---
name: pudding-scrolly
description: Turn a research question and dataset into an evidence-audited editorial web story. Use for Pudding-inspired data journalism, scrollytelling, annotated charts, interactive explainers, or narrative visualization in Svelte.
---

# Pudding Scrolly

Build **Pudding-inspired editorial data stories**, not visual clones of The Pudding. Reproduce the useful reasoning pattern: question → evidence → competing story directions → editorial choice → visual grammar → implementation → verification.

## Core rule

Do not start by choosing a chart or generating Svelte. First establish what the data can support, compare plausible story directions, and make the numerical evidence auditable.

Use this sequence:

1. **Audit input** — inspect fields, types, missingness, duplicates, ranges, units, analytical grain, and source limitations.
2. **Resolve semantics** — use a data contract when roles/units are ambiguous. Never infer meaning from field names alone when that could change the claim.
3. **Generate candidates** — derive multiple defensible analytical directions instead of stopping at the first matching chart pattern.
4. **Rank, then judge** — use deterministic scoring for triage; apply editorial/domain judgment before publication.
5. **Select with fallback** — reject candidates that fail story-spec, quality, or renderer gates and try the next one.
6. **Design narrative beats** — hook → baseline → reveal → comparison/explanation → conclusion.
7. **Choose visual grammar** — visual form follows analytical task and narrative operation.
8. **Verify claims independently** — recompute quantitative evidence from raw data.
9. **Implement and inspect** — build the smallest Svelte experience that communicates the chosen story clearly.
10. **Validate delivery** — data claims, build, mobile layout, accessibility, reduced motion, sourcing, and attribution.

Read:

- `references/editorial-workflow.md` for editorial sequencing;
- `references/editorial-scoring.md` for candidate ranking limits;
- `references/data-contract.md` for explicit field semantics;
- `references/visual-grammar.md` for visual selection;
- `references/story-spec.md` for the analysis/rendering contract;
- `references/claim-audit.md` for numeric verification;
- `references/quality-rubric.md` before delivery.

## Preferred structured-data workflow

When data is available, use the full pipeline:

```bash
python scripts/pipeline.py path/to/data.csv \
  --question "Your research question" \
  --schema path/to/data-schema.json
```

`--schema` is optional but recommended when labels, units, time fields, identifiers, or measures are not self-evident.

The pipeline writes:

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

Use `/lab` to inspect the ranked candidate board and audit trail. Use `/generated` to inspect the selected baseline story.

## Candidate policy

Candidate scores are deterministic proxies for evidence strength, coverage, effect size, distinctiveness, visual fit, simplicity, question alignment, and known risk penalties.

Do **not** describe the score as newsworthiness or truth. It cannot assess social significance, novelty in the world, ethics, fairness, causal validity, or domain importance. The agent/editor must review those dimensions.

If the top candidate is semantically weak despite scoring well, choose another candidate and document why.

## Story specification

Before bespoke implementation, maintain a valid story spec containing at least:

- `question`
- `audience`
- `primary_insight`
- `evidence`
- `beats`
- `visuals`
- `sources`
- `caveats`

Generated specs also include selection metadata and, when supplied, field metadata. Validate with:

```bash
python scripts/validate_story.py generated/story-spec.json
python scripts/verify_claims.py generated/story-spec.json path/to/data.csv
```

If either fails, do not continue to publication output.

## Narrative operations

Think in operations before chart names:

- **establish** — give the reader a baseline;
- **compare** — show meaningful differences;
- **reveal** — introduce the central change or surprise;
- **highlight** — direct attention to a subset or outlier;
- **filter** — remove irrelevant marks/categories;
- **reorder** — make rank or structure legible;
- **zoom** — move overview → detail;
- **annotate** — attach interpretation to evidence;
- **accumulate** — show a quantity building;
- **morph** — change representation only when the transition teaches something.

Do not default to scrollytelling. A static annotated chart, small multiples, stepper, map, or explorable can be better.

## Scrollytelling decision

Use sticky scroll only when at least one is true:

- the same visual needs several sequential transformations;
- the reader must preserve spatial context while the argument advances;
- staged annotation materially reduces cognitive load;
- the story depends on a meaningful reveal.

Avoid it for simple lookup, ranking, or free exploration.

## Implementation constraints

- Prefer semantic HTML and lightweight Svelte state.
- Separate transforms from rendering code.
- Use SVG for modest vector charts; Canvas only when mark count requires it.
- Label important values directly when practical.
- Provide textual equivalents for essential visual conclusions.
- Support keyboard focus and `prefers-reduced-motion`.
- Design mobile intentionally; do not merely shrink desktop.
- Keep raw field keys separate from human labels/units.
- Do not hotlink proprietary Pudding fonts, logos, or brand assets.
- Attribute upstream code when derived from third-party starters.

## Baseline vs publication design

The generic renderer is a correctness baseline, not a final art direction. Once the story spec and claim audit pass, replace it with bespoke Svelte when the editorial idea benefits from stronger annotation, small multiples, a meaningful visual metaphor, scroll transformations, or exploration.

When replacing the renderer, preserve the underlying evidence calculations and rerun the claim audit.

## Delivery checklist

Before declaring the story complete:

1. Validate the data contract when present.
2. Review the candidate board and justify the selected direction.
3. Re-run `scripts/validate_story.py`.
4. Re-run `scripts/verify_claims.py` against the raw data.
5. Run `python scripts/qa_story.py --root .`.
6. Run unit tests (`npm run test:skill`).
7. Build with `npm run build`.
8. Inspect desktop and mobile widths.
9. Verify every quantitative sentence against structured evidence.
10. Test the first screen without scrolling.
11. Test reduced motion and keyboard use.
12. Confirm source attribution, caveats, and non-affiliation language.

If any hard check fails, revise before delivery.
