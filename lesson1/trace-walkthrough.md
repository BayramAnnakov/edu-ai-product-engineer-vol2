# Read the receipts before making a savings claim

All examples below are real recorded calls from24 October 2026 on synthetic cases or public documentation. They are sanitized excerpts, not exact replayable provider requests. The separate practice projects are authored fixtures.

Run `python3 scripts/inspect_traces.py` from the repository root, or open [the JSONL files](traces/README.md). No Langfuse account or API key is needed.

## Cache: predict → counters → economics

1. A timestamp changes before a long repeated prefix. Predict whether the second request reuses it.
2. Read `cache-pair.jsonl`. Changing-prefix calls read 0 cached tokens each; stable cold writes 12,124 tokens; stable warm reads 12,069 and writes 55.
3. Compare each cold/warm pair including writes: stable $0.0338264 versus changing $0.0625520,45.92%lower in this one pair.
4. Stable cold took 3.67s, warm 4.00s. This sample supports lower token-priced cost, not a speedup. These are dated usage-price calculations, not reconciled bills.
5. This long public-document workload is different from the short scoring prompt. The two scorer receipts have zero cache reads/writes.

## Scoring: a valid typed answer can still be wrong

Read `scoring-boundary.jsonl`: same synthetic source has 24 employees/4 sales staff; the contract requires at least 50/10. The required score is1 / not_icp. The large model returns1; Jev returns3 / not_icp while citing a real supplied record. The evidence ID and JSON shape are valid; the decision is wrong.

Ask: what does that error do downstream, and what is its business cost? The fixture does not show whether a sales workflow actually admitted or reviewed the lead. Jev has seven Choice questions in one paid request here; all returned usage is counted. It has no effort parameter; low/high replay aliases do not create a real effort comparison. One selected error does not estimate a population error rate.

## Separate test verdict and business decision

[Bayram’s public post1844](https://t.me/ProductsAndStartups/1844) describes a different 616-case test: about 25% lower cost and 2.6× speed while lost good leads increased 1.4%→4.3%. The formal test failed; the owner chose rollout with followthrough. This is reported history, not the later follow-up result or this tiny sample. Preserve both records; a proposed classroom trial authorizes no production rollout.
