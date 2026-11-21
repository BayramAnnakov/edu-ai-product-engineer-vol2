---
name: kill-resume-drill
description: Rehearse a worker outage around one synthetic or sandboxed external write and verify recovery against the owning service.
---
Pick a disposable local copy and a single logical request. Record its current approval and destination. First ask the learner what could have happened from the worker's last message alone. Show the workflow journal next and collect the learner's choice of decisive evidence before revealing the destination receipt. Place the interruption after the service commits the write and before the workflow receives its return value.

While the worker is down, withdraw approval on a separate pending request and submit an authorized routing correction for another. Deliver the same scheduled follow-up twice. Restart with the same workflow identity and compare the service receipts with the job history. Verify the original receipt, the correctly suppressed action and the still-permitted action with updated data. Resume once more and check for extra writes.

Then issue a fresh approved request for the same account or project, with a different event ID and request ID. Deliver its event twice through the ordinary inbox. Inspect both the inbox and the destination. The new request should complete exactly once and keep the original receipt intact. A policy that deduplicates by account will lose this new request.

Use the CLI in the supplied starter. For another product, choose a local PR registry or a local document store and use its native operation identity. Record the inputs, evidence mode, counts and one owner decision. Ask for real service receipts before calling an external operation complete.
