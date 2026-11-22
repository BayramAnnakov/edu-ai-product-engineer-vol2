---
name: kill-resume-drill
description: Rehearse a worker crash around one external write in the user's own project (a PR, a message, a draft, a file, a ticket, a payment in test mode) and prove recovery from the destination's records, not from the worker's log. Use when the user asks to test crash recovery, retries, duplicates or idempotency for a job, or invokes /kill-resume-drill.
---

# Kill-resume drill

Goal: one external write in the user's project survives a worker crash at the worst moment. A retry returns the
first result. A redelivered trigger does nothing new. A genuinely new request still gets through. A revoked or
changed instruction is honoured at write time. Proof comes from the destination's own records.

Work only in a disposable copy or a sandbox (a local registry, a test-mode account, a scratch folder). Never touch a
production destination or a git remote. If the only destination is production, stop and say so.

## 1. Fill the card with the user, before any code

Ask the user for each line, offer your reading of the code, and let them decide. Write the card to `drill-card.md`.

1. **The write.** One call that changes something outside the worker.
2. **The request identity.** What names this logical request before the model runs, and survives a restart. It
   must be created once per request and stored, so every retry reuses it. A UUID minted when the request is created
   and persisted is fine; an attempt ID, a UUID minted per attempt, a timestamp or model-generated text is not. Also name the trigger identity
   (event or message ID), which is a different thing.
3. **The destination's contract.** Exactly one of: it honours an idempotency key; it has a natural key that can be
   looked up (an existing PR for a branch, a file at a path, a message with a client reference); or nothing. With
   nothing, say plainly that a crash between the write and the record leaves an unknown outcome, and plan to record
   intent before the write and to escalate instead of retrying blind.
4. **What is read again at write time.** Approval, recipient, amount, target. Name the source that owns each.

## 2. Predict, then crash

Before running anything, ask the user what could have happened from the worker's last message alone, and which
record would settle it. Then interrupt the worker after the destination commits and before the worker records the
result (kill the process; do not raise a handled exception). Inspect the destination and compare it with the
prediction.

## 3. Recover and try to break it

Run each case and inspect the destination after each:

- Resume with the same request identity: the first result comes back and the destination holds one item.
- Deliver the same trigger twice: one handled event.
- While the worker is down, revoke approval on a different, still-pending request, and correct the recipient of
  another: resume skips the first and uses the new recipient for the second. A write that already committed stays
  committed; recovering it returns its receipt, and undoing it would be a separate compensating action.
- Send a new trigger for an existing request: it must reach a worker and return the existing result. A key that
  deduplicates triggers by request loses this event silently, and the item count does not reveal it.
- Send a new request for the same account, project or issue: exactly one new item.
- Resume once more: nothing changes.

These expectations assume the destination honours a key or can be looked up. If line 3 is "nothing", the
expected result of the crash case is different: the worker finds an intent with no recorded outcome and escalates
instead of resending; count that escalation as the pass. With a lookup, also say what a lookup cannot see: a write
still in flight, or one not yet visible. A negative lookup does not prove the write never happened.

Then deliberately swap the identity in step 2 for a plausible wrong one (account, request instead of event, attempt)
and show which case catches it. If no existing check fails, write the check that does.

## 4. Report

Record in `drill-card.md`: the card, the prediction, each case with the destination's evidence (IDs, URLs, counts),
which wrong identity was caught by which check, and one owner decision (keep, change, or what is still unknown).
Label anything not executed as not verified. A workflow status of SUCCESS is not evidence that the write happened
once.

In the Lead Scout lab the same drill is already scripted: `python lab.py run`, `verify` and `reconcile`.
