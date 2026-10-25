# Lead Scout practice for Codex and Claude Code

Help the student complete one bounded optimization in the final 25 minutes. They are learning to choose and evaluate a change, not to operate a CLI. Run the commands for them and explain the few decisions they must make. Use the student's language.

## Context and evidence

Lead Scout returns a priority score, short reason and supporting record IDs. The public business policy is in README.md and data.json.scoring_criteria. The package has 30 synthetic development cases with actual recorded Sol/Luna/Terra answers and Jev executor choices. References are public practice labels, not unseen evaluation. Replay is local and free of new provider calls. Coding-agent usage, local code, fetching, infrastructure and human review are unpriced.

Jev chooses Luna or Sol; the selected scorer produces the company score. A code rule can finish an answer only when the policy and available evidence fully determine it. Missing/conflicting/unsupported evidence must make a narrow rule abstain. Do not assume that routing or a bigger model improves this task.

## Student interaction

1. Read this file, README.md, router.py and lab.py. Inspect the public policy and a few relevant records with `python3 lab.py inspect --case D-015` (pick other dev IDs as needed). Explain the fixed Luna-alone baseline and the candidate options in plain language.
2. Ask the student to choose one hypothesis, quality floor, minimum useful cost/correct improvement and tuning-time limit. Bundle these into one concise question. Suggest at most two concrete interventions if they need help. Do not fill their forecast silently or choose their final verdict.
3. After they choose, initialize the candidate, fill work/prediction.json and change one thing in router.py or work/policy.json. Offer one small code rule or routing condition; keep the scope manageable. Use 5 minutes to define, 10 to edit/run, 10 to inspect/decide. Existing files or a locked forecast must be preserved; use a fresh extracted folder for a new experiment.
4. Run the experiment and inspect quality/errors before savings. If no new errors occur, inspect an abstention/boundary or an actual recorded model mistake. Explain what disappeared, all incurred attempts, the measured effect and what remains unknown. Add focused boundary checks appropriate to the new rule; the harness tests are not proof that the student's change is correct.
5. Ask the student for a verdict and reason: revert, insufficient-evidence, or test-further. Export with a relevant --trace-case. Open/summarize work/decision.md, point to decision.json and tested-router.py, and name the next independent evidence needed. A passing dev result does not authorize deployment.

## Commands you execute

Use the available Python 3.10+ interpreter (`python3`, or `py -3` on Windows). No pip/npm install, server, Langfuse login or API key is needed.

- `python3 -m unittest -q test_lab.py` — harness checks, not candidate validation.
- `python3 lab.py compare` — direct recorded models plus Jev routing.
- `python3 lab.py inspect --case D-015` — policy, source records and actual outputs.
- `python3 lab.py init --model luna` — explicit candidate executor; sol/terra also supported.
- `python3 lab.py run` — local candidate versus immutable Luna baseline.
- `python3 lab.py export --decision test-further --trace-case D-015 --reason "Student's chosen rationale and next evidence"` — choose the student's actual verdict/case/reason.

The full kit also contains ../../skills/bakeoff/SKILL.md. Read it when present; installation is optional for this exercise. In Codex the installed invocation is $bakeoff; in Claude Code it is /bakeoff. The small ZIP works with these instructions alone.

## Boundaries

Edit only router.py, work/policy.json and newly created work outputs/tests. Preserve lab.py, test_lab.py, manifest.json, data.json, references, saved calls, pricing and latency. Never branch on a company/case ID, expected label or recorded answer. Only public input facts can choose a route. Unknown inputs/prompts/models need new evidence; do not substitute an answer or invent a result.

Count every Jev, scorer and structural fallback call. Gold correctness must never trigger fallback. Do not adjust a floor after observing results, hide a failed gate, extend a locked cap, overwrite a prior exercise or claim the known dev cases are a fresh validation. Do not create keys, send data, call providers, deploy, publish or schedule reminders/followthrough for this practice. If Python or usable evidence is unavailable, help complete an explicitly unexecuted experiment brief instead of fabricating execution.
