# Prototype tournament

A validated concept board is permission to **prototype**, not permission to select. The tournament exists to stop the first implemented idea from winning by sunk cost.

```text
READY_FOR_PROTOTYPE
        ↓
3–6 cheap claim-bearing prototypes
        ↓
same desktop + mobile screenshot contract
        ↓
score independently + apply hard gates
        ↓
SELECT / COMBINE / PIVOT / PUT_DOWN
        ↓
implementation handoff
```

## Prototype only the risky moment

Do not build headers, transitions, full navigation, decorative motion, or a complete article. Build the smallest state that can falsify the concept's promise. If the concept claims that sequence matters, prototype the sequence. If it claims reader agency adds understanding, prototype the decision the reader makes. If a static composition may be enough, make that static alternative equally serious.

Every concept on the board must enter the tournament. Do not quietly drop the static direction before comparison.

## Equal screenshot contract

Capture each prototype at the same two viewports used by browser QA:

- desktop: 1440 × 900;
- mobile: 390 × 844.

The committed tournament manifest stores one route and one expected screenshot path for every concept/viewport. A comparison is not complete until every expected screenshot exists.

For the example story, query parameters isolate aliases without changing the underlying prototype code:

```text
/stories/global-mental-health/prototypes?focus=A
/stories/global-mental-health/prototypes?focus=B
/stories/global-mental-health/prototypes?focus=C
```

Aliases make the review less vulnerable to labels such as “interactive”, “scrolly”, or “dashboard”. The form is still recorded in the manifest for auditability.

## Seven dimensions, 100 points

Each dimension is scored 1–5 and normalized to its weight:

| Dimension | Weight | Question |
| --- | ---: | --- |
| reader realization | 20 | Can a reader state the intended insight? |
| evidence fidelity | 20 | Are units, caveats, missingness, uncertainty, and provenance preserved? |
| visual necessity | 15 | Does the visual materially improve understanding over prose? |
| interaction economy | 15 | Does the chosen level of interaction — including none — earn its complexity? |
| reader effort | 10 | Can the claim be understood without avoidable work or controls? |
| mobile viability | 10 | Does the same conclusion survive a narrow touch viewport? |
| accessibility equivalence | 10 | Is the evidence available without hover, motion, or vision-only cues? |

A static prototype is **not** penalized for having no interaction. In `interaction_economy`, `none` can score 5 when interaction would add work without adding understanding.

## Hard gates

A prototype is eliminated regardless of total score when:

- `evidence_fidelity < 3`;
- `mobile_viability < 3`;
- `accessibility_equivalence < 3`;
- or the judge records a concrete hard failure.

Among prototypes that clear the hard gates, `70/100` is the survival threshold. The threshold is a comparison aid, not proof of taste or publication quality.

## Outcomes

The tournament deliberately permits four endings:

- `SELECT` — one surviving concept becomes the implementation base;
- `COMBINE` — two or more survivors contribute distinct, compatible jobs;
- `PIVOT` — the prototypes reveal that the argument needs a different visual/editorial frame;
- `PUT_DOWN` — no prototype earns production cost.

Never force a winner when every concept fails. `PIVOT` and `PUT_DOWN` are valid editorial successes.

## Commands

Create a tournament from a validated board:

```bash
python scripts/pudding.py tournament init stories/example/concept-board.json \
  --route /stories/example/prototypes \
  --output stories/example/prototype-tournament.json
```

Validate the manifest before implementation:

```bash
python scripts/pudding.py tournament validate stories/example/prototype-tournament.json \
  --stage manifest
```

After screenshots are captured and an editor/agent records scores, verdicts, notes, and the final decision:

```bash
python scripts/pudding.py tournament validate stories/example/prototype-tournament.json \
  --stage decision
```

CI can additionally require the referenced screenshot files to exist:

```bash
python scripts/pudding.py tournament validate stories/example/prototype-tournament.json \
  --stage evidence --evidence-root .
```

The generated Markdown report is a compact screenshot matrix plus ranking and decision record. The JSON remains the canonical handoff.

## Implementation handoff

A selected outcome must retain at least two explicit constraints learned from the comparison. These should be concrete, for example:

- keep the winning direct-label treatment because it reduced reader effort;
- preserve the mobile fallback that made the same conclusion available without hover;
- import one useful annotation from an eliminated guided concept without importing its interaction machinery;
- keep reporting-year and missingness cues adjacent to the marks because hiding them caused an evidence-fidelity failure.

Do not hand off “make it prettier” or “build concept B”. The purpose of the tournament is to preserve **why** the concept won and **what not to lose** during production.
