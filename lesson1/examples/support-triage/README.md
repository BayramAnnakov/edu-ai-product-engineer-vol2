# support-triage

Reuse a password-reset result only when an entry exists, tenant/knowledge version/locale match the request, the entry is unexpired as of the request day, and the request is neither urgent nor ambiguous. Other intents require the model path. Cross-tenant reuse is unacceptable. The authored model bank is a fixture, not a production model evaluation.

Use `$bakeoff` (Codex) or `/bakeoff` (Claude). Read this contract and inspect `workflow.py` and development cases. Change only `choose_route`; `cheap_answer` is supplied. The runner gives the router only `input`, never expected labels or case ID. Do not use ID/label lookups.

Start with development runs. Keep evaluation labels AND eval-model-bank.json unopened until the router and experiment are frozen. Hashing a file for freeze does not require reading its contents into the agent context. The dev bank is separate to avoid accidental leakage. Every output, dollar amount and latency in this example is an **authored fixture**; executing the router is real Python execution, but it makes no model calls. The provisional judge accepts every output deliberately; exact task labels catch incorrect shortcuts.

```bash
python3 runner.py --split dev --arm baseline --out work/dev-baseline.jsonl
python3 runner.py --split dev --arm candidate --out work/dev-candidate.jsonl
```

For held-out comparison, set cases=eval.json, dev_cases=dev.json, pins=[workflow.py, runner.py, dev-model-bank.json, eval-model-bank.json], quality_floor_percent=100, minimum_cost_reduction_percent=10, max_job_p95_seconds=10, max_total_cost_usd=3.0, prior_receipts=[work/dev-baseline.jsonl, work/dev-candidate.jsonl] and max_tuning_minutes=20. Put that contract beside these files before freezing; all paths are relative to the contract. Use the bakeoff helper to freeze, compare, and record a separate decision. Read receipt-format.md for commands.

An observed cache reuse here is an application result reuse; it is not a provider prompt-cache hit. Enrichment/review/infra costs are unpriced and review effort is unmeasured. Retain these limits in your result.

Evaluation inputs vary paths, source combinations and boundary cases (coding), or tenant, version, locale and freshness (support); they are not renamed copies of development inputs. Semantic representativeness remains a judgment. Both splits are authored, not production data.
