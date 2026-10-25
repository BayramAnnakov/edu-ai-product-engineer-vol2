# Choosing what to measure

Use the smallest boundary that still reaches the user's useful result. A successful API response, valid JSON and a real citation are different from a correct task outcome.

| Observation | Lever to consider | Reject it when |
|---|---|---|
| Explicit bounded predicate | Code/rule, with abstention elsewhere | It misclassifies a meaningful boundary case |
| Recomputed unchanged valid answer | Result cache with scope/version/freshness | Wrong-user, stale or changed-input reuse occurs |
| Repeated long stable prefix | Provider prompt cache | Usage shows no reads, or writes/storage/recovery erase savings |
| Redundant context or verbose output | Token packaging/retrieval/output changes | Decision-critical evidence or required behavior disappears |
| Work can wait | Batch | Queue/retry time misses the deadline |
| Routine work on expensive inference | Model, typed prediction, effort or cascade | Quality fails or router/fallback overhead erases the gain |
| Faster scoring barely changes completion | Critical-path improvement, or stop | Whole-job upside is negligible |

Compare total spend for equal task counts as well as spend/correct. A lower ratio does not price the consequences of an extra error. Keep false positives and false negatives visible. Include abandoned attempts; retries are work, not new cases.

Provider cache reads are reused prefix computation; result caching reuses an answer. Their validity rules differ. Use actual read/write usage and price every token once under that provider's billing convention. Count cold + warm together at the intended reuse volume. A lower bill need not mean lower latency.

Use measured whole-job wall time; do not sum parallel call latencies and call that end-to-end time. Composed replay timing stays labeled as composed. State whether human review/rework was actually measured and over how many items. Thirty cases can expose failures but cannot establish a stable p95 or rare error rate.

A provisional judge can miss defects. Preserve raw outputs and independent labels, inspect disagreements, and state any shared labeling assumptions. If a sample has judge acceptance equal to task correctness, do not manufacture a judge failure.
