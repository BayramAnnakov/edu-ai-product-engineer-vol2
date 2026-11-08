"""Offline Lead Scout teaching routes. Run python3 retrieval.py --help."""

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import time

CORPUS = Path(__file__).with_name("records.json")
QUERIES = {
    "control": "What did Alder Freight A-17 say about budget cuts on the call?",
    "join": "Which shortlisted accounts mentioned budget cuts on a call and still had an open deal?",
    "discover": "Which companies mentioned budget cuts on a call and had an open deal at the snapshot?",
}
LARGE_CORPUS = Path(__file__).with_name("records-large.json")
# The cost block estimates what each route hands the model to read. Four characters per token is a rough rule for
# English JSON; an API token counter gives the exact figure. The price covers the input side only, because every
# route answers in a few lines.
PRICE_PER_MTOK = 2.00  # USD per million input tokens: Claude Sonnet 5.5 list price on 6 Oct 2026
CONCEPTS = {
    "budget": {"budget", "spend", "cuts", "reduction"},
    "call": {"call", "discovery", "spoke", "meeting"},
    "deal": {"deal", "opportunity", "open", "active", "closed", "stage"},
}


def tokens(text):
    return re.findall(r"[\w-]+", text.lower())


def concept_vector(words):
    return [sum(words[word] for word in group) for group in CONCEPTS.values()]


def cosine(left, right):
    denominator = math.hypot(*left) * math.hypot(*right)
    return sum(x * y for x, y in zip(left, right)) / denominator if denominator else 0


def search(records, query, k):
    """Fuse BM25 with a small, authored concept vocabulary using RRF."""
    terms = [Counter(tokens(f"{row['account_id']} {row['text']}")) for row in records]
    average_length = sum(map(lambda row: sum(row.values()), terms)) / len(terms)
    query_terms = Counter(tokens(query))
    df = {word: sum(word in row for row in terms) for word in query_terms}
    lexical, concepts = [], []
    for record, document in zip(records, terms):
        length = sum(document.values())
        length_penalty = 1.2 * (0.25 + 0.75 * length / average_length)
        score = sum(
            math.log1p((len(terms) - df[word] + 0.5) / (df[word] + 0.5))
            * frequency * 2.2 / (frequency + length_penalty)
            for word in query_terms if (frequency := document[word])
        )
        lexical.append((record["id"], score))
        concepts.append((record["id"], cosine(concept_vector(query_terms), concept_vector(document))))
    fused = Counter()
    for channel in (lexical, concepts):
        ranking = sorted(((key, score) for key, score in channel if score), key=lambda item: (-item[1], item[0]))
        for rank, (source_id, _) in enumerate(ranking, 1):
            fused[source_id] += 1 / (60 + rank)
    by_id = {row["id"]: row for row in records}
    return [by_id[source_id] for source_id in sorted(fused, key=lambda key: (-fused[key], key))[:k]]


def crm_lookup(records, accounts, snapshot):
    """Return CRM rows at the requested snapshot. Older statuses are separate."""
    return [
        row for row in records
        if row["kind"] == "crm" and row["account_id"] in accounts and row["date"] == snapshot
    ]


def decide(evidence, shortlist, snapshot):
    results = {}
    for account in shortlist:
        calls = [r for r in evidence if r["kind"] == "call" and r["account_id"] == account and r["date"] <= snapshot]
        status = crm_lookup(evidence, {account}, snapshot)
        budget_calls = [r for r in calls if r["budget_cuts"]]
        if budget_calls and len(status) == 1:
            results[account] = {
                "verdict": "include" if status[0]["status"] == "open" else "exclude",
                "sources": [budget_calls[0]["id"], status[0]["id"]],
            }
        else:
            results[account] = {
                "verdict": "unknown", "sources": [r["id"] for r in budget_calls],
                "missing": "budget-cut call evidence" if not budget_calls else "one current deal status",
            }
    return results


def estimate_tokens(payload):
    return math.ceil(len(json.dumps(payload, ensure_ascii=False)) / 4)


def cost(question, reads, rows, supported=None, price=PRICE_PER_MTOK):
    """What the model reads on this route. Each read is one model call that sees the question and the evidence so far."""
    context_tokens = sum(estimate_tokens([QUERIES[question], evidence]) for evidence in reads)
    usd = round(context_tokens * price / 1_000_000, 5)
    result = {
        "basis": "estimated: 4 characters per token, input side only",
        "price_usd_per_mtok": price,
        "model_reads": len(reads),
        "context_tokens_est": context_tokens,
        "usd_per_answer_est": usd,
        "full_corpus_tokens_est": estimate_tokens([QUERIES[question], rows]),
    }
    if supported is not None:
        result["usd_per_supported_include_est"] = round(usd / supported, 5) if supported else None
    return result


def budget_accounts(rows, snapshot):
    """Every account with a budget-cut call on or before the snapshot. The discover question's candidate universe."""
    return sorted({r["account_id"] for r in rows if r["kind"] == "call" and r["budget_cuts"] and r["date"] <= snapshot})


