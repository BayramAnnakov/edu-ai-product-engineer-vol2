#!/usr/bin/env python3
"""Student-only client: public cases/policy, never instructor source or labels."""
import argparse
import http.cookiejar
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPCookieProcessor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, help="The instructor's workshop URL")
    parser.add_argument("--cookies", default=".workshop-cookies.txt")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("status"); sub.add_parser("url"); sub.add_parser("cases"); sub.add_parser("init"); sub.add_parser("baseline"); sub.add_parser("free-wins")
    run = sub.add_parser("run"); run.add_argument("--policy", default="policy.json"); run.add_argument("--prediction", default="prediction.json"); run.add_argument("--effort", choices=["fixed", "adaptive"], required=True)
    sub.add_parser("freeze"); sub.add_parser("evaluate")
    export = sub.add_parser("export"); export.add_argument("--out", default="decision.md")
    args = parser.parse_args()
    jar = http.cookiejar.MozillaCookieJar(args.cookies)
    if Path(args.cookies).exists(): jar.load(ignore_discard=True, ignore_expires=True)
    client = build_opener(HTTPCookieProcessor(jar))

    def call(path, data=None, raw=False):
        headers = {"Content-Type": "application/json"}
        if os.environ.get("W1_ROOM_CODE"): headers["X-Workshop-Code"] = os.environ["W1_ROOM_CODE"]
        req = Request(args.host.rstrip("/")+path, data=json.dumps(data).encode() if data is not None else None, headers=headers)
        try:
            with client.open(req) as r: payload = r.read()
        except HTTPError as ex:
            message = ex.read().decode(); ex.close(); raise RuntimeError(message) from None
        finally:
            jar.save(ignore_discard=True, ignore_expires=True)
        return payload.decode() if raw else json.loads(payload)

    if args.action == "init":
        state = call("/api/state")
        for name, data in [("policy.json", state["policy"]), ("prediction.json", state["prediction"])]:
            if not Path(name).exists(): Path(name).write_text(json.dumps(data, indent=2))
        print("policy.json and prediction.json ready. Edit one routing condition; write your effect before running.")
    elif args.action in ("baseline", "free-wins"):
        config = "incumbent" if args.action == "baseline" else "free-wins"
        result = call("/api/run", {"config": config})
        print(json.dumps(result["dev"][config]["summary"], indent=2))
    elif args.action == "run":
        state = call("/api/state")
        if not state["experiment_started"]:
            call("/api/save", {"prediction": json.loads(Path(args.prediction).read_text())})
        call("/api/save", {"policy": json.loads(Path(args.policy).read_text())})
        state = call("/api/run", {"config": "hybrid-"+args.effort})
        print(json.dumps(state["dev"]["hybrid-"+args.effort]["summary"], indent=2))
    elif args.action == "freeze":
        call("/api/preflight", {}); print(json.dumps(call("/api/freeze", {})["frozen"], indent=2))
    elif args.action == "evaluate":
        state = call("/api/evaluate", {}); print(json.dumps({k:v["summary"] for k,v in state["evaluation"].items()}, indent=2))
    elif args.action == "cases": print(json.dumps(call("/api/cases?split=dev"), indent=2))
    elif args.action == "url": print(call("/api/links")["audience"])
    elif args.action == "export": Path(args.out).write_text(call("/api/export", raw=True)); print(args.out)
    else:
        state = call("/api/state"); print(json.dumps({k:state[k] for k in ("mode", "version", "scene", "frozen", "decision")}, indent=2))


if __name__ == "__main__":
    try: main()
    except (ValueError, OSError, RuntimeError) as ex: print(str(ex), file=sys.stderr); raise SystemExit(1)
