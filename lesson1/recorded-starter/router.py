"""Editable routing code. Use available facts, never expected labels or case IDs."""
import dataset as F

def rule(case, strict=True):
    c = case["contract"]
    if not c or c["status"] != "active":
        return None
    if strict and (not c["verified"] or c["account_id"] != case["account_id"] or c["expires"] <= F.AS_OF or case["conflicting"]):
        return None
    return {"score": 1, "reason_code": "locked_in_competitor", "evidence_ids": [c["record_id"]]}


def complex_case(case, threshold):
    # Deliberately only observable pre-answer inputs, never labels or case IDs.
    uncertainty = (50 if case["headcount"] is None else 0) + (80 if case["conflicting"] else 0)
    uncertainty += 60 if case["contract"] and case["contract"]["account_id"] != case["account_id"] else 0
    return uncertainty >= threshold
