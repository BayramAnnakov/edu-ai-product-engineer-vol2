# Integrations and data sync

All four excerpts are for Client A.

## SYNC-01 · Oct 12 · Technical planning

**Implementation:** Which field joins imported records to our CRM?
**Data lead:** Use the CRM account ID. Display names change and are for presentation.

## SYNC-02 · Oct 19 · Sandbox replay

**Data lead:** The import retried the same event.
**Implementation:** Use the source event ID to deduplicate. Save the import receipt for the launch checklist.

## SYNC-03 · Oct 26 · Discrepancy review

**Support:** Some rows are missing from the report after the import.
**Data lead:** Reconcile source and destination row counts. Open a support case with the run ID if the difference persists.

## SYNC-04 · Nov 2 · Reporting handoff

**Data lead:** The reporting view excludes test records using the environment field.
**Analyst:** I’ll keep that filter in the report definition so the weekly totals can be reproduced.
