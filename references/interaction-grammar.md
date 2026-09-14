# Interaction grammar

`pudding-skill` treats interaction as an editorial operation, not decoration. A page is not “Pudding-like” merely because it contains charts, hover states, or animation.

## Core pattern: guide → hand off

The preferred pattern for a genuinely interactive visual essay is:

```text
question
  ↓
reader baseline
  ↓
guided scrollytelling
  same graphic, explicit states
  one argument per step
  ↓
editorial handoff
  ↓
reader exploration
  filters / hover / click / lookup
  ↓
method + caveat + provenance
```

The guided section teaches the reader how to read the evidence before the explorable asks them to make their own comparisons.

A supplied single-file HTML visual essay has also been distilled into `references/single-file-scrolly-pattern.md`. Read that reference when a guided sticky-scroll concept wins the prototype tournament or when a user explicitly provides an HTML scrolly whose **interaction mechanics** should be learned. The reusable implementation shell is `src/components/ScrollyShell.svelte`.

Learn structure—full-height hook, sticky frame, step rail, re-entrant renderer states, parameter sensitivity steps, chapter rhythm, closing mode change, and mobile transformation—without copying source-specific numbers, prose, styling, expert quotations, or unsupported assumptions.

## What earns scroll

Use sticky scrollytelling only when the same visual frame benefits from sequential transformation. Good reasons include:

- preserving spatial context while one comparison changes;
- revealing one layer at a time;
- moving overview → subset → annotation → conclusion;
- making a transition itself teach something;
- reducing cognitive load by staging a dense visual.

Do not use sticky scroll for a simple ranking, lookup table, or a set of unrelated charts.

## State contract

Every scroll state must be explicit and re-entrant. A reader may jump from step 1 to step 4, scroll backwards, resize the browser, or enter halfway down the page.

Each state should therefore define the complete visual state it needs rather than relying on a previous animation having finished.

At minimum record:

- stable step ID;
- narrative operation (`establish`, `reveal`, `compare`, `highlight`, `zoom`, `annotate`, `morph`);
- claim/evidence references;
- marks visible;
- marks emphasized/de-emphasized;
- annotation text;
- axis/domain changes;
- transition meaning;
- evidence status (`OBSERVED`, `LITERATURE ESTIMATE`, `DERIVED`, `SCENARIO`, or `ASSUMPTION`) for material numbers;
- textual equivalent of the visual conclusion.

Do not let a dramatic hero or sticky state strip away the evidence status that would have been visible in a table or methodology section.

## No scroll-jacking

Observe natural scrolling. Never take over wheel/touch movement, force a scroll position, or create a fake scroll container solely for effect.

IntersectionObserver or Scrollama-style step detection is preferred because it lets the browser own scroll physics.

`ScrollyShell.svelte` follows this contract: it observes semantic step sections, selects the most visible intersecting step, exposes stable `data-step-id` markers, and never intercepts scrolling.

## Guide, then explore

When a story includes a free explorer, do not lead with the dashboard unless lookup itself is the story.

A common sequence is:

1. guided state establishes scale;
2. guided state reveals the key comparison;
3. guided state explains the relevant caveat;
4. reader receives controls using the same data/definitions;
5. missingness, reporting year, and uncertainty remain visible during exploration.

The explorable may offer metric switching, hover, click-to-pin, filtering, or search, but the controls must serve a question rather than maximize feature count.

The guide → explore sequence is **not mandatory**. If the tournament selects a static form, do not add a scrolly or explorer merely because reusable components exist. If the guided scrolly wins but free exploration adds no reader value, end with method/source material instead of inventing a dashboard.

## Interaction must not change the evidence contract

Interaction can change which verified evidence is shown. It must not create new numerical meaning without verification.

Examples:

- switching from psychiatrists to nurses is a view change;
- filtering to a region is a view change if the underlying rows are unchanged;
- computing a new ratio or aggregate is a new claim and must pass claim verification;
- turning missing values into zero is never a harmless view change.

Parameter sliders deserve additional scrutiny. They are appropriate for sensitivity analysis only when the parameter is an explicit assumption or user preference, its defensible range is documented, and every resulting value remains visibly `DERIVED`, `SCENARIO`, or `ASSUMPTION`. A slider is not evidence.

## Mobile

Decide deliberately whether the mobile version should keep the scrolly or stack the states.

Keep sticky scroll when transitions are central to understanding. Stack when the interaction is mostly flourish or when the graphic cannot remain legible in a short mobile viewport.

For a mobile sticky version:

- shorten the sticky graphic to roughly 43–56svh rather than consuming the whole viewport;
- keep the visual frame simpler than desktop;
- use opaque or near-opaque step cards over/below the sticky visual;
- preserve a textual conclusion in every step;
- make range/choice controls full-width with practical touch targets;
- test short and tall phone viewports;
- avoid controls that depend on hover.

## Reduced motion

`prefers-reduced-motion` should remove or greatly reduce interpolation without removing information. The state change may be instantaneous; the conclusion must still be legible.

Decorative count-ups, pulsing indicators, floating paper motifs, bobbing scroll cues, and continuous belt/wave animations should stop or collapse to their final state under reduced motion. A reader should never need animation to learn a number.

## Accessibility

- interactive SVG regions need accessible names when keyboard focusable;
- every mouse interaction needs an equivalent touch/keyboard path when it carries information;
- hover is an enhancement, not the sole access path;
- for dense maps, prefer hover as a desktop enhancement and provide a select/search/pin control for keyboard and touch rather than making every tiny geography a fake button;
- pinned/selected state must be visible without relying on color alone where practical;
- dynamic visual state changes should not spam live regions;
- step conclusions remain semantic HTML even when the graphic is SVG/Canvas;
- active-step styling should not rely only on low opacity for meaning;
- source and caveat text remain regular HTML;
- sticky graphics must not cover focused controls or text.

## Bilingual interaction

Language is presentation state, not data state. Switching language must never reset the selected metric, country, scroll state, or underlying evidence.

Keep reusable translation state separate from numeric datasets. For public reports, prefer one shared route with a language switch over duplicate `/zh` and `/en` copies unless SEO/localization requirements demand separate routes.

The public report registry may store localized metadata as:

```json
{
  "title": {
    "zh": "世界的隐形负担",
    "en": "The world's invisible burden"
  }
}
```

Persist the reader's language preference locally and allow a `?lang=zh|en` URL parameter for sharing.

## Chapter rhythm

Long interactive reports benefit from deliberate density changes:

```text
full-height hook
→ prose reset
→ guided sticky evidence
→ interlude / statement
→ guided or static evidence
→ reflective closing
→ method + evidence ledger
```

Do not make every viewport a chart. A palette or background-mode change can mark a narrative transition, but visual drama must not substitute for a new evidence state.

## QA

For a guided story, browser QA should cover at least:

- hero/default state;
- first guided state;
- a middle guided state;
- final guided state;
- backward-scroll state restoration;
- explorable default state when an explorer exists;
- one changed metric/filter or parameter state when controls exist;
- mobile and desktop;
- short and tall mobile viewports;
- keyboard focus through controls;
- reduced motion;
- no horizontal overflow;
- missing-data state where relevant;
- source/caveat visibility;
- both languages for critical public copy when bilingual.

A passing screenshot score does not prove the interaction works editorially. An editor/agent should still answer:

1. Does every interaction teach or enable a meaningful comparison?
2. Does the reader know what changed and why?
3. Does the page hand off control at the right moment—or correctly avoid a handoff when exploration is unnecessary?
4. Can the same conclusion be understood on mobile and with reduced motion?
5. Are uncertainty, dates, evidence status, and missingness still visible when the reader interacts?
6. Can every sticky state be entered directly and reconstructed without depending on a previous animation?

## Current repository references

- `src/components/ScrollyShell.svelte` is the generic, evidence-neutral sticky-scroll shell learned from the supplied single-file HTML interaction pattern.
- `references/single-file-scrolly-pattern.md` documents the full replication grammar and the source-specific liabilities that must **not** be copied.
- `src/components/GlobalMentalHealthScrolly.svelte` remains a historical guided implementation example, but the production global-mental-health story deliberately selected a static winner in its prototype tournament. Its existence is therefore evidence that a reusable scrolly component is an option, not a production default.
- `src/components/GlobalMentalHealthExplorer.svelte` remains an example of secondary reader-controlled depth; in current production it belongs on the optional Atlas route rather than the primary argument path.
