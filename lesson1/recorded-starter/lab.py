#!/usr/bin/env python3
"""Local recorded-call lab. Standard library only; no server, API keys or network calls."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import engine as E

ROOT = Path(__file__).resolve().parent
STATE = Path(".lab-state.json")
BLANK = {"hypothesis": "", "minimum_gain": None, "quality_floor": None, "stop_minutes": None}


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def config_hash(policy, prediction):
    return E.F.fingerprint({"policy": policy, "prediction": prediction, "router": sha(ROOT / "router.py"),
                            "engine": sha(ROOT / "engine.py")})


def validate_prediction(p):
    if set(p) != set(BLANK) or not isinstance(p["hypothesis"], str) or not p["hypothesis"].strip():
        raise ValueError("Write your hypothesis and choose all three limits in prediction.json first.")
    for key in ("minimum_gain", "quality_floor", "stop_minutes"):
        value = p[key]
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"Choose a finite number for {key}; blank is not zero.")
        if not (0 < value <= 120 if key == "stop_minutes" else 0 <= value <= 100):
            raise ValueError(f"Invalid {key}: percentages must be 0–100; minutes must be >0 and <=120.")


def load_bank():
    manifest = read(ROOT / "manifest.json")
    for name, expected in manifest["immutable_files"].items():
        if sha(ROOT / name) != expected:
            raise ValueError(f"Recorded data changed: {name}. Use a new experiment for changed inputs.")
    bank = read(ROOT / "data/recorded-dev.json")
    responses = {}
    for name in bank.pop("parts"):
        part = read(ROOT / name)
        if responses.keys() & part.keys():
            raise ValueError("Duplicate recorded request.")
        responses.update(part)
    bank["responses"] = responses
    for key, row in bank["responses"].items():
        if E.F.fingerprint(row["request"]) != key or not row["request"]["case"]["id"].startswith("D-"):
            raise ValueError("Invalid development recording.")
    return bank


def display(label, result, reference=None):
    s = result["summary"]
    unit = s["cost"] / s["q"] if s["q"] else None
    line = f"{label}: {s['q']}/{s['n']} correct; model cost " + str(round(s["cost"], 6))
    line += "; cost/correct " + (str(round(unit, 6)) if unit is not None else "undefined")
    if reference and unit is not None and reference["summary"]["q"]:
        b = reference["summary"]
        if b["cost"] > 0:
            line += f"; {100 * (1 - unit / (b['cost'] / b['q'])):.1f}% lower vs reference"
    print(line)
    print(f"  cache read/write: {s['cached_tokens']}/{s['cache_write_tokens']}; companies: {s['n']}")


def gates(result, reference, prediction):
    verdict = E.assess({"free-wins": reference, "candidate": result}, prediction)["rows"]["candidate"]
    print("  quality gate: " + ("PASS" if verdict["quality_pass"] else "FAIL") +
          "; combined quality/savings gate: " + ("PASS" if verdict["passes"] else "FAIL"))
    return verdict


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--start", choices=["compact", "rule-starter"], required=True,
                      help="Choose the starting policy explicitly; no optimization is selected silently.")
    commands.add_parser("compare")
    run = commands.add_parser("run")
    run.add_argument("--effort", choices=["fixed", "adaptive"], required=True)
    commands.add_parser("freeze")
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--packet", required=True, type=Path)
    export = commands.add_parser("export")
    export.add_argument("--decision", choices=["keep", "revert", "insufficient-evidence"], required=True)
    export.add_argument("--reason", required=True)
    args = parser.parse_args(argv)
    bank = load_bank()

    if args.command == "init":
        if any(p.exists() for p in (STATE, Path("policy.json"), Path("prediction.json"))):
            raise ValueError("An exercise already exists here. Use a separate folder for a new attempt.")
        policy = {**E.DEFAULT_POLICY, "rules": args.start == "rule-starter"}
        write("policy.json", policy)
        write("prediction.json", BLANK)
        write(STATE, {"start": args.start, "references": {}, "dev": {}, "started": None,
                      "locked_prediction": None, "frozen": None, "evaluation": None, "incomplete": []})
        print(f"Starting policy chosen: {args.start}. Rule={policy['rules']}; Jev=False; strict checks=True.")
        print("Fill prediction.json before tuning. Replay makes no API calls and needs no keys.")
        return

    state = read(STATE)
    policy = E.validate_policy(read("policy.json"))
    prediction = read("prediction.json")
    if args.command == "compare":
        state["references"] = {
            "starting": E.run("dev", "incumbent", E.DEFAULT_POLICY, bank),
            "compact": E.run("dev", "free-wins", E.DEFAULT_POLICY, bank),
            "rule-starter": E.run("dev", "hybrid-fixed", {**E.DEFAULT_POLICY, "rules": True}, bank),
        }
        for name, result in state["references"].items():
            display(name, result, state["references"]["compact"] if name == "rule-starter" else None)
        print("Prediction and tuning clock are unchanged. Detailed attempts remain in .lab-state.json.")
    elif args.command == "run":
        if state["frozen"]:
            raise ValueError("This policy is frozen. Start a separate exercise to change it.")
        validate_prediction(prediction)
        if "compact" not in state["references"]:
            raise ValueError("Run compare first to establish the compact-input reference.")
        if state["locked_prediction"] is not None and prediction != state["locked_prediction"]:
            raise ValueError("Prediction limits locked at the first tuning run.")
        if state["started"] is None:
            state["started"] = time.time()
            state["locked_prediction"] = copy.deepcopy(prediction)
            write(STATE, state)
        if time.time() - state["started"] > prediction["stop_minutes"] * 60:
            raise ValueError("Tuning time cap exhausted. Export your evidence and decision.")
        name = "hybrid-" + args.effort
        try:
            result = E.run("dev", name, policy, bank)
        except E.LabError as ex:
            if ex.partial:
                state["incomplete"].append(ex.partial)
                write(STATE, state)
            raise
        result["experiment_hash"] = config_hash(policy, prediction)
        state["dev"][name] = result
        display(name, result, state["references"].get("compact"))
        result["gate"] = gates(result, state["references"]["compact"], prediction)
        starter = state["references"].get("rule-starter")
        if starter and state["start"] == "rule-starter":
            display("Marginal change vs the supplied rule starter", result, starter)
        if result["summary"]["q"] / result["summary"]["n"] * 100 < prediction["quality_floor"]:
            print("Quality floor failed on dev. Stopping and exporting a rejection is a complete outcome.")
    elif args.command == "freeze":
        validate_prediction(prediction)
        if state["locked_prediction"] != prediction:
            raise ValueError("Run the declared experiment before freezing.")
        digest = config_hash(policy, prediction)
        if any(state["dev"].get(k, {}).get("experiment_hash") != digest for k in ("hybrid-fixed", "hybrid-adaptive")):
            raise ValueError("Run both effort variants with this policy/router before freezing.")
        if state["frozen"] and state["frozen"]["hash"] != digest:
            raise ValueError("A different policy is already frozen.")
        state["frozen"] = {"hash": digest, "policy": copy.deepcopy(policy), "prediction": copy.deepcopy(prediction)}
        print("Policy and router frozen. The instructor releases the separate evaluation packet afterwards.")
    elif args.command == "evaluate":
        if not state["frozen"] or state["frozen"]["hash"] != config_hash(policy, prediction):
            raise ValueError("Freeze first; policy, prediction and router must remain unchanged.")
        if state["evaluation"]:
            print("Recovering the saved evaluation; it is not run again.")
        else:
            packet = read(args.packet)
            expected = read(ROOT / "manifest.json")["evaluation_packet_sha256"]
            if sha(args.packet) != expected or packet["version"] != E.F.VERSION:
                raise ValueError("This is not the instructor's evaluation packet for this exercise.")
            E.F.CASES["s1"] = packet["cases"]
            bank["responses"].update(packet["responses"])
            bank["source"] = "Actual recorded calls with the instructor-released evaluation packet"
            state["evaluation"] = {k: E.run("s1", k, policy, bank) for k in E.CONFIGS}
        for name, result in state["evaluation"].items():
            display(name, result, state["evaluation"]["free-wins"])
            gates(result, state["evaluation"]["free-wins"], prediction)
    elif args.command == "export":
        if not args.reason.strip() or not state["dev"]:
            raise ValueError("Complete a development run and explain the decision first.")
        scope = "Held-out evaluation" if state["evaluation"] else "Development only; final evaluation not run"
        current = config_hash(policy, prediction)
        runs = state["evaluation"] or state["dev"]
        receipt = {"scope": scope, "decision": args.decision, "reason": args.reason,
                   "policy": policy, "prediction": prediction, "frozen": state["frozen"], "results": runs,
                   "current_experiment_hash": current,
                   "stale_dev_runs": [k for k, r in state["dev"].items() if r["experiment_hash"] != current],
                   "incomplete_attempts": state["incomplete"]}
        write("decision.json", receipt)
        lines = ["# Lead Scout experiment decision", "", scope, "", "Decision: " + args.decision,
                 "Reason: " + args.reason, "", "Replay of actual recorded calls; no fresh API spend.",
                 "Costs use recorded token usage and dated rates. Data-fetch timing is simulated.", "",
                 "| Configuration | Correct / N | Model cost | Cost / correct |", "|---|---:|---:|---:|"]
        for name, result in runs.items():
            s = result["summary"]
            lines.append(f"| {name} | {s['q']} / {s['n']} | {s['cost']:.6f} | {s['cost_q']} |")
        lines += ["", "The JSON preserves outputs, usage, attempted-call accounting and stale/incomplete runs.",
                  "This decision is an experiment record; deployment is a separate owner decision."]
        Path("decision.md").write_text("\n".join(lines) + "\n")
        print("Saved decision.md and decision.json. Share sanitized evidence through the course's chosen channel.")
    write(STATE, state)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, E.LabError) as ex:
        print(str(ex), file=sys.stderr)
        raise SystemExit(1)
