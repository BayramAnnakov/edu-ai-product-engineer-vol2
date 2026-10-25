"""Recorded policy execution; no private case generator or course judge."""
import copy
import json
import time
import dataset as F
import router as ROUTER

DEFAULT_POLICY = {"rules": False, "strict": True, "typed": False, "fallback": True, "threshold": 50,
                  "fixed_effort": "high", "cache": True, "trim": True, "budget": 2.0}
CONFIGS = ["incumbent", "free-wins", "typed", "rules", "hybrid-fixed", "hybrid-adaptive"]


class LabError(ValueError):
    def __init__(self, message, partial=None):
        super().__init__(message)
        self.partial = partial


def validate_policy(policy):
    if set(policy) != set(DEFAULT_POLICY):
        raise LabError("Policy fields differ from the supported manifest. Reload the policy template.")
    for k in ("rules", "strict", "typed", "fallback", "cache", "trim"):
        if type(policy[k]) is not bool:
            raise LabError(f"{k} must be true or false")
    if type(policy["threshold"]) is not int or not 0 <= policy["threshold"] <= 100:
        raise LabError("threshold must be an integer from 0 to 100")
    if policy["fixed_effort"] not in ("low", "high"):
        raise LabError("fixed_effort must be low or high")
    if type(policy["budget"]) not in (int, float) or not 0.01 <= policy["budget"] <= 10:
        raise LabError("Budget must be $0.01–$10 per configuration")
    return policy


def rule(case, strict=True):
    return ROUTER.rule(F.public_case(case), strict)

def complex_case(case, threshold):
    return ROUTER.complex_case(F.public_case(case), threshold)

