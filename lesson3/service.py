"""Small local drafts service, with a database separate from the DBOS journal."""

import json
import os
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from uuid import uuid4

import policy

ACCOUNTS = {"A-17": "Alder Freight", "A-53": "Birch Labs", "A-151": "Elm Textiles"}
ALDER = {
    "event_id": "job-17",
    "request_id": "outreach/17/nov",
    "account": "A-17",
    "queued_contact": "CFO",
}
TIMER = {
    "event_id": "timer-53",
    "request_id": "outreach/53/nov",
    "account": "A-53",
    "queued_contact": "CFO",
}
TIMER_DUE_TICK = 10
DECEMBER = dict(ALDER, event_id="job-dec-17", request_id="outreach/17/dec")
# A new event that refers to the existing November request, e.g. a CRM reconciliation.
RECONCILE = dict(ALDER, event_id="reconcile-17")
PILOT = {
    "event_id": "job-151",
    "request_id": "outreach/151/nov",
    "account": "A-151",
    "queued_contact": "CFO",
}


def folder():
    return Path(os.environ["SCOUT_LAB_STATE"])


@contextmanager
def transaction():
    with closing(sqlite3.connect(folder() / "service.sqlite", timeout=20)) as db:
        db.row_factory = sqlite3.Row
        with db:
            db.execute("BEGIN IMMEDIATE")
            yield db


def record(db, kind, detail):
    db.execute("INSERT INTO history(kind,detail) VALUES (?,?)", (kind, detail))


def deliver(db, event, delivery_id):
    key = policy.inbox_key(event, delivery_id)
    added = db.execute(
        "INSERT OR IGNORE INTO inbox(key,event) VALUES (?,?)", (key, json.dumps(event))
    ).rowcount
    record(
        db,
        "enqueued" if added else "repeat delivery",
        f"{delivery_id} / {event['event_id']} / {key}",
    )


def initialize():
    folder().mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents an accidental restart from erasing a rehearsal.
    (folder() / "service.sqlite").touch(exist_ok=False)
    with transaction() as db:
        db.executescript("""
        CREATE TABLE accounts(id TEXT PRIMARY KEY, name TEXT, approval TEXT, contact TEXT, revision TEXT);
        CREATE TABLE drafts(id INTEGER PRIMARY KEY, request_key TEXT UNIQUE, account TEXT, recipient TEXT, revision TEXT);
        CREATE TABLE inbox(key TEXT PRIMARY KEY, event TEXT, status TEXT DEFAULT 'pending', result TEXT);
        CREATE TABLE history(seq INTEGER PRIMARY KEY, kind TEXT, detail TEXT);
        CREATE TABLE phases(name TEXT PRIMARY KEY);
        CREATE TABLE timers(id TEXT PRIMARY KEY, due_tick INTEGER, event TEXT);
        """)
        db.executemany(
            "INSERT INTO accounts VALUES (?,?, 'approved','CFO','OWNER-OLD')",
            ACCOUNTS.items(),
        )
        deliver(db, ALDER, "wire-01")
        db.execute(
            "INSERT INTO timers VALUES (?,?,?)",
            (TIMER["event_id"], TIMER_DUE_TICK, json.dumps(TIMER)),
        )
        record(db, "timer armed", f"{TIMER['event_id']} / due at tick {TIMER_DUE_TICK}")


def commit_outage_updates():
    with transaction() as db:
        if not db.execute(
            "INSERT OR IGNORE INTO phases VALUES ('owner updates')"
        ).rowcount:
            return
        db.execute(
            "UPDATE accounts SET approval='revoked' WHERE id=?", (TIMER["account"],)
        )
        record(db, "approval service", "REVOKE-53 / Birch / committed")
        db.execute(
            "UPDATE accounts SET contact='procurement', revision='OWNER-07' WHERE id=?",
            (PILOT["account"],),
        )
        record(db, "verified correction", "OWNER-07 / Client A / procurement first")


