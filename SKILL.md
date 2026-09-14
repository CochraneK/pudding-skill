---
name: pudding-scrolly
description: Turn a domain or industry question into an auditable research dossier when data is missing, then turn trustworthy structured evidence into an editorial web story, publication-ready first draft, and screenshot-reviewed visual experience. Use for industry research, source and numeric-evidence audits, data acquisition planning, Pudding-inspired data journalism, scrollytelling, annotated charts, interactive explainers, narrative visualization, or data-story prototyping in Svelte.
---

# Pudding Scrolly

Build **Pudding-inspired editorial data stories**, not visual clones of The Pudding. When trustworthy structured data does not yet exist, first build an auditable research dossier. Reproduce the useful reasoning pattern: question → research dossier when needed → evidence → competing story directions → contrastive concepts → cheap prototypes → screenshot tournament → editorial choice → visual grammar → independently verified claims → first draft → implementation → browser verification → screenshot review → bounded refinement.

## Core rule

Do not start by choosing a chart, writing a headline, or generating production Svelte. First establish what the data can support, compare plausible story directions, and make the numerical evidence auditable. After a concept board passes, prototype competing forms before committing to one implementation.

Use this sequence:

0. **Gate the concept when needed** — when work starts from a broad topic or ambitious bespoke story, run the Pudding DNA gate before expensive research/production. The valid result may be `CONTINUE`, `PIVOT`, `PIVOT_NONVISUAL`, or `PUT_DOWN`; the workflow is not required to ship a visual story.
1. **Research when data is missing** — if the surviving concept lacks a trustworthy dataset, build a research dossier: definitions → source map → primary evidence → numeric claims → conflict resolution → data acquisition plan. Do not invent a dataset to skip this step.
2. **Audit input** — inspect fields, types, missingness, duplicates, ranges, units, analytical grain, and source limitations.
3. **Resolve semantics** — use a data contract when roles/units are ambiguous. Never infer meaning from field names alone when that could change the claim.
4. **Generate candidates** — derive multiple defensible analytical directions instead of stopping at the first matching chart pattern.
5. **Rank, then judge** — use deterministic scoring for triage; apply editorial/domain judgment before publication.
6. **Select with fallback** — reject analytical candidates that fail story-spec, quality, or renderer gates and try the next one.
7. **Design narrative beats** — hook → baseline → reveal → comparison/explanation → conclusion.
8. **Contrast concepts** — before bespoke implementation, develop and validate 3–6 structurally different visual concepts, including a serious static/no-interaction alternative.
9. **Run a prototype tournament** — implement only the hardest claim-bearing moment for every concept, capture equivalent desktop/mobile screenshots, score them with interaction-neutral criteria, apply hard gates, then `SELECT`, `COMBINE`, `PIVOT`, or `PUT_DOWN`. Do not force a winner.
10. **Choose visual grammar** — recommend the best editorial form while preserving a deterministic baseline renderer.
11. **Verify claims independently** — recompute quantitative evidence from raw data.
12. **Generate a first-draft package** — headline, dek, sections, annotations, methodology, caveats, and claim provenance.
13. **Implement and inspect** — build the smallest production Svelte experience that communicates the tournament decision clearly.
14. **Validate delivery** — data claims, build, mobile layout, accessibility, reduced motion, sourcing, attribution, dependency gate, and real-browser QA.
15. **Review screenshots** — separate measurable browser evidence from visual/editorial judgment and inspect every desktop/mobile capture.
16. **Refine safely** — apply only bounded automatic fixes; use agent/manual source edits for art direction, then rerun the full browser/visual loop.
17. **Benchmark pipeline changes** — when candidate scoring, selection, claim verification, visual grammar, provenance, or tournament logic changes, run the curated regression corpus and explain any expectation change instead of weakening the gate.

Read:

- `references/pudding-dna.md` before committing an ambitious topic to a visual-story format; it defines the editorial gate, public-story study corpus, and continue/pivot/put-down policy;
- `references/research-dossier.md` when the user starts with a topic/question but lacks a trustworthy dataset;
- `references/editorial-workflow.md` for editorial sequencing;
- `references/editorial-scoring.md` for candidate ranking limits;
- `references/data-contract.md` for explicit field semantics;
- `references/concept-board.md` after evidence supports the argument and before any bespoke visual implementation;
- `references/prototype-tournament.md` immediately after the concept board passes; it defines the equal screenshot contract, interaction-neutral scoring, hard gates, and implementation handoff;
- `references/visual-grammar.md` for visual selection;
- `references/interaction-grammar.md` for guided scrollytelling, reader handoff, exploration, bilingual interaction, and no-scroll-jacking rules;
- `references/story-spec.md` for the analysis/rendering contract;
- `references/claim-audit.md` for numeric verification;
- `references/first-draft.md` for copy/provenance rules;
- `references/visual-refinement-loop.md` for screenshot review and bounded iteration;
- `references/benchmark.md` for the v2.6 regression corpus, scoring dimensions, and baseline policy;
- `references/quality-rubric.md` before delivery.

