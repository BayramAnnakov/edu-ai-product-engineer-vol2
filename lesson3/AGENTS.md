# Lead Scout Workshop 3

Help the learner run the durable-execution drill. All accounts and events are synthetic and local. The recovery lab
needs Python 3.11+ and the pinned `dbos` package (`pip install -r requirements.txt` in a virtual environment); it
needs no model key. The browser worksheet, `learner-worksheet.html`, is the common path.

Follow `README.md` in order. Before each command, ask the learner for their prediction and let them write it in the
worksheet; do not reveal outputs or receipts ahead of the step that produces them. After a command, point the learner
at the destination records (the drafts and inbox in the printed JSON; drafts come first) rather than the worker's
status.

For the repair, the learner decides the three choices in `policy.py`: how to identify an inbox event across
deliveries, how to identify a logical write across attempts, and where the current recipient comes from. Ask them to
explain both identities in their own words before you edit anything, then implement their choice. Do not edit
`service.py`, `worker.py`, `lab.py` or `check_policy.py` during the repair. Use a fresh `--state` directory for every
trial and keep the failing starter's `trial-1/report.json`.

For "Break your green checks", follow the prompt in `README.md`; there you may add one test to `check_policy.py`.
For the team comparison, `python compare.py` prints the recording; a live run needs the learner's own Claude Code
login and their explicit go-ahead, because it spends model budget.

To apply the drill to the learner's own project, use `.claude/skills/kill-resume-drill/SKILL.md` in a disposable copy
of that project. Do not ask for or use credentials, and never write to a production destination.
