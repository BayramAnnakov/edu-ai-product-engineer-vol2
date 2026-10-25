#!/usr/bin/env python3
"""Offline, standard-library experiment freeze/comparison/decision helper."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys


class EvidenceError(ValueError):
    pass


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(x, field, nullable=False):
    if x is None and nullable:
        return None
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0:
        raise EvidenceError(f"{field} must be a finite nonnegative number" + (" or null" if nullable else ""))
    return x


def dump(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def cases_at(path):
    cases = read(path)
    if not isinstance(cases, list) or not cases:
        raise EvidenceError("A nonempty case list is required")
    ids = [c.get("id") for c in cases]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise EvidenceError("Case IDs must be nonempty and unique")
    if any(not isinstance(c.get("group"), str) or not c["group"] for c in cases):
        raise EvidenceError("Every case needs an entity/group for split checks")
    return cases


def input_key(case):
    # IDs/groups alone can disguise a renamed development replay.
    if "input" not in case:
        return None
    return json.dumps(case["input"], sort_keys=True, ensure_ascii=False, allow_nan=False)


def prior_cost(paths):
    known, unknown = 0.0, 0
    for path in paths:
        ids = set()
        for line in Path(path).read_text().splitlines():
            if not line.strip(): continue
            row = json.loads(line)
            if not isinstance(row.get("attempts"), list): raise EvidenceError("Prior receipt needs attempted work")
            for a in row["attempts"]:
                if not a.get("id") or a["id"] in ids: raise EvidenceError("Repeated/missing attempt ID in prior receipt")
                ids.add(a["id"])
                cost = number(a.get("cost_usd"), "prior cost_usd", True)
                if cost is None: unknown += 1
                else: known += cost
    return {"known_cost_usd": known, "unknown_cost_attempts": unknown}


def freeze(contract_path, out):
    cp = Path(contract_path).resolve()
    c = read(cp)
    for key in ("name", "task_contract", "hypothesis", "baseline", "candidate", "label_source"):
        if not isinstance(c.get(key), str) or not c[key].strip():
            raise EvidenceError(f"Contract requires {key}")
    if c.get("stage") not in ("held-out", "dev-screening"):
        raise EvidenceError("stage must be held-out or dev-screening")
    for key in ("quality_floor_percent", "minimum_cost_reduction_percent"):
        if number(c.get(key), key) > 100:
            raise EvidenceError(f"{key} must be at most 100")
    number(c.get("max_total_cost_usd"), "max_total_cost_usd")
    if not number(c.get("max_tuning_minutes"), "max_tuning_minutes"):
        raise EvidenceError("max_tuning_minutes must be positive")
    number(c.get("max_job_p95_seconds"), "max_job_p95_seconds", True)
    paths = [cp, (cp.parent / c["cases"]).resolve()]
    cases = cases_at(paths[1])
    if c.get("dev_cases"):
        dev_path = (cp.parent / c["dev_cases"]).resolve()
        dev = cases_at(dev_path)
        if c["stage"] == "held-out" and {x["group"] for x in cases} & {x["group"] for x in dev}:
            raise EvidenceError("Development and held-out entities overlap")
        dev_inputs = {input_key(x) for x in dev if input_key(x) is not None}
        if c["stage"] == "held-out" and dev_inputs & {input_key(x) for x in cases if input_key(x) is not None}:
            raise EvidenceError("Held-out inputs repeat development inputs, even though IDs/groups may differ")
        paths.append(dev_path)
    prior_paths = [(cp.parent / p).resolve() for p in c.get("prior_receipts", [])]
    if len(set(prior_paths)) != len(prior_paths): raise EvidenceError("Repeated prior receipt file")
    previous = prior_cost(prior_paths)
    paths.extend(prior_paths)
    paths.extend((cp.parent / p).resolve() for p in c.get("pins", []))
    if Path(out).exists():
        raise EvidenceError("Lock already exists; start a separately named experiment")
    lock = {"schema": 1, "contract_path": str(cp), "contract": c,
            "case_path": str(paths[1]), "prior_cost": previous,
            "unique_evaluation_inputs": len({input_key(x) for x in cases}) if all(input_key(x) is not None for x in cases) else None,
            "files": {str(p): digest(p) for p in paths}}
    dump(out, lock)
    return lock


def verify_lock(lock):
    for path, sha in lock["files"].items():
        if not Path(path).is_file() or digest(path) != sha:
            raise EvidenceError(f"Frozen input changed: {path}")


def load_rows(path, cases):
    rows = {}
    attempts = set()
    allowed = {c["id"]: c for c in cases}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        key = r.get("case_id")
        if key not in allowed or key in rows:
            raise EvidenceError(f"Unknown or repeated case: {key}")
        if r.get("evidence_mode") not in ("fixture", "recorded-provider", "live-provider"):
            raise EvidenceError("Every row needs an explicit evidence_mode")
        for field in ("judge_accepted", "serious_failure"):
            if not isinstance(r.get(field), bool):
                raise EvidenceError(f"{key}: {field} must be boolean")
        number(r.get("job_seconds"), "job_seconds", True)
        number(r.get("review_seconds"), "review_seconds", True)
        case = allowed[key]
        if "output" not in r: raise EvidenceError(f"{key}: output is required; null must be explicit")
        if "expected" in case:
            correct = json.dumps(r["output"], sort_keys=True, allow_nan=False) == json.dumps(case["expected"], sort_keys=True, allow_nan=False)
            if "task_correct" in r and r["task_correct"] is not correct:
                raise EvidenceError(f"{key}: supplied grade contradicts the frozen exact label")
        else:
            if not isinstance(r.get("task_correct"), bool) or not r.get("label_source"):
                raise EvidenceError(f"{key}: independent task_correct and label_source required")
            correct = r["task_correct"]
        r["task_correct"] = correct and not r["serious_failure"]
        if not isinstance(r.get("attempts"), list):
            raise EvidenceError(f"{key}: attempted work must be a list")
        for a in r["attempts"]:
            aid = a.get("id")
            if not isinstance(aid, str) or not aid or aid in attempts:
                raise EvidenceError("Attempt IDs must be nonempty and unique within an arm")
            attempts.add(aid)
            if a.get("status") not in ("success", "error"):
                raise EvidenceError(f"{aid}: status must be success or error")
            number(a.get("cost_usd"), "cost_usd", True)
            for field in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"):
                if field in a:
                    number(a[field], field, True)
        rows[key] = r
    return rows


def percentile(values, p):
    return sorted(values)[math.ceil(len(values) * p) - 1] if values else None


def summarize(rows, cases):
    attempts = [a for r in rows.values() for a in r["attempts"]]
    q = sum(r["task_correct"] for r in rows.values())
    a = sum(r["judge_accepted"] for r in rows.values())
    known = all(x.get("cost_usd") is not None for x in attempts)
    total = sum(x["cost_usd"] for x in attempts) if known else None
    times = [r["job_seconds"] for r in rows.values() if r.get("job_seconds") is not None]
    reviewed = [r["review_seconds"] for r in rows.values() if r.get("review_seconds") is not None]
    return {"n": len(cases), "returned": len(rows), "complete": len(rows) == len(cases),
            "task_correct": q, "judge_accepted": a,
            "quality_percent": q / len(cases) * 100,
            "serious_failures": sum(r["serious_failure"] for r in rows.values()),
            "machine_cost_usd": total, "known_attempt_cost_usd": sum(x["cost_usd"] for x in attempts if x.get("cost_usd") is not None),
            "unknown_cost_attempts": sum(x.get("cost_usd") is None for x in attempts),
            "cost_per_correct": total / q if known and q else None,
            "cost_per_judge_accepted": total / a if known and a else None,
            "attempts": len(attempts), "failed_attempts": sum(x["status"] == "error" for x in attempts),
            "job_p95_seconds": percentile(times, .95) if len(times) == len(cases) else None,
            "review_seconds": sum(reviewed) if reviewed else None, "reviewed_items": len(reviewed),
            "evidence_modes": sorted({r["evidence_mode"] for r in rows.values()}),
            "missing_cases": [c["id"] for c in cases if c["id"] not in rows],
            "error_cases": [key for key, r in rows.items() if not r["task_correct"]]}


def comparison(lock, baseline_path, candidate_path):
    verify_lock(lock)
    c = lock["contract"]
    cases = cases_at(lock["case_path"])
    br, cr = load_rows(baseline_path, cases), load_rows(candidate_path, cases)
    b, k = summarize(br, cases), summarize(cr, cases)
    reduction = (1 - k["cost_per_correct"] / b["cost_per_correct"]) * 100 if b["cost_per_correct"] and k["cost_per_correct"] is not None else None
    quality = k["quality_percent"] + 1e-10 >= c["quality_floor_percent"] and k["serious_failures"] == 0
    latency = None if k["job_p95_seconds"] is None and c["max_job_p95_seconds"] is not None else c["max_job_p95_seconds"] is None or k["job_p95_seconds"] <= c["max_job_p95_seconds"]
    prior = lock.get("prior_cost", {"known_cost_usd": 0, "unknown_cost_attempts": 0})
    all_known = b["machine_cost_usd"] is not None and k["machine_cost_usd"] is not None and prior["unknown_cost_attempts"] == 0
    total_cost = prior["known_cost_usd"] + b["known_attempt_cost_usd"] + k["known_attempt_cost_usd"]
    budget = total_cost <= c["max_total_cost_usd"] + 1e-10 if all_known else None
    gain = reduction + 1e-10 >= c["minimum_cost_reduction_percent"] if reduction is not None else None
    complete = b["complete"] and k["complete"]
    gates = {"quality": quality, "minimum_cost_reduction": gain, "latency": latency, "budget": budget}
    verdict = "inconclusive" if not complete else "failed" if any(x is False for x in gates.values()) else "inconclusive" if any(x is None for x in gates.values()) else "worked"
    # Preserve actual input rows so a reviewer can inspect every error and paid attempt.
    return {"schema": 1, "contract": c, "frozen_files": lock["files"],
            "unique_evaluation_inputs": lock.get("unique_evaluation_inputs"),
            "budget_accounting": {"prior": prior, "known_total_cost_usd": total_cost, "all_costs_known": all_known},
            "input_files": {str(Path(p).resolve()): digest(p) for p in (baseline_path, candidate_path)},
            "baseline": b, "candidate": k, "cost_reduction_percent": reduction,
            "gates": gates, "experiment_verdict": verdict, "owner_decision": None,
            "rows": {"baseline": list(br.values()), "candidate": list(cr.values())},
            "limits": ["Evidence modes are labels supplied by the runner, not authenticated receipts.",
                       "Offline or recorded rows do not establish fresh production savings.",
                       "Small samples do not establish stable p95 or rare failure rates.",
                       "Human review/rework remains separate from machine cost."]}


def fmt(n):
    return "unknown" if n is None else f"{n:.6f}"


def markdown(report):
    c = report["contract"]
    scope = "Dev screening only; held-out evaluation not run." if c["stage"] == "dev-screening" else "Held-out comparison of the supplied cases."
    lines = [f"# {c['name']}", "", scope, "", f"Task: {c['task_contract']}", f"Hypothesis: {c['hypothesis']}", "",
             "| Arm | Correct / N | Judge / N | Machine $ | $ / correct | Calls | Job p95 s | Review coverage |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for key in ("baseline", "candidate"):
        s = report[key]
        lines.append(f"| {key} | {s['task_correct']}/{s['n']} | {s['judge_accepted']}/{s['n']} | {fmt(s['machine_cost_usd'])} | {fmt(s['cost_per_correct'])} | {s['attempts']} | {fmt(s['job_p95_seconds'])} | {s['reviewed_items']}/{s['n']} |")
    lines += ["", f"Cost/correct reduction: {fmt(report['cost_reduction_percent'])}%", f"Frozen experiment verdict: **{report['experiment_verdict']}**", "", "Gates: " + json.dumps(report["gates"]),
              "", "## Errors and incomplete evidence", json.dumps({k: {x: report[k][x] for x in ("error_cases", "missing_cases", "unknown_cost_attempts", "evidence_modes")} for k in ("baseline", "candidate")}, indent=2),
              "", "## Experiment budget (development/setup + this comparison)", json.dumps(report["budget_accounting"], indent=2),
              "", "Unique evaluation inputs: " + str(report.get("unique_evaluation_inputs")),
              "", "## Owner decision", json.dumps(report.get("owner_decision"), ensure_ascii=False, indent=2),
              "", "## Evidence limitations"]
    lines += ["- " + x for x in report["limits"]]
    return "\n".join(lines) + "\n"


def write_report(report, out):
    folder = Path(out)
    folder.mkdir(parents=True, exist_ok=True)
    rp = folder / "report.json"
    if rp.exists():
        raise EvidenceError("Report exists; use a new output directory")
    dump(rp, report)
    rp.with_suffix(".sha256").write_text(digest(rp) + "\n")
    (folder / "report.md").write_text(markdown(report), encoding="utf-8")


def decide(path, choice, reason, conditions):
    p = Path(path)
    if digest(p) != p.with_suffix(".sha256").read_text().strip():
        raise EvidenceError("Comparison report changed; preserve its original verdict")
    r = read(p)
    if not reason.strip():
        raise EvidenceError("An owner rationale is required")
    if choice == "keep" and r["experiment_verdict"] != "worked":
        raise EvidenceError("Frozen gates did not pass; keep cannot relabel this experiment")
    if choice == "bounded-trial" and not all(isinstance(conditions.get(k), str) and conditions[k].strip() for k in ("owner", "value", "exposure", "rollback", "checkpoint")):
        raise EvidenceError("A bounded trial needs owner, value/error cost, exposure, rollback and checkpoint")
    r["owner_decision"] = {"choice": choice, "reason": reason, "conditions": conditions if choice == "bounded-trial" else None,
                           "authorizes_deployment": False}
    return r


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("init"); p.add_argument("--out", required=True)
    p = sub.add_parser("freeze"); p.add_argument("--contract", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("compare")
    for x in ("lock", "baseline", "candidate", "out"): p.add_argument("--" + x, required=True)
    p = sub.add_parser("decide"); p.add_argument("--report", required=True); p.add_argument("--out", required=True)
    p.add_argument("--choice", choices=("keep", "revert", "insufficient-evidence", "bounded-trial"), required=True)
    p.add_argument("--reason", required=True)
    for x in ("owner", "value", "exposure", "rollback", "checkpoint"): p.add_argument("--" + x, default="")
    a = parser.parse_args()
    if a.action == "init":
        out = Path(a.out); out.mkdir(parents=True, exist_ok=False)
        for f in ("experiment.json", "decision.md"):
            shutil.copyfile(Path(__file__).resolve().parents[1] / "assets" / f, out / f)
        print(f"Templates created in {out}; fill the contract before freezing.")
    elif a.action == "freeze":
        freeze(a.contract, a.out); print("Experiment frozen; no API calls made.")
    elif a.action == "compare":
        r = comparison(read(a.lock), a.baseline, a.candidate); write_report(r, a.out)
        print(json.dumps({"verdict": r["experiment_verdict"], "gates": r["gates"], "cost_reduction_percent": r["cost_reduction_percent"]}))
    else:
        r = decide(a.report, a.choice, a.reason, {x: getattr(a, x).strip() for x in ("owner", "value", "exposure", "rollback", "checkpoint")})
        out = Path(a.out)
        if out.exists(): raise EvidenceError("Decision file exists; select another output path")
        out.write_text(markdown(r), encoding="utf-8")
        out.with_suffix(".json").write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n")
        print(f"Decision saved to {out}; original gate preserved; no deployment authorized.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, KeyError, ValueError) as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(1)
