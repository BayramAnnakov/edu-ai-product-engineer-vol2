# Validation — 25 October 2026 (Pacific)

## What ran

- **18 automated checks** for quality gates, independent task/judge values, failed/unknown work, missing cases, duplicate attempts, frozen-input drift, shared entities, renamed duplicate inputs, all-stage budget, zero-correct denominators, report integrity, dev-only export and both installation targets.
- The skill-creator frontmatter/scaffold validator passes. The validator used temporary PyYAML tooling; the distributed kit uses Python standard library only.
- Release guard checks local document links, actual trace-file hashes and configured private-data patterns. The original six excerpts were also checked against private originals: numeric usage/cost/latency are unchanged and scoring error semantics retained.
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

The original fixture-project tests establish controlled fixture execution and skill usability by agents across two separate projects. Model outputs, prices and job times in those projects are authored. The fixture model bank is perfect by construction; review/infra/agent-compute costs are unpriced. Actual paid model calls in these tests: 0. No production savings, model-quality generalization or human learning/retention is established.

Installers were executed into isolated project directories for Codex and Claude and preserve an existing skill. Discovery paths/invocation syntax were checked against official docs; cross-version slash-menu behavior was not exercised in every host. The helper verifies supplied receipts retrospectively; it does not enforce a live provider spending/time limit or authenticate a runner's evidence label.

The five-question HTML replay was traversed in the browser: counters, economics and outputs reveal progressively, navigation is gated, the own-workflow form generates a real downloaded Markdown plan, and no browser warnings/errors were recorded. Local-file URL automation is blocked by the browser policy, so browser verification used a loopback server; the HTML contains inline data/CSS/JS and no runtime network dependency.


## Recorded Lead Scout classroom starter — 24 Oct 2026

The standalone starter contains 30 public development examples with reference labels and 480 exact recorded request variants. It includes no final cases, private case generator/course judge, API credentials or private trace URLs. Seven additional checks pass. A clean-ZIP run with network access disabled completed explicit initialization, reference comparison, policy edit, fixed/adaptive dev, freeze, separate evaluation-packet import, saved-result recovery and decision export. Thirty-six policy/configuration comparisons match original task correctness, model cost, attempts and cache counters. This is software acceptance evidence; it does not establish classroom pacing or human learning outcomes.

## Current model-choice practice — 25 Oct 2026

The model-choice starter contains 30 synthetic development cases with actual Sol, Luna and Terra outputs and Jev executor choices. Seven offline checks pass: complete CLI/export, recorded model comparison, all router calls/rule coverage counted, fixed baseline under router edits, public scoring criteria included, supporting evidence required, and valid-format/wrong-score distinction. The student opens the folder in Codex or Claude Code; AGENTS.md and CLAUDE.md guide the agent to run commands and evaluate the hypothesis, while the student chooses limits/verdict. No skill installation, provider key or server is needed. All prediction fields start blank and the baseline choice is explicit. No evaluation cases or private course judge are distributed.

The instructor separately recorded 240 model/router calls on development and entity-disjoint evaluation cases, froze the protocol before the new evaluation, and uploaded traces to the private instructor project. Total new model-study spend was $0.17728625 at dated usage rates. On the 30 evaluation cases, Sol/Luna were 30/30; Terra 27/30; Jev routing 30/30 but more expensive than Luna alone. These small authored-label samples do not establish production reliability or human learning. Four new sanitized physical-call excerpts bring the selected trace set to ten.

An independent agent also applied bakeoff to actual Onsa company-profile coalescing code outside these starter projects. Eight crafted local batches preserved 124 outputs while upstream fixture attempts fell from 92 to 28. Real field dollar cost remained unknown, so the helper verdict stayed inconclusive. This was local mechanism/transfer evidence, not production savings.


## Final agent-led acceptance

