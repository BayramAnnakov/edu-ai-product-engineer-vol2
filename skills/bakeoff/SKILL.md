---
name: bakeoff
description: "Test a bounded cost or latency optimization in an agent or LLM workflow, preserve task quality, and produce a traceable keep/revert decision. Use for workflow bakeoffs, cache/model/routing experiments, or deciding whether an optimization is worth keeping."
---

# Bakeoff

Produce one defensible optimization decision for the user's workflow. Start from the actual work and available evidence; do not require a model swap, router, provider or particular savings target.

## Establish the experiment

Map request → useful completed result, including tools, retries, fallbacks and human correction. Define task correctness separately from valid formatting, real citations and provisional judge acceptance. Price the important error directions before choosing a quality floor.

Inspect the actual implementation and traces. Select one promising lever: remove work with a bounded rule; reuse a valid result; preserve a stable prompt prefix; trim irrelevant tokens; batch if the deadline permits; change model/effort/routing; or fix the critical path. A cache flag is not evidence of a hit. A typed answer is not evidence of correctness. Read [measurement.md](references/measurement.md) when choosing a metric or interpreting cache/routing evidence.

If evidence is absent, create a concrete experiment plan and mark it unexecuted. Do not invent labels, provider outputs, prices, usage or latency to complete a scorecard. Offline fixture runs can test a harness or mechanism; they cannot establish model quality, production savings or human learning.

Use a separate output directory. Copy [experiment.json](assets/experiment.json) and [decision.md](assets/decision.md), or run `python3 <this-skill>/scripts/bakeoff.py init --out <directory>`. Adapt the templates to the workflow. Keep tuning cases separate from evaluation and split related entities together. Freeze task contract, inputs, rubric, versions and intended changed mechanism before evaluation. Choose floors and budgets from the user's consequences; 30 cases and a 90% floor are not universal requirements.

## Execute within scope

First screen the candidate on development data. If it fails, stop that candidate and save a dev-only rejection with a trace and the next evidence needed. There is no requirement to open the held-out set to produce an artifact. After changing the hypothesis, start a new experiment; do not tune on held-out failures.

For a continuing experiment, run incumbent and candidate on the same frozen task cases. Read [receipt-format.md](references/receipt-format.md) only when using the bundled helper. It supports existing JSONL receipts and exact-output labels; semantic tasks may use independent human labels with their provenance retained. It does not call model APIs or make an unaudited judge authoritative.

Every attempt counts, including failed calls, router, adapter and fallback work. Unknown cost stays unknown and incomplete attempts stay visible. Include queue time in end-to-end latency and creation/storage/recovery in cache economics. Use provider-reported counters and dated pricing for new paid experiments; verify the chosen provider's current official documentation rather than copying historical prices from the examples.

Follow the host project's authorization rules. This skill does not grant permission for paid calls, deployment, external messages, uploads or publishing. Do not extend a spend/time cap silently. If the cap or a required dependency blocks execution, preserve completed evidence and return a scoped rejection or inconclusive decision.

## Decide and transfer

Inspect actual errors before economics, then the whole-job effect and displaced human work. Report fixed case counts, all machine spend, cost per task-correct result, provisional acceptance separately, error direction, review coverage and evidence limitations. An absent review measurement is not zero review effort; a zero correct denominator has no finite cost/correct.

Keep the frozen experiment verdict distinct from the owner decision. A failed gate stays failed. The owner can revert, seek more evidence, or explicitly propose a bounded trial with owner, expected business value/accepted error cost, exposure limit, rollback and checkpoint. A trial proposal authorizes no deployment. Do not prefill the owner's rationale as though it were an independent judgment.

Return a decision record, tested configuration, scorecard, at least one consequential trace and a proposed next experiment for the user's own workflow. For a shipped change whose effect needs later traffic, register the expected effect and measured follow-up using the project's followthrough process or equivalent. Check immediately when the answer already exists. Do not create reminders for unexecuted proposals.
