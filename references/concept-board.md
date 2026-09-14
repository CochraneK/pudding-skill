# Contrastive concept board

A passing pitch is **not** permission to start coding the first visual idea. The concept board forces several structurally different ways of communicating the same evidence to exist before bespoke implementation begins.

This stage addresses a recurring failure mode in automated data-story production:

```text
insight
  ↓
first plausible chart
  ↓
code investment
  ↓
sunk-cost attachment
  ↓
polish the wrong form
```

The preferred sequence is:

```text
supported argument + verified evidence
  ↓
3–6 contrasting concepts
  ↓
cheap prototypes of the riskiest ideas
  ↓
equal desktop/mobile screenshots
  ↓
prototype tournament
  ↓
select / combine / pivot / put down
  ↓
only then bespoke implementation
```

## Required contrast

A board must contain at least three complete concepts and at least two distinct forms and interaction jobs. One concept must be an intentionally static or no-interaction alternative.

That static alternative is not a straw man. It answers a serious editorial question:

> Would a clear sequence of annotated static visuals explain this better than custom interaction?

If yes, use it.

## Concept contract

Each concept records:

- the reader realization it is responsible for;
- why visual treatment adds meaning beyond prose;
- concrete evidence dependencies;
- the visual metaphor or organizing frame;
- interaction job, including `none`;
- mobile strategy;
- accessibility equivalent;
- a cheap prototype test;
- a kill condition;
- at most two public-story references, each expressed as a transferable editorial operation rather than surface style.

The board validator rejects references phrased as requests to copy a style or clone a look. Reference stories are provocations, not templates.

## Commands

Create a scaffold:

```bash
python scripts/pudding.py concept init \
  --story-id example \
  --question "What changed?" \
  --argument "The change is concentrated rather than evenly distributed."
```

After the agent/editor develops all directions:

```bash
python scripts/pudding.py concept validate generated/concept-board.json
```

A passing result is `READY_FOR_PROTOTYPE`, not `SELECTED` or `APPROVED`.

## Using the Pudding study corpus

`benchmarks/pudding-study-corpus.json` can supply references, but use it contrastively. A board should ask things like:

- what if this is strongest as a static chart sequence?
- what if the reader needs to commit a belief before the reveal?
- what if uncertainty or assumptions should become controllable?
- what if one concrete exemplar should teach the visual grammar before showing the population?
- what if participation or personalization is the evidence-bearing medium?

Do not ask “which Pudding story looks most like mine?” and retrieve its layout.

## Prototype handoff

Prototype the **hardest claim-bearing moment**, not the header, transitions, or decorative motion. Every concept on the validated board must enter the prototype tournament, including the static/no-interaction direction.

The tournament compares:

1. reader realization;
2. evidence fidelity;
3. visual necessity;
4. interaction economy — including whether `none` is the best interaction choice;
5. reader effort;
6. mobile viability;
7. accessibility equivalence.

Evidence fidelity, mobile viability, and accessibility equivalence are hard gates. A visually exciting concept cannot compensate for failing them, and no-interaction is not penalized when it communicates the claim with less reader effort.

A concept may pass the deterministic board validator and still be eliminated by screenshot review. That is expected. Continue with `references/prototype-tournament.md`; do not begin bespoke implementation merely because the board says `READY_FOR_PROTOTYPE`.
