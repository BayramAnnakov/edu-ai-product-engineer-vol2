"""Editable pre-answer policy. Never use case IDs or reference answers as shortcuts."""

def answer_rule(case):
    c=case.get('contract')
    if (c and c.get('status')=='active' and c.get('verified')
        and c.get('account_id')==case['account_id'] and c.get('expires','')>'2026-10-25'
        and not case.get('conflicting')):
        return {'score':1,'reason_code':'locked_in_competitor','evidence_ids':[c['record_id']]}
    return None


def choose_model(case,recorded_jev_choice,default_model):
    # Add one bounded condition using only the public company facts.
    return recorded_jev_choice if recorded_jev_choice is not None else default_model
