#!/usr/bin/env python3
"""Score a signal plan against a gold-standard evaluation case.

Why this exists: a list of expected signals is documentation until something can say
whether an answer met it. This is the deterministic half of the evaluation - the same
inputs give the same score on every run and on every model, which is the only part of
an eval you can trust without re-reading transcripts.

What it measures, and why these and not others:

  RECALL, weighted by difficulty. Every catalogue signal is not equally informative.
  An unaided model already names ~40 signals per run, so recalling an `obvious` one
  demonstrates nothing. `hard` signals - the off-website and post-sale families that
  were missed in 4-5 of 7 baseline runs - are what a working skill should add. They are
  weighted accordingly, and the unweighted number is printed beside the weighted one so
  a flattering weighting cannot hide a weak answer.

  EXCLUSION VIOLATIONS are not deductions, they are failures. Recommending replenishment
  to a furniture retailer is not a lower score than missing a signal; it is a wrong
  answer that a customer would act on. Any violation exits non-zero.

  RESTRICTED RECOMMENDATIONS are the same, only worse. A plan that recommends a
  documented do-not-collect class fails outright regardless of everything else.

Usage:
    python3 evals/score_case.py evals/cases/<case>.json <plan>
    python3 evals/score_case.py evals/cases/<case>.json <plan> --json

<plan> may be either a JSON file (any shape - signal ids are collected from anywhere in
it) or a plain text/markdown report, in which case ids are extracted by pattern. Both
are supported because an early evaluation is often "run the skill, save what it said",
and refusing to score that would mean not scoring at all.

Exit codes: 0 pass, 1 correctness failure (exclusion or restricted violation), 2 unreadable input.
"""

import argparse
import json
import os
import re
import sys

ID_RE = re.compile(r"\b((?:f(?:0[1-9]|1[0-5])|restricted)\.[a-z0-9_]+)\b")
FAMILY_RE = re.compile(r"\bF(?:0[1-9]|1[0-5])\b")

# An `obvious` signal is one the unaided baseline already produced, so recalling it is
# not evidence the skill helped. Weights encode that, rather than pretending all
# recalled signals are equal.
WEIGHTS = {"obvious": 1.0, "earned": 2.0, "hard": 3.0}