A clean browser-downloaded release was opened as a coding-agent project using its AGENTS.md and Claude entry file. An agent simulated student choices, tested a new verified-size rule before Luna with a 100% dev floor and 5% useful-gain target, inspected rejecting boundaries and exported the readable decision, JSON and exact code. All 30 known development answers remained correct; recorded attempts fell 30→27 and model cost/correct fell 10.7683%. Ten local rejecting probes abstained. The decision was test-further, with independent cases and unmeasured implementation/review cost still required. Total technical exercise elapsed was 4m31s inside the 25-minute allowance, including an export-format repair and final clean-release recheck. No new provider calls were made. This is agent execution in an existing Python runtime, not human pacing, a clean operating-system install or broad model-quality validation.

The final distribution has 97 text files and passes the configured privacy/link/trace-hash guard, 18 helper/kit tests and seven current model-starter tests. The original recorded starter is optional history. Codex and Claude Code share the supplied instructions; cross-version host menus and participant laptops still need their own preflight.

## Workshop 2 kit — 8 November 2026

`lesson2/` is the Workshop 2 learner starter, byte for byte the take-home ZIP. Checked before publishing: every Lab A command and the three extension-corpus commands ran in a bare `python:3.10-slim` container from the ZIP; `checks.py` shows its four intended failures in the shipped starter and passes with a reference guard kept outside this repository; a clean Claude Code session made the four checks pass from `README.md` alone; the dreaming pass and four fresh-reader sessions ran in clean `claude -p` sessions, one run each. The extension-corpus numbers in `README.md` (recall 0, 11 and 32 of 32; token estimates) are asserted by the instructor's verifier against `records-large.json`. The RLM figures quoted in `README.md` come from one recorded sandbox run; the recording itself, the deck and the instructor notes are not in this repository. Not measured: a timed session with participants.

## Workshop 3 kit — 21 November 2026

`lesson3/` is the Workshop 3 learner starter, the take-home ZIP plus this `AGENTS.md`. Checked before publishing, from the ZIP: the starter fails as intended (0/4 unit checks, 3/7 recovery checks, verify exit 1); a correct repair kept outside this repository passes 4/4 and 7/7; an account-keyed inbox fails one unit check and one recovery check; a request-keyed inbox passes every supplied check and loses the `reconcile-17` event (0 jobs, verify still 7/7), which is the point of "Break your green checks". The whole path also ran in a bare `python:3.11` container. In clean Claude Code sessions (one run each): the "Break your green checks" prompt produced the failing test and restored a passing policy; `kill-resume-drill` ran on two other public projects and wrote a drill card for each, one of which found three real defects. The skill's wording was clarified after those two runs. `recorded-comparison.json` is one recorded run per configuration in a fixed order, so it does not support cost or quality claims. Not measured: a timed session with participants.

Update, 21 Nov evening: `lesson3/` now matches the restructured learner ZIP exactly (AGENTS.md included; the drill skill ships under `lesson3/skills/` so no agent loads it during the repair; the worksheet holds the repair results until the learner saves an explanation of both identities; README carries the homework spec and extensions). Rehearsed again from the ZIP with the same results; the skill rerun on two other projects is recorded separately.

Update, 21 Nov night: Workshop 3 is now three fix cycles, one `policy.py` function each (`draft_key`, `inbox_key`, `recipient`), with expected counts 1/4 · 4/7, 3/4 · 6/7, 4/4 · 7/7 recorded by the instructor's rehearsal and re-checked in a bare python:3.11 container from this kit. `lab.py` prints a readable summary (`--json` for raw data). The drill skill lives only in the repository's `skills/kill-resume-drill/`, not in `lesson3/`, so no coding agent reads it during the repair. Clean agent sessions with `lesson3/AGENTS.md` changed one function per fix and asked when the learner had not chosen.

Update, 22 Nov: `lesson3/` matches the learner ZIP 44393781… The one-vs-three comparison moved to a side-experiment section at the debrief (live run optional, after class); the worksheet asks for the W1 quality floor in section 4. Rehearsed from the ZIP with the same counts (starter 0/4 · 3/7 → fix 1 1/4 · 4/7 → fix 2 3/4 · 6/7 → all three 4/4 · 7/7).
