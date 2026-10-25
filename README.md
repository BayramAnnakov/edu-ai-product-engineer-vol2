# AI Product Engineer — Vol. 2

Student materials for the advanced course: six workshops that build on a working agent. Workshop 1 asks: **can this work disappear, what does a correct completed job cost, and what would make us keep the change?**

For the online classroom exercise, get the standalone recorded-call ZIP from the instructor before class. Its [Lead Scout source and instructions](lesson1/recorded-starter/README.md) are here; run it locally at the first hands-on block. The broader take-home walkthrough is for after the evaluation discussion. It includes actual development recordings and needs no instructor host, provider account or API keys.

Start with [Workshop 1 take-home](lesson1/README.md). The kit works with Python 3.10+ and has no runtime dependencies or required provider account.

- [Install/use bakeoff](#use-bakeoff-in-your-own-project): one bounded optimization, quality gates and an accountable decision.
- [Worksheet](lesson1/worksheet.md) and [homework](lesson1/homework.md): transfer to a workflow you own.
- [Actual sanitized traces](lesson1/traces/README.md): provider usage, cache counters and a real model mistake.
- [Coding-review](lesson1/examples/coding-review/README.md) and [support-triage](lesson1/examples/support-triage/README.md): separate offline projects for practicing the method.
- [Recorded classroom starter](lesson1/recorded-starter/README.md): local policy experiments using actual saved calls; final evaluation packet released separately after freeze.
- [Optional hosted client](lesson1/workshop-client/README.md): reconnect to an instructor host only when that mode is used.
- [Validation](VALIDATION.md): what has actually been tested and what remains unverified.

## Use bakeoff in your own project

Clone this repository, then install into a target project (the installer refuses to overwrite an existing skill):

```bash
git clone https://github.com/BayramAnnakov/edu-ai-product-engineer-vol2.git
cd edu-ai-product-engineer-vol2
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

[Open the offline Field Notes replay](lesson1/replay.html): five questions, progressive reveals, actual sanitized receipts and a downloadable own-workflow plan. Download the repository ZIP and open this HTML file locally; GitHub’s code view does not execute it. No server or account is required.
