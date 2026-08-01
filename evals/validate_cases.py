#!/usr/bin/env python3
"""Cross-validate evaluation cases against the catalogue they score against.

The dominant defect found reviewing the first eight cases was not a wrong expectation
but an UNSATISFIABLE one: a case requiring a signal whose `applicability` facets the
case's own gold profile gates out. A tool that honours applicability - which is the
whole point of applicability - would drop the row and be marked wrong for it. That is
the worst kind of test, because it punishes correct behaviour, and no amount of careful
reading catches it reliably across 152 inclusions.

So it is a check. Each finding is one of two things and the script says which:
  CASE DEFECT       the expectation is wrong; drop or demote the inclusion
  CATALOGUE DEFECT  the expectation is right and the facets are too narrow

It cannot tell them apart on its own - that is a judgement - so it reports the conflict
with both sides printed and leaves the decision to a human.

Usage:
    python3 evals/validate_cases.py [cases_dir] [--json]

Exit codes: 0 clean, 1 errors, 2 unreadable input.
"""

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FAMILIES = os.path.join(REPO, "data", "families")
DEFAULT_CASES = os.path.join(HERE, "cases")

# Facets worth cross-checking: single-valued on the profile, list-valued on the signal.
# Tri-state booleans are checked separately because null means "not a constraint".
CROSSCHECK = ["b2b_b2c", "business_model", "sales_motion", "purchase_motion",
              "consideration", "purchase_cycle", "consumable_vs_durable"]
TRISTATE = ["requires_plg_motion", "has_review_site_category", "dev_audience",
            "has_owned_community"]

# Fields every case must carry so the suite is comparable across shapes. Cases may add
# shape-specific fields freely; they just may not omit these.
CORE_PROFILE_FIELDS = ["b2b_b2c", "business_model", "sales_motion"]


def load_catalogue():
    sigs = {}
    for p in sorted(glob.glob(os.path.join(FAMILIES, "*.json"))):
        with open(p, encoding="utf-8") as fh:
            for s in json.load(fh)["signals"]:
                sigs[s["id"]] = s
    return sigs


def accepted(profile, field):
    """The values a case is willing to accept for a profile field, or None if unstated."""
    node = profile.get(field)
    if node is None:
        return None
    if isinstance(node, dict):
        vals = node.get("accept")
    else:
        vals = node
    if vals is None:
        return None
    if not isinstance(vals, list):
        vals = [vals]
    flat = []
    for v in vals:
        flat.extend(v if isinstance(v, list) else [v])
    return [v for v in flat if isinstance(v, str)]


