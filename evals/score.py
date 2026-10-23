#!/usr/bin/env python3
"""Score a security-auditor findings.json against an eval case's ground truth.

Usage: python3 -I evals/score.py <case.json> <findings.json> [--json]

A ground-truth item counts as found when one record names its scope (function,
template, route, or contract) in the fingerprint, title, or a trace or evidence scope,
AND mentions at least one of its keywords in the fingerprint, title, description, or
root cause. Confirmed records that match no ground-truth item are listed as
"unmatched". They are not counted as false positives automatically: an audit can
find real bugs the ground truth does not list, so a human adjudicates them and records
the decision in the results file.
"""
import json
import sys


def text_of(record, *keys):
    parts = []
    for key in keys:
        value = record.get(key)
        if isinstance(value, str):
            parts.append(value)
    return " ".join(parts).lower()


def scopes_of(record):
    out = [record.get("fingerprint", ""), record.get("title", "")]
    for key in ("trace", "evidence"):
        for step in record.get(key, []) or []:
            if isinstance(step, dict):
                out.append(str(step.get("scope", "")))
                out.append(str(step.get("file", "")))
    return " ".join(out).lower()


def matches(item, record):
    scope = item["scope"].lower()
    if scope not in scopes_of(record):
        return False
    body = text_of(record, "fingerprint", "title", "description", "root_cause", "claimed_root_cause")
    return any(k.lower() in body for k in item["keywords"])


def main(argv):
    as_json = "--json" in argv
    args = [a for a in argv[1:] if a != "--json"]
    if len(args) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    with open(args[0], encoding="utf-8") as h:
        case = json.load(h)
    with open(args[1], encoding="utf-8") as h:
        records = json.load(h)

    truth = case["ground_truth"]
    by_verdict = {"confirmed": [], "needs_validation": [], "rejected": []}
    for r in records:
        by_verdict.setdefault(r.get("verdict"), []).append(r)

    found, found_nv, missed = [], [], []
    for item in truth:
        if any(matches(item, r) for r in by_verdict["confirmed"]):
            found.append(item["id"])
        elif any(matches(item, r) for r in by_verdict["needs_validation"]):
            found_nv.append(item["id"])
        else:
            missed.append(item["id"])

    unmatched = [
        r.get("fingerprint")
        for r in by_verdict["confirmed"]
        if not any(matches(item, r) for item in truth)
    ]
    rejected_truth = [
        item["id"] for item in truth
        if any(matches(item, r) for r in by_verdict["rejected"]) and item["id"] in missed
    ]
    total = len(truth)
    confirmed = len(by_verdict["confirmed"])
    result = {
        "case": case["id"],
        "ground_truth": total,
        "found_confirmed": found,
        "found_needs_validation": found_nv,
        "missed": missed,
        "wrongly_rejected": rejected_truth,
        "recall_confirmed": round(len(found) / total, 3) if total else None,
        "recall_any": round((len(found) + len(found_nv)) / total, 3) if total else None,
        "confirmed_records": confirmed,
        "unmatched_confirmed_for_adjudication": unmatched,
        "precision_lower_bound": round(len(found) / confirmed, 3) if confirmed else None,
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