def request_for(case, executor, effort, cache, trim, models=None):
    """Fingerprint concrete rendered input and executor identity, not just a preset name."""
    identity = copy.deepcopy((models or {}).get(executor, {"provider": "illustration", "model": f"authored-{executor}-v1", "adapter_version": "w1-contract-v1"}))
    c = F.public_case(case)
    schema = {"type": "object", "properties": {
        "score": {"type": "integer", "minimum": 1, "maximum": 5},
        "reason_code": {"type": "string", "enum": F.REASONS},
        "evidence_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2}},
        "required": ["score", "reason_code", "evidence_ids"], "additionalProperties": False}
    criteria = json.dumps(F.RUBRIC, sort_keys=True, ensure_ascii=False)
    lead_text = json.dumps(c, sort_keys=True, ensure_ascii=False, separators=(",", ":") if trim else None, indent=None if trim else 2)
    metadata = "" if cache else f"<MESSAGE_METADATA>case={c['id']}; as_of={F.AS_OF}</MESSAGE_METADATA>\n"
    user = metadata + "<SCORING_CRITERIA>" + criteria + "</SCORING_CRITERIA>\n<LEAD>" + lead_text + "</LEAD>"
    return {"case": c, "rubric_version": F.VERSION, "executor": executor, "identity": identity,
            "prefix_version": "stable-v1" if cache else "metadata-v0", "input_version": "trim-v1" if trim else "full-v1",
            "payload": {"system": "Score the supplied synthetic account against the criteria. Return only the shared JSON contract. Cite only supplied record IDs.",
                        "messages": [{"role": "user", "content": user}], "effort": effort, "max_output_tokens": 4096, "response_schema": schema}}


def response(case, executor, effort, policy, bank=None):
    req = request_for(case, executor, effort, policy["cache"], policy["trim"], bank.get("models") if bank else None)
    key = F.fingerprint(req)
    if bank is not None:
        if key not in bank["responses"]:
            raise LabError(f"Unseen request {key[:12]}; no answer substituted. Preflight failed.")
        r = bank["responses"][key]
        if F.fingerprint(r["request"]) != key:
            raise LabError("Recorded request fingerprint mismatch")
        return copy.deepcopy(r["answer"]), sum(call["cost_usd"] for call in r["calls"]), r["latency_s"], key, len(r["calls"])
    raise LabError("Recorded calls only: no answer is invented and no provider is called.")


def invocations(case, config, policy):
    """Plan from pre-answer inputs only; shared by execution and bank coverage."""
    if config == "rules" or config.startswith("hybrid") and policy["rules"] and rule(case, policy["strict"]) is not None:
        return []
    executor = "large"
    if config == "typed" or config.startswith("hybrid") and policy["typed"] and not complex_case(case, policy["threshold"]):
        executor = "typed"
    effort = "high" if config in ("incumbent", "free-wins", "typed") else policy["fixed_effort"]
    if config == "hybrid-adaptive":
        effort = "high" if complex_case(case, policy["threshold"]) else "low"
    actual = copy.deepcopy(policy)
    if config == "incumbent": actual.update(cache=False, trim=False)
    plan = [(executor, effort, actual)]
    if executor == "typed" and policy["fallback"] and complex_case(case, 1):
        plan.append(("large", "high", actual))
    return plan


def hard_check(case, answer):
    if not isinstance(answer, dict) or set(answer) != {"score", "reason_code", "evidence_ids"}:
        return False
    ids = answer["evidence_ids"]
    return (type(answer["score"]) is int and 1 <= answer["score"] <= 5 and answer["reason_code"] in F.REASONS
            and isinstance(ids, list) and 1 <= len(ids) <= 2 and all(isinstance(x, str) for x in ids)
            and len(set(ids)) == len(ids) and set(ids).issubset({r["id"] for r in case["records"]})
            and any(r["id"] in ids and answer["reason_code"] in r.get("supports", []) for r in case["records"]))


def execute_case(case, config, policy, bank=None):
    steps, answer, model_calls, cost, latency, key = [], None, 0, 0.0, 0.0, None
    use_rules = config == "rules" or config.startswith("hybrid") and policy["rules"]
    if use_rules:
        t = time.perf_counter()
        answer = rule(case, policy["strict"])
        seconds = time.perf_counter()-t
        steps.append({"step": "rules", "status": "resolved" if answer else "abstained", "cost": 0.0, "seconds": seconds})
        latency += seconds
    used_fallback = False
    executor = "rules" if answer else None
    for i, (executor, effort, actual) in enumerate(invocations(case, config, policy)):
        answer, paid, seconds, key, calls = response(case, executor, effort, actual, bank)
        if paid is None or seconds is None:
            raise LabError("Response is missing cost or latency provenance; repair the bank before comparison")
        cost += paid; latency += seconds; model_calls += calls
        used_fallback = i > 0
        step = {"step": executor + (" fallback" if i else ""), "effort": effort, "status": "answered", "cost": paid, "seconds": seconds, "request_hash": key}
        if bank:
            calls = bank["responses"][key]["calls"]
            step["receipts"] = [{"id": c.get("id"), "usage": c["usage"], "cost_usd": c["cost_usd"],
                                 "trace_url": c.get("trace_url")} for c in calls]
        steps.append(step)
    valid = answer is not None and hard_check(case, answer)
    correct = valid and all(answer[k] == case["label"][k] for k in ("score", "reason_code"))
    accepted = None
    return {"id": case["id"], "company": case["company"], "executor": executor, "answer": answer, "valid": valid,
            "correct": correct, "judge_accepted": accepted, "serious_failure": answer is not None and not valid,
            "abstained": answer is None, "fallback": used_fallback, "calls": model_calls, "cost": cost,
            "scoring_s": round(latency, 4), "enrichment_s": case["enrichment_s"], "pipeline_s": case["enrichment_s"]+latency,
            "steps": [{"step": "enrichment", "status": "already fetched", "cost": 0, "seconds": case["enrichment_s"]}]+steps,
            "request_hash": key}


def percentile(values, q):
    values = sorted(values)
    return values[round((len(values)-1)*q)] if values else None


def summary(rows):
    q = sum(r["correct"] for r in rows); a = None; cost = sum(r["cost"] for r in rows)
    usages = [(c.get("usage") or {}) for r in rows for s in r["steps"] for c in s.get("receipts", [])]
    inp = sum(u.get("input_tokens", 0) for u in usages)
    cached = sum(u.get("input_tokens_details", {}).get("cached_tokens", 0) for u in usages)
    return {"input_tokens": inp, "output_tokens": sum(u.get("output_tokens", 0) for u in usages),
            "cached_tokens": cached, "cache_write_tokens": sum(u.get("input_tokens_details", {}).get("cache_write_tokens", 0) for u in usages),
            "cache_hit_ratio": cached/inp if inp else None,
            "n": len(rows), "q": q, "a": a, "cost": round(cost, 6), "cost_q": round(cost/q, 6) if q else None,
            "cost_a": round(cost/a, 6) if a else None, "serious": sum(r["serious_failure"] for r in rows),
            "abstained": sum(r["abstained"] for r in rows), "fallback": sum(r["fallback"] for r in rows),
            "coverage": sum(r["executor"] == "rules" for r in rows), "calls": sum(r["calls"] for r in rows),
            "enrichment_p95": percentile([r["enrichment_s"] for r in rows], .95),
            "scoring_p50": percentile([r["scoring_s"] for r in rows], .5), "scoring_p95": percentile([r["scoring_s"] for r in rows], .95),
            "pipeline_p50": percentile([r["pipeline_s"] for r in rows], .5), "pipeline_p95": percentile([r["pipeline_s"] for r in rows], .95)}


def assess(results, prediction):
    """Apply the same frozen quality/economics gates to every comparator."""
    base = results["free-wins"]
    bq = base["summary"]["q"]
    baseline = sum(r["cost"] for r in base["rows"])/bq if bq else None
    gates = {}
    for config, result in results.items():
        s = result["summary"]
        cost_q = sum(r["cost"] for r in result["rows"])/s["q"] if s["q"] else None
        gain = (1-cost_q/baseline)*100 if baseline and cost_q is not None else None
        quality = bool(s["n"] and s["q"]/s["n"]*100 >= float(prediction["quality_floor"]) and not s["serious"])
        passes = quality and gain is not None and gain+1e-8 >= float(prediction["minimum_gain"])
        gates[config] = {"quality_pass": quality, "gain_percent": gain, "passes": passes, "cost_q": cost_q}
    eligible = [k for k,v in gates.items() if v["passes"]]
    best = min(eligible, key=lambda k:gates[k]["cost_q"]) if eligible else None
    return {"rows": gates, "cheapest_passing": best}


def run(split, config, policy, bank=None):
    validate_policy(policy)
    if split not in F.CASES or config not in CONFIGS:
        raise LabError("Unknown split or configuration")
    rows = []
    def incomplete(case_id, reason):
        return {"config": config, "split": split, "status": "incomplete", "policy_hash": F.fingerprint(policy),
                "rows": rows, "summary": summary(rows), "blocked_case": case_id, "stop_reason": reason,
                "evidence_mode": "Recorded-response simulation" if bank else "Illustration"}
    for c in F.CASES[split]:
        try:
            row = execute_case(c, config, policy, bank)
        except LabError as ex:
            ex.partial = incomplete(c["id"], str(ex)); raise
        if sum(x["cost"] for x in rows)+row["cost"] > policy["budget"]:
            why = f"Budget cap reached after {len(rows)} cases; no partial run promoted. Increase the predeclared budget on dev."
            partial = incomplete(c["id"], why)
            partial["blocked_estimated_cost"] = row["cost"]
            raise LabError(why, partial)
        rows.append(row)
    return {"config": config, "split": split, "policy_hash": F.fingerprint(policy), "rows": rows, "summary": summary(rows),
            "evidence_mode": "Recorded-response simulation" if bank else "Illustration",
            "source": bank["source"] if bank else "Authored fixture responses; no model calls or billed spend",
            "economics": "Composed from metered call receipts; no new provider spend during replay" if bank and bank.get("measurement") else "Composed recorded estimates" if bank else "Illustrative assumptions, not measured model performance",
            "enrichment": "Synthetic teaching timing; not a live fetch", "version": F.VERSION}
