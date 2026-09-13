# Editorial workflow

## 1. Frame the question

Rewrite the request as one answerable question. Prefer questions with a measurable comparison, change, distribution, relationship, or geographic pattern.

Bad: “Make this dataset interesting.”

Better: “Which cities experienced the largest divergence between rent and income after 2015?”

Record the intended audience and what they likely know already.

## 2. Audit before analysis

Check:

- row grain and keys;
- units and denominators;
- missingness and suspicious sentinel values;
- duplicate rows or identifiers;
- categorical cardinality;
- date coverage and gaps;
- numeric ranges and outliers;
- whether values are nominal, ordinal, rates, shares, indexes, or totals.

Do not convert an observation into a causal claim unless the evidence supports causality.

## 3. Rank candidate insights

A useful editorial insight should score well on four questions:

1. **Evidence** — is it clearly supported by the data?
2. **Importance** — does it matter to the stated question?
3. **Specificity** — can it be expressed as a concrete statement?
4. **Visual potential** — can a reader see the evidence rather than merely trust prose?

Prefer one primary insight and a few supporting insights. A story with six unrelated “interesting facts” is usually weaker than a story with one coherent argument.

## 4. Write narrative beats

Each beat should change either the reader’s knowledge or the visual state. Common progression:

1. Hook — why this question matters.
2. Baseline — establish the normal pattern or initial distribution.
3. Reveal — show the central divergence, transition, or outlier.
4. Compare — test whether the reveal is broad or concentrated.
5. Explain/caveat — add context without overclaiming.
6. Conclusion — state what the evidence does and does not show.

A beat that adds no new information should be removed.

## 5. Choose production mode

Use the simplest mode that serves the story:

- **annotated static** for one main comparison or pattern;
- **small multiples** for repeated comparison across categories;
- **stepper** when readers benefit from discrete stages but not continuous scroll;
- **scrollytelling** when one visual transforms through a sequence;
- **explorable** when reader-selected comparisons are the point;
- **map** only when geography is analytically meaningful.

Do not combine modes unless each mode has a distinct editorial job.

## 6. Implement from a story spec

Keep data transformation, narrative copy, and rendering separable. The chart should be reproducible from the story spec and source data. Avoid hard-coded pixel coordinates for data values when a scale can express the relationship.

## 7. Edit after rendering

Rendering is part of editing. Inspect what the reader actually sees, then remove clutter. Typical revision order:

1. fix incorrect or ambiguous data;
2. simplify the visual encoding;
3. strengthen annotation;
4. shorten prose;
5. tune motion and spacing;
6. adapt mobile layout.