def check_case(case, sigs, findings):
    cid = case.get("case_id", "<no case_id>")
    profile = case.get("expected_profile") or {}
    inc = case.get("must_include_signals") or []
    exc = case.get("must_exclude_signals") or []
    restricted = case.get("must_flag_restricted") or []

    def add(sev, field, msg, detail=None):
        findings.append({"severity": sev, "case_id": cid, "field": field,
                         "message": msg, "detail": detail})

    for field in CORE_PROFILE_FIELDS:
        if field not in profile:
            add("error", f"expected_profile.{field}",
                "missing from the core profile set, so this case cannot be compared "
                "with the others on the axis that decides most applicability")

    inc_ids = {s["id"] for s in inc}
    exc_ids = {s["id"] for s in exc}
    for sid in sorted(inc_ids & exc_ids):
        add("error", "must_include/must_exclude",
            f"{sid} is in both lists, so the case cannot be satisfied")

    for group, label in ((inc, "must_include_signals"), (exc, "must_exclude_signals"),
                         (restricted, "must_flag_restricted")):
        for s in group:
            if s["id"] not in sigs:
                add("error", label, f"{s['id']} does not exist in the catalogue")

    fam_exp = set(case.get("families_expected") or [])
    fam_na = {f["family"] if isinstance(f, dict) else f
              for f in (case.get("families_not_applicable") or [])}
    for f in sorted(fam_exp & fam_na):
        add("error", "families_expected/families_not_applicable",
            f"{f} is in both lists. These arrays are the machine-readable contract, so "
            "a scorer computing family coverage gets an undefined result. Express a "
            "'partially applicable' family in prose, not by listing it twice")

    # The main event: is each required signal reachable given the case's own profile?
    for s in inc:
        sig = sigs.get(s["id"])
        if not sig:
            continue
        app = sig.get("applicability") or {}
        for facet in CROSSCHECK:
            allowed = app.get(facet)
            if not allowed or not isinstance(allowed, list):
                continue
            case_vals = accepted(profile, facet)
            if case_vals is None:
                continue
            if not set(case_vals) & set(allowed):
                add("error", f"must_include_signals[{s['id']}]",
                    f"unsatisfiable on '{facet}': the case accepts {sorted(case_vals)} "
                    f"but the signal allows {sorted(allowed)}. A tool honouring "
                    "applicability drops this row and is marked wrong for being right",
                    detail="Decide which side is wrong: demote the inclusion (CASE "
                           "DEFECT) or widen the signal's facets (CATALOGUE DEFECT)")
        for facet in TRISTATE:
            need = app.get(facet)
            if need is None:
                continue
            case_vals = accepted(profile, facet)
            if case_vals is None:
                continue
            truthy = [v for v in case_vals if v in (True, "true", "True")]
            falsy = [v for v in case_vals if v in (False, "false", "False")]
            if need is True and falsy and not truthy:
                add("error", f"must_include_signals[{s['id']}]",
                    f"unsatisfiable: the signal requires {facet} true, the case accepts "
                    f"only {sorted(case_vals)}")

    for s in exc:
        sig = sigs.get(s["id"])
        if not sig:
            continue
        app = sig.get("applicability") or {}
        gated = []
        for facet in CROSSCHECK:
            allowed = app.get(facet)
            case_vals = accepted(profile, facet)
            if allowed and case_vals and not set(case_vals) & set(allowed):
                gated.append(facet)
        if gated:
            add("info", f"must_exclude_signals[{s['id']}]",
                f"already gated out by applicability on {gated}. This is not a defect: a "
                "tool that runs the filter can never emit it, so the exclusion tests "
                "whether the filter was actually RUN rather than hand-waved - which is a "
                "real failure mode, since a model can recognise a plausible shortlist and "
                "write the report without executing anything. Just do not count it as "
                "evidence the tool reasoned well about this company")

    hard = sum(1 for s in inc if s.get("how_obvious") == "hard")
    if inc and hard == 0:
        add("warn", "must_include_signals",
            "no inclusion is marked 'hard'. Unaided models already name ~40 signals per "
            "run, so a case made only of obvious and earned signals does not "
            "discriminate")
    if not exc:
        add("warn", "must_exclude_signals",
            "no exclusions. A case with nothing to get wrong cannot catch a wrong answer")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases", nargs="?", default=DEFAULT_CASES)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.cases, "*.json"))) \
        if os.path.isdir(args.cases) else [args.cases]
    if not paths:
        print(f"CANNOT READ: no case files in {args.cases}", file=sys.stderr)
        return 2

    try:
        sigs = load_catalogue()
    except (OSError, json.JSONDecodeError) as exc:
        print(f"CANNOT READ CATALOGUE: {exc}", file=sys.stderr)
        return 2

    findings, cases = [], []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as fh:
                case = json.load(fh)
        except json.JSONDecodeError as exc:
            findings.append({"severity": "error", "case_id": os.path.basename(p),
                             "field": "<file>", "message": f"not valid JSON - {exc}"})
            continue
        cases.append(case)
        check_case(case, sigs, findings)

    errors = [f for f in findings if f["severity"] == "error"]
    warns = [f for f in findings if f["severity"] == "warn"]
    infos = [f for f in findings if f["severity"] == "info"]

    if args.json:
        print(json.dumps({"cases": len(cases), "findings": findings}, indent=2))
        return 1 if errors else 0

    print(f"CASES  {len(cases)} checked against {len(sigs)} catalogue signals")
    print()
    if errors:
        print(f"ERRORS ({len(errors)})")
        for f in errors:
            print(f"  {f['case_id']} :: {f['field']}")
            print(f"      {f['message']}")
            if f.get("detail"):
                print(f"      -> {f['detail']}")
        print()
    if warns:
        print(f"WARNINGS ({len(warns)})")
        for f in warns:
            print(f"  {f['case_id']} :: {f['field']}")
            print(f"      {f['message']}")
        print()
    if infos:
        print(f"INFO ({len(infos)}) - exclusions already gated out by applicability. "
              "These test that the filter RAN, not that the tool reasoned well.")
        for f in infos[:6]:
            print(f"  {f['case_id']} :: {f['field']}")
        if len(infos) > 6:
            print(f"  ... and {len(infos) - 6} more")
        print()
    print("PASS" if not errors else f"FAIL - {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
