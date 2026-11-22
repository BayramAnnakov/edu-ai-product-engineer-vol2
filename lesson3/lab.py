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
            "reconcile",
            "inspect",
            "run",
            "verify",
        ],
    )
    p.add_argument(
        "--state", required=True, type=Path, help="One dedicated directory per run"
    )
    p.add_argument(
        "--json", action="store_true", help="Print raw JSON instead of the summary"
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
    if action == "reconcile":
        try:
            service.deliver_reconcile()
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
        if args.json:
            print(json.dumps(report["checks"], indent=2))
        else:
            print(show_outcome(data))
            print(show_checks(report["checks"], args.state / "report.json"))
        if not all(report["checks"].values()):
            sys.exit(1)
    elif action == "reconcile":
        event = service.RECONCILE["event_id"]
        summary = {
            "event": event,
            "request": service.RECONCILE["request_id"],
            "deliveries": [
                f"{h['kind']}: {h['detail']}"
                for h in data["history"]
                if h["kind"] in ("enqueued", "repeat delivery")
                and h["detail"].split(" / ")[1] == event
            ],
            "jobs": [
                {"key": j["key"], "status": j["status"], "result": j["result"]}
                for j in data["jobs"]
                if j["event"]["event_id"] == event
            ],
            "drafts": len(data["drafts"]),
        }
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            lines = [f"New event {event} for the existing request {summary['request']}"]
            lines += ["  inbox: " + d for d in summary["deliveries"]]
            lines.append(f"  jobs run for it: {len(summary['jobs'])}")
            lines += [f"    {j['key']}  {j['status']}  returned {j['result']}" for j in summary["jobs"]]
            lines.append(f"  drafts in the service: {summary['drafts']}")
            print("\n".join(lines))
    elif action == "crash":
        journal = {
            "worker_exit": code,
            "workflows": data["workflows"],
            "completed_steps": data["completed_steps"],
        }
        if args.json:
            print(json.dumps(journal, indent=2))
        else:
            print(f"Worker exited with {code} (killed in the middle of a step).")
            print(show_journal(data))
    elif args.json:
        print(json.dumps(data, indent=2))
    else:
        print(show_state(data))


def show_journal(data):
    steps = {}
    for row in data["completed_steps"]:
        steps.setdefault(row["id"], []).append(row["step"])
    lines = ["DBOS JOURNAL  (which steps finished, per workflow)"]
    for w in data["workflows"]:
        lines.append(f"  {w['id']:<22} {w['status']:<8} finished: {', '.join(steps.get(w['id'], [])) or '-'}")
    return "\n".join(lines) if data["workflows"] else "DBOS JOURNAL  (empty)"


def show_state(data):
    lines = ["DRAFTS SERVICE  (what exists at the destination)"]
    for d in data["drafts"]:
        name = service.ACCOUNTS.get(d["account"], d["account"])
        lines.append(f"  {d['id']}  {d['account']:<6} {name:<14} {d['request']:<17} to {d['recipient']:<12} {d['revision']}")
    if not data["drafts"]:
        lines.append("  (no drafts)")
    lines.append("")
    lines.append("INBOX  (one row per inbox key; a repeat key is not run again)")
    for j in data["jobs"]:
        e = j["event"]
        lines.append(f"  key {j['key']:<17} event {e['event_id']:<12} request {e['request_id']:<17} {j['status']:<8} {j['result'] or ''}")
    lines.append("")
    lines.append(show_journal(data))
    lines.append("")
    lines.append("HISTORY")
    for h in data["history"]:
        lines.append(f"  {h['seq']:>3}  {h['kind']:<20} {h['detail']}")
    return "\n".join(lines)


def show_outcome(data):
    drafts, jobs = data["drafts"], data["jobs"]
    ids = lambda request: ", ".join(d["id"] for d in drafts if d["request"] == request) or "none"
    runs = lambda event: sum(j["event"]["event_id"] == event for j in jobs)
    elm = ", ".join(d["recipient"] for d in drafts if d["account"] == service.PILOT["account"]) or "none"
    birch = sum(d["account"] == service.TIMER["account"] for d in drafts)
    return "\n".join([
        "WHAT HAPPENED AT THE DESTINATION",
        f"  Alder November ({service.ALDER['request_id']}): drafts {ids(service.ALDER['request_id'])}",
        f"  Alder December ({service.DECEMBER['request_id']}): {runs(service.DECEMBER['event_id'])} job(s) run, drafts {ids(service.DECEMBER['request_id'])}",
        f"  Birch timer ({service.TIMER['event_id']}): handled {runs(service.TIMER['event_id'])} time(s), drafts {birch}",
        f"  Elm ({service.PILOT['request_id']}): draft to {elm}",
        "  Every record: python lab.py inspect --state <folder>",
        "",
    ])


def show_checks(checks, path):
    passed = sum(checks.values())
    lines = [f"Recovery checks: {passed} of {len(checks)} pass  (report: {path})"]
    lines += [f"  {'PASS' if ok else 'FAIL'}  {name}" for name, ok in checks.items()]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