## Pudding DNA gate and study corpus

For a broad topic or bespoke visual essay, create a `story-concept.json` and run `python scripts/pudding.py pitch path/to/story-concept.json` before committing to production. A passing gate is only permission to investigate further. `PIVOT_NONVISUAL` and `PUT_DOWN` are successful editorial outcomes when the visual case or evidence path does not justify a story.

Study `benchmarks/pudding-study-corpus.json` with `npm run pudding:study` before choosing an interaction pattern. Learn transferable editorial operations across multiple public stories—question, human stake, evidence strategy, visual necessity, interaction job, reader handoff, caveat strategy—and never retrieve a nearest-neighbor layout or imitate Pudding typography, colors, jokes, CSS, or assets. The separate `benchmarks/pudding-dna-corpus.json` is synthetic and exists only to regression-test gate decisions.

## Contrastive concept board

Once research/data audit supports the argument, do not code the first plausible visual. Create a concept board with `python scripts/pudding.py concept init ...`, develop 3–6 complete directions, then run `python scripts/pudding.py concept validate generated/concept-board.json`. One direction must be a serious static/no-interaction alternative. A passing result is `READY_FOR_PROTOTYPE`, never automatic selection. Read `references/concept-board.md` for the contract.

A board is incomplete as a decision instrument until its concepts are actually compared. Do not silently drop the static direction, the least fashionable direction, or the concept that is harder to implement before the tournament. The purpose of this stage is to create genuine alternatives, not to decorate a choice already made.

## Prototype tournament

After `READY_FOR_PROTOTYPE`, create a tournament manifest:

```bash
python scripts/pudding.py tournament init generated/concept-board.json \
  --route /stories/example/prototypes \
  --output generated/prototype-tournament.json
```

Build only the **hardest claim-bearing moment** for every concept. Do not spend on headers, decorative motion, transitions, or a complete article. Give every concept the same screenshot contract at desktop and mobile widths, then judge the captures rather than the implementation effort already invested.

The canonical seven dimensions are:

- reader realization — can someone state the intended insight?
- evidence fidelity — are units, caveats, missingness, uncertainty, and provenance preserved?
- visual necessity — does the visual materially improve understanding over prose?
- interaction economy — does the chosen interaction level, including `none`, earn its complexity?
- reader effort — can the claim be understood without avoidable work or controls?
- mobile viability — does the same conclusion survive a narrow touch viewport?
- accessibility equivalence — is the evidence available without hover, motion, or vision-only cues?

`evidence_fidelity`, `mobile_viability`, and `accessibility_equivalence` are hard gates. A visually impressive prototype cannot compensate for failing them. A static prototype is not penalized for having no interaction; `none` can score highest when interaction adds work without adding understanding.

Once screenshots have been inspected and scores/notes recorded, validate the decision:

```bash
python scripts/pudding.py tournament validate generated/prototype-tournament.json --stage decision
```

CI or another evidence-bearing environment can additionally require every referenced screenshot to exist:

```bash
python scripts/pudding.py tournament validate generated/prototype-tournament.json \
  --stage evidence --evidence-root .
```

Valid outcomes are `SELECT`, `COMBINE`, `PIVOT`, and `PUT_DOWN`. Never force `SELECT` when every prototype is eliminated. A selected outcome must preserve explicit implementation constraints learned from the comparison so production polish does not erase why the concept won.

Read `references/prototype-tournament.md` for the full scoring and handoff contract.

## Research-first workflow

Use this when the user has a topic or industry question but no reliable structured dataset yet. The Agent performs the browsing/retrieval; the deterministic module records provenance and compiles the handoff.

```bash
python scripts/pudding.py research init \
  --topic "Global mental health" \
  --question "Where does treatment capacity lag behind need?"

# After the agent populates sources, claims, conflicts, and data targets:
python scripts/pudding.py research validate generated/research/research-dossier.json
python scripts/pudding.py research compile generated/research/research-dossier.json
```

The compiled research package contains `research-report.md`, `source-ledger.json`, `numeric-evidence.csv`, `data-acquisition-plan.md`, and the canonical `research-dossier.json`. Only VERIFIED and QUALIFIED numeric claims enter `numeric-evidence.csv`; conflict/lead-only/rejected figures remain visible but cannot silently become story input.

A material numeric claim should carry its value, unit, geography, period, population/denominator, source IDs, locator (page/table/figure/query), definition/method note, uncertainty when available, license note, status, and confidence. Prefer primary sources and preserve query parameters for dynamic data tools.

