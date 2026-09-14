# Screenshot-driven visual refinement loop

v2.5 adds a bounded visual-review loop after data, claim, build, and browser-delivery gates.

The loop has four distinct responsibilities. Do not collapse them into one opaque "visual score".

## 1. Browser delivery QA

`browser_qa.mjs` remains the mechanical delivery gate. It checks runtime errors, network failures, overflow, basic accessibility structure, keyboard reachability, reduced motion, and writes desktop/mobile screenshots.

A PASS here means the page is mechanically healthy at the tested routes and viewports. It does **not** mean the composition is publication-ready.

## 2. Deterministic visual probe

Run against the same production preview:

```bash
npm run qa:visual-probe -- --base-url http://127.0.0.1:4173 --out .qa/visual-probe.json
```

The probe records observable browser facts such as:

- long-form copy measure in `em`;
- minimum copy font size and line-height ratio;
- heading-level jumps;
- mobile touch-target dimensions;
- clipped text containers;
- computed text/background contrast;
- chart/visual aspect ratios;
- first-visual position and sticky-element count.

These are diagnostics, not art direction.

## 3. Deterministic critic + agent screenshot review

Convert the probe into a review contract:

```bash
python scripts/pudding.py review .qa/visual-probe.json
```

This writes:

```text
.qa/visual-review.json
.qa/visual-review.md
```

The critic can classify measurable issues as error, warning, or info. CI may fail on errors, but warnings are review prompts by default.

Even a score of 100 still leaves `agent_review.status = PENDING`. An agent/editor must inspect every screenshot and judge qualities that browser metrics cannot establish reliably:

- whether the first screen earns attention;
- hierarchy and editorial pacing;
- whitespace rhythm;
- annotation collisions or ambiguity;
- chart label legibility;
- whether mobile feels intentionally composed rather than merely unbroken;
- whether a visual metaphor is helping or distracting;
- whether the page feels over-designed or under-designed for the evidence.

Record screenshot observations using the schema embedded in `visual-review.json`. Claims about screenshots must point to visible evidence.

## 4. Bounded refinement

Plan refinements with:

```bash
python scripts/pudding.py refine .qa/visual-review.json \
  --agent-review .qa/agent-visual-review.json
```

The automatic allowlist is deliberately small:

- `tighten_copy_measure`
- `increase_text_leading`
- `increase_touch_targets`

To apply only those low-risk overrides:

```bash
python scripts/pudding.py refine .qa/visual-review.json \
  --agent-review .qa/agent-visual-review.json \
  --apply
```

This regenerates `src/styles/refinement.css`. The auto-refiner does not edit data, claims, chart transforms, arbitrary colors, Svelte structure, or bespoke layout logic.

Everything outside the allowlist is a manual/agent source edit.

## Before/after rule

Every applied refinement must be followed by:

1. production build;
2. browser delivery QA;
3. visual probe + critic;
4. inspection of the new screenshots;
5. comparison with the previous screenshots/report.

Keep a change only when it fixes the stated problem without introducing a regression.

The automatic loop stops after **two** refinement passes. If the page still needs work after that, treat the problem as an art-direction or component-design task rather than endlessly tuning global CSS.

## What this loop is not

It is not a substitute for a designer, editor, domain expert, or visual-capable agent. It is an evidence trail and a safe iteration protocol.

Never report "visual QA passed" solely because a deterministic score is high. Report mechanical status, deterministic findings, and screenshot-review verdict separately.
