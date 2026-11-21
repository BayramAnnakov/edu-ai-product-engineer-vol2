"""Change these three decisions, then rehearse in a new state directory."""


def inbox_key(event, delivery_id):
    return delivery_id


def draft_key(event, attempt_id):
    return attempt_id


def recipient(event, account):
    return event["queued_contact"]
