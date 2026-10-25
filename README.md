# AI Product Engineer — Vol. 2

Student materials for the advanced course: six workshops that build on a working agent. Workshop 1 asks: **can this work disappear, what does a correct completed job cost, and what would make us keep the change?**

The core online workshop uses the instructor’s shared simulation: less reasoning, a cheaper model, rules, then Jev choosing an executor. Participants make predictions and decisions aloud. The final 25 minutes are for one bounded individual application to a ready own workflow or the optional recorded starter. For local starter practice, open the extracted starter folder in Codex or Claude Code and ask it to read AGENTS.md. The agent handles commands; you choose the hypothesis, limits and verdict. An available Python runtime is sufficient; no skill installation, instructor host, provider account or API keys are needed. The broader worked take-home walkthrough follows the evaluation discussion.

Start with [Workshop 1 take-home](lesson1/README.md). The kit works with Python 3.10+ and has no runtime dependencies or required provider account.

- [Install/use bakeoff](#use-bakeoff-in-your-own-project): one bounded optimization, quality gates and an accountable decision.
- [Worksheet](lesson1/worksheet.md) and [homework](lesson1/homework.md): transfer to a workflow you own.
- [Actual sanitized traces](lesson1/traces/README.md): provider usage, cache counters and a real model mistake.
- [Coding-review](lesson1/examples/coding-review/README.md) and [support-triage](lesson1/examples/support-triage/README.md): separate offline projects for practicing the method.
- [Model-choice classroom starter](lesson1/model-choice-starter/README.md): local policy experiments using actual saved calls; 30 development cases with actual Sol/Luna/Terra calls and Jev choices; no keys or server.
- [Optional hosted client](lesson1/workshop-client/README.md): reconnect to an instructor host only when that mode is used.
- [Validation](VALIDATION.md): what has actually been tested and what remains unverified.

## Let your coding agent evaluate your hypothesis

Open the starter in Codex or Claude Code and ask it to read AGENTS.md. For a ready own project, give the agent skills/bakeoff/SKILL.md from this kit (or install it below) and say:

> Help me choose and evaluate one bounded cost or latency hypothesis on this workflow. Ask me for the quality floor and budget, run the comparison using my existing evidence/runner, inspect a consequential case, and let me choose the final verdict. If execution inputs are missing, return an explicitly unexecuted plan.

The agent handles code, commands and scorecards. You own the hypothesis, acceptable trade-offs and decision. New paid calls require your authorized access and budget; recorded starter practice does not.

## Use bakeoff in your own project

Download the instructor’s take-home ZIP and extract it, or clone this repository if you have access. From the extracted repository root, install into a target project (the installer refuses to overwrite an existing skill):

```bash
python3 scripts/install_skill.py --host codex --target /path/to/your/project
# Or:
python3 scripts/install_skill.py --host claude --target /path/to/your/project
```

In **Codex**, invoke `$bakeoff`; in **Claude Code**, invoke `/bakeoff`. Example:

> Use bakeoff on this workflow. Inspect the code and available traces. Find one promising cost or latency lever, define costly error types and a frozen experiment, and test within my authorized scope. Return the evidence and a separate owner decision. If data are missing, produce an explicit unexecuted plan.

The same SKILL.md bundle is copied to `.agents/skills/bakeoff` (Codex) or `.claude/skills/bakeoff` (Claude). [Official OpenAI skill docs](https://learn.chatgpt.com/docs/build-skills) and [official Claude skill docs](https://code.claude.com/docs/en/skills) were checked 24 October 2026. Installation does not add keys, connectors or hooks.

## Try it without an API key

Open either example project in your coding agent and invoke the skill using its path, or install it into that example folder. Its README supplies the contract and run commands. Edit only the router, screen on dev, then freeze and evaluate if justified. Outputs/costs/times in those two projects are **authored fixtures**. They test the method and Python routing code; they are not production savings or fresh LLM results.

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_bundle.py
python3 scripts/inspect_traces.py
```

Do not send personal/customer data with a homework submission. Publish a sanitized decision and the minimum traces needed to support it. The instructor's private evaluator, held-out answer key, provider credentials and private Langfuse project are not included.

[Open the optional historical cache/scorer replay](lesson1/replay.html): five questions, progressive reveals, actual sanitized receipts and a downloadable own-workflow plan. Download the repository ZIP and open this HTML file locally; GitHub’s code view does not execute it. No server or account is required.
