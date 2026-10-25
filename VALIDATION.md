# Validation — 24 October 2026 (Pacific)

## What ran

- **18 automated checks** for quality gates, independent task/judge values, failed/unknown work, missing cases, duplicate attempts, frozen-input drift, shared entities, renamed duplicate inputs, all-stage budget, zero-correct denominators, report integrity, dev-only export and both installation targets.
- The skill-creator frontmatter/scaffold validator passes. The validator used temporary PyYAML tooling; the distributed kit uses Python standard library only.
- Release guard checks local document links, actual trace-file hashes and configured private-data patterns. Six excerpts were also checked against private originals: numeric usage/cost/latency are unchanged and scoring error semantics retained.
- Two fresh independent learner agents used only the skill, project contract and raw offline project. They edited their own routers, screened on dev, froze before evaluation and produced decisions and own-workflow next experiments.

| Corrected forward test | Dev / eval correctness per arm | Candidate mechanism | Fixture cost/correct | Total dev+eval fixture cost | Authored job p95 | Actual agent time |
|---|---|---|---|---|---|---|
| Coding review | 30/30 and 30/30 | Documentation-only bypass; generated cases still use model | $0.020→$0.016 (20% lower) | $2.16/$3 | 9s→9s | 202.551s |
| Support triage | 30/30 and 30/30 | Scoped, current, matching result reuse; defer other cases | $0.020→$0.016 (20% lower) | $2.16/$3 | 9s→9s | 196.5s |

Coding also passed 17 boundary probes; support passed 10 extra dev probes and 30 held-out route checks. Evaluation inputs are distinct from dev inputs; banks were not read into learner context before freeze. Each chose keep **only in its isolated fixture**, with no deployment authorization. The [worked example](lesson1/worked-example/README.md) preserves the coding result, traces and reasoning.

## Problems the tests caught

The initial examples reused all evaluation input content under new IDs/groups. A shared model-output bank could also leak evaluation outputs during source inspection. The helper initially omitted earlier development runs from the total cap. Those first results are mechanism-only evidence and are not presented as clean held-out validation.

The distributed version splits model banks, varies evaluation boundary conditions and rejects exact dev/eval content overlap as well as entity overlap. It hashes prior development/setup receipt files and includes them in the experiment budget. The fresh independent tests above used that corrected package.

## Limits

These tests establish controlled fixture execution and skill usability by agents across two separate projects. Model outputs, prices and job times in those projects are authored. The fixture model bank is perfect by construction; review/infra/agent-compute costs are unpriced. Actual paid model calls in these tests: 0. No production savings, model-quality generalization or human learning/retention is established.

Installers were executed into isolated project directories for Codex and Claude and preserve an existing skill. Discovery paths/invocation syntax were checked against official docs; cross-version slash-menu behavior was not exercised in every host. The helper verifies supplied receipts retrospectively; it does not enforce a live provider spending/time limit or authenticate a runner's evidence label.

The five-question HTML replay was traversed in the browser: counters, economics and outputs reveal progressively, navigation is gated, the own-workflow form generates a real downloaded Markdown plan, and no browser warnings/errors were recorded. Local-file URL automation is blocked by the browser policy, so browser verification used a loopback server; the HTML contains inline data/CSS/JS and no runtime network dependency.


## Recorded Lead Scout classroom starter — 24 Oct 2026

The standalone starter contains 30 public development examples with reference labels and 480 exact recorded request variants. It includes no final cases, private case generator/course judge, API credentials or private trace URLs. Seven additional checks pass. A clean-ZIP run with network access disabled completed explicit initialization, reference comparison, policy edit, fixed/adaptive dev, freeze, separate evaluation-packet import, saved-result recovery and decision export. Thirty-six policy/configuration comparisons match original task correctness, model cost, attempts and cache counters. This is software acceptance evidence; it does not establish classroom pacing or human learning outcomes.
