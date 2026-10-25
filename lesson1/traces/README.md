# Sanitized actual trace examples

Open [cache-pair.jsonl](cache-pair.jsonl) , [model-choice-routing.jsonl](model-choice-routing.jsonl) and the earlier [scoring-boundary.jsonl](scoring-boundary.jsonl), or run `python3 scripts/inspect_traces.py` from repository root. Follow [the worksheet](../trace-walkthrough.md) before inspecting results.

Ten selected real recorded provider calls on public/synthetic inputs. Numeric usage/cost/latency and error semantics are retained; identifying metadata and full prompt text are removed or replaced. The [manifest](manifest.json) records scope, transformations and file hashes. No private Langfuse link, provider key, customer input, original held-out dataset or grader is needed.

These excerpts are readable without an account. They are not complete requests or live replay fixtures. Prices are dated 24–25 October 2026, calculated from returned usage, and are not invoices or current pricing recommendations. The model-choice starter uses actual recorded calls; the coding-review/support-triage examples use separately labeled authored fixtures.

## Model choice and Jev routing — 25 Oct

model-choice-routing.jsonl contains four new selected physical-call excerpts: Sol, Luna, Terra and Jev. The scorers see the same task; Jev returns only an executor choice. Terra's schema-valid score is wrong on this example, while the cited record actually exists in the synthetic input. Model costs use each model's own dated rates. A routing workflow costs Jev plus the selected scorer; the router excerpt alone is not the whole job. Identifiers were replaced and full input text omitted. The selected example is not an error-rate estimate.
