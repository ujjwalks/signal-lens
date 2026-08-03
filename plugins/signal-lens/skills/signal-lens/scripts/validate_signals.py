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
five components and this script derives the score from them with fixed weights. The
model cannot assert a rank; it has to state what produces one, and a reader who
disagrees can argue with a component rather than with a vibe.

The weights are a judgement, stated in one place, and are not measured. They are:

    stage             x2   how close the observable sits to a decision.
    evidence_density  x3   how many of {numeric_pattern, date_pattern, query.near} the
                           spec ENFORCES. This is what separates venting from intent.
    separability      x2   whether the doppelganger can be expressed as a rule. Low
                           separability caps precision however good the query is.
    reach             x1   whether one detection enumerates a cohort.
    contestedness     x2   how little competition is already fishing this signal.

Two of those were corrected after the first real run, against finboard.ai, produced a
ranking that was visibly wrong in two ways:

  - `count_of` was populated on 26 of 26 detectable specs, so it contributed 1 to every
    density and discriminated nothing. Density was really measuring two things on a
    0-2 range while being reported out of 3. It now counts `numeric_pattern`, a regex
    that has to contain a digit class, so the COUNT gate costs something to claim.
  - stage at x3 buried the only uncontested volume in the market. "Does not know this
    category exists" ranked 27th of 28, while the library calls that type the one place
    with no competition at all. `contestedness` now carries its own weight, and stage
    dropped to x2.

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

# TWO SCORES, NOT ONE. The components answer two different questions and mixing them
# answers neither. Correlating a single combined score against the library's own /10
# judgements gave Spearman 0.41 — and the disagreements were structural, not noise:
# every signal the combined score under-rated converts well and is hard to specify
# precisely, and the one it over-rated is easy to specify and converts less.
#
#   DETECTABILITY — how precisely can this be caught, with what exists today.
#   VALUE         — how much is a catch worth, if you catch it.
#
# A signal can be high on one and zero on the other, and those are the interesting
# ones: high value with no detection method is the phase 3 build list.
DETECT_WEIGHTS = {"evidence_density": 3, "separability": 2}
VALUE_WEIGHTS = {"stage": 2, "contestedness": 2, "reach": 1}
DETECT_MAX = 3 * 3 + 2 * 2   # 13
VALUE_MAX = 4 * 2 + 2 * 2 + 2 * 1  # 14

# A pattern only counts as enforcing something if it can actually match a digit. A
# field being non-empty costs nothing to write; a working regex does not.
HAS_DIGIT_CLASS = re.compile(r"\\d|\[0-9\]|\\p\{N\}")

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


def detectability(s):
    """How precisely this can be caught with what exists today.

    Zero when there is no known method — not a low number, zero, because "we cannot
    detect this at all" and "we can detect this badly" are different states and the
    first one is what phase 3 exists to change.

    A required baseline costs 2: you can read current state on day one but not
    movement, and movement is the signal. That penalty decays to nothing once
    snapshots exist, which is worth saying to the seller rather than hiding.
    """
    if s.get("method") == "none_known":
        return 0
    r = s.get("rank") or {}
    v = sum(DETECT_WEIGHTS[k] * int(r.get(k, 0) or 0) for k in DETECT_WEIGHTS)
    if (s.get("baseline") or {}).get("required"):
        v -= 2
    return max(0, v)


def value(s):
    """How much a catch is worth, independent of whether you can catch it."""
    r = s.get("rank") or {}
    return sum(VALUE_WEIGHTS[k] * int(r.get(k, 0) or 0) for k in VALUE_WEIGHTS)


def score(rank):
    """Kept for the inflated-component cross-check, which only reads evidence_density."""
    return sum(DETECT_WEIGHTS.get(k, 0) * int(rank.get(k, 0) or 0) for k in DETECT_WEIGHTS)


def enforced(s):
    """What the spec actually requires, as opposed to what it says it requires."""
    m = s.get("must_also_have") or {}
    num = str(m.get("numeric_pattern") or "")
    dat = str(m.get("date_pattern") or "")
    return sum([bool(num and HAS_DIGIT_CLASS.search(num)),
                bool(dat and HAS_DIGIT_CLASS.search(dat)),
                bool((s.get("query") or {}).get("near"))])


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
        # Surfaces listed twice inflate nothing but signal a spec assembled carelessly.
        surfaces = [str(x).strip() for x in (s.get("surface") or [])]
        if len(surfaces) != len(set(surfaces)):
            dupes = sorted({x for x in surfaces if surfaces.count(x) > 1})
            warnings.append((f"{where}.surface",
                             f"listed more than once: {', '.join(dupes)}. Harmless to a "
                             "reader and a sign the spec was assembled rather than written."))

        rank = s.get("rank") or {}
        if isinstance(rank, dict) and rank.get("evidence_density") is not None:
            supported = enforced(s)
            if int(rank.get("evidence_density") or 0) > supported:
                errors.append((f"{where}.rank.evidence_density",
                               f"claims {rank['evidence_density']} but the spec enforces "
                               f"only {supported} of {{numeric_pattern with a digit class, "
                               "date_pattern with a digit class, query.near}}. Naming a "
                               "noun in count_of is free; a working pattern is not, and "
                               "only the pattern counts."))
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
            "value": value(s),
            "detectability": detectability(s),
            "components": {k: r.get(k) for k in
                           ("stage", "contestedness", "reach",
                            "evidence_density", "separability")},
            "detectable": s.get("method") != "none_known",
            "needs_baseline": bool((s.get("baseline") or {}).get("required")),
        })
    return sorted(out, key=lambda x: (-x["value"], -x["detectability"], x["signal"]))


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
        print(f"{'value':>5} {'detect':>7}   {'stg/con/rch | evd/sep':>21}  signal")
        print(f"{'/'+str(VALUE_MAX):>5} {'/'+str(DETECT_MAX):>7}")
        for r in rows:
            c = r["components"]
            comp = (f"{c['stage']}/{c['contestedness']}/{c['reach']} | "
                    f"{c['evidence_density']}/{c['separability']}")
            mark = "" if r["detectable"] else " *"
            base = " b" if r["needs_baseline"] else ""
            print(f"{r['value']:>5} {r['detectability']:>7}   {comp:>21}  "
                  f"{r['signal'][:52]}{mark}{base}")

        build = [r for r in rows if r["detectability"] == 0]
        weak = [r for r in rows
                if 0 < r["detectability"] <= DETECT_MAX // 3 and r["value"] >= VALUE_MAX // 2]
        if build:
            print(f"\n* {len(build)} worth having and not detectable at all. Highest is "
                  f"{build[0]['signal'][:46]!r} at value {build[0]['value']}/{VALUE_MAX}. "
                  "That is the build list, not a set of rows to delete.")
        if weak:
            print(f"\n  {len(weak)} more are worth having and only weakly specifiable — "
                  "high value, low detectability. Sharpening those queries is cheaper "
                  "than building anything new.")
        if any(r["needs_baseline"] for r in rows):
            n = sum(1 for r in rows if r["needs_baseline"])
            print(f"\n  b = {n} need a stored earlier observation, so they are scored 2 "
                  "lower today than they will be once snapshots exist. You can read "
                  "current state on day one; movement takes a second look.")
        print(f"\nTwo scores because they answer different questions: whether a catch is "
              f"worth having, and whether you can catch it. Both are priors until "
              "backtested against closed-won data.")
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
