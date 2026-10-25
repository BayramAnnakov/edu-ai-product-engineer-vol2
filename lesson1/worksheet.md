# One bounded optimization

Copy this into your project; fill before evaluating.

1. **Accepted work:** request → useful result, permitted actions, independent source of correctness.
2. **Error consequences:** what happens when we reject a good item, admit a poor item or lack evidence? What is one such error worth?
3. **Baseline:** fixed case count, correctness/errors, all machine spend, $/correct, whole-job time, measured review/rework (or unknown).
4. **One lever:** what work disappears or changes, why it applies, and where it must abstain. Use the [diagnostic table](framework.md).
5. **Frozen experiment:** hypothesis, minimum useful effect, quality floor, deadline, time/spend cap, task cases, versions/config/rubric, group-disjoint tuning/evaluation.
6. **Observed evidence:** actual errors first; then cost/correct and total dollars for equal N; then end-to-end time. Include failed attempts, router and fallback.
7. **Two records:** experiment verdict; separately, keep/revert/more evidence/bounded-trial decision and business rationale. A trial needs owner, value/error cost, exposure cap, rollback and checkpoint.
8. **Transfer:** next experiment on your own workflow; later measured check only if a shipped change needs traffic.

Example: saving four cents across30 cases alongside two extra wrong decisions does not price the harm of those errors. Decide the acceptable loss before seeing savings.

Use [the decision template](../skills/bakeoff/assets/decision.md) or the helper's exported report. Keep unknown values unknown. Hashing files protects against accidental drift; it does not establish independent labels or prevent someone intentionally inspecting held-out data.
