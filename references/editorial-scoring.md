# Editorial candidate scoring

The deterministic scorer is a **triage mechanism**, not an editor. It helps compare multiple supported story directions before an agent applies contextual judgment.

## Components

Each candidate receives 0–100 component scores for:

- **evidence** — more usable observations increase confidence;
- **coverage** — share of source rows used by the calculation;
- **effect** — magnitude of the measured change/relationship relative to an appropriate baseline;
- **distinctiveness** — how clearly the leading group/feature separates from the runner-up;
- **visual fit** — whether the pattern has a direct, legible baseline encoding;
- **simplicity** — fewer fields/transforms are easier to explain and audit;
- **question relevance** — lexical/intent alignment with the supplied research question.

A **risk penalty** lowers scores for patterns that are easy to overstate, such as correlation with repeated time observations or pooled averages across time.

## What the score cannot know

Do not interpret the score as newsworthiness, social importance, surprise, causal validity, fairness, or cultural relevance. Those require domain context and editorial judgment.

The ranking is most useful for answering: **“Which evidence-backed directions deserve editorial attention first?”**

## Selection behavior

`scripts/select_story.py` evaluates candidates in rank order. A candidate must:

1. produce a valid story spec;
2. clear deterministic editorial gates;
3. dry-run successfully through the baseline renderer.

If the top candidate fails, selection automatically tries the next candidate and records every attempt in `selection-report.json`.

## Question intent hints

The scorer gives modest bonuses when the question signals a matching analytical operation, for example:

- “diverge”, “gap”, “separate” → change-gap candidate;
- “relationship”, “correlation” → correlation candidate;
- “distribution”, “spread”, “median” → distribution candidate;
- “trend”, “change”, “growth” → time-change candidate;
- “highest”, “lowest”, “rank” → group comparison candidate.

These are ranking hints only. They never create evidence that is not present in the data.
