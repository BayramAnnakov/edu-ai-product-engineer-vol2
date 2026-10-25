# Offline comparison helper

Python 3.10+ standard library; no API calls, credentials or package installation. Commands are relative to the skill folder's `scripts/bakeoff.py`.

1. Fill an experiment contract. Its `cases` path is relative to that contract. `pins` lists task/rubric/config/adapter files, also relative to it.
2. `freeze --contract experiment.json --out lock.json` records the exact contract, case data and pinned file hashes. The helper refuses changed files later. This protects against accidental drift; hashes are not an access-control or cryptographic attestation system.
3. Execute the workflow using its own runner; save one JSONL row per case for baseline and candidate. The helper never executes an arbitrary command supplied in a trace.
4. `compare --lock lock.json --baseline baseline.jsonl --candidate candidate.jsonl --out report` writes JSON and Markdown. Missing cases remain in N and make the verdict inconclusive. Duplicate cases/attempt IDs, extra cases, invalid costs and changed pins are rejected.
5. `decide --report report/report.json --choice revert --reason '...' --out decision.md` records a separate owner decision. `keep` requires all frozen gates to pass; `bounded-trial` additionally requires `--owner`, `--value`, `--exposure`, `--rollback`, `--checkpoint`. `--value` includes accepted error cost. The original gate verdict remains intact.

Case file is a JSON list of `{ "id": "case-01", "group": "entity-01", "expected": "review" }`. Evaluation groups must not occur in the optional `dev_cases` file. Exact labels are suitable for the bundled bounded examples. Omit `expected` for semantic tasks and supply `task_correct` as an independently established boolean plus `label_source` on every returned row. If expected exists, the helper recomputes correctness and rejects a contradictory supplied grade. It does not infer correctness from judge acceptance.

Each receipt row:

```json
{"case_id":"case-01","output":"review","judge_accepted":true,"serious_failure":false,"job_seconds":1.2,"review_seconds":null,"evidence_mode":"fixture","attempts":[{"id":"case-01-call-1","status":"success","cost_usd":0.002,"input_tokens":120,"output_tokens":8,"cache_read_tokens":0,"cache_write_tokens":0}]}
```

`evidence_mode` is `fixture`, `recorded-provider`, or `live-provider`. `job_seconds` is measured end-to-end in live runs; authored or composed in offline runs and labeled accordingly. `review_seconds:null` means unmeasured. Set unknown `cost_usd` to null; do not substitute zero. Include failed attempts too. Empty attempts means no model call (e.g. deterministic rule); put infrastructure/tool costs in separate attempts if known. IDs must be unique within each comparison arm; pairing the same physical receipt in separate replay policies is permitted but is not new spend.

The report calculates machine cost/correct separately from cost/judge-accepted; it does not monetize unmeasured human work. Threshold comparisons are inclusive. List earlier development/setup JSONL files in `prior_receipts` before freeze; their hashes and attempted costs are included in `max_total_cost_usd` together with both comparison arms. Do not omit prior work merely to pass the cap. This is retrospective verification, not a live spend guard. Enforce actual paid-call reservations and the tuning-time limit in your runner. Schema validation cannot prove that a `live-provider` label or human grade is truthful.

When cases contain `input`, freeze rejects exact development/evaluation input overlap regardless of renamed IDs and reports the count of unique evaluation inputs. It cannot detect every semantic near-duplicate: inspect entity/temporal splits and shared answer sources too. Do not open a model-output bank containing evaluation answers before freeze. Keep dev/evaluation banks separate.

For a dev rejection, set `stage:"dev-screening"` before freeze and compare those dev cases. The exported heading explicitly states dev-only; it does not claim held-out validation. Do not pretend a rejected candidate is production-ready.
