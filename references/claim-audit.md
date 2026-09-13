# Quantitative claim audit

`scripts/verify_claims.py` independently recomputes structured evidence from the raw input data. This catches drift between the story spec and the source data.

Current auditable evidence kinds:

- `change_gap` — start/end changes for two measures and their difference;
- `change` — stored start value, end value, and delta;
- `group_mean` — group mean and observation count, plus optional lowest-group comparison;
- `correlation` — Pearson r and paired observation count;
- `distribution` — minimum, median, maximum, and n.

The pipeline fails if recomputed values do not match the evidence object.

This is **numeric verification**, not semantic verification. It cannot determine whether a denominator is appropriate, whether a metric is ethically meaningful, whether a causal interpretation is justified, or whether prose accurately communicates uncertainty. Those remain editorial responsibilities.
