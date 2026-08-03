#!/usr/bin/env python3
"""Check a produced signal plan against the skill's own output contract.

Every defect this checks for shipped, and every one was found by a user running the skill
rather than by an eval. That is the argument for it existing: the paid harness measures
routing and reasoning well and cannot see an artifact at all, because it asks the agent to
describe what it *would* run. A row count cannot exist in a plan.

So this reads the thing the skill actually produced and asks whether it satisfies what the
skill says it produces. It costs nothing, needs no model, and gives the same answer twice.

    python3 evals/check_output.py <plan-file> [--json]

Exit codes: 0 pass, 1 contract violated, 2 unreadable.
"""

import argparse
import csv
import io
import json
import os
import re
import sys

REQUIRED_COLUMNS = ["signal", "what_you_see", "where", "channel", "why_it_matters",
                    "who_the_lead_is", "strength", "false_positive", "detection"]
MIN_ROWS = 20

# Phrases that mean the working method leaked into an answer written for a seller. Each
# was observed in a real run.
LEAKAGE = re.compile(
    r"\bthe (?:filter|catalogue|library|shortlist|reference)\b|stored (?:default|value)|"
    r"\bstep [1-9]\b|references/|SKILL\.md|working method|in this run|"
    r"nothing in these checks", re.I)

# "permitted" and friends are forbidden because the skill is not in a position to clear
# anyone, and a seller reads clearance as permission.
CLEARANCE = re.compile(r"\b(?:is|are)\s+(?:permitted|allowed|fine to collect|safe to collect)\b", re.I)


def extract_csv(text):
    """Pull the CSV block out of a plan, whether fenced or bare."""
    fenced = re.search(r"```(?:csv)?\s*\n(signal,what_you_see.*?)```", text, re.S)
    block = fenced.group(1) if fenced else None
    if block is None:
        i = text.find("signal,what_you_see")
        if i == -1:
            return None
        block = text[i:]
    rows = list(csv.reader(io.StringIO(block)))
    if not rows:
        return None
    header = [h.strip() for h in rows[0]]
    body = [r for r in rows[1:] if any(c.strip() for c in r)]
    return header, body


def check(text):
    findings = []

    def bad(sev, what, detail=""):
        findings.append({"severity": sev, "check": what, "detail": detail})

    parsed = extract_csv(text)
    if not parsed:
        bad("error", "csv-present",
            "no CSV found. The contract is a CSV whose header starts `signal,what_you_see`. "
            "Prose lets a plan compress silently, which is the failure this format exists "
            "to prevent")
        return findings, {"rows": 0}
    header, body = parsed

    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        bad("error", "columns", f"missing required columns: {', '.join(missing)}")
    extra = [c for c in header if c not in REQUIRED_COLUMNS]
    if extra:
        bad("warn", "columns", f"unexpected columns: {', '.join(extra)}")

    n = len(body)
    if n < MIN_ROWS:
        bad("error", "row-count",
            f"{n} rows. The contract floor is {MIN_ROWS} - below that the plan has "
            "summarised rather than enumerated, and a later filter can only choose from "
            "what was listed")

    idx = {c: header.index(c) for c in REQUIRED_COLUMNS if c in header}

    def cell(row, col):
        i = idx.get(col)
        return (row[i].strip() if i is not None and i < len(row) else "")

    empty = {c: 0 for c in REQUIRED_COLUMNS if c in idx}
    na_without_reason = 0
    generic_channel = 0
    for row in body:
        for c in empty:
            if not cell(row, c):
                empty[c] += 1
        if cell(row, "what_you_see").lower() in ("n/a", "na", "-"):
            why = cell(row, "why_it_matters")
            if len(why) < 25:
                na_without_reason += 1
        ch = cell(row, "channel").lower()
        if ch and not re.search(r"r/|/|\.|register|newsletter|board|forum|discord|slack|"
                                r"page|profile|thread|sub", ch) and len(ch) < 12:
            generic_channel += 1

    for c, k in sorted(empty.items()):
        if k:
            sev = "error" if c in ("false_positive", "detection", "why_it_matters") else "warn"
            bad(sev, f"empty:{c}",
                f"{k} of {n} rows have no {c}. "
                + ("A signal with no stated lookalike is one nobody stress-tested"
                   if c == "false_positive" else
                   "Without this a later phase cannot decide what is buildable"
                   if c == "detection" else "Required by the contract"))
    if na_without_reason:
        bad("warn", "na-rows",
            f"{na_without_reason} n/a rows give no business reason. An unexplained n/a is "
            "indistinguishable from a type that was forgotten")
    if generic_channel:
        bad("warn", "channel-specificity",
            f"{generic_channel} rows name a platform but not a surface (e.g. 'LinkedIn' "
            "rather than a named community, board or profile type)")

    leaks = sorted({m.group(0) for m in LEAKAGE.finditer(text)})
    if leaks:
        bad("warn", "tooling-leakage",
            f"working method visible to the reader: {', '.join(leaks[:6])}")
    clear = [m.group(0) for m in CLEARANCE.finditer(text)]
    if clear:
        bad("error", "clearance-language",
            f"asserts clearance ({clear[0]!r}). Report a null result as a null result")

    if not re.search(r"do not use|must not|exclude|never collect", text, re.I):
        bad("error", "exclusions", "no do-not-use section")

    return findings, {"rows": n, "columns": len(header)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile(args.plan):
        print(f"CANNOT READ: {args.plan}", file=sys.stderr)
        return 2
    with open(args.plan, encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    findings, stats = check(text)
    errors = [f for f in findings if f["severity"] == "error"]
    warns = [f for f in findings if f["severity"] == "warn"]

    if args.json:
        print(json.dumps({"plan": os.path.basename(args.plan), **stats,
                          "findings": findings}, indent=2))
        return 1 if errors else 0

    print(f"PLAN  {os.path.basename(args.plan)}  —  {stats['rows']} rows")
    print()
    for group, label in ((errors, "ERRORS"), (warns, "WARNINGS")):
        if group:
            print(f"{label} ({len(group)})")
            for f in group:
                print(f"  {f['check']}")
                if f["detail"]:
                    print(f"      {f['detail']}")
            print()
    print("PASS" if not errors else f"FAIL — {len(errors)} contract violations")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
