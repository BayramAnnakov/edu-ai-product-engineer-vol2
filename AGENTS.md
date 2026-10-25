# AI Product Engineer Vol. 2 student kit

This is the student-only workshop kit. Start with lesson1/README.md. For the 25-minute in-session exercise, use lesson1/model-choice-starter and follow its AGENTS.md; do not require students to install a skill or operate the CLI themselves. Explain options, collect their hypothesis/limits, run one bounded experiment, inspect evidence, then ask for their owner decision. The coding agent handles commands and files.

The reusable method is skills/bakeoff/SKILL.md. Read it directly; installation into another project is optional via scripts/install_skill.py. Codex invocation after installation is $bakeoff; Claude Code invocation is /bakeoff. No provider keys are needed for the recorded starter or fixture examples.

Evidence modes matter: model-choice-starter uses actual saved calls on known development data. Coding-review/support-triage use authored fixtures. The optional older replay/recorded-starter has Jev as final scorer; the current lesson uses Jev to choose Luna or Sol. Ten sanitized trace excerpts omit complete prompt text and private identifiers. Never treat these as production validation or a live provider benchmark.

Do not edit the supplied reference data, recordings, prices, latency, evaluator or manifest to improve a score. Do not branch on expected answers or case IDs. Keep all attempt costs, failures, unknowns and quality gates visible. No API-key creation, paid calls, external messages, deployment, publication or reminders/followthrough are authorized by this practice. An own-workflow paid experiment needs the student's actual authorized access and budget. If execution inputs are absent, return a clearly unexecuted experiment brief.
