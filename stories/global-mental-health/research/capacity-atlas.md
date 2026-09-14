# Global Mental Health Capacity Atlas — data contract

This layer turns public WHO Global Health Observatory country indicators into a transparent capacity atlas. It is intentionally **not** a synthetic mental-health score.

The compiler retains the latest non-missing observation for each country and indicator, preserves the observation year, and keeps missing values as missing. Current metrics include total mental-health workforce, psychiatrists, nurses, psychologists, government mental-health spending share, and outpatient facilities. WHO region metadata is used for regional summaries.

A separate historical mismatch lens pairs WHO's **2015 depression prevalence estimate** with the latest available workforce observation only when both exist. Because the two measurements can come from different years and depression is only one condition, this layer is descriptive context rather than a current need score, causal estimate, or country ranking.

Every atlas view must expose the reporting year and data coverage. Countries without an observation must render as unavailable rather than zero.
