# Sanitized actual trace examples

Open [cache-pair.jsonl](cache-pair.jsonl) and [scoring-boundary.jsonl](scoring-boundary.jsonl), or run `python3 scripts/inspect_traces.py` from repository root. Follow [the worksheet](../trace-walkthrough.md) before inspecting results.

Six real recorded provider calls on public/synthetic inputs. Numeric usage/cost/latency and error semantics are retained; identifying metadata and full prompt text are removed or replaced. The [manifest](manifest.json) records scope, transformations and file hashes. No private Langfuse link, provider key, customer input, original held-out dataset or grader is needed.

These excerpts are readable without an account. They are not complete requests or live replay fixtures. Prices are dated 24 October 2026, calculated from returned usage, and are not invoices or current pricing recommendations. The standalone practice projects use separately labeled authored fixtures.
