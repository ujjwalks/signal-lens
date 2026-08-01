#!/usr/bin/env python3
"""Prototype of filter_signals.py, used to build the arm-C payload for the control.

This is deliberately crude: applicability overlap scoring, no legal gate, no clamping.
It exists to answer one question the control needs answered honestly - given a coarse
profile, which rows would the real filter put in front of the model, and how many tokens
is that? It must not consult the eval cases, because the gold sets would leak the answer
into the arm they are meant to score.

The projection matters as much as the selection. A full row is ~35 facets; a 15-row
shortlist at full width is ~24k tokens, which does not fit a body budget. So rows are
projected to the facets that carry the measured delta - how to obtain it, who it attaches
to, whether you may, and what breaks it - and the rest are dropped.

Usage:
    python3 evals/prototype_filter.py <profile.json> [-n 15] [--json]
"""

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FAMILIES = os.path.join(os.path.dirname(HERE), "data", "families")

FACETS = ["b2b_b2c", "business_model", "sales_motion", "purchase_motion",
          "consideration", "purchase_cycle", "consumable_vs_durable", "triggers"]
TRISTATE = ["requires_plg_motion", "has_review_site_category", "dev_audience",
            "has_owned_community"]


def load():
    buildable, restricted = [], []
    for p in sorted(glob.glob(os.path.join(FAMILIES, "*.json"))):
        with open(p, encoding="utf-8") as fh:
            for s in json.load(fh)["signals"]:
                (restricted if s["id"].startswith("restricted.") else buildable).append(s)
    return buildable, restricted


def score(sig, profile):
    """Applicability overlap. A facet the profile does not state is not a constraint."""
    app = sig.get("applicability") or {}
    pts = 0.0
    for f in FACETS:
        allowed, have = app.get(f), profile.get(f)
        if not allowed or have is None:
            continue
        have = have if isinstance(have, list) else [have]
        if set(have) & set(allowed):
            pts += 2.0
        else:
            return None  # hard gate: the profile excludes this row
    for f in TRISTATE:
        need, have = app.get(f), profile.get(f)
        if need is None or have is None:
            continue
        if need is True and have is False:
            return None
        if need == have:
            pts += 1.0
    boost = set(app.get("industry_boost") or []) & set(profile.get("industries") or [])
    pts += 1.5 * len(boost)
    # Feasibility, not strength: every strength value in the catalogue is an author
    # estimate, so ranking on it would rank on nothing. Rank on whether rung 1 is
    # reachable with records already held.
    pts += {"available_now": 3.0, "website_instrumentation": 2.0, "public_cost_free": 2.0,
            "integration": 1.0, "user_permission": 1.0, "partial": 0.5,
            "partner": 0.0, "licensed": 0.0, "unavailable": -2.0}.get(
        sig.get("availability"), 0.0)
    return pts


def project(sig):
    """Keep the facets that carry the delta; drop the rest."""
    rung1 = (sig.get("capability_ladder") or [{}])[0]
    fresh = sig.get("freshness") or {}
    return {
        "id": sig["id"],
        "family": sig["family"],
        "name": sig["name"],
        "definition": sig["definition"],
        "question_answered": sig.get("question_answered"),
        "required_raw_fields": sig.get("required_raw_fields"),
        "identity_level": sig.get("identity_level"),
        "data_class": sig.get("data_class"),
        "source_class": sig.get("source_class"),
        "collection_method": sig.get("collection_method"),
        "rung_1": {"how": rung1.get("how"), "requires": rung1.get("requires")},
        "ladder_rungs_total": len(sig.get("capability_ladder") or []),
        "availability": sig.get("availability"),
        "permission_requirement": sig.get("permission_requirement"),
        "sensitivity": sig.get("sensitivity"),
        "freshness": {"type": fresh.get("type"), "half_life_days": fresh.get("half_life_days")},
        "false_positives": sig.get("false_positives"),
        "confirmation_signals": sig.get("confirmation_signals"),
        "activation_direction": sig.get("activation_direction"),
        "access_conditions": sig.get("access_conditions"),
    }


def project_restricted(sig):
    return {"id": sig["id"], "name": sig["name"],
            "prohibition_basis": sig.get("prohibition_basis"),
            "activation_direction": sig.get("activation_direction")}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("profile")
    ap.add_argument("-n", type=int, default=15)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    with open(args.profile, encoding="utf-8") as fh:
        profile = json.load(fh)

    buildable, restricted = load()
    scored = [(score(s, profile), s) for s in buildable]
    kept = sorted([(p, s) for p, s in scored if p is not None],
                  key=lambda t: (-t[0], t[1]["id"]))
    dropped = len(scored) - len(kept)
    short = [project(s) for _, s in kept[:args.n]]
    payload = {"profile_id": profile.get("id"),
               "shortlist": short,
               "prohibitions": [project_restricted(s) for s in restricted],
               "gated_out": dropped,
               "considered": len(buildable)}

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"PROFILE {profile.get('id')}")
        print(f"  {len(buildable)} rows considered, {dropped} gated out by applicability, "
              f"top {len(short)} returned")
        for p, s in kept[:args.n]:
            print(f"  {p:5.1f}  {s['id']:44} {s['availability']}")
        est = len(json.dumps(payload)) // 4
        print(f"\n  payload ~{est} tokens ({len(json.dumps(payload))} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