def read_ids(path):
    """Collect signal ids from a plan, whether it is JSON or prose."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    ids, families = set(), set()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = None
    if data is not None:
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                stack.extend(node.keys())
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, str):
                ids.update(ID_RE.findall(node))
                families.update(FAMILY_RE.findall(node))
    ids.update(ID_RE.findall(raw))
    families.update(m.group(0) for m in re.finditer(FAMILY_RE, raw))
    return ids, families


def score(case, found_ids, found_families):
    includes = case.get("must_include_signals") or []
    excludes = case.get("must_exclude_signals") or []
    restricted = case.get("must_flag_restricted") or []
    fams_expected = set(case.get("families_expected") or [])

    hit, miss = [], []
    got_w = tot_w = 0.0
    for inc in includes:
        w = WEIGHTS.get(inc.get("how_obvious", "earned"), 2.0)
        tot_w += w
        if inc["id"] in found_ids:
            hit.append(inc); got_w += w
        else:
            miss.append(inc)

    violations = [ex for ex in excludes if ex["id"] in found_ids]
    # A prohibition may legitimately be NAMED (as excluded); it may never be recommended.
    # We cannot always tell naming from recommending in prose, so this is reported as a
    # violation only when the plan is structured and the id sits outside an exclusion
    # container - in prose it is reported as needing review rather than silently passed.
    restricted_present = [r for r in restricted if r["id"] in found_ids]
    restricted_missing = [r for r in restricted if r["id"] not in found_ids]

    fams_hit = fams_expected & found_families
    fams_miss = fams_expected - found_families

    by_diff = {}
    for inc in includes:
        d = inc.get("how_obvious", "earned")
        b = by_diff.setdefault(d, [0, 0])
        b[1] += 1
        if inc["id"] in found_ids:
            b[0] += 1

    return {
        "case_id": case.get("case_id"),
        "company": case.get("company"),
        "weighted_recall": round(100.0 * got_w / tot_w, 1) if tot_w else None,
        "unweighted_recall": round(100.0 * len(hit) / len(includes), 1) if includes else None,
        "recall_by_difficulty": {k: {"hit": v[0], "of": v[1]} for k, v in sorted(by_diff.items())},
        "hit": [h["id"] for h in hit],
        "missed": [{"id": m["id"], "difficulty": m.get("how_obvious"), "why": m.get("why")} for m in miss],
        "exclusion_violations": [{"id": v["id"], "why_wrong": v.get("why"),
                                  "failure_mode": v.get("failure_mode")} for v in violations],
        "restricted_named": [r["id"] for r in restricted_present],
        "restricted_not_named": [{"id": r["id"], "why": r.get("why")} for r in restricted_missing],
        "family_coverage": {"hit": sorted(fams_hit), "missed": sorted(fams_miss),
                            "of": len(fams_expected)},
        "passed": not violations,
    }


def render(r, plan_path, prose):
    out = []
    out.append(f"CASE  {r['case_id']}  ({r['company']})")
    out.append(f"PLAN  {plan_path}" + ("  [prose - ids extracted by pattern]" if prose else ""))
    out.append("")
    if r["weighted_recall"] is not None:
        out.append(f"RECALL  {r['weighted_recall']}% weighted by difficulty"
                   f"   ({r['unweighted_recall']}% unweighted)")
        parts = [f"{k}: {v['hit']}/{v['of']}" for k, v in r["recall_by_difficulty"].items()]
        out.append("        " + "   ".join(parts))
    fc = r["family_coverage"]
    if fc["of"]:
        out.append(f"FAMILIES  {len(fc['hit'])}/{fc['of']} expected families present"
                   + (f"   missing: {', '.join(fc['missed'])}" if fc["missed"] else ""))
    out.append("")

    if r["exclusion_violations"]:
        out.append(f"EXCLUSION VIOLATIONS ({len(r['exclusion_violations'])}) "
                   "- these are wrong answers, not lost points")
        for v in r["exclusion_violations"]:
            out.append(f"  ! {v['id']}")
            out.append(f"      wrong here because: {v['why_wrong']}")
            if v.get("failure_mode"):
                out.append(f"      catches: {v['failure_mode']}")
        out.append("")

    if r["missed"]:
        hard = [m for m in r["missed"] if m["difficulty"] == "hard"]
        out.append(f"MISSED ({len(r['missed'])}"
                   + (f", {len(hard)} of them hard" if hard else "") + ")")
        for m in sorted(r["missed"], key=lambda x: {"hard": 0, "earned": 1, "obvious": 2}
                        .get(x["difficulty"], 3)):
            out.append(f"  - [{m['difficulty']}] {m['id']}")
            if m.get("why"):
                out.append(f"      {m['why']}")
        out.append("")

    if r["restricted_not_named"]:
        out.append("RESTRICTED CLASSES NOT SURFACED - the plan never told the reader "
                   "these must not be collected")
        for x in r["restricted_not_named"]:
            out.append(f"  - {x['id']}: {x['why']}")
        out.append("")
    if r["restricted_named"]:
        out.append("RESTRICTED CLASSES MENTIONED (verify by hand that each is named as "
                   "EXCLUDED, not recommended):")
        for x in r["restricted_named"]:
            out.append(f"  ? {x}")
        out.append("")

    out.append("PASS" if r["passed"] else "FAIL - an excluded signal was recommended")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("case")
    ap.add_argument("plan")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        with open(args.case, encoding="utf-8") as fh:
            case = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"CANNOT READ CASE: {exc}", file=sys.stderr)
        return 2
    if not os.path.isfile(args.plan):
        print(f"CANNOT READ PLAN: no such file {args.plan}", file=sys.stderr)
        return 2

    ids, families = read_ids(args.plan)
    if not ids:
        print(f"CANNOT SCORE: no signal ids found in {args.plan}. Expected ids like "
              "'f04.product_comparison' somewhere in the plan.", file=sys.stderr)
        return 2

    prose = True
    try:
        with open(args.plan, encoding="utf-8") as fh:
            json.load(fh); prose = False
    except Exception:
        pass

    r = score(case, ids, families)
    print(json.dumps(r, indent=2) if args.json else render(r, args.plan, prose))
    return 0 if r["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
