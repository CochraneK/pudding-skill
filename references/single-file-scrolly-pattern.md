# Single-file scrolly pattern

This pattern captures the transferable interaction grammar learned from the supplied `学术的浪费-滚动交互报告.html`. It is a **structural reference**, not a source of factual claims, visual identity, prose, or data.

The source page demonstrates a compact browser-native scrollytelling system: a full-viewport hero, a sticky graphic frame, long narrative steps, `IntersectionObserver` state changes, SVG render functions, lightweight range-input parameterization, a closing band, and a mobile fallback. Learn those mechanics without copying its unverified estimates or treating its styling as a Pudding house style.

## What to copy conceptually

```text
full-height hook
→ short framing prose
→ sticky visual frame + narrative steps
→ one complete visual state per step
→ optional parameter step
→ contrast / consequence sequence
→ reflective closing
→ method / caveat / source ledger
```

This is a useful **scrolly shell** when the same visual frame benefits from sequential transformation. It is not the default answer for every story. The concept board and prototype tournament can still select a static or explorable form instead.

## 1. Hero as a scale-setting instrument

The hero should do one editorial job, usually establishing scale or urgency.

Useful ingredients:

- `min-height: 100svh` or an equivalent full-viewport frame;
- one headline and one claim-bearing number;
- one short deck explaining why the number matters;
- optional progressive count-up only when it reinforces scale;
- optional lightweight ticker when its rate is an audited model;
- a scroll cue that disappears from importance once the reader starts.

Do **not** present a modelled ticker as a live database feed. Label whether it is observed, derived, modelled, or assumed.

## 2. Sticky graphic + narrative step rail

Desktop layout:

```text
┌──────────────────────┬───────────────────┐
│                      │ step 1            │
│   sticky graphic     │                   │
│   same frame         │ step 2            │
│   changes by state   │                   │
│                      │ step 3            │
└──────────────────────┴───────────────────┘
```

Canonical CSS shape:

```css
.scrolly {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(18rem, .8fr);
  gap: clamp(2rem, 6vw, 6rem);
  align-items: start;
}

.graphic {
  position: sticky;
  top: 0;
  height: 100svh;
  display: grid;
  align-items: center;
}

.step {
  min-height: 88svh;
  display: flex;
  align-items: center;
}
```

The graphic may be SVG, HTML, Canvas, or a Svelte component. Prefer SVG for modest vector mark counts because it is inspectable, responsive, and accessible.

## 3. State machine: every step must be complete

The supplied HTML uses `IntersectionObserver` to choose a renderer from `data-viz`. The transferable rule is stronger than that implementation detail:

> Every step defines the complete visual state required for that step.

Do not write transitions that only work if step 2 has already played before step 3. Readers scroll backward, jump with anchors, resize, restore tabs, and enter mid-page.

A production state should be describable as:

```json
{
  "id": "capacity-gap",
  "operation": "compare",
  "claim_refs": ["claim-04"],
  "graphic_state": "capacity-gap",
  "annotation": "...",
  "text_equivalent": "..."
}
```

Use stable step IDs rather than coupling editorial meaning to array positions.

## 4. Natural scroll detection

Use browser-owned scrolling. Prefer `IntersectionObserver` or Scrollama-style observation.

Recommended behavior:

- no wheel interception;
- no forced `scrollTo` during ordinary reading;
- no fake internal scroll container;
- root margin around the middle reading band, e.g. `-40% 0px -40% 0px`;
- set the active state directly from the intersecting step;
- initialize a valid first state before observation begins.

The reusable repository component is `src/components/ScrollyShell.svelte`.

## 5. Renderer registry instead of one giant conditional

The source HTML maps step types to render functions. Preserve that idea in Svelte with explicit state components, snippets, or a renderer registry.

Conceptually:

```js
const renderers = {
  establish: renderEstablish,
  compare: renderCompare,
  uncertainty: renderUncertainty,
  consequence: renderConsequence
};
```

This is preferable to accumulating dozens of unrelated `if (activeIndex === ...)` branches.

Names should describe the **editorial operation or evidence state**, not decorative chart names.

## 6. Parameter steps: make assumptions visible

The supplied HTML places range sliders directly inside selected sticky states. This is valuable when the story contains a genuine sensitivity question.

Good parameter interaction:

```text
assumption
→ reader changes value
→ only derived quantities respond
→ source / assumption status stays visible
→ conclusion shows how sensitive it is
```

Bad parameter interaction:

