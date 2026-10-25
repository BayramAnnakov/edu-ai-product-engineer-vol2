# Lead Scout: recorded-call starter

Use this optional exercise in the final individual-practice block or after the workshop. The core workshop uses the instructor’s shared simulation. Python 3.10+ is enough. No installs, server, provider account or API keys are needed.

The included outputs are actual OpenAI GPT-6.1 Sol and TypeSafe Jev calls recorded on 24 October 2026, using synthetic company cases. Token usage and model costs come from those recordings. Replay spends no new API money. Company-data fetching time is simulated.

## Optional preparation

Download and extract the ZIP. Open a terminal in the extracted folder and check Python. Then verify the bundle:

    python3 --version
    python3 -m unittest discover -s tests -v

On Windows, use py -3 instead of python3 if that is your installed Python command.

The ZIP contains the development examples, their reference answers/evidence-support annotations, and recorded model branches. Labels and support annotations are excluded from routing and provider inputs. Final evaluation data is supplied separately after policy freeze. It contains no provider keys, private Langfuse links or instructor case generator.

## During individual practice (90–115 minutes), or at home

Choose the starting policy explicitly:

    python3 lab.py init --start rule-starter
    python3 lab.py compare

The rule starter includes the strict competitor-contract rule we inspected together. The large model handles the remaining cases; Jev is initially off. This is a supplied starting configuration, not an experimentally proven best policy.

If the first experiment is adding the contract rule itself, use a fresh folder and choose this alternative instead:

    python3 lab.py init --start compact

That starts with compact input and the large model, with the contract rule and Jev both off. Choose the path that matches the workshop discussion; the init command refuses to overwrite an existing attempt.

## Predict, edit one thing, then run

Fill all fields in prediction.json: hypothesis, minimum cost-per-correct improvement, task-quality floor and tuning time in minutes. They start blank. The savings gate uses the compact-input reference. Choose tolerances from business needs before tuning.

To explore model choice, change typed from false to true in policy.json. If the shared workshop already used this change, choose a new routing condition in router.py instead. For the rule experiment, change only rules from false to true. Keep strict true: it defines the rule we discussed. fallback is configured for eligible model routes; it does not activate Jev by itself. Threshold is an authored routing-feature score, not model confidence. Leave effort high for the first comparison.

    python3 lab.py run --effort fixed
    python3 lab.py run --effort adaptive

The first tuning run starts and locks the prediction/time limit. Later edits are allowed within that limit, but both variants must use the same final policy and router before freeze. Jev has no effort setting, so changing effort may affect only large-model routes. Every attempted executor and fallback remains in the detailed accounting.

The report compares your resulting policy against the compact reference. With the rule starter, it also compares against that same starter so that you can see what your additional change contributes.

Read failures before averages. A lower-cost policy can still fail the quality floor. You may stop on dev and export a rejection:

    python3 lab.py export --decision revert --reason "Explain the observed quality/cost trade-off"

## Continue after practice only when justified

    python3 lab.py freeze

For a later independent evaluation, the instructor releases a separate packet through the course materials after freeze. Reusing examples discussed together is practice rather than fresh validation. It works locally too:

    python3 lab.py evaluate --packet /path/to/evaluation-packet.json

The frozen policy, prediction and router must remain unchanged. Repeating evaluate recovers the saved result. Export the decision and actual outputs:

    python3 lab.py export --decision keep --reason "Explain the evidence and best alternative"

You get decision.md and decision.json. Save the result for the closing discussion or homework.

## What you can change

Edit policy.json or, with your coding assistant, the routing code in router.py. Use only facts available before the model answer. Do not branch on case IDs, expected labels or copied answers. Preserve the required score/reason/evidence contract.

Changing prompts, input facts, output contracts or provider models needs new recordings or live calls; an unseen recorded request stops rather than inventing an answer. For live work on your own workflow later, use your own provider account, local credentials and authorized budget. The classroom ZIP never makes those calls.

Task correctness checks score/reason against public dev references, the answer's structure, supplied record IDs and annotated support for the selected reason. Evidence meaning still needs inspection; no private course judge is included. The visible dev set is not evidence of production reliability.
