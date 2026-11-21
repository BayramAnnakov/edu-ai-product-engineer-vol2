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

The crash command shows the worker exit and DBOS journal. Inspect reads the drafts service as well. In the worksheet, forecast Alder’s next receipt, the handling of Birch’s two timer deliveries after revocation, and Elm’s recipient after the W2 correction. Save that forecast before continuing.

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

## Team debrief

Run the following at the debrief to print the captured comparison. For a live run, open team-output.txt instead.

    python compare.py

Identify the matching packet input, name two overlapping calls and cite their intervals. Each arm ran once in a fixed order with different cache usage. Record the accepted count and elapsed time for one configuration, then give a keep/change/repeat decision and the next comparison that would test it. Use the worksheet to export decision.md. For transfer to your own job, invoke /kill-resume-drill or open .claude/skills/kill-resume-drill/SKILL.md.