def run(corpus, question, route, k=2, price=PRICE_PER_MTOK):
    start = time.perf_counter()
    rows = corpus["records"]
    shortlist = corpus["shortlist"]
    snapshot = corpus["snapshot"]
    trace = []
    reads = []  # the evidence the model sees at each call
    # The join question judges the fixed shortlist. The discover question has to find its own candidates.
    accounts = budget_accounts(rows, snapshot) if question == "discover" else shortlist
    if route == "programmatic":
        # The corpus stays outside the model prompt. Code emits just matching rows.
        evidence = [
            r for r in rows
            if r["kind"] == "call" and r["account_id"] in accounts and r["date"] <= snapshot
        ] + crm_lookup(rows, set(accounts), snapshot)
        trace.append({"operation": "filter and join on account_id", "sources": [r["id"] for r in evidence]})
        reads.append(list(evidence))
    else:
        pool = [r for r in rows if r["account_id"] in shortlist] if question == "join" else rows
        evidence = search(pool, QUERIES[question], k)
        trace.append({"operation": "hybrid retrieval", "k": k, "sources": [r["id"] for r in evidence]})
        reads.append(list(evidence))
        if question == "discover":
            accounts = sorted({r["account_id"] for r in evidence if r["kind"] == "call" and r["budget_cuts"]})
            trace.append({"operation": "candidate accounts named by the first pass", "accounts": accounts})
    if question == "control":
        matching_calls = [r for r in evidence if r["kind"] == "call" and r["account_id"] == "A-17"]
        answer = {"source": matching_calls[0]["id"], "text": matching_calls[0]["text"]} if matching_calls else {"source": None}
        reason = "one call answers the control question" if matching_calls else "required call missing"
    else:
        answer = decide(evidence, accounts, snapshot)
        if route == "dynamic":
            gaps = [key for key, row in answer.items() if row.get("missing") == "one current deal status"]
            if gaps:
                found = crm_lookup(rows, set(gaps), snapshot)
                trace.append({"operation": "batched CRM lookup", "accounts": gaps, "sources": [r["id"] for r in found]})
                seen = {r["id"] for r in evidence}
                evidence += [r for r in found if r["id"] not in seen]
                reads.append(list(evidence))
                answer = decide(evidence, accounts, snapshot)
        resolved = all(row["verdict"] != "unknown" for row in answer.values())
        if question == "discover":
            if not answer:
                reason = "the first pass named no candidate; raise k or change the route"
            elif resolved:
                reason = "every candidate has a decision; check coverage for what the first pass never saw"
            else:
                reason = "candidates stop at the route budget with gaps"
        else:
            reason = "both shortlist decisions have evidence" if resolved else "stop at the route budget with gaps"
    result = {
        "mode": "offline deterministic replay", "question": question, "route": route,
        "trace": trace, "evidence": evidence, "answer": answer, "stop_reason": reason,
    }
    if question == "discover":
        # The answer key is the corpus itself: an include needs a budget-cut call and one open CRM row at the snapshot.
        truth = decide(rows, budget_accounts(rows, snapshot), snapshot)
        qualifying = sorted(a for a, row in truth.items() if row["verdict"] == "include")
        supported = [a for a in qualifying if answer.get(a, {}).get("verdict") == "include"]
        result["coverage"] = {
            "qualifying_accounts": len(qualifying), "candidates_from_first_pass": len(accounts),
            "supported_includes": len(supported), "recall": round(len(supported) / len(qualifying), 2) if qualifying else None,
            "missed": [a for a in qualifying if a not in supported],
            "candidates_not_qualifying": [a for a in accounts if truth.get(a, {}).get("verdict") != "include"],
        }
    supported_count = result["coverage"]["supported_includes"] if question == "discover" else None
    result["cost"] = cost(question, reads, rows, supported_count, price)
    result["local_ms"] = round((time.perf_counter() - start) * 1000, 3)
    return result


def load_corpus(path=CORPUS):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", choices=QUERIES)
    parser.add_argument("route", choices=["static", "dynamic", "programmatic"])
    parser.add_argument("--k", type=int, choices=range(1, 51), metavar="1-50", default=2, help="records the first pass returns")
    parser.add_argument("--corpus", type=Path, default=CORPUS, help=f"records file; the extension corpus is {LARGE_CORPUS.name}")
    parser.add_argument("--brief", action="store_true", help="print trace, answer, coverage, cost and stop_reason without the evidence rows")
    parser.add_argument("--price-per-mtok", type=float, default=PRICE_PER_MTOK, metavar="USD",
                        help=f"input price per million tokens for the cost estimate (default {PRICE_PER_MTOK:.2f}, Sonnet 5.5 list price)")
    args = parser.parse_args()
    result = run(load_corpus(args.corpus), args.question, args.route, args.k, args.price_per_mtok)
    if args.brief:
        result = {key: value for key, value in result.items() if key != "evidence"}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
