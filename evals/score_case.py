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

# A signal id appearing in a plan does not mean the plan RECOMMENDED it. The skill is
# specifically designed to emit a do-not-use bucket and a must-not-collect list - that
# was failure #9, produced by 0 of 7 baseline runs - and both of those name excluded ids
# by construction. Scoring every mention as a recommendation failed the exact answer the
# skill exists to produce. So mentions are classified by the context they sit in.
NEGATIVE_CONTEXT = re.compile(
    r"do[\s_-]*not[\s_-]*(use|collect|instrument|build|track)|don'?t\s+use|"
    r"excluded?|exclusion|must[\s_-]*not|should[\s_-]*not|not[\s_-]*recommended|"
    r"avoid|prohibit|restricted|blocked|out[\s_-]*of[\s_-]*scope|"
    r"not[\s_-]*applicable|rejected|suppress|no[\s_-]*known[\s_-]*use",
    re.I)
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6}|\*\*|[-*]\s+\*\*)\s*(.+?)\s*(\*\*)?\s*$")


def negative(text):
    """Is this text an exclusion context?

    Signal ids are stripped first. Without that, `restricted.health_status_inference`
    matches the word 'restricted' in its own id, so a plan RECOMMENDING a prohibited
    class scored as though it had correctly excluded it - a false negative on the one
    check that must never produce one.
    """
    return bool(NEGATIVE_CONTEXT.search(ID_RE.sub(" ", text or "")))

# An `obvious` signal is one the unaided baseline already produced, so recalling it is
# not evidence the skill helped. Weights encode that, rather than pretending all
# recalled signals are equal.
WEIGHTS = {"obvious": 1.0, "earned": 2.0, "hard": 3.0}


def _walk_json(node, path, out):
    """Collect (id, negative_context) from JSON, using the key path as context."""
    in_negative_path = negative(" ".join(path))
    if isinstance(node, dict):
        for k, v in node.items():
            _walk_json(v, path + [str(k)], out)
    elif isinstance(node, list):
        for v in node:
            _walk_json(v, path, out)
    elif isinstance(node, str):
        local = in_negative_path or negative(node)
        for sid in ID_RE.findall(node):
            out.append((sid, local))


def _walk_prose(raw, out):
    """Collect (id, negative_context) from markdown, using the enclosing heading."""
    section_negative = False
    for line in raw.splitlines():
        m = HEADING_RE.match(line)
        if m and not ID_RE.search(line):
            section_negative = negative(m.group(2))
            continue
        line_negative = section_negative or negative(line)
        for sid in ID_RE.findall(line):
            out.append((sid, line_negative))


def read_ids(path):
    """Split a plan's signal ids into what it RECOMMENDED and what it EXCLUDED.

    Returns (recommended, excluded, families, is_prose).
    """
    with open(path, encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    try:
        data = json.loads(raw)
        prose = False
    except json.JSONDecodeError:
        data, prose = None, True

    mentions = []
    if data is not None:
        _walk_json(data, [], mentions)
    else:
        _walk_prose(raw, mentions)

    recommended = {sid for sid, neg in mentions if not neg}
    excluded = {sid for sid, neg in mentions if neg} - recommended

    # Families are inferred from what was RECOMMENDED, plus any explicit F## mention.
    # Inferring from ids matters: a plan that lists f04.product_comparison has covered
    # F04 whether or not it spells the family code out, and requiring the code punished
    # correct answers for a formatting choice.
    families = {sid.split(".")[0].upper() for sid in recommended
                if not sid.startswith("restricted.")}
    families.update(FAMILY_RE.findall(raw))
    return recommended, excluded, families, prose


def score(case, recommended, excluded_by_plan, found_families):
    includes = case.get("must_include_signals") or []
    excludes = case.get("must_exclude_signals") or []
    restricted = case.get("must_flag_restricted") or []
    fams_expected = set(case.get("families_expected") or [])

    hit, miss = [], []
    got_w = tot_w = 0.0
    for inc in includes:
        w = WEIGHTS.get(inc.get("how_obvious", "earned"), 2.0)
        tot_w += w
        if inc["id"] in recommended:
            hit.append(inc); got_w += w
        else:
            miss.append(inc)

    # Only a RECOMMENDED excluded signal is a violation. Naming it in a do-not-use
    # bucket is the correct behaviour and is credited, not punished.
    violations = [ex for ex in excludes if ex["id"] in recommended]
    correctly_excluded = [ex for ex in excludes if ex["id"] in excluded_by_plan]
    # A prohibition may be NAMED as excluded; it may never be recommended.
    restricted_flagged = [r for r in restricted if r["id"] in excluded_by_plan]
    restricted_recommended = [r for r in restricted if r["id"] in recommended]
    restricted_missing = [r for r in restricted
                          if r["id"] not in excluded_by_plan and r["id"] not in recommended]

    fams_hit = fams_expected & found_families
    fams_miss = fams_expected - found_families

    by_diff = {}
    for inc in includes:
        d = inc.get("how_obvious", "earned")
        b = by_diff.setdefault(d, [0, 0])
        b[1] += 1
        if inc["id"] in recommended:
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
        "correctly_excluded": [e["id"] for e in correctly_excluded],
        "exclusions_of": len(excludes),
        "restricted_flagged": [r["id"] for r in restricted_flagged],
        "restricted_recommended": [{"id": r["id"], "why": r.get("why")} for r in restricted_recommended],
        "restricted_not_named": [{"id": r["id"], "why": r.get("why")} for r in restricted_missing],
        "family_coverage": {"hit": sorted(fams_hit), "missed": sorted(fams_miss),
                            "of": len(fams_expected)},
        "passed": not violations and not restricted_recommended,
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

    if r["correctly_excluded"]:
        out.append(f"CORRECTLY EXCLUDED  {len(r['correctly_excluded'])}/{r['exclusions_of']} "
                   "trap signals were named in a do-not-use bucket rather than recommended")
        out.append("")

    if r["restricted_recommended"]:
        out.append("PROHIBITED CLASSES RECOMMENDED - outright failure")
        for x in r["restricted_recommended"]:
            out.append(f"  !! {x['id']}: {x['why']}")
        out.append("")

    if r["restricted_not_named"]:
        out.append("RESTRICTED CLASSES NOT SURFACED - the plan never told the reader "
                   "these must not be collected")
        for x in r["restricted_not_named"]:
            out.append(f"  - {x['id']}: {x['why']}")
        out.append("")
    if r["restricted_flagged"]:
        out.append("PROHIBITED CLASSES CORRECTLY SURFACED AS EXCLUDED:")
        for x in r["restricted_flagged"]:
            out.append(f"  ok {x}")
        out.append("")

    if r["passed"]:
        out.append("PASS")
    elif r["restricted_recommended"]:
        out.append("FAIL - a documented do-not-collect class was recommended")
    else:
        out.append("FAIL - an excluded signal was recommended")
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

    recommended, excluded_by_plan, families, prose = read_ids(args.plan)
    if not recommended and not excluded_by_plan:
        print(f"CANNOT SCORE: no signal ids found in {args.plan}. Expected ids like "
              "'f04.product_comparison' somewhere in the plan.", file=sys.stderr)
        return 2

    r = score(case, recommended, excluded_by_plan, families)
    print(json.dumps(r, indent=2) if args.json else render(r, args.plan, prose))
    return 0 if r["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
