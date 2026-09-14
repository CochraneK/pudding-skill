# Production handoff contract

A prototype tournament is not complete when a winner is merely named. The production implementation must preserve **why the winner won** and must not quietly reintroduce the losing interaction pattern after polish begins.

This stage sits between `prototype-tournament.json` and production Svelte.

## Purpose

The handoff contract makes the editorial decision executable. It records:

- the selected form and primary interaction job;
- the narrative beat order that production must preserve;
- the material claims and evidence tokens that must remain directly visible;
- useful lessons borrowed from losing concepts without importing their rejected interaction machinery;
- optional secondary-depth routes that must not become prerequisites for first-pass comprehension;
- interaction jobs and source-level implementation tokens that are forbidden from returning to the primary story.

The contract is intentionally narrower than a design system. It does not prescribe typography, spacing, animation curves, or visual style. It protects the editorial job that survived the tournament.

## Tournament schema

A `SELECT` or `COMBINE` decision that proceeds to production should include `decision.production_contract`:

```json
{
  "route": "/stories/example",
  "primary_form": "annotated_static",
  "primary_interaction_job": "none",
  "required_sequence": ["need", "priority", "capacity"],
  "required_claims": [
    {
      "id": "main-gap",
      "tokens": ["1,647×", "$0.04", "$65.89"]
    }
  ],
  "borrowed_lessons": [
    {
      "from_concept_id": "guided-alternative",
      "keep": "the editorial sequence",
      "reject_interaction_job": "reveal"
    }
  ],
  "optional_depth": [
    {
      "from_concept_id": "explorer-alternative",
      "route": "/stories/example/atlas",
      "interaction_job": "compare"
    }
  ],
  "forbidden_primary_interaction_jobs": ["reveal", "compare"],
  "forbidden_source_tokens": ["OldScrolly", "OldExplorer"]
}
```

`required_claims.tokens` should be minimal, material evidence strings that a reader must be able to see without operating the optional depth layer. Do not put decorative copy into this list.

## Compile

Normalize the tournament decision into a committed production artifact:

```bash
python scripts/production_handoff.py compile \
  stories/example/prototype-tournament.json \
  --output stories/example/production-contract.json
```

The compiled artifact includes a SHA-256 fingerprint over the story id, tournament outcome, selected concepts, and structured production contract. If the tournament decision changes, the committed production contract becomes stale and validation fails.

## Source validation

Production should expose explicit semantic markers rather than forcing the validator to infer editorial intent from class names:

```html
<section
  data-production-winner="static-gap-atlas"
  data-primary-interaction="none"
>
  <article data-story-beat="need" data-claim-id="need-scale">…</article>
  <article data-story-beat="priority" data-claim-id="public-priority">…</article>
  <article data-story-beat="capacity" data-claim-id="spending-gap">…</article>
</section>
```

Borrowed and optional concepts should also be named:

```html
<div data-borrowed-from="care-capacity-ladder">…</div>
<section data-optional-depth="country-capacity-explorer">…</section>
```

Validate the committed contract and source together:

```bash
python scripts/production_handoff.py validate \
  stories/example/prototype-tournament.json \
  stories/example/production-contract.json \
  --source src/routes/stories/example/+page.svelte
```

A passing result is `PRODUCTION_ALIGNED`.

## Browser validation

Source validation catches obvious drift before a build. CI must also validate the rendered page because framework composition can reintroduce controls or hide required evidence.

```bash
npm run qa:production-contract -- \
  --base-url http://127.0.0.1:4173 \
  --contract stories/example/production-contract.json
```

The browser gate checks the production route at a mobile viewport and verifies:

- the runtime winner and interaction markers match the tournament;
- required beats appear in the required order;
- every required claim contains its evidence tokens;
- a `none` interaction winner does not contain primary buttons, selects, inputs, sliders, or equivalent controls;
- borrowed lessons are present as explicit handoff markers;
- optional-depth concepts are reachable through their declared route rather than being required to understand the main claim.

## Drift policy

If production needs to depart materially from the winner, do **not** weaken or delete the contract just to make CI pass. Choose one of these paths:

1. refine the implementation while keeping the same editorial job;
2. rerun the relevant prototypes and update the tournament decision with new screenshot evidence;
3. explicitly `PIVOT` if the winning concept no longer survives production constraints.

A production contract is evidence of a decision, not a permanent ban on redesign. It simply requires redesign to return through the decision process instead of happening invisibly in CSS or component selection.
