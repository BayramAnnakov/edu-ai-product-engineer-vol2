# coding-review-canonical-docs-only-bypass

Held-out comparison of the supplied cases.

Task: Return clear only for a nonempty documentation-only change (.md under docs/ or exact root README.md), or exclusively src/generated/ with verified provenance and unchanged generator. Mixed changes, empty input, spoofed generated paths, dependencies, absolute paths, and dot segments require review. Exact authored expected labels define task correctness. False clear is consequential; an unnecessary model call is a cost error. The authored model bank is perfect. Candidate intentionally only bypasses canonical documentation-only changes and routes all else to model.
Hypothesis: Removing model work only when all paths are canonical relative documentation paths preserves 100% exact task correctness and reduces fixture machine cost per correct result by at least 10%. Reject invalid or ambiguous paths; no ID, group, expected-label or bank access in router. No caching or model swap.

| Arm | Correct / N | Judge / N | Machine $ | $ / correct | Calls | Job p95 s | Review coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 30/30 | 30/30 | 0.600000 | 0.020000 | 30 | 9.000000 | 0/30 |
| candidate | 30/30 | 30/30 | 0.480000 | 0.016000 | 24 | 9.000000 | 0/30 |

Cost/correct reduction: 20.000000%
Frozen experiment verdict: **worked**

Gates: {"quality": true, "minimum_cost_reduction": true, "latency": true, "budget": true}

## Errors and incomplete evidence
{
  "baseline": {
    "error_cases": [],
    "missing_cases": [],
    "unknown_cost_attempts": 0,
    "evidence_modes": [
      "fixture"
    ]
  },
  "candidate": {
    "error_cases": [],
    "missing_cases": [],
    "unknown_cost_attempts": 0,
    "evidence_modes": [
      "fixture"
    ]
  }
}

## Experiment budget (development/setup + this comparison)
{
  "prior": {
    "known_cost_usd": 1.0800000000000005,
    "unknown_cost_attempts": 0
  },
  "known_total_cost_usd": 2.1600000000000006,
  "all_costs_known": true
}

Unique evaluation inputs: 30

## Owner decision
{
  "choice": "keep",
  "reason": "Keep the frozen documentation-only bypass in this isolated fixture: all 30 evaluation cases remain task-correct and fixture cost/correct falls 20%, with development plus comparison cost $2.16 under $3. This is a learner decision for the fixture only; it provides no production rollout or provider-quality evidence.",
  "conditions": null,
  "authorizes_deployment": false
}

## Evidence limitations
- Evidence modes are labels supplied by the runner, not authenticated receipts.
- Offline or recorded rows do not establish fresh production savings.
- Small samples do not establish stable p95 or rare failure rates.
- Human review/rework remains separate from machine cost.

## Next experiment in my own workflow
Test summary-first report reading against full dumps, on disjoint independently labeled reports. Reject missed gates, costs or evidence limitations; count fallback and correction work. This is a proposal only.
