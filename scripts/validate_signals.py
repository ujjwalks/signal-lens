#!/usr/bin/env python3
"""Validate phase 2 detection specs, and compute their ranks.

Phase 1 enumerates. Phase 2 says, for each signal, exactly what has to be detected —
which surface, which pattern, which qualifiers, which disqualifiers, and how long it
stays live. Nothing is dropped: a signal nobody can currently detect keeps its entry
with `method: none_known`, because a high-ranked undetectable signal is the argument
for building a tool in phase 3, and deleting it loses that argument permanently.

WHY THE RANK IS COMPUTED HERE RATHER THAN WRITTEN BY THE MODEL.

A model writing `strong` in a column is unfalsifiable, and this repo has already
established that every strength figure is a prior until backtested. So the spec states
four components and this script derives the score from them with fixed weights. The
model cannot assert a rank; it has to state what produces one, and a reader who
disagrees can argue with a component rather than with a vibe.

The weights are a judgement, stated in one place, and are not measured. They are:

    stage             x3   how close the observable sits to a decision. The library's
                           highest-scoring signal is the latest-stage one, so this
                           carries the most weight.
    evidence_density  x3   how many of {count, date, named incumbent} the query
                           REQUIRES. This is what separates venting from intent.
    separability      x2   whether the doppelganger can be expressed as a rule. Low
                           separability caps precision however good the query is.
    reach             x1   whether one detection enumerates a cohort.

    python3 scripts/validate_signals.py signal-lens/example.com.signals.json
    python3 scripts/validate_signals.py <file> --profile signal-lens/example.com.json
    python3 scripts/validate_signals.py <file> --ranked   # ordered, with components
    python3 scripts/validate_signals.py <file> --json

Exit codes: 0 valid, 1 invalid, 2 unreadable.
"""

import argparse
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "signals_schema.json")

WEIGHTS = {"stage": 3, "evidence_density": 3, "separability": 2, "reach": 1}
MAX_SCORE = 4 * 3 + 3 * 3 + 2 * 2 + 2 * 1  # 27

# Platform names that are not surfaces. "LinkedIn" does not tell anyone where to look;
# a named newsletter or a specific board does.
BARE_PLATFORM = re.compile(
    r"^(linkedin|reddit|twitter|x|facebook|instagram|tiktok|youtube|google|"
    r"the web|online|social media|forums|communities|review sites?)$", re.I)


