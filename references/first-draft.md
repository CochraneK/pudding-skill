# Publication-ready first-draft contract

v2.4 adds a deterministic first-draft layer after evidence selection and independent claim verification. The output is designed to be editable, not blindly publishable.

## Required ordering

Do not draft prose before the selected story passes:

1. data profiling and semantic review;
2. candidate generation and ranking;
3. deterministic quality/renderer gates;
4. story-spec validation;
5. independent quantitative claim verification.

Only then generate `story-draft.json` and `story-draft.md`.

## Draft package

The draft JSON contains:

- `headline` and `dek`;
- narrative `sections` with an editorial operation;
- `visual_plan` separating the recommended publication grammar from the baseline renderer;
- evidence-linked `annotations`;
- source note and methodology;
- caveats and data notes;
- field glossary with labels/units/descriptions when supplied;
- `provenance.claims` mapping each quantitative copy claim to structured evidence.

Every generated draft remains `EDITORIAL_REVIEW_REQUIRED`.

## Claim provenance

A section can carry `claim_refs`. Each `claim_ref` maps to `provenance.claims`, which maps back to an evidence index in the validated story spec.

When an agent rewrites quantitative copy:

- preserve the corresponding `claim_ref` if the factual meaning is unchanged;
- rerun claim verification if the numerical or comparative meaning changes;
- do not add a new quantitative assertion without adding structured evidence and verification;
- distinguish verified quantities from interpretation, context, or causal language.

## Visual grammar vs baseline renderer

The baseline renderer exists to guarantee a reproducible, inspectable build. The recommended visual grammar can be richer.

Example:

```text
change-gap evidence
  recommended publication form: slopegraph
  deterministic baseline renderer: ranked bar
```

A richer recommendation must never silently replace the baseline if it cannot be generated and tested reliably. Bespoke implementation comes after the evidence and draft contracts are stable.

## Publication review

Before publication, an editor/agent must still review:

- whether the story is actually meaningful outside the dataset;
- whether aggregation/denominators are defensible;
- whether the headline overstates the evidence;
- whether correlation is being described causally;
- whether important subgroups or uncertainty are hidden;
- whether the recommended visual is the clearest accessible form;
- whether mobile composition and annotations remain readable.
