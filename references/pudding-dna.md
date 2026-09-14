# Pudding DNA: editorial gate before data production

This document turns public lessons from The Pudding's pitch and process material into an **operational approximation** for `pudding-skill`.

It is **not** an official Pudding rubric, not a brand/style imitation guide, and not a claim that a deterministic score can reproduce editorial taste. The gate exists to stop the Agent from mistaking “we have data” or “we can build a scrolly” for “we have a story.”

Primary public references:

- The Pudding pitch guidance: https://pudding.cool/pitch/
- Continue / pivot / put it down: https://pudding.cool/process/pivot-continue-down/
- Responsive scrollytelling: https://pudding.cool/process/responsive-scrollytelling/
- The Pudding's AI story experiment: https://pudding.cool/2024/07/ai/

## The key shift

Old default:

```text
data
  ↓
insight
  ↓
chart
  ↓
interaction
```

Preferred editorial sequence:

```text
curiosity
  ↓
question
  ↓
argument
  ↓
so what?
  ↓
human angle / soul
  ↓
data receipts
  ↓
aha / surprise
  ↓
visual necessity
  ↓
multiple concepts + storyboard
  ↓
interaction earns its place (or is omitted)
  ↓
CONTINUE / PIVOT / PIVOT_NONVISUAL / PUT_DOWN
  ↓
only then research, production, and QA
```

## Dimensions

### 1. Argument, not topic

A topic is “global mental health,” “EVs,” or “basketball ethics.” A story needs a declarative claim that can be challenged, refined, or disproved.

A strong argument answers: **what are we saying, not merely what are we looking at?**

### 2. Soul / human angle

The pitch should state why a person cares, what obsession or discomfort motivates the work, and what the reader might feel differently about afterward.

The gate does not attempt to score humor or taste directly. It only checks whether the pitch contains a specific human stake instead of an institutional topic description.

### 3. Data receipts

A story cannot advance because a hypothetical dataset would be nice to have. Record whether the data is:

- `verified` — already available and understood;
- `obtainable` — a credible acquisition path exists;
- `speculative` — plausible but not verified;
- `blocked` — required data is inaccessible.

Blocked data with no fallback is a first-class **PUT_DOWN** condition, not an invitation to invent numbers.

### 4. Visual necessity

Ask the harsh question:

> If all charts were replaced by prose, would almost the same story remain?

If yes, pivot to a nonvisual form instead of forcing graphics. A Pudding-inspired visual story should gain meaning from seeing, hearing, comparing, moving through, or manipulating evidence.

### 5. Aha / distinctive entry point

The pitch should contain a specific surprise, contradiction, test, or unusually concrete entry point. “Here is a comprehensive overview” is not enough.

### 6. Interaction must earn its place

No interaction is a valid choice. A static annotated visual can score as well as an explorable.

Interaction only earns credit when it has a cognitive/editorial job such as compare, reveal, highlight, zoom, annotate, accumulate, morph, explore, lookup, simulate, or play. “Make it feel interactive” earns nothing.

### 7. Iteration before implementation

Do not jump from a passing pitch to bespoke Svelte. Generate multiple visual concepts, storyboard them cheaply, and prototype the hardest interaction before committing to production.

The purpose is not to create more deliverables; it is to give the editor a real choice.

### 8. Killability

A healthy workflow states in advance what evidence would make the team pivot or stop. Without kill conditions, every sunk cost becomes an argument to publish.

## Decisions

`pudding_gate.py` can return four decisions:

- **CONTINUE** — the concept is strong enough to justify the next research/prototype stage. This is not publication approval.
- **PIVOT** — preserve the useful core, but revise the argument, human angle, data path, surprise, interaction, or iteration plan.
- **PIVOT_NONVISUAL** — the argument and evidence may be strong, but the visual case is weak. Do not force it into a data story.
- **PUT_DOWN** — the current concept should stop, usually because the evidence path is blocked or the pitch is too weak to justify production.

A deterministic score is only triage. An editor/agent may override a threshold **only by documenting why**; it may not override a blocked-data hard stop with fabricated evidence.

## Pitch contract

A concept file should contain at least:

```json
{
  "id": "example",
  "question": "What question started the investigation?",
  "argument": "One declarative sentence stating the thesis.",
  "why_you": "Why this question creates genuine curiosity.",
  "human_angle": "What person-level stake or recognition makes it matter.",
  "tone_or_obsession": "Optional voice, obsession, humor, friction, or specificity.",
  "aha": "What should surprise or reframe the reader?",
  "distinctive_entry_point": "Why this is not a generic report on the topic.",
  "data_plan": {
    "status": "verified",
    "sources": ["source"],
    "method": "How the central evidence will be constructed and verified.",
    "limitations": "Known limits.",
    "fallback": "What can still answer the question if the preferred data fails."
  },
  "visual_case": {
    "why_visual": "What understanding becomes possible because the reader can see/hear/manipulate evidence.",
    "first_whiteboard": "The first low-cost visual idea.",
    "visual_concepts": ["concept A", "concept B", "concept C"]
  },
  "interaction": {
    "job": "reveal",
    "rationale": "Why interaction changes understanding. Use 'none' when it does not."
  },
  "prototype_plan": "What to prototype before full implementation.",
  "iteration_plan": "How competing concepts will be compared.",
  "kill_conditions": ["condition 1", "condition 2"]
}
```

## Corpus and holdout policy

`benchmarks/pudding-dna-corpus.json` contains two kinds of cases:

1. concise analytical annotations of public Pudding stories;
2. synthetic anti-pattern pitches.

Some cases are marked `calibration`; others are `holdout`. The holdout is deliberately kept in the same committed corpus so CI can verify behavior, but weights should not be weakened merely to make one failing case green. If expectations change, explain the editorial reason in the PR.

The benchmark is intentionally modest: it verifies **decision consistency**, not taste acquisition. Real taste still requires reading projects, generating alternatives, screenshot/prototype review, and human editorial judgment.

## Workflow integration

Before launching a research dossier for a broad topic, create a concept and run:

```bash
python scripts/pudding.py pitch stories/example/story-concept.json
```

Then:

```text
CONTINUE
  → research / data audit / prototypes

PIVOT
  → revise concept, then rerun gate

PIVOT_NONVISUAL
  → write/report it in a better nonvisual form

PUT_DOWN
  → stop; preserve notes; do not manufacture a story to satisfy the pipeline
```

This gate sits **before** `research` and `story`. Passing it never replaces source verification, claim audit, browser QA, screenshot review, or editorial review.