```text
slider exists because interaction feels impressive
```

Requirements:

- the default value is defensible and documented;
- min/max are justified;
- every output affected by the parameter is labelled as derived/scenario;
- the core observed evidence remains visually distinct;
- range controls receive an accessible label and a mobile touch target;
- interaction never converts missing values into zero or invents evidence.

## 7. Progress bar is navigation feedback, not evidence

A 2–3px top progress bar is acceptable as lightweight reading feedback. It must not be used as a chart encoding or suggest analytical precision.

Use passive scroll listeners or CSS scroll-driven animation when browser support requirements permit.

## 8. Chapter rhythm

A strong long-form sequence alternates density:

```text
hero
→ prose reset
→ scrolly evidence
→ short interlude / statement
→ scrolly evidence
→ reflective closing
→ methodology / evidence ledger
```

Do not make every viewport a chart. Empty space, prose, and visual resets are editorial tools.

## 9. Dark closing band

The supplied HTML changes palette for the closing section. The transferable function is not the dark color itself; it is the **mode change**:

- stop introducing new evidence;
- summarize what the reader should now believe;
- distinguish findings from values/recommendations;
- end with a question, implication, or action only if supported;
- immediately follow with method, caveats, and sources.

Do not hide caveats in a visually de-emphasized footer if they materially qualify the main claim.

## 10. Mobile transformation

Desktop sticky scrolly does not automatically deserve mobile sticky scrolly.

Default mobile adaptation for this pattern:

```text
sticky visual shortened to ~43–56svh
+ narrative cards stack below/over it
+ controls become full width
+ multi-column closing content becomes one column
```

If the graphic becomes illegible, switch to stacked static states instead. The same conclusion must survive without desktop hover or long viewport height.

## 11. Reduced motion

When `prefers-reduced-motion: reduce`:

- remove decorative drift, bobbing, pulsing, and long interpolation;
- state changes may be instantaneous;
- never remove the evidence, annotations, or selected state;
- count-up/ticker animation should not be required to learn the number.

## 12. Accessibility contract

At minimum:

- step text remains ordinary semantic HTML;
- the active state is not conveyed only by opacity/color;
- every chart state has a nearby textual conclusion;
- controls have labels and keyboard operation;
- focus targets are at least practical touch size on mobile;
- sources/caveats are HTML, not burned into SVG only;
- no information is available only on hover;
- sticky visuals do not cover focused content.

## 13. Evidence-status badges

The source HTML is visually compelling but mixes observations and Fermi assumptions too aggressively. The skill should **improve** this when replicating the structure.

For material numbers, expose one of:

- `OBSERVED`
- `LITERATURE ESTIMATE`
- `DERIVED`
- `SCENARIO`
- `ASSUMPTION`

A dramatic number is not allowed to shed its status badge just because it is in a hero, sticky graphic, or closing statement.

## 14. Do not copy these source-specific liabilities

Do not learn the following as reusable patterns:

- hard-coded publication counts as universal truth;
- calling a wide-database estimate “measured” without preserving database scope;
- converting subjective `useful / useless / harmful` buckets into factual global counts;
- presenting stylized expert-perspective text as direct quotations;
- translating speculative opportunity cost into guaranteed alternate social value;
- extrapolating retraction growth as a forecast without scenario labels.

These are content/evidence issues, not interaction requirements.

## 15. When the pattern wins the tournament

If a guided sticky concept wins, production handoff should explicitly preserve:

```json
{
  "form": "guided-scrolly",
  "interaction_job": "stage one evidence transformation at a time while preserving spatial context",
  "must_preserve": [
    "one stable graphic frame",
    "complete re-entrant states",
    "claim status visible at point of use",
    "mobile textual equivalence"
  ],
  "must_not_reintroduce": [
    "scroll-jacking",
    "decorative controls",
    "hover-only evidence",
    "unlabelled modelled counters"
  ]
}
```

If a static concept wins, this pattern remains a learned option and should **not** be forced into production.

## 16. QA checklist

For every story using this pattern, capture and inspect:

- hero desktop/mobile;
- first, middle, and final sticky steps;
- backward-scroll state restoration;
- one parameter default and one changed value;
- short phone viewport and tall phone viewport;
- keyboard focus on controls;
- reduced-motion rendering;
- no horizontal overflow;
- source/caveat visibility;
- direct entry to a mid-page anchor if anchors are supported.

A scrolly is complete only when the scroll mechanics, the evidence contract, and the mobile reading experience all survive QA.