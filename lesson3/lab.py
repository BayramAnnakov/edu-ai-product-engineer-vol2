"""Rehearse in an isolated local directory. All accounts and events are synthetic."""

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from time import monotonic

import service


def worker(action):
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("worker.py")), action],
        capture_output=True,
        text=True,
        timeout=45,
    )
    expected = -signal.SIGKILL if action == "crash" else 0
    if proc.returncode != expected:
        raise RuntimeError(
            f"{action}: exit {proc.returncode}; expected {expected}. {proc.stderr[-2000:]}{proc.stdout[-500:]}"
        )
    return proc.returncode


def checks(before, after):
    by_account = {
        account: [d for d in after["drafts"] if d["account"] == account]
        for account in service.ACCOUNTS
    }
    timer = [
        j for j in after["jobs"] if j["event"]["event_id"] == service.TIMER["event_id"]
    ]
    alder = [
        j for j in after["jobs"] if j["event"]["event_id"] == service.ALDER["event_id"]
    ]
    original = before["drafts"][0]["id"] if before["drafts"] else None
    november = [
        d["id"]
        for d in by_account["A-17"]
        if d["request"] == service.ALDER["request_id"]
    ]
    december = [
        d["id"]
        for d in by_account["A-17"]
        if d["request"] == service.DECEMBER["request_id"]
    ]
    later_jobs = [j for j in after["jobs"] if j["event"] == service.DECEMBER]
    later_deliveries = [
        (h["kind"], h["detail"].split(" / ")[0])
        for h in after["history"]
        if h["kind"] in ("enqueued", "repeat delivery")
        and h["detail"].split(" / ")[1] == service.DECEMBER["event_id"]
    ]
    timer_history = [
        row for row in after["history"] if service.TIMER["event_id"] in row["detail"]
    ]
    decisions = [row for row in timer_history if row["kind"] == "skipped"]
    deliveries = [
        row for row in timer_history if row["kind"] in ("enqueued", "repeat delivery")
    ]
    return {
        "service committed before workflow completion": len(before["drafts"]) == 1
        and [w["status"] for w in before["workflows"]] == ["PENDING"]
        and [r["step"] for r in before["completed_steps"]] == ["claim"],
        "original receipt recovered": november == [original]
        and len(alder) == 1
        and alder[0]["result"] == original,
        "revoked draft suppressed": not by_account["A-53"]
        and bool(timer)
        and all(j["result"] == "skipped: revoked" for j in timer),
        "two deliveries resolved once": len(timer) == 1
        and before["timers"]
        == [{"id": service.TIMER["event_id"], "due_tick": service.TIMER_DUE_TICK}]
        and [row["detail"].split(" / ")[0] for row in deliveries]
        == ["wire-02", "wire-03"]
        and [row["kind"] for row in deliveries] == ["enqueued", "repeat delivery"]
        and len(decisions) == 1,
        "verified correction used": [
            (d["recipient"], d["revision"]) for d in by_account["A-151"]
        ]
        == [("procurement", "OWNER-07")],
        "workflow history complete": len(after["workflows"]) == len(after["jobs"])
        and all(w["status"] == "SUCCESS" for w in after["workflows"])
        and all(j["status"] == "done" for j in after["jobs"]),
        "new request on the same account delivered once": later_deliveries
        == [("enqueued", "wire-05"), ("repeat delivery", "wire-06")]
        and len(later_jobs) == 1
        and later_jobs[0]["status"] == "done"
        and december == [later_jobs[0]["result"]]
        and december[0] != original,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "action",
        choices=[
            "init",
            "crash",
            "outage",
            "resume",
            "december",
            "inspect",
            "run",
            "verify",
        ],
    )
    p.add_argument(
        "--state", required=True, type=Path, help="One dedicated directory per run"
    )
    args = p.parse_args()
    os.environ["SCOUT_LAB_STATE"] = str(args.state.resolve())
    action = args.action
    start = monotonic()
    if action in ("init", "run"):
        try:
            service.initialize()
        except FileExistsError:
            p.error(
                "This trial already exists. Inspect or resume it, or choose a new --state directory."
            )
    elif not (args.state / "service.sqlite").is_file():
        p.error("Initialize this state directory first.")
    checkpoint = args.state / "after-crash.json"
    if action in ("crash", "run"):
        if checkpoint.exists():
            p.error(
                "This worker already crashed. Inspect its saved checkpoint or continue with outage."
            )
        code = worker("crash")
        before = service.inspect()
        checkpoint.write_text(
            json.dumps({"exit_code": code, "state": before}, indent=2)
        )
    if action in ("outage", "run"):
        if not checkpoint.exists():
            p.error("Run the crash first.")
        service.outage()
    if action in ("resume", "run"):
        worker("resume")
    if action in ("december", "run"):
        try:
            service.deliver_december()
        except ValueError as exc:
            p.error(str(exc))
        worker("resume")
    data = service.inspect()
    if action in ("run", "verify"):
        if not checkpoint.exists():
            p.error("Run the crash first so there is a service receipt to verify.")
        snapshot = json.loads(checkpoint.read_text())
        report = {
            "format": "scout-recovery-v2",
            "crash_exit": snapshot["exit_code"],
            "at_crash": snapshot["state"],
            "after_resume": data,
            "checks": checks(snapshot["state"], data),
        }
        if action == "run":
            report["elapsed_s"] = round(monotonic() - start, 3)
        (args.state / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report["checks"], indent=2))
        if not all(report["checks"].values()):
            sys.exit(1)
    elif action == "crash":
        print(
            json.dumps(
                {
                    "worker_exit": code,
                    "workflows": data["workflows"],
                    "completed_steps": data["completed_steps"],
                },
                indent=2,
            )
        )
    else:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
