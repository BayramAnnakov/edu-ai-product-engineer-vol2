#!/usr/bin/env python3
"""Read sanitized examples without a provider or Langfuse account."""
import json
from pathlib import Path


def main():
    folder = Path(__file__).resolve().parents[1] / "lesson1" / "traces"
    rows = [json.loads(line) for line in (folder / "cache-pair.jsonl").read_text().splitlines()]
    print("Actual recorded public-document cache calls; dated usage prices, not invoices.")
    print("Condition\tRead\tWrite\tUSD\tSeconds")
    for r in rows:
        d = r["usage"]["input_tokens_details"]
        print(f"{r['condition']}\t{d['cached_tokens']}\t{d['cache_write_tokens']}\t{r['cost_usd']:.7f}\t{r['latency_seconds']:.3f}")
    changing = sum(r["cost_usd"] for r in rows if r["condition"].startswith("changing"))
    stable = sum(r["cost_usd"] for r in rows if r["condition"].startswith("stable"))
    print(f"Cold+warm pair: changing ${changing:.7f}; stable ${stable:.7f}; reduction {(1-stable/changing)*100:.2f}%")
    print("\nActual recorded calls on one selected synthetic development case; not a population error-rate estimate.")
    for line in (folder / "scoring-boundary.jsonl").read_text().splitlines():
        r = json.loads(line)
        print(f"{r['model']}: output={json.dumps(r['output'])}; ${r['cost_usd']:.7f}; {r['latency_seconds']:.3f}s")
    print("Earlier Jev-as-final-scorer example. Current Jev task is executor choice.")
    print("Earlier Jev-as-final-scorer example. Current Jev task is executor choice.")
    print("Expected score1/not_icp from the visible contract. A valid citation and schema do not prove the score.")

    print("\nCurrent same-task model comparison and one-choice Jev router; selected excerpts only.")
    for line in (folder / "model-choice-routing.jsonl").read_text().splitlines():
        r = json.loads(line)
        print(f"{r['model']}: output={json.dumps(r['output'])}; ${r['cost_usd']:.7f}; {r['latency_seconds']:.3f}s")
    print("A routed workflow costs Jev plus its selected scorer, not Jev alone.")
    print("\nCurrent same-task model comparison and one-choice Jev router; selected excerpts only.")
    for line in (folder / "model-choice-routing.jsonl").read_text().splitlines():
        r = json.loads(line)
        print(f"{r['model']}: output={json.dumps(r['output'])}; ${r['cost_usd']:.7f}; {r['latency_seconds']:.3f}s")
    print("A routed workflow costs Jev plus its selected scorer, not Jev alone.")

if __name__ == "__main__":
    main()