def outage():
    commit_outage_updates()
    with transaction() as db:
        if not db.execute(
            "INSERT OR IGNORE INTO phases VALUES ('deliveries')"
        ).rowcount:
            return
        # Advance the fixture clock. Both wire deliveries come from the same stored timer.
        record(db, "clock advanced", f"tick {TIMER_DUE_TICK}")
        due = db.execute(
            "SELECT event FROM timers WHERE due_tick<=?", (TIMER_DUE_TICK,)
        )
        for timer in due:
            event = json.loads(timer["event"])
            deliver(db, event, "wire-02")
            deliver(db, event, "wire-03")
        deliver(db, PILOT, "wire-04")


def create_draft(event):
    account_id = event["account"]
    request_key = policy.draft_key(event, uuid4().hex)
    with transaction() as db:
        # Receipt and effect commit together. Approval and routing use the same transaction.
        old = db.execute(
            "SELECT id FROM drafts WHERE request_key=? AND account=?",
            (request_key, account_id),
        ).fetchone()
        if old:
            result = f"D-{old['id']:03d}"
            record(db, "receipt replay", f"{event['request_id']} / {result}")
            return result
        account = db.execute(
            "SELECT * FROM accounts WHERE id=?", (account_id,)
        ).fetchone()
        if account["approval"] != "approved":
            record(db, "skipped", f"{event['event_id']} / current approval revoked")
            return "skipped: revoked"
        contact = policy.recipient(event, account)
        draft_id = db.execute(
            "INSERT INTO drafts(request_key,account,recipient,revision) VALUES (?,?,?,?)",
            (request_key, account_id, contact, account["revision"]),
        ).lastrowid
        result = f"D-{draft_id:03d}"
        record(db, "draft committed", f"{event['request_id']} / {result} / {contact}")
        return result


def deliver_december():
    with transaction() as db:
        if not db.execute("INSERT OR IGNORE INTO phases VALUES ('december')").rowcount:
            return
        if not db.execute("SELECT 1 FROM phases WHERE name='deliveries'").fetchone():
            raise ValueError("Deliver and resume the outage events first.")
        if db.execute("SELECT 1 FROM inbox WHERE status!='done' LIMIT 1").fetchone():
            raise ValueError("Resume the November jobs first.")
        deliver(db, DECEMBER, "wire-05")
        deliver(db, DECEMBER, "wire-06")


def deliver_reconcile():
    with transaction() as db:
        if not db.execute(
            "INSERT OR IGNORE INTO phases VALUES ('reconcile')"
        ).rowcount:
            return
        if not db.execute("SELECT 1 FROM phases WHERE name='december'").fetchone():
            raise ValueError("Run the December phase first.")
        if db.execute("SELECT 1 FROM inbox WHERE status!='done' LIMIT 1").fetchone():
            raise ValueError("Resume the December jobs first.")
        deliver(db, RECONCILE, "wire-07")


def inspect():
    with transaction() as db:

        def rows(query):
            return [dict(row) for row in db.execute(query)]

        data = {
            "drafts": rows(
                "SELECT printf('D-%03d',id) AS id, account,recipient,revision FROM drafts ORDER BY id"
            ),
            "jobs": rows("SELECT key,event,status,result FROM inbox ORDER BY rowid"),
            "timers": rows("SELECT id,due_tick FROM timers ORDER BY due_tick,id"),
            "history": rows("SELECT seq,kind,detail FROM history ORDER BY seq"),
        }
    for row in data["jobs"]:
        row["event"] = json.loads(row["event"])
    # The service logs the logical request even when the starter chose an attempt key.
    intents = {}
    for entry in data["history"]:
        if entry["kind"] == "draft committed":
            request, receipt, _ = entry["detail"].split(" / ", 2)
            intents[receipt] = request
    for draft in data["drafts"]:
        draft["request"] = intents[draft["id"]]
    ledger = folder() / "dbos.sqlite"
    data["workflows"] = []
    data["completed_steps"] = []
    if ledger.exists():
        with closing(sqlite3.connect(ledger)) as db:
            data["workflows"] = [
                dict(id=r[0], status=r[1])
                for r in db.execute(
                    "SELECT workflow_uuid,status FROM workflow_status ORDER BY workflow_uuid"
                )
            ]
            data["completed_steps"] = [
                dict(id=row[0], step=row[1])
                for row in db.execute(
                    "SELECT workflow_uuid,function_name FROM operation_outputs ORDER BY workflow_uuid,function_id"
                )
            ]
    return data
