"""A disposable DBOS worker. Only the disposable child is interrupted."""

import json
import os
import signal
import sys

from dbos import DBOS, SetWorkflowID
import service

DBOS(
    config={
        "name": "scout-workshop",
        "system_database_url": f"sqlite:///{service.folder() / 'dbos.sqlite'}",
        "executor_id": "local",
        "application_version": "workshop-3",
        "enable_otlp": False,
        "console_log_level": "ERROR",
    }
)


@DBOS.step()
def claim(key):
    with service.transaction() as db:
        row = db.execute("SELECT event FROM inbox WHERE key=?", (key,)).fetchone()
        service.record(db, "claimed", key)
        return json.loads(row["event"])


@DBOS.step()
def submit(event):
    receipt = service.create_draft(event)
    if event["account"] == "A-17" and sys.argv[1] == "crash":
        # The service committed; DBOS has not yet received this step's return value.
        os.kill(os.getpid(), signal.SIGKILL)
    return receipt


@DBOS.workflow()
def handle(key):
    return submit(claim(key))


def main():
    DBOS.launch()
    try:
        for row in service.inspect()["jobs"]:
            if row["status"] == "done":
                continue
            key = row["key"]
            with SetWorkflowID(f"followup/{key}"):
                result = handle(key)
            with service.transaction() as db:
                db.execute(
                    "UPDATE inbox SET status='done',result=? WHERE key=?", (result, key)
                )
                service.record(db, "acknowledged", f"{key} / {result}")
    finally:
        DBOS.destroy()


if __name__ == "__main__":
    main()
