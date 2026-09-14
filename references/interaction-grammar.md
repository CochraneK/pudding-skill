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

- narrative operation (`establish`, `reveal`, `compare`, `highlight`, `zoom`, `annotate`, `morph`);
- marks visible;
- marks emphasized/de-emphasized;
- annotation text;
- axis/domain changes;
- transition meaning;
- textual equivalent of the visual conclusion.

## No scroll-jacking

Observe natural scrolling. Never take over wheel/touch movement, force a scroll position, or create a fake scroll container solely for effect.

IntersectionObserver or Scrollama-style step detection is preferred because it lets the browser own scroll physics.

## Guide, then explore

When a story includes a free explorer, do not lead with the dashboard unless lookup itself is the story.

A common sequence is:

1. guided state establishes scale;
2. guided state reveals the key comparison;
3. guided state explains the relevant caveat;
4. reader receives controls using the same data/definitions;
5. missingness, reporting year, and uncertainty remain visible during exploration.

The explorable may offer metric switching, hover, click-to-pin, filtering, or search, but the controls must serve a question rather than maximize feature count.

## Interaction must not change the evidence contract

Interaction can change which verified evidence is shown. It must not create new numerical meaning without verification.

Examples:

- switching from psychiatrists to nurses is a view change;
- filtering to a region is a view change if the underlying rows are unchanged;
- computing a new ratio or aggregate is a new claim and must pass claim verification;
- turning missing values into zero is never a harmless view change.

## Mobile

Decide deliberately whether the mobile version should keep the scrolly or stack the states.

Keep sticky scroll when transitions are central to understanding. Stack when the interaction is mostly flourish or when the graphic cannot remain legible in a short mobile viewport.

For a mobile sticky version:

- keep the visual frame simpler than desktop;
- use opaque or near-opaque step cards over the sticky visual;
- preserve a textual conclusion in every step;
- test short and tall phone viewports;
- avoid controls that depend on hover.

## Reduced motion

`prefers-reduced-motion` should remove or greatly reduce interpolation without removing information. The state change may be instantaneous; the conclusion must still be legible.

## Accessibility

- interactive SVG regions need accessible names when keyboard focusable;
- every mouse interaction needs an equivalent touch/keyboard path when it carries information;
- hover is an enhancement, not the sole access path;
- pinned/selected state must be visible without relying on color alone where practical;
- dynamic visual state changes should not spam live regions;
- source and caveat text remain regular HTML.

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

## QA

For a guided + explore story, browser QA should cover at least:

- first guided state;
- a middle guided state;
- final guided state;
- explorable default state;
- one changed metric/filter state;
- mobile and desktop;
- keyboard focus through controls;
- reduced motion;
- no horizontal overflow;
- missing-data state;
- both languages for critical public copy.

A passing screenshot score does not prove the interaction works editorially. An editor/agent should still answer:

1. Does every interaction teach or enable a meaningful comparison?
2. Does the reader know what changed and why?
3. Does the page hand off control at the right moment?
4. Can the same conclusion be understood on mobile and with reduced motion?
5. Are uncertainty, dates, and missingness still visible when the reader explores?

The global mental-health story is the current reference implementation: `GlobalMentalHealthScrolly.svelte` demonstrates the guided sticky state machine, and `GlobalMentalHealthExplorer.svelte` demonstrates the same-page handoff into reader-controlled exploration.
