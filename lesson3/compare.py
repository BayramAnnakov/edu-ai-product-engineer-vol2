"""Same 20-account job and five model packets. Vary only worker count and evidence handoff."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
import subprocess
from urllib.error import HTTPError
from pathlib import Path
from queue import Empty, Queue
import sqlite3
from tempfile import TemporaryDirectory
from time import perf_counter
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
MODEL = "gpt-5.4-nano-2026-03-17"
MODES = ("single", "shared", "messages")
SYSTEM = """You research Lead Scout accounts. Use only the supplied call and CRM evidence. Snapshot 2026-11-07.
If the number of CRM records on the snapshot date is not exactly one, choose unknown. Otherwise eligible requires
an explicit budget cut on the call and an open/active current opportunity. Any other case is ineligible.
For each account return its account ID, decision, the call ID, and all current CRM IDs. Output JSON only."""
ROW = {
    "type": "object",
    "properties": {
        "account": {"type": "string"},
        "decision": {"type": "string", "enum": ["eligible", "ineligible", "unknown"]},
        "call": {"type": "string"},
        "crm": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["account", "decision", "call", "crm"],
    "additionalProperties": False,
}
SCHEMA = {
    "type": "object",
    "properties": {"rows": {"type": "array", "items": ROW}},
    "required": ["rows"],
    "additionalProperties": False,
}
MAX_OUTPUT = 700
# Standard token prices, USD per million, for the pinned snapshot.
INPUT, CACHED, OUTPUT = 0.20, 0.02, 1.25


def fingerprint(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def query(packet):
    return {
        "model": MODEL,
        "input": json.dumps(packet, separators=(",", ":")),
        "instructions": SYSTEM,
        "reasoning": {"effort": "none"},
        "max_output_tokens": MAX_OUTPUT,
        "store": False,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "research",
                "schema": SCHEMA,
                "strict": True,
            }
        },
    }


def ask(payload):
    request = Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=75) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(
            f"Provider returned HTTP {exc.code}. Check the course key, model access and budget. Use the recording if unavailable."
        ) from None
    if result["status"] != "completed":
        raise RuntimeError(
            f"Response {result['id']} ended {result['status']}. No automatic retries."
        )
    answer = "".join(
        c["text"]
        for item in result["output"]
        if item["type"] == "message"
        for c in item["content"]
        if c["type"] == "output_text"
    )
    return {
        "response": result["id"],
        "model": result["model"],
        "usage": result["usage"],
        "rows": json.loads(answer)["rows"],
    }


def ask_cli(payload, ceiling):
    env = dict(os.environ)
    for name in ("CLAUDECODE", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        env.pop(name, None)
    cmd = [
        "claude",
        "-p",
        "--model",
        "claude-sonnet-5-5",
        "--effort",
        "low",
        "--tools",
        "",
        "--strict-mcp-config",
        "--setting-sources",
        "",
        "--no-session-persistence",
        "--system-prompt",
        SYSTEM,
        "--json-schema",
        json.dumps(SCHEMA),
        "--max-budget-usd",
        str(ceiling),
        "--output-format",
        "json",
    ]
    with TemporaryDirectory() as work:
        proc = subprocess.run(
            cmd,
            input=payload["input"],
            text=True,
            capture_output=True,
            cwd=work,
            env=env,
            timeout=100,
        )
    if proc.returncode:
        raise RuntimeError(
            "Claude call did not finish. Check the CLI login and packet ceiling."
        )
    result = json.loads(proc.stdout)
    if result.get("is_error") or not result.get("structured_output"):
        raise RuntimeError("Claude returned no structured research result.")
    return {
        "response": result.get("uuid") or result["session_id"],
        "model": list(result["modelUsage"])[0],
        "usage": result["usage"],
        "usd": result["total_cost_usd"],
        "rows": result["structured_output"]["rows"],
    }


def cost(usage):
    cached = usage["input_tokens_details"]["cached_tokens"]
    return (
        (usage["input_tokens"] - cached) * INPUT
        + cached * CACHED
        + usage["output_tokens"] * OUTPUT
    ) / 1e6


def authorize_and_grade(path, accounts, replies):
    """Commit permitted drafts in a fresh service table and inspect actual state to grade."""
    with sqlite3.connect(path) as db:
        db.execute(
            "CREATE TABLE accounts(id TEXT PRIMARY KEY, approval TEXT, recipient TEXT)"
        )
        db.execute(
            "CREATE TABLE drafts(request TEXT PRIMARY KEY, account TEXT UNIQUE, recipient TEXT)"
        )
        db.executemany(
            "INSERT INTO accounts VALUES (?,?,?)",
            [(r["account"], r["approval"], r["recipient"]) for r in accounts],
        )
        outcomes = []
        for row in accounts:
            aid = row["account"]
            matches = [v for v in replies if v.get("account") == aid]
            value = matches[0] if len(matches) == 1 else {}
            if value.get("decision") == "eligible":
                db.execute(
                    "INSERT INTO drafts SELECT ?,id,recipient FROM accounts WHERE id=? AND approval='approved'",
                    ("nov/" + aid, aid),
                )
            actual = db.execute(
                "SELECT recipient FROM drafts WHERE account=?", (aid,)
            ).fetchone()
            expected = (
                row["recipient"]
                if row["expected_research"] == "eligible"
                and row["approval"] == "approved"
                else None
            )
            recipient = actual[0] if actual else None
            ok = (
                value.get("decision") == row["expected_research"]
                and recipient == expected
                and value.get("call") == row["call"]["id"]
                and sorted(value.get("crm", [])) == sorted(row["current_crm_ids"])
            )
            outcomes.append(
                {
                    "account": aid,
                    "accepted": ok,
                    "decision": value.get("decision"),
                    "draft_to": recipient,
                }
            )
        return outcomes


def experiment(mode, accounts, directory, cap, provider):
    blocks = [accounts[i : i + 4] for i in range(0, len(accounts), 4)]
    n = 1 if mode == "single" else 3
    # Each worker indexes the CRM for the same logical partition in both team configurations.
    shards = [
        {r["account"]: r["crm"] for index, r in enumerate(accounts) if index % n == w}
        for w in range(n)
    ]
    shared = {
        aid: records for partition in shards for aid, records in partition.items()
    }
    jobs = Queue()
    mail = [Queue() for _ in range(n)]
    started = perf_counter()
    for index in range(len(blocks)):
        jobs.put(index)

    def task(w):
        output = []
        if mode == "messages":
            # Direct peer messages carry the CRM evidence to the worker assigned that packet.
            for index, block in enumerate(blocks):
                owner = index % n
                if owner != w:
                    part = {
                        r["account"]: shards[w][r["account"]]
                        for r in block
                        if r["account"] in shards[w]
                    }
                    if part:
                        mail[owner].put((index, w, part))
            local_blocks = list(range(w, len(blocks), n))
            received = {index: {} for index in local_blocks}
            routes = {index: [] for index in local_blocks}
            needed = sum(
                1
                for index in local_blocks
                for source in range(n)
                if source != w
                and any(r["account"] in shards[source] for r in blocks[index])
            )
            for _ in range(needed):
                index, sender, part = mail[w].get(timeout=30)
                received[index].update(part)
                routes[index].append(
                    {"from": sender + 1, "to": w + 1, "accounts": list(part)}
                )
            indices = iter(local_blocks)
        else:

            def take():
                while True:
                    try:
                        yield jobs.get_nowait()
                    except Empty:
                        return

            indices = take()
        for index in indices:
            crm = {**shards[w], **received[index]} if mode == "messages" else shared
            packet = [
                {"account": r["account"], "call": r["call"], "crm": crm[r["account"]]}
                for r in blocks[index]
            ]
            payload = query(packet)
            # UTF-8 byte count plus fixed API framing allowance is a conservative token bound for this fixture.
            upper = (
                (len(json.dumps(payload).encode()) + 512) * INPUT + MAX_OUTPUT * OUTPUT
            ) / 1e6
            if provider == "api" and upper > cap / len(blocks):
                raise ValueError(
                    "Cap too low for a bounded call. No call submitted for this packet."
                )
            begin = perf_counter()
            if provider == "api":
                result = ask(payload)
                result["usd"] = cost(result["usage"])
            else:
                result = ask_cli(payload, cap / len(blocks))
            output.append(
                {
                    "packet": index + 1,
                    "worker": w + 1,
                    "request_sha256": fingerprint([SYSTEM, SCHEMA, payload["input"]]),
                    "messages": routes[index] if mode == "messages" else [],
                    "start_s": round(begin - started, 3),
                    "end_s": round(perf_counter() - started, 3),
                    **result,
                }
            )
        return output

    with ThreadPoolExecutor(n) as pool:
        calls = sorted(
            (call for worker in pool.map(task, range(n)) for call in worker),
            key=lambda c: c["packet"],
        )
    outcomes = authorize_and_grade(
        directory / (mode + ".sqlite"), accounts, [r for c in calls for r in c["rows"]]
    )
    total = round(sum(c["usd"] for c in calls), 8)
    if total > cap:
        raise RuntimeError("Metered spend exceeded reserved cap.")
    return {
        "mode": mode,
        "elapsed_s": round(perf_counter() - started, 3),
        "accepted": sum(o["accepted"] for o in outcomes),
        "usd": total,
        "cap_usd": cap,
        "outcomes": outcomes,
        "calls": calls,
    }


def trace_observations(runs):
    packet = [run["calls"][0] for run in runs]
    hashes = {call["request_sha256"] for call in packet}
    match = (
        f"Packet 1 input hash {packet[0]['request_sha256'][:12]} matches across all three configurations."
        if len(hashes) == 1
        else "Packet 1 inputs differ across configurations."
    )
    calls = runs[1]["calls"]
    for i, left in enumerate(calls):
        for right in calls[i + 1 :]:
            if max(left["start_s"], right["start_s"]) < min(
                left["end_s"], right["end_s"]
            ):
                intervals = [
                    f"packet {c['packet']} on worker {c['worker']} ({c['start_s']:.3f}–{c['end_s']:.3f} s)"
                    for c in (left, right)
                ]
                return match, "Shared-index calls overlap: " + " and ".join(
                    intervals
                ) + "."
    return match, "The shared-index recording contains no overlapping call intervals."


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--live", action="store_true")
    p.add_argument(
        "--max-budget-usd",
        type=float,
        default=0.25,
        help="Ceiling for each whole configuration",
    )
    p.add_argument("--output", type=Path)
    p.add_argument("--provider", choices=["api", "claude"], default="claude")
    a = p.parse_args()
    accounts = json.loads((HERE / "accounts.json").read_text())
    if a.live:
        if not 0 < a.max_budget_usd <= 1 or (
            a.provider == "api" and not os.environ.get("OPENAI_API_KEY")
        ):
            p.error(
                "Provide OPENAI_API_KEY and a positive per-configuration cap up to $1."
            )
        dest = a.output or Path("comparison.json")
        # Preserve partial receipts and prevent an accidental repeated paid run.
        with dest.open("x") as output:
            output.write("{}\n")
        data = {
            "model": MODEL if a.provider == "api" else "claude-sonnet-5-5",
            "fixture_sha256": fingerprint(accounts),
            "provider": a.provider,
            "runs": [],
            "pricing": "standard USD from metered tokens"
            if a.provider == "api"
            else "CLI-reported list-price estimate on signed-in subscription",
        }
        with TemporaryDirectory() as tmp:
            for mode in MODES:
                data["runs"].append(
                    experiment(mode, accounts, Path(tmp), a.max_budget_usd, a.provider)
                )
                dest.write_text(json.dumps(data, indent=2) + "\n")
    else:
        data = json.loads((HERE / "recorded-comparison.json").read_text())
        if data["fixture_sha256"] != fingerprint(accounts):
            raise ValueError("Recording mismatches the fixture.")
    if [r["mode"] for r in data["runs"]] != list(MODES):
        raise ValueError("Incomplete comparison")
    for r in data["runs"]:
        print(
            f"{r['mode']:9} {r['accepted']}/20  ${r['usd']:.6f}  {r['elapsed_s']:.2f} s  {len(r['calls'])} calls"
        )
        print(
            "  packet 1:",
            json.dumps(
                {
                    k: r["calls"][0][k]
                    for k in ("worker", "start_s", "end_s", "messages")
                }
            ),
        )

    for observation in trace_observations(data["runs"]):
        print(observation)
    print(
        "One run per configuration in fixed order. Cache usage and model responses can vary. Repeat with varied order before attributing cost, quality or speed differences."
    )


if __name__ == "__main__":
    main()
