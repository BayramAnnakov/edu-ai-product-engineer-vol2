# Lead Scout · Durable execution

Open learner-worksheet.html first. If you work with a coding agent, ask it to read AGENTS.md before anything else. The worksheet asks for a prediction before each step and reveals the next commands only after you save it. You can complete the recorded path in a browser.

**Four words.** A *worker* is a replaceable process that runs one step at a time (not a subagent; it calls no model). The *journal* is the record, kept outside the worker, of which steps finished. *Durable execution*: a new worker reads the journal, skips every finished step and runs the unfinished one again. A *receipt* is the ID the drafts service returns for a write, for example a draft ID.

**The story.** Lead Scout writes follow-up emails as drafts in a drafts service, where a person reviews and sends them. Every draft needs an approval. Each draft belongs to one *request*, for example `outreach/17/nov`: Alder Freight's November follow-up.

## Setup before class

Use Python 3.11+ on macOS, Linux or WSL. Run these in the extracted folder. The recovery lab uses local synthetic accounts and needs no model key.

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt

Every `lab.py` command prints a readable summary: the drafts service first, then the inbox, the DBOS journal and the history. Add `--json` for the raw data.

## 1. The crash

    python lab.py init --state trial-1
    python lab.py crash --state trial-1
    python lab.py inspect --state trial-1

`crash` kills the worker in the middle of a step and shows only the journal. `inspect` shows the drafts service too.

## 2. The outage

While the worker is down, Birch Labs' approval is withdrawn, Birch's scheduled reminder (a timer) fires twice, and Elm Textiles' contact moves to procurement. Write your forecast in the worksheet, then:

    python lab.py outage --state trial-1
    python lab.py resume --state trial-1

## 3. The starter's report

Alder approves a second follow-up, for December (`outreach/17/dec`); its event arrives twice. Run it on the starter and keep the report:

    python lab.py december --state trial-1
    python lab.py verify --state trial-1

`verify` writes trial-1/report.json and exits 1: the starter passes 3 of 7 checks. Keep that file for the worksheet. Each failing check is one of the three fixes below.

## 4. Three fixes, one function each

`policy.py` holds three choices. Fix one at a time. Before each fix, decide which identity the function should return and tell your coding agent; it should change only that function. After each fix, run the unit checks and the whole drill in a new folder.

**Fix 1 · duplicate write.** `draft_key` decides what the drafts service treats as the same request. The starter returns the attempt ID.

    python -m unittest -v check_policy
    python lab.py run --state fix-1

Expected: 1 of 4 unit checks, 4 of 7 recovery checks. "original receipt recovered" turns green. Look at December and Birch in the output: the work still runs twice.

**Fix 2 · lost or doubled event.** A sender that hears no answer sends again, so one event can arrive in several *deliveries* (wire-02, wire-03). An *event* is one thing that happened (timer-53, job-dec-17). A *request* is one intended write (outreach/17/dec). `inbox_key` decides what the inbox treats as already seen.

    python -m unittest -v check_policy
    python lab.py run --state fix-2

Expected: 3 of 4 unit checks, 6 of 7 recovery checks.

**Fix 3 · stale data.** `recipient` decides which contact the draft uses. Elm has two: the one queued with the job and the account's current one, which its owner changed while the worker was down.

    python -m unittest -v check_policy
    python lab.py run --state trial-2
    python lab.py resume --state trial-2

Expected: 4 of 4 unit checks, 7 of 7 recovery checks, and the second resume changes nothing. If trial-2 already exists from an earlier attempt, use trial-2b; the worksheet checks the report's contents, not the folder name. Attach trial-1/report.json and trial-2/report.json to the local-run worksheet. The recorded path has a separate notification to diagnose. Forecasts can be exported as prediction.md.

## 5. Break your green checks

After all three fixes pass 7/7, give your coding agent the prompt from the “Break your green checks” slide:

> My policy.py passes all checks. Try to break it. Save a copy as policy.good.py. The inbox key could plausibly be the event ID or the request ID: try both. For each, run the unit checks, then `python lab.py run --state trial-N`, `python lab.py reconcile --state trial-N` and `python lab.py verify --state trial-N` with a fresh N. Tell me how many jobs reconcile-17 got and what verify said for each key. Then add one test to check_policy.py that tells the two keys apart, keep the key you trust, and show every check passing.

`reconcile` delivers a new event, reconcile-17, that asks again about the existing November request, and prints the jobs it got and the draft count. It should get the existing receipt back.

## Your own write

Fill the four lines in the worksheet's last section: the write, the request key, the destination's contract and what you read again at write time. For homework, get `skills/kill-resume-drill` from the course repository (github.com/BayramAnnakov/edu-ai-product-engineer-vol2) and copy it into your project's `.claude/skills/` (Claude Code picks it up as /kill-resume-drill; in Codex, ask it to read that SKILL.md and follow it). Then have your agent run the drill on that write in a disposable copy.

## Side experiment: one agent or three

A separate run, not the crash lab: the same five research calls on 20 W2 accounts, one at a time or three in parallel. Before you look, write the quality floor and time limit from your W1 decision.md that would make three in parallel worth it. Then print the recording:

    python compare.py

Optional, after class, with a Claude Code login: repeat it live. The cap applies to each of the three configurations; use a fresh output filename for each paid run.

    python compare.py --live --provider claude --max-budget-usd 0.25 --output my-team-run.json

Identify the matching packet input, name two calls that ran at the same time and cite their intervals. Each configuration ran once in a fixed order with different cache usage. Record the accepted count and elapsed time for one configuration, then give a keep/change/repeat decision and the next comparison that would test it. Use the worksheet to export decision.md.

## Homework

Due before Workshop 4 on 6 December. Cap: 3–4 hours.

- **Track A, building with agents:** one issue → PR pipeline, in a throwaway repository you create for the drill (or a local stand-in for the PR registry; say which). The PR identity is the key (for example branch `issue-<n>`); the agent checks for an existing PR before creating one. Kill a run after the PR is created, resume it, and show the original URL. A new issue must still produce a new PR.
- **Track B, an agent inside your product:** your product's longest job. Durable state plus an idempotency key (a request key) on its one real external action, and an approval check at write time. Carry a correction into the outage and show the record at the destination.
- **Both tracks:** start from the four-line card in the worksheet and run /kill-resume-drill on that write in a disposable copy. Submit `drill-card.md` from the drill and `decision.md` from the worksheet. Where your work genuinely splits into independent parts, add the same one-agent-versus-team comparison on it.

Extensions, if you have time:

- **The sequential task.** Run the team comparison on work whose steps depend on each other, and measure whether the team helps or hurts.
- **Two critics.** Compare a critic that sees only the evidence with one that reads the workers' conclusions.
- **Agent teams as a demo.** Experimental; expect many more tokens than one agent (not measured in this lab).