## Preferred structured-data workflow

The unified entry point is:

```bash
python scripts/pudding.py story path/to/data.csv \
  --question "Your research question" \
  --schema path/to/data-schema.json
```

The pipeline accepts CSV, TSV, row-oriented JSON, JSONL, and NDJSON. `--schema` is optional but recommended when labels, units, time fields, identifiers, or measures are not self-evident.

For focused work:

```bash
python scripts/pudding.py inspect path/to/data.jsonl
python scripts/pudding.py candidates path/to/data.csv --question "What changed?"
python scripts/pipeline.py path/to/data.csv --question "What changed?"
python scripts/pudding.py benchmark
```

The pipeline writes:

```text
generated/profile.json
generated/candidates.json
generated/story-spec.json
generated/selection-report.json
generated/evaluation.json
generated/claim-audit.json
generated/visual-plan.json
generated/story-draft.json
generated/story-draft.md
src/data/story-candidates.json
src/data/story-selection.json
src/data/story-evaluation.json
src/data/story-claim-audit.json
src/data/story-draft.json
src/data/auto-story.json
```

Use `/lab` to inspect the ranked candidate board and audit trail. Use `/generated` to inspect the selected baseline story. Use `/benchmark` to inspect the curated regression corpus and scoring contract.

## Candidate policy

Candidate scores are deterministic proxies for evidence strength, coverage, effect size, distinctiveness, visual fit, simplicity, question alignment, and known risk penalties.

Do **not** describe the score as newsworthiness or truth. It cannot assess social significance, novelty in the world, ethics, fairness, causal validity, or domain importance. The agent/editor must review those dimensions.

If the top candidate is semantically weak despite scoring well, choose another candidate and document why.

## Story specification

Before drafting or bespoke implementation, maintain a valid story spec containing at least:

- `question`
- `audience`
- `primary_insight`
- `evidence`
- `beats`
- `visuals`
- `sources`
- `caveats`

Generated specs also include selection metadata, visual-plan metadata, and, when supplied, field metadata. Validate with:

```bash
python scripts/validate_story.py generated/story-spec.json
python scripts/verify_claims.py generated/story-spec.json path/to/data.csv
```

If either fails, do not continue to publication output.

## First-draft contract

`story-draft.json` is an editable publication draft, not an authorization to publish. It must retain `status: EDITORIAL_REVIEW_REQUIRED` until editorial review is complete.

The draft includes:

- `headline` and `dek`;
- narrative sections with operations and `claim_refs`;
- a visual recommendation plus baseline renderer;
- annotations linked to structured evidence;
- methodology, source note, caveats, and data notes;
- a field glossary when metadata is present;
- `provenance.claims`, mapping quantitative copy back to evidence indices.

When rewriting quantitative copy, preserve the `claim_ref` if meaning is unchanged. If the number, comparison, aggregation, denominator, or causal implication changes, update structured evidence and rerun claim verification. Never introduce an unverified number just because it improves the prose.

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

Do not default to scrollytelling. A static annotated chart, dot plot, slopegraph, small multiples, stepper, map, or explorable can be better.

## Visual grammar policy

`visual_grammar.py` deliberately distinguishes:

- **recommended visual** — the editorial form that best matches the evidence/narrative operation;
- **baseline renderer** — the simpler chart that the deterministic Svelte renderer can build and QA today.

For example, change-gap evidence may recommend a slopegraph while retaining a ranked bar as the safe baseline.

Do not silently replace a passing baseline with a richer bespoke form unless that implementation can also pass build, accessibility, mobile, and browser QA. For bespoke stories that went through a concept board, the tournament decision is an additional constraint: the richer production form should implement the winning editorial job, not simply the easiest reusable component.

## Scrollytelling decision

Use sticky scroll only when at least one is true:

- the same visual needs several sequential transformations;
- the reader must preserve spatial context while the argument advances;
- staged annotation materially reduces cognitive load;
- the story depends on a meaningful reveal.

Avoid it for simple lookup, ranking, or free exploration.

When scrollytelling is justified, use a **guide → handoff → explore** contract by default: keep one stable graphic frame, make every scroll state explicit and re-entrant, advance one narrative operation per step, then return control to the reader with a purposeful explorable when free comparison adds value. Do not equate interactivity with a dashboard full of controls.

Never scroll-jack. Observe natural scrolling with IntersectionObserver/Scrollama-style triggers. Language switching is presentation state: it must not reset selected metrics, countries, scroll state, or evidence.

## Implementation constraints

