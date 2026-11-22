# Lead Scout · Durable execution

Open learner-worksheet.html first. Alder's last message was “Creating draft…” Write your first move with the recovery terminal idle. After the journal appears, write down which service record would distinguish the possible outcomes. The worksheet then reveals the crash commands. You can complete the recorded path in a browser.

## Setup before class

Use Python 3.11+ on macOS, Linux or WSL. Run these in the extracted folder. The recovery lab uses local synthetic accounts and needs no model key.

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt

If you have a Claude Code login, you can start the separate 20-account comparison in a second terminal. Activate the same environment there. Leave its output until the debrief.

    python compare.py --live --provider claude --max-budget-usd 0.25 --output my-team-run.json > team-output.txt

The cap applies to each of the three configurations. Use a fresh output filename for each paid run. For the offline path, wait until the debrief to run the supplied recording.

## After both opening predictions

    python lab.py init --state trial-1
    python lab.py crash --state trial-1
    python lab.py inspect --state trial-1

`inspect`, `resume` and `december` print the whole service state as JSON. The drafts come first, so scroll up to the top of the output. The crash command shows the worker exit and DBOS journal. Inspect reads the drafts service as well. In the worksheet, forecast Alder’s next receipt, the handling of Birch’s two timer deliveries after revocation, and Elm’s recipient after the W2 correction. Save that forecast before continuing.

    python lab.py outage --state trial-1
    python lab.py resume --state trial-1

Compare your forecast with the November receipts. Now Alder approves a fresh December request. The same December event arrives twice. Predict how many drafts should exist for this account across both months.

    python lab.py december --state trial-1
    python lab.py verify --state trial-1

December uses the ordinary inbox, DBOS worker, and drafts service. Verification writes trial-1/report.json and exits 1 for the intentionally failing starter. Keep that report for your worksheet.

## Repair and repeat

The worker and service transaction are supplied. Ask your coding agent to read policy.py, service.py, worker.py and check_policy.py. Ask it to repair the three choices in policy.py so redelivery, independent events, logical writes and current routing behave correctly. Preserve the tests. Explain the event key and request key in your own words before checking its changes.

    python -m unittest -v check_policy
    python lab.py run --state trial-2
    python lab.py verify --state trial-2
    python lab.py resume --state trial-2

The combined run includes the crash, outage, November recovery and December follow-up. A complete repair passes four policy tests and seven end-to-end checks. Use a fresh trial directory after each policy change. Attach the starter and repaired report.json files to the local-run worksheet. The recorded path has a separate notification to diagnose. Forecasts can be exported as prediction.md.

## Break your green checks

After your repair passes 7/7, give your coding agent the prompt from the “Break your green checks” slide:

> My policy.py passes all checks. Try to break it. Save a copy as policy.good.py. The inbox key could plausibly be the event ID or the request ID: try both. For each, run the unit checks, then `python lab.py run --state trial-N`, `python lab.py reconcile --state trial-N` and `python lab.py verify --state trial-N` with a fresh N. Tell me how many jobs reconcile-17 got and what verify said for each key. Then add one test to check_policy.py that fails with the key that lost the event, show it failing, put back the key that kept it and show every check passing.

It tries both plausible inbox keys in fresh trial folders with

    python lab.py run --state trial-3
    python lab.py reconcile --state trial-3
    python lab.py verify --state trial-3

`reconcile` delivers a new event, reconcile-17, for the existing November request and prints its jobs and the draft count. Note what verify says, then have the agent write the test that catches the key that lost the event.

## Your own write

Fill the four lines in the worksheet's last section: the write, the request identity, the destination's contract and what you read again at write time. For homework, copy `.claude/skills/kill-resume-drill` into your project's `.claude/skills/` (Claude Code picks it up as /kill-resume-drill; in Codex, ask it to read that SKILL.md and follow it). Then have your agent run the drill on that write in a disposable copy.

## Team debrief

Run the following at the debrief to print the captured comparison. For a live run, open team-output.txt instead.

    python compare.py

Identify the matching packet input, name two overlapping calls and cite their intervals. Each arm ran once in a fixed order with different cache usage. Record the accepted count and elapsed time for one configuration, then give a keep/change/repeat decision and the next comparison that would test it. Use the worksheet to export decision.md.
