# Lead Scout starter for Codex and Claude Code

Open this extracted folder as a project in **Codex or Claude Code**. Paste:

> Read AGENTS.md and help me run one bounded bakeoff in 25 minutes. Explain my options, ask me to choose the hypothesis and limits, then run the experiment and help me interpret the evidence. I will choose the final decision.

Your coding agent handles the commands and files. You choose the change, acceptable errors, useful improvement and final verdict. No skill installation, provider account, API key, server or Langfuse login is needed. An available Python 3.10+ interpreter is sufficient. Codex reads AGENTS.md; CLAUDE.md points Claude Code to the same instructions.

Use about 5 minutes to define the experiment, 10 to edit and run, and 10 to inspect evidence and decide. With no own case, this is your practice case. The full take-home kit also includes the reusable bakeoff skill for your own projects.

## The business policy

Lead Scout prioritizes companies for sales teams. Fit means B2B SaaS, 50–1000 verified employees and at least 10 sales staff. A verified below-minimum company or agency scores 1 / not_icp. A current verified same-company competitor contract without conflict scores 1 / locked_in_competitor. Missing/conflicting evidence scores 3 / not_icp; current budget freeze scores 2; fit scores 4; fit with a fresh buying signal scores 5. Every answer needs a short reason and 1–2 real same-company supporting record IDs. The exact public criteria are in data.json.

The package contains 30 synthetic development companies and actual Sol/Luna/Terra answers plus Jev executor choices recorded on 25 October 2026. Jev selects Luna or Sol; the selected model supplies the score. The baseline remains fixed Luna alone even when you edit the candidate router. Try a new narrow rule or routing condition rather than repeating the classroom comparison. Rules must abstain outside their evidence boundary.

## What you leave with

Your agent saves work/decision.md (readable decision), work/decision.json (full evidence) and work/tested-router.py (exact tested code). Inspect one actual mistake or boundary before choosing revert, insufficient-evidence or test-further. This is known development practice, with no independent evaluation or production claim. Local code, infrastructure, fetching, review and coding-agent usage remain unpriced; replay makes no new provider calls.

For independent application, collect separate examples from your own workflow and use bakeoff within your authorized access and budget. No held-out cases, private grader, credentials or private trace links are included here. Changed facts, prompts or model identities require new evidence.

The command reference and coding-agent instructions are in [AGENTS.md](AGENTS.md). All prediction fields begin blank. The first run locks the forecast and starts its tuning cap. Preserve an existing work folder; use a fresh extracted copy for a new experiment.
