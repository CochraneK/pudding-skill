# Global Mental Health Capacity Atlas — data contract

This layer turns public WHO Global Health Observatory country indicators into a transparent capacity atlas. It is intentionally **not** a synthetic mental-health score.

The compiler retains the latest non-missing observation for each country and indicator, preserves the observation year, and keeps missing values as missing. Usable public layers currently include psychiatrists, mental-health nurses, psychologists, government mental-health spending share, and outpatient facilities. WHO region metadata is used for regional summaries. The public `MH_21` total-workforce endpoint currently yields no usable observations, so the atlas does not fabricate a total-workforce layer from the professional subgroups.

The implemented route is `/stories/global-mental-health/atlas`. Across the 234 WHO country/area dimension entries, the committed audit has 146 psychiatrist observations, 127 nurse observations, 120 psychologist observations, 139 outpatient-facility observations, and 78 government-spending-share observations. Data years remain visible because most workforce/service observations are from 2013–2017 and the spending-share table is from 2011.

A separate historical mismatch lens pairs WHO's **2015 depression prevalence estimate** with the latest available psychiatrist-density observation only when both exist. The overlap is 142 countries in the current audit. Because the two measurements can come from different years and depression is only one condition, this layer is descriptive context rather than a current need score, causal estimate, or country ranking.

Every atlas view must expose the reporting year and data coverage. Countries without an observation must render as unavailable rather than zero. Indicator switching uses ordinary keyboard-focusable buttons; the SVG map and scatter plot carry text alternatives and per-mark labels, while the surrounding prose states the essential conclusions without requiring hover interaction.

The atlas is included in production browser and screenshot QA at desktop and mobile widths. Its delivery gate covers the field story plus atlas as separate routes so an interactive-layer regression cannot be hidden by the narrative page passing.
