# Further reading and case scope

Primary sources inspected for the workshop; provider APIs/prices should be checked again for a new live experiment.

- [OpenAI latency optimization](https://developers.openai.com/api/docs/guides/latency-optimization): work elimination, requests and the critical path.
- [OpenAI cost/quality cookbook](https://developers.openai.com/cookbook/examples/optimize_cost_and_quality): experiment structure; distinguish illustrative formulas from real runs.
- [Applied LLMs practitioner lessons](https://applied-llms.org/#tuning-and-optimizing-workflows): workflow reuse and structure.
- [Anthropic effective agents](https://www.anthropic.com/engineering/building-effective-agents): simple structures and task-specific routing.
- [Anthropic context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents): retain decision-critical context.
- [RouteLLM](https://www.lmsys.org/blog/2024-07-01-routellm/) and [FrugalGPT](https://arxiv.org/abs/2305.05176): routing/cascades; benchmark gains do not transfer automatically.
- [Google Batch](https://ai.google.dev/gemini-api/docs/batch-api) and [context caching](https://ai.google.dev/gemini-api/docs/caching): verify current chosen API, usage and turnaround.
- [Eugene Yan on task-specific evals](https://eugeneyan.com/writing/evals/): price relevant errors and audit the judge.

**Workshop case C:** a production page-usability precheck moved bounded cases to rules and retained fallback; an overbroad extension was rejected. Its observed follow-up reduced model checks per scrape 0.78→0.29 over 9,843 scrapes. This is a pre/post step-level observation with limited quality audit, not randomized whole-bill evidence.

**Separate case B:** a 200-case scoring replay and small staging observation found a faster scorer; fetching remained a bottleneck. B is a different episode, not C's after-period. The takeaway is to remeasure the full job before choosing the next optimization. Raw proprietary code, internal source links and private operational traces are excluded from this student bundle.

The public cache/scoring excerpts in this repository are separate recorded experiments on synthetic/public inputs, not customer production traces.