def _walk():
    """Reuse the schema walker from validate_profile.py so there is one of them."""
    spec = importlib.util.spec_from_file_location(
        "validate_profile", os.path.join(HERE, "validate_profile.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.walk


def score(rank):
    """Deterministic. Same components in, same number out, on every run and every model."""
    return sum(WEIGHTS[k] * int(rank.get(k, 0) or 0) for k in WEIGHTS)


def semantic_checks(doc, profile=None):
    errors, warnings = [], []
    signals = doc.get("signals") or []

    seen = {}
    for i, s in enumerate(signals):
        if not isinstance(s, dict):
            continue
        where = f"signals[{i}]"
        name = str(s.get("signal", "")).strip()
        method = s.get("method")

        # A name used twice means two rows were merged upstream or one was copied.
        key = name.lower()
        if key and key in seen:
            errors.append((where, f"duplicate signal name, also at signals[{seen[key]}]. "
                                  "Two entries with one name means the CSV row they came "
                                  "from was split badly or copied."))
        elif key:
            seen[key] = i

        # none_known must be argued, not used as a hiding place.
        if method == "none_known":
            if not str(s.get("unspecifiable_because", "")).strip():
                errors.append((f"{where}.unspecifiable_because",
                               "required when method is none_known. Say why this signal "
                               "resists specification — a reason about the signal, never "
                               "'could not think of a query'. It stays in the list so "
                               "phase 3 can revisit it."))
        else:
            if not s.get("query"):
                errors.append((f"{where}.query",
                               f"method is {method!r} but there is no query. A method "
                               "without a pattern is a plan to write one later."))
            if s.get("observable") == "none":
                errors.append((f"{where}.observable",
                               "'none' is only valid when method is none_known."))

        # Surfaces have to be navigable.
        for j, surf in enumerate(s.get("surface") or []):
            if BARE_PLATFORM.match(str(surf).strip()):
                errors.append((f"{where}.surface[{j}]",
                               f"{surf!r} is a platform, not a surface. Name the board, "
                               "community, register, product page or profile type — "
                               "otherwise nobody knows where to look."))

        # A signal with no stated lookalike is one nobody stress-tested.
        if method != "none_known" and not [d for d in (s.get("disqualifiers") or [])
                                           if str(d).strip()]:
            warnings.append((f"{where}.disqualifiers",
                             "empty. Every signal has a twin that shares its vocabulary "
                             "and inverts its meaning; if you cannot name it, precision "
                             "is unknown rather than high."))

        # State comparison without a baseline is not a signal, it is a reading.
        if method == "state_diff":
            b = s.get("baseline") or {}
            if not b.get("required"):
                errors.append((f"{where}.baseline.required",
                               "state_diff compares against an earlier observation, so a "
                               "baseline is required by definition. 'Their rating is 3.9' "
                               "is a fact; 'it fell from 4.6' is the signal."))

        # The count gate is the one that separates venting from intent.
        if profile and method != "none_known":
            noun = ((profile.get("artifacts") or {}).get("severity_noun") or {}).get("noun")
            stated = ((s.get("must_also_have") or {}).get("count_of") or "").strip()
            if noun and stated and noun.strip().lower() not in stated.lower():
                warnings.append((f"{where}.must_also_have.count_of",
                                 f"counts {stated!r}, but the profile's severity noun is "
                                 f"{noun!r}. Counting the wrong noun sorts the market by "
                                 "the wrong thing."))

        # evidence_density claims must be visible in the spec.
        rank = s.get("rank") or {}
        if isinstance(rank, dict) and rank.get("evidence_density") is not None:
            m = s.get("must_also_have") or {}
            supported = sum([bool(m.get("count_of")), bool(m.get("date_from_text")),
                             bool((s.get("query") or {}).get("near"))])
            if int(rank.get("evidence_density") or 0) > supported:
                errors.append((f"{where}.rank.evidence_density",
                               f"claims {rank['evidence_density']} but the spec requires "
                               f"only {supported} of {{count_of, date_from_text, "
                               "query.near}}. The component has to be readable off the "
                               "spec, or the rank is an assertion again."))
    return errors, warnings


def validate(doc, profile=None):
    with io.open(SCHEMA_PATH, encoding="utf-8") as fh:
        schema = json.load(fh)
    structural = []
    _walk()(doc, schema, "", structural)
    sem_err, warns = semantic_checks(doc, profile)

    by_path = dict(sem_err)
    merged, seen = [], set()
    for path, msg in structural:
        if path in seen:
            continue
        seen.add(path)
        merged.append((path, by_path.get(path, msg)))
    for path, msg in sem_err:
        if path not in seen:
            seen.add(path)
            merged.append((path, msg))
    return merged, warns


def ranked(doc):
    out = []
    for s in doc.get("signals") or []:
        if not isinstance(s, dict):
            continue
        r = s.get("rank") or {}
        out.append({
            "signal": s.get("signal", "(unnamed)"),
            "score": score(r),
            "components": {k: r.get(k) for k in WEIGHTS},
            "detectable": s.get("method") != "none_known",
        })
    return sorted(out, key=lambda x: (-x["score"], x["signal"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("specs", help="path to <domain>.signals.json, or - for stdin")
    ap.add_argument("--profile", help="the seller profile, for cross-checks")
    ap.add_argument("--ranked", action="store_true", help="print the ranking and exit")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        if args.specs == "-":
            name, doc = "(stdin)", json.loads(sys.stdin.read())
        else:
            name = os.path.basename(args.specs)
            with io.open(args.specs, encoding="utf-8") as fh:
                doc = json.load(fh)
    except FileNotFoundError:
        print(f"NO SPECS: {args.specs}\nStep 8 has not run for this seller.", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"NOT VALID JSON: {args.specs}\n  {exc}", file=sys.stderr)
        return 2

    profile = None
    if args.profile:
        try:
            with io.open(args.profile, encoding="utf-8") as fh:
                profile = json.load(fh)
        except (OSError, json.JSONDecodeError):
            print(f"could not read profile {args.profile}", file=sys.stderr)
            return 2

    if args.ranked:
        rows = ranked(doc)
        print(f"{'score':>5}  {'':1} {'stg/evd/sep/rch':>15}  signal")
        for r in rows:
            c = r["components"]
            comp = f"{c['stage']}/{c['evidence_density']}/{c['separability']}/{c['reach']}"
            flag = " " if r["detectable"] else "*"
            print(f"{r['score']:>5}  {flag} {comp:>15}  {r['signal'][:60]}")
        undet = [r for r in rows if not r["detectable"]]
        if undet:
            print(f"\n* {len(undet)} not detectable by any known method. Highest is "
                  f"{undet[0]['signal'][:50]!r} at {undet[0]['score']} — that is the "
                  "argument for what to build next, not a row to delete.")
        print(f"\nScores are out of {MAX_SCORE}, computed from stated components with "
              "fixed weights. Every component is a prior until backtested against "
              "closed-won data.")
        return 0

    errors, warnings = validate(doc, profile)
    rows = ranked(doc)

    if args.json:
        print(json.dumps({"specs": name, "valid": not errors, "count": len(rows),
                          "errors": [{"path": p, "message": m} for p, m in errors],
                          "warnings": [{"path": p, "message": m} for p, m in warnings],
                          "ranked": rows}, indent=2))
        return 1 if errors else 0

    print(f"SPECS  {name}  —  {len(rows)} signals")
    print()
    for group, label in ((errors, "ERRORS"), (warnings, "WARNINGS")):
        if group:
            print(f"{label} ({len(group)})")
            for path, msg in group:
                print(f"  {path}")
                print(f"      {msg}")
            print()
    if errors:
        print(f"INVALID — {len(errors)} problem(s). Detection built on these would "
              "inherit every one.")
    else:
        undet = sum(1 for r in rows if not r["detectable"])
        print(f"VALID — {len(rows)} specs, {undet} with no known detection method"
              + (f", {len(warnings)} warning(s)." if warnings else "."))
        print("Run with --ranked to see the ordering.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
