# Worked example after trying the exercise

This is the actual corrected coding-review forward test, not a scripted outcome. A fresh agent chose a conservative documentation-only bypass and left generated changes on the model path.

- [Decision](decision.md): frozen verdict plus separate fixture-only owner choice.
- [Scorecard and raw paired rows](scorecard.json): all 30 evaluation cases per arm, previous costs, gates and output/attempt evidence. Local filesystem paths were relabeled relative to the example project; numeric results and outputs are unchanged.
- [Tested router](router.py): only pre-answer inputs, no label/case-ID lookup.

Read eval-10 for the traversal boundary that still needs model review; eval-02 for a safely skipped call. Both use authored model outputs/costs/timings. The report is fixture evidence and authorizes no production deployment.