- Prefer semantic HTML and lightweight Svelte state.
- Separate transforms from rendering code.
- Use SVG for modest vector charts; Canvas only when mark count requires it.
- Label important values directly when practical.
- Provide textual equivalents for essential visual conclusions.
- Support keyboard focus and `prefers-reduced-motion`.
- Design mobile intentionally; do not merely shrink desktop.
- Keep raw field keys separate from human labels/units.
- Do not hotlink proprietary Pudding fonts, logos, analytics, or brand assets.
- Attribute upstream code when derived from third-party starters.

## Baseline vs publication design

The generic renderer is a correctness baseline, not a final art direction. Once the story spec, claim audit, visual plan, first-draft provenance, and—when used—the prototype tournament pass, replace it with bespoke Svelte when the winning editorial idea benefits from stronger annotation, small multiples, a meaningful visual metaphor, scroll transformations, or exploration.

When replacing the renderer, preserve the underlying evidence calculations and rerun the claim audit. Preserve the tournament's implementation handoff unless later screenshot evidence gives a documented reason to revise it.

## Browser delivery QA

After the static checks and production build pass, test the built site in a real Chromium process. Start `vite preview`, then run:

```bash
npm run qa:browser -- --base-url http://127.0.0.1:4173 --out .qa
```

The default browser gate visits `/`, `/generated`, and `/lab` at desktop and mobile widths with reduced motion enabled. CI extends this to benchmark and bespoke story routes. It fails on uncaught exceptions, browser console errors, network failures, horizontal overflow, missing page structure, duplicate IDs, images without `alt`, unnamed interactive controls, or a broken keyboard Tab path. It writes PNG screenshots plus `.qa/browser-qa.json`.

Browser QA is a delivery gate, not an aesthetic score. Prototype-tournament screenshots may use the same browser harness, but their editorial scores must still be recorded separately in the tournament manifest.

## Screenshot-driven visual review

While the same production preview is running, collect deterministic visual evidence:

```bash
npm run qa:visual-probe -- --base-url http://127.0.0.1:4173 --out .qa/visual-probe.json
python scripts/pudding.py review .qa/visual-probe.json
```

This adds copy measure, leading, font size, heading hierarchy, touch-target size, clipping, computed contrast, visual aspect ratio, first-visual position, and sticky-density evidence.

`visual-review.json` deliberately keeps `agent_review.status = PENDING` even when its deterministic score is 100. The agent/editor must inspect every screenshot and record a separate visual verdict. Never write “visual QA passed” based only on the deterministic score.

For a review that calls for bounded fixes:

```bash
python scripts/pudding.py refine .qa/visual-review.json \
  --agent-review .qa/agent-visual-review.json \
  --apply
```

Automatic actions are restricted to readable copy width, copy leading, and coarse-pointer control height. They are written to `src/styles/refinement.css`. The refiner cannot change data, quantitative claims, chart transforms, Svelte structure, arbitrary colors, or bespoke art direction.

After any refinement, rebuild and rerun browser QA + visual probe + screenshot inspection. Compare before/after evidence and keep the change only when the stated problem improves without regression. The automatic loop stops after two passes.

## Delivery checklist

Before declaring the story complete:

1. Validate the data contract when present.
2. Review the candidate board and justify the selected analytical direction.
3. Re-run `scripts/validate_story.py`.
4. Re-run `scripts/verify_claims.py` against the raw data.
5. For bespoke visual stories, validate the contrastive concept board and confirm the static/no-interaction alternative was seriously developed.
6. Run the prototype tournament: inspect equivalent desktop/mobile screenshots, record scores/notes, apply hard gates, and document `SELECT`, `COMBINE`, `PIVOT`, or `PUT_DOWN`.
7. If the tournament selects/combines a direction, preserve its implementation handoff in the production build; if it pivots or puts the story down, do not continue as though a winner existed.
8. Review `generated/visual-plan.json`; confirm the recommended form fits the evidence and the tournament outcome.
9. Review `generated/story-draft.json` and verify every `claim_ref` still maps to the intended evidence.
10. Run `python scripts/qa_story.py --root .`.
11. Run unit tests (`npm run test:skill`).
12. Run the editorial benchmark (`npm run benchmark`) when core pipeline behavior changed.
13. Build with `npm run build`.
14. Run browser delivery QA against the built preview.
15. Run the visual probe and deterministic critic.
16. Inspect all desktop/mobile screenshots and record a separate agent/editor visual verdict.
17. If refinement is needed, apply only allowlisted auto-actions or an explicit source edit; then rerun the full visual loop.
18. Inspect desktop and mobile widths as editorial compositions, not just overflow checks.
19. Verify every quantitative sentence against structured evidence.
20. Test the first screen without scrolling.
21. Test reduced motion and keyboard use.
22. Confirm source attribution, caveats, and non-affiliation language.
23. Confirm the npm audit gate has no high or critical advisories.

If any hard check fails, revise before delivery.
