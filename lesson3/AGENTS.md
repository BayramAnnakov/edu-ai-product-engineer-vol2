# Lead Scout Workshop 3

Help the learner run the durable-execution drill. All accounts and events are synthetic and local. The recovery lab
needs Python 3.11+ and the pinned `dbos` package (`pip install -r requirements.txt` in a virtual environment); it
needs no model key. The browser worksheet, `learner-worksheet.html`, is the common path.

Follow `README.md` in order. Before each command, ask the learner for their prediction and let them write it in the
worksheet; do not reveal outputs or receipts ahead of the step that produces them. After a command, point the learner
at the destination records (the drafts service, which `lab.py` prints first) rather than the worker's status. Use
`--json` only when you need the raw data yourself.

During the repair, do not open `check_policy.py` or the `checks` function in `lab.py` before the learner has chosen
the return value: they encode the answers. Run them afterwards; if they fail, read the failing test name aloud and ask
the learner to choose again.

The repair is three separate fixes, in this order: `draft_key`, then `inbox_key`, then `recipient`. For each fix:
ask the learner which identity the function should return and why, change only that one function to what they chose,
then run `python -m unittest -v check_policy` and the drill in that fix's own folder: `python lab.py run --state fix-1`
for the first fix, `--state fix-2` for the second, `--state trial-2` for the third (if trial-2 already exists, use trial-2b; the worksheet
checks the report's contents). Never reuse a folder. Do not change the other
two functions, even when you can see what they need. If the learner's choice does not turn the expected checks green,
show the failing check and ask them to choose again rather than fixing it for them. Do not edit `service.py`,
`worker.py`, `lab.py` or `check_policy.py` during the repair. Keep the failing starter's `trial-1/report.json`.

For "Break your green checks", follow the prompt in `README.md`; there you may add one test to `check_policy.py`.
For the team comparison, `python compare.py` prints the recording; a live run needs the learner's own Claude Code
login and their explicit go-ahead, because it spends model budget.

To apply the drill to the learner's own project after the lab, the learner gets `skills/kill-resume-drill` from the
course repository and copies it into that project's `.claude/skills/`; run it in a disposable copy of that project. Do not ask for or use credentials, and never write to a
production destination.

