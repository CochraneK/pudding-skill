# Visual grammar

Choose visuals from the analytical task and narrative operation.

| Task | Strong defaults | Avoid by default |
|---|---|---|
| Magnitude comparison | ordered bar, dot plot | pie with many categories |
| Ranking | ordered bar, lollipop, bump over time | unsorted bars |
| Change over time | line, area, slope | bars for dense long series |
| Before/after | slope, connected dot | two unrelated charts |
| Distribution | histogram, strip, beeswarm, box plot | averages alone |
| Relationship | scatter, connected scatter when time matters | dual-axis charts |
| Part-to-whole | stacked bar, 100% stacked bar | many-slice donut |
| Geography | locator map, choropleth, proportional symbols | map when location is incidental |
| Flow | Sankey/alluvial when flows are few and meaningful | dense spaghetti flow diagrams |

## Narrative operation → visual treatment

### Establish
Show context and scale. Keep all marks visible and annotations minimal.

### Compare
Use a common baseline or aligned scales. Direct labels are preferable to legends when the set is small.

### Reveal
Change one thing at a time. Preserve spatial continuity so the reader understands what changed.

### Highlight
Mute context; emphasize the subset. Do not encode emphasis with color alone when accessibility matters.

### Filter
Remove or fade marks only when the reader has already seen the broader context.

### Reorder
Animate rank changes sparingly. If motion is not essential, show before/after states instead.

### Zoom
Use zoom to expose detail, not to manufacture drama. Maintain orientation with labels or persistent reference marks.

### Annotate
Attach interpretation near evidence. Prefer a short declarative annotation over a detached paragraph.

## Color

Use color semantically:

- neutral tones for context;
- one emphasis color for the main story;
- distinct hues only for categories readers must track;
- diverging palettes only around a meaningful midpoint;
- sequential palettes for ordered magnitude.

Do not copy The Pudding’s brand palette as a shortcut to “looking Pudding-like.”

## Motion

Motion is justified when it explains state change, preserves object constancy, or controls reveal. Avoid ambient motion. Respect `prefers-reduced-motion` and ensure the story remains intelligible without animation.

## Mobile

Mobile is an editorial layout, not a scaled desktop page. Common adaptations:

- move sticky charts above the active step;
- shorten annotations;
- reduce simultaneous categories;
- use direct labels where legends become awkward;
- replace hover-only interactions with tap/focus or persistent labels.
