# Apply the cost-optimization method to your workflow

Participant framework, draft 24 October 2026. Use on a product agent, coding-agent pipeline or ordinary LLM workflow. This is a portable worksheet and agent brief; the packaged [bakeoff skill](../skills/bakeoff/SKILL.md) is included. Do not treat a reasoning-only review as an executed optimization.

## 1. Define useful completion

Write the task, what counts as an accepted result, the costly failure types, permitted actions and when to escalate. State who can label correctness. Separate task correctness, supporting evidence, valid format and a judge's provisional acceptance. If the judge is unaudited, report its passes as a proxy and keep independent task labels.

Choose the smallest workflow boundary that still includes the user's result: request → accepted result. Include failed and abandoned attempts. Do not optimize only a call while hiding extra work elsewhere.

## 2. Measure and check the instrument

Use a representative, versioned case set. Keep tuning cases separate from a frozen evaluation set; split related entities together. For a first pilot, 30 cases can expose failures, but cannot prove a rare failure rate or a stable p95. Name important slices and missing coverage. Oversample rare costly failures for diagnosis; report those slices separately and use the operational mix when estimating overall economics.

For each step record calls, input/output/reasoning/cache usage without double counting, retries, provider/tool costs and elapsed time. Trace the critical path when steps run concurrently. Check a sample against provider-reported usage and the relevant billing convention.

At the workflow level record accepted/task cases, costly failures, all machine spend per accepted outcome, measured human review/rework minutes per accepted reviewed outcome, and end-to-end time. Keep source values, computed estimates, recorded examples and current live observations distinguishable. If there are zero accepted outcomes, do not report a finite cost per acceptance. In W1 report two separate ratios: spend per task-correct output passing hard checks, and spend per provisional judge acceptance. The latter is a proxy; a judge that over-accepts must not make an incorrect route appear economically better.

## 3. Choose a lever from the work, not from habit

| What you observe | Candidate intervention | Check that could reject it |
|---|---|---|
| A bounded question has an explicit data/rule answer | Execute code or rules; retain model fallback for uncovered cases | A rule misses a meaningful class, accepts unsafe content or cannot handle a boundary case |
| Identical valid results are recomputed | Application/result cache with scope, version and freshness rules | Stale, wrong-user or changed-input reuse |
| A large stable prefix repeats | Provider prompt cache | Rendered-prefix churn or low hits; creates/storage/recovery exceed savings; current API lacks the assumed path |
| Bulky context, tool schemas or output dominates | Remove redundant tokens, retrieve narrowly, return structured fields | Decision-critical evidence or required behavior disappears |
| Many requests can wait | Provider Batch / asynchronous work | Deadline, turnaround or retry behavior is unacceptable |
| Expensive inference handles routine cases | Smaller/typed model, effort choice, router/cascade | Costly false accepts/rejects increase; router/fallback overhead erases gains |
| Calls serialize needlessly or repeat bookkeeping | Remove a round trip, move nonessential work off the critical path, parallelize independent work | A dependency, approval or state transition breaks; spend rises beyond its limit |
| A faster model barely changes completion | Fix the current critical-path step or stop | The next candidate has negligible whole-job upside |

The workshop demonstrates the promised cache/batch/token → model/routing → rules/code ladder. In your own workflow, use this table to prioritize the measured bottleneck. You do not need to exhaust every rung or build a router when a direct rule suffices.

## 4. Predeclare one bounded experiment

Fill this before seeing candidate results:

> For **[workflow/version]**, baseline **[metric/value/window]**. Change **[one mechanism]**. Expect **[minimum useful effect]** on **[cases/slice]** while preserving **[task-quality floor, costly-failure rule and deadline]**. Freeze **[inputs, model/configuration, rubric and split]**. Stop after **[time/spend]** or when **[gate]** fails. Revert with **[specific action]**. Evidence will be **[trace/usage/output artifacts]**.

For prompt caching, compare the exact serialized requests and find the first changed prefix token; test prompt/history transformations together and verify provider cache usage. A shorter prompt can still cost more if reuse breaks. For routing, count the router, every attempted executor and fallback. For caches, include creation/storage/recovery and amortize at the expected reuse volume. For batching, include queue time. For a learned or changed configuration, report setup/evaluation cost separately and, where useful, its break-even volume. Do not invent prices, billing coverage or a confidence threshold.

## 5. Evaluate quality, then economics, then the whole job

Run the incumbent and frozen candidate on the same evaluation tasks with the same task information and acceptance definition. Change only the declared mechanism where feasible; if changes are bundled, name the bundle. Inspect disagreements and important slices, including failures and timeouts. Calibrate a judge against independent labels where it matters.

Record the task-case denominator once; retries are extra work, not extra cases. Report absolute counts and sample limitations. Measure the entire user-facing result as well as the changed step. A cheaper call with worse accepted-outcome cost is rejected. A step-level improvement without a whole-job effect is reported at its actual scope.

Recorded-response simulation may test new routing code only against exact matching requests/configurations/prefixes. Reject missing branches. Its composed cost/timing remain estimates. A mock or static price formula cannot establish model quality or live latency.

## 6. Close the loop

Record the **experiment verdict** separately from the **owner decision**: keep, revert, insufficient evidence, or propose a bounded trial. Use these evidence verdicts:

- **Worked:** the predeclared effect and relevant quality/operational gates were measured and met at the stated scope.
- **Failed:** an effect or gate failed. Keep that verdict and stop tuning on the evaluation feedback; do not move the frozen threshold to manufacture a pass.
- **Partial:** a narrower effect was demonstrated, such as cheaper scoring with no whole-job improvement.
- **Inconclusive:** the data or measurement coverage cannot decide. Name what would settle it.

A failed soft threshold can still inform a different business decision. In [Bayram’s post 1844](https://t.me/ProductsAndStartups/1844), the formal quality test failed, but the owner accepted a speed/cost trade-off with followthrough. A bounded-trial proposal must name the accountable owner, business value and accepted error cost, exposure limit, rollback trigger and checkpoint. It does not authorize deployment or actions outside the task contract. Keep the original verdict; a new hypothesis gets new evaluation data.

If a deployed change needs later traffic, register its expected effect, measured baseline, comparison method, date/volume, owner and rollback decision. A check ends with a measured verdict; if data are insufficient, explicitly reschedule. Use followthrough or your team's equivalent. Register nothing for an optimization you only proposed or a readiness check you can perform now.

## 7. One output to take to a teammate

Submit one decision record: task/acceptance contract; workflow map; baseline and candidate scorecard; tested lever and fixed comparison; one consequential trace; frozen gate verdict and owner decision (with trial conditions when applicable); evidence limitations; and the later check if needed. Label controlled fixture, historical replay and real workplace results separately.

### Brief to paste into your coding agent

> Analyze this agent/LLM workflow for cost and latency. First map the path to an accepted result and ask for missing evidence. Check usage accounting, then rank possible interventions across avoided calls/rules, result and prompt caching, token reduction, batch, model/effort/routing, retries and workflow structure. Estimate upside and include displaced work. Propose one bounded experiment with a quality floor, budget, frozen evaluation and rollback. Before executing paid calls, deployment or external actions, follow this project's authorization rules. Report observed facts, estimates and untested proposals separately. Return a decision record, not an unsupported savings claim.

The framework is written and reviewable. Its portability and teaching effectiveness remain to be tested with learners; see [VALIDATION.md](../VALIDATION.md) for the skill’s independent fixture-project tests and limitations.
