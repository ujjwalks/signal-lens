#!/usr/bin/env python3
"""Validate data/signals.json against the acquisition-row contract.

The contract exists because the baseline study found the failure this catalogue
fixes is not *naming* signals - unaided models name ~40 per run - but knowing how
to obtain each one. At best 8 of ~50 named signals carried any data fields, and
0/7 runs assigned an identity level. So an entry that cannot say how it is
acquired is not a catalogue entry; it is a signal name, which is free.

Two rule classes are enforced:

  CONFORMANCE  every entry carries the required fields with in-enum values.
  SAFETY       a `restricted` entry must NOT carry an implementation path.
               Printing "excluded: health_status_inference" must never require
               shipping the recipe for it. This is a hard fail, not a warning.

Usage:
    python3 scripts/validate_catalogue.py [path/to/signals.json] [--json]

Exit codes: 0 clean, 1 errors found, 2 could not read the catalogue.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CATALOGUE = os.path.join(HERE, os.pardir, "data", "families")

# --- the 15 families, and how many signals the source spec enumerates for each ---
FAMILIES = {
    "F01": ("Problem and need recognition", 5),
    "F02": ("Discovery and search", 6),
    "F03": ("Content and social influence", 7),
    "F04": ("Product and category evaluation", 6),
    "F05": ("Fit, compatibility, and requirements", 6),
    "F06": ("Price, affordability, and value validation", 6),
    "F07": ("Commitment and reciprocal commitment", 8),
    "F08": ("Transaction and payment readiness", 4),
    "F09": ("Delivery, onboarding, and implementation preparation", 4),
    "F10": ("Product usage, ownership, and replacement", 6),
    "F11": ("Recurring purchase, renewal, and replenishment", 5),
    "F12": ("Personal, household, and occasion triggers", 8),
    "F13": ("Business, operational, and regulatory triggers", 8),
    "F14": ("Social, group, advisor, and authority signals", 6),
    "F15": ("Environmental, market, and competitive triggers", 7),
}
EXPECTED_TOTAL = sum(n for _, n in FAMILIES.values())  # 92

IDENTITY_LEVELS = {"visitor", "individual", "household", "account",
                   "buying_group", "asset", "location", "transaction"}
DATA_CLASSES = {"behavioral_event", "transactional_record", "declared_attribute",
                "calendar_join", "external_feed"}
SOURCE_CLASSES = {"first_party_web", "first_party_backend", "crm", "commerce_platform",
                  "product_analytics", "support_system", "marketplace", "review_platform",
                  "public_record", "news_feed", "partner_feed", "licensed_dataset",
                  "user_authorized_connection", "offline_system"}
COLLECTION_METHODS = {"tracking", "api", "export", "upload", "declaration",
                      "inference", "licensed"}
# Availability answers "can it be obtained?" - a COST/EFFORT axis.
AVAILABILITY = {"available_now", "website_instrumentation", "integration",
                "user_permission", "partner", "licensed", "public_cost_free",
                "partial", "unavailable", "restricted", "should_not_be_collected"}
# Permission answers "may it be obtained?" - deliberately ORTHOGONAL to availability,
# because the source spec's own wording is "available from LAWFUL public sources" and
# collapsing the two lets `public_cost_free` be misread as clearance.
PERMISSION = {"none", "notice", "explicit_consent", "contractual_access",
              "regulated_access"}
SENSITIVITY = {"low", "medium", "high", "restricted"}
ACTIVATION_DIRECTION = {"engage", "suppress", "route"}
LATENCY = {"realtime", "hourly", "daily", "weekly", "monthly", "irregular"}
FRESHNESS_TYPES = {"hard_expiry", "decaying", "persistent_fact"}
INDEPENDENCE = {"independent", "vendor_published", "practitioner_survey",
                "author_estimate"}
COVERAGE_TREND = {"declining", "stable", "rising"}
CIPA_EXPOSURE = {"none", "low", "medium", "high"}

INTENT_DIMENSIONS = {"need", "category", "fit", "preference", "requirements", "budget",
                     "value", "readiness", "authority", "urgency", "commitment",
                     "timing", "channel", "risk", "confidence", "identity_scope"}

ID_RE = re.compile(r"^(f(?:0[1-9]|1[0-5])|restricted)\.[a-z0-9_]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_TOP = [
    "id", "family", "name", "definition", "question_answered", "intent_dimensions",
    "identity_level", "data_class", "source_class", "collection_method",
    "availability", "permission_requirement", "sensitivity", "activation_direction",
    "strength", "reliability", "latency", "freshness", "false_positives",
    "applicability", "sourcing_verified_at",
]
# Fields that describe HOW TO BUILD the signal. A restricted entry must carry none.
IMPLEMENTATION_FIELDS = ["capability_ladder", "required_raw_fields", "min_data",
                         "optional_supporting_fields", "access_conditions"]

NUMERIC_EVIDENCE_FACETS = ["strength", "reliability", "coverage"]


class Findings:
    def __init__(self):
        self.rows = []

    def add(self, sev, entry_id, field, msg):
        self.rows.append({"severity": sev, "id": entry_id, "field": field,
                          "message": msg})

    def errors(self):
        return [r for r in self.rows if r["severity"] == "error"]

    def warnings(self):
        return [r for r in self.rows if r["severity"] == "warn"]


def _enum(f, eid, field, value, allowed, required=True):
    if value is None:
        if required:
            f.add("error", eid, field, "missing")
        return
    if value not in allowed:
        sample = ", ".join(sorted(allowed)[:6])
        f.add("error", eid, field,
              f"{value!r} is not a valid value (expected one of: {sample}...)")


def _enum_list(f, eid, field, values, allowed):
    if not isinstance(values, list) or not values:
        f.add("error", eid, field, "must be a non-empty list")
        return
    for v in values:
        if v not in allowed:
            f.add("error", eid, field, f"{v!r} is not a valid value")


def check_entry(entry, f):
    eid = entry.get("id", "<no id>")

    for key in REQUIRED_TOP:
        if key not in entry or entry[key] is None:
            f.add("error", eid, key, "required field is missing")

    if not ID_RE.match(str(eid)):
        f.add("error", eid, "id",
              "must be lowercase 'fNN.snake_name' (or 'restricted.snake_name')")

    fam = entry.get("family")
    if fam not in FAMILIES:
        f.add("error", eid, "family", f"{fam!r} is not one of F01..F15")
    elif not str(eid).startswith("restricted.") and not str(eid).startswith(fam.lower() + "."):
        f.add("error", eid, "id", f"id prefix does not match family {fam}")

    for field, allowed in (
        ("identity_level", IDENTITY_LEVELS),
        ("data_class", DATA_CLASSES),
        ("collection_method", COLLECTION_METHODS),
        ("availability", AVAILABILITY),
        ("permission_requirement", PERMISSION),
        ("sensitivity", SENSITIVITY),
        ("activation_direction", ACTIVATION_DIRECTION),
        ("latency", LATENCY),
    ):
        _enum(f, eid, field, entry.get(field), allowed)

    _enum_list(f, eid, "intent_dimensions", entry.get("intent_dimensions"),
               INTENT_DIMENSIONS)
    if "source_class" in entry:
        sc = entry["source_class"]
        _enum_list(f, eid, "source_class", sc if isinstance(sc, list) else [sc],
                   SOURCE_CLASSES)

    for field in ("strength", "reliability"):
        v = entry.get(field)
        if v is not None and (not isinstance(v, int) or not 1 <= v <= 5):
            f.add("error", eid, field, f"must be an integer 1-5, got {v!r}")

    fresh = entry.get("freshness")
    if isinstance(fresh, dict):
        _enum(f, eid, "freshness.type", fresh.get("type"), FRESHNESS_TYPES)
        if fresh.get("type") == "decaying" and not fresh.get("half_life_days"):
            f.add("error", eid, "freshness.half_life_days",
                  "a decaying signal must state its half-life in days")
    elif "freshness" in entry:
        f.add("error", eid, "freshness", "must be an object with a 'type'")

    if entry.get("sourcing_verified_at") and not DATE_RE.match(
            str(entry["sourcing_verified_at"])):
        f.add("error", eid, "sourcing_verified_at", "must be YYYY-MM-DD")
    if entry.get("coverage_trend"):
        _enum(f, eid, "coverage_trend", entry["coverage_trend"], COVERAGE_TREND)

    legal = entry.get("legal") or {}
    if not isinstance(legal, dict):
        f.add("error", eid, "legal", "must be an object")
    else:
        if legal.get("cipa_exposure"):
            _enum(f, eid, "legal.cipa_exposure", legal["cipa_exposure"], CIPA_EXPOSURE)
        for boolean in ("special_category_risk", "terminal_equipment_access",
                        "person_level_resolution", "gpc_survivable",
                        "third_party_broker_dependence"):
            if boolean in legal and not isinstance(legal[boolean], bool):
                f.add("error", eid, f"legal.{boolean}", "must be true or false")

    fps = entry.get("false_positives")
    if not isinstance(fps, list) or not fps:
        f.add("error", eid, "false_positives",
              "must name at least one alternative explanation - a signal with no "
              "stated false positive is a signal nobody stress-tested")

    # --- provenance: an unevidenced number is not a measurement -------------
    evidence = entry.get("evidence") or []
    if not isinstance(evidence, list):
        f.add("error", eid, "evidence", "must be a list")
        evidence = []
    claimed = set()
    for i, ev in enumerate(evidence):
        if not isinstance(ev, dict):
            f.add("error", eid, f"evidence[{i}]", "must be an object")
            continue
        claimed.add(ev.get("claim"))
        _enum(f, eid, f"evidence[{i}].independence", ev.get("independence"),
              INDEPENDENCE)
        if ev.get("as_of") and not DATE_RE.match(str(ev["as_of"])):
            f.add("error", eid, f"evidence[{i}].as_of", "must be YYYY-MM-DD")
        if ev.get("independence") in ("independent", "vendor_published",
                                      "practitioner_survey") and not ev.get("source_url"):
            f.add("error", eid, f"evidence[{i}].source_url",
                  "a non-estimate claim must cite a URL")

    for facet in NUMERIC_EVIDENCE_FACETS:
        if entry.get(facet) is not None and facet not in claimed:
            f.add("warn", eid, facet,
                  f"{facet} carries no evidence entry - it will clamp to the neutral "
                  "midpoint at render time rather than being taken at face value")

    # --- cross-field coherence --------------------------------------------
    # These combinations are individually in-enum and jointly incoherent. Each one
    # was found by red team on a real entry before it was a rule here; a finding
    # that stays prose recurs on the next contributor.
    perm = entry.get("permission_requirement")
    avail = entry.get("availability")
    restricted = (entry.get("sensitivity") == "restricted"
                  or avail in ("restricted", "should_not_be_collected"))
    if not restricted:
        if legal.get("terminal_equipment_access") and perm == "none":
            f.add("error", eid, "permission_requirement",
                  "terminal_equipment_access is true but permission is 'none'. Reading or "
                  "writing on a visitor's device is non-essential access under ePrivacy "
                  "Art 5(3)/PECR reg 6 and needs consent in the EEA and UK - 'none' is the "
                  "floor of the enum, so this row would clear every permission gate. Use at "
                  "least 'notice', or move the capture server-side and set the flag false")
        if legal.get("person_level_resolution") and perm == "none":
            f.add("error", eid, "permission_requirement",
                  "person_level_resolution is true but permission is 'none'. Resolving a "
                  "natural person always carries at least a transparency duty; data obtained "
                  "from a source other than the individual owes notice under GDPR Art 14")
        if (avail == "public_cost_free" and perm == "none"
                and legal.get("person_level_resolution")):
            f.add("error", eid, "availability",
                  "public_cost_free + permission 'none' + person-level resolution is the "
                  "free-equals-lawful collapse the two axes exist to prevent. Free to obtain "
                  "is not free to use")

        # The safety rule below keys on `sensitivity` and `availability`, both of which
        # the author chooses. That is enough for an honest author and useless against a
        # careless or adversarial one: relabelling sensitivity 'restricted' -> 'high'
        # and availability 'should_not_be_collected' -> 'integration' walks a full
        # special-category build path straight through. So also key on the SEMANTICS.
        # Inferring a special-category attribute is the prohibited class by definition,
        # whatever the entry calls itself. Declared and consented special-category data
        # is a different thing and stays legal here.
        if legal.get("special_category_risk") and entry.get("collection_method") == "inference":
            f.add("error", eid, "collection_method",
                  "special_category_risk with collection_method 'inference' IS the "
                  "prohibited class, regardless of how the entry is labelled. Deriving a "
                  "special-category attribute from behaviour has no GDPR Art 9(2) condition "
                  "available to it. Either the signal is a declared/consented variant (fix "
                  "collection_method) or it belongs in restricted.* with no build path")
        if legal.get("special_category_risk") and perm in ("none", "notice"):
            f.add("warn", eid, "permission_requirement",
                  f"special_category_risk is true but permission is {perm!r}. Art 9 needs a "
                  "condition stronger than notice - usually explicit consent, or a "
                  "regulated-access basis. One of the two fields is wrong; decide which")

    # --- applicability -----------------------------------------------------
    app = entry.get("applicability")
    if not isinstance(app, dict):
        f.add("error", eid, "applicability", "must be an object")
    else:
        if not app.get("b2b_b2c"):
            f.add("error", eid, "applicability.b2b_b2c", "required")
        for tri in ("requires_plg_motion", "has_review_site_category",
                    "dev_audience", "has_owned_community"):
            if tri in app and app[tri] not in (True, False, None):
                f.add("error", eid, f"applicability.{tri}",
                      "must be true, false, or null (null = not a constraint; it must "
                      "never be read as false)")

    # --- SAFETY: a restricted entry must ship no implementation path -------
    if restricted:
        if not str(eid).startswith("restricted."):
            f.add("error", eid, "id",
                  "a restricted entry must use a family-level prohibition id "
                  "('restricted.health_status_inference'), never a per-signal "
                  "inference id - the catalogue documents what must not be built, "
                  "it does not name a build target")
        for field in IMPLEMENTATION_FIELDS:
            if entry.get(field):
                f.add("error", eid, field,
                      f"restricted entries must not carry {field} - publishing the "
                      "prohibition must never require publishing the recipe")
        if not entry.get("prohibition_basis"):
            f.add("error", eid, "prohibition_basis",
                  "a restricted entry must state the basis for the prohibition")
    else:
        if not entry.get("required_raw_fields"):
            f.add("error", eid, "required_raw_fields",
                  "a non-restricted entry must state the minimum fields needed to "
                  "detect it - 'how do we get this' is the whole point of the row")
        ladder = entry.get("capability_ladder")
        if not isinstance(ladder, list) or not ladder:
            f.add("error", eid, "capability_ladder",
                  "must give at least one rung: what a company can do TODAY, and "
                  "ideally the upgrade above it")
        else:
            for i, rung in enumerate(ladder):
                if not isinstance(rung, dict) or not rung.get("how"):
                    f.add("error", eid, f"capability_ladder[{i}]",
                          "each rung needs a 'how'")

    return restricted


def check_catalogue(entries, f):
    ids = [e.get("id") for e in entries]
    for dup, n in Counter(ids).items():
        if n > 1:
            f.add("error", dup, "id", f"duplicate id appears {n} times")

    known = set(ids)
    for e in entries:
        for ref in (e.get("confirmation_signals") or []):
            if ref not in known:
                f.add("error", e.get("id"), "confirmation_signals",
                      f"references unknown signal id {ref!r}")

    by_family = Counter(e.get("family") for e in entries
                        if not str(e.get("id", "")).startswith("restricted."))
    coverage = []
    for fam, (label, expected) in FAMILIES.items():
        got = by_family.get(fam, 0)
        coverage.append((fam, label, got, expected))
        if got == 0:
            f.add("error", fam, "family",
                  f"{fam} ({label}) has no entries - the 15-family walk is the "
                  "structural fix for the blind spots the baseline study found")
    return coverage


def load_catalogue(path):
    """Load one shard or a directory of them.

    The catalogue is sharded one file per family so that a contributor edits one
    small file, and so that entries can be authored in parallel without merge
    conflicts. Nothing is generated, so there is no source-vs-build drift.
    Returns (entries, sources) or raises ValueError with a readable message.
    """
    paths = []
    if os.path.isdir(path):
        paths = sorted(os.path.join(path, n) for n in os.listdir(path)
                       if n.endswith(".json"))
        if not paths:
            raise ValueError(f"no .json shards found in {path}")
    elif os.path.isfile(path):
        paths = [path]
    else:
        raise ValueError(f"no catalogue at {path}")

    entries, sources = [], []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{os.path.relpath(p)} is not valid JSON - {exc}")
        got = data.get("signals") if isinstance(data, dict) else data
        if not isinstance(got, list):
            raise ValueError(f"{os.path.relpath(p)}: expected a list of signals, or "
                             "an object with a 'signals' key")
        entries.extend(got)
        sources.append((os.path.relpath(p), len(got)))
    return entries, sources


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("catalogue", nargs="?", default=DEFAULT_CATALOGUE,
                    help="a shard, or a directory of shards (default: data/families)")
    ap.add_argument("--json", action="store_true", help="emit structured JSON")
    ap.add_argument("--shard-only", action="store_true",
                    help="skip whole-catalogue checks (family coverage, cross-shard "
                         "references) so a single family can be validated while the "
                         "rest are still being authored")
    args = ap.parse_args()

    try:
        entries, sources = load_catalogue(args.catalogue)
    except ValueError as exc:
        print(f"CANNOT READ: {exc}", file=sys.stderr)
        return 2

    f = Findings()
    n_restricted = sum(1 for e in entries if check_entry(e, f))
    coverage = [] if args.shard_only else check_catalogue(entries, f)

    buildable = len(entries) - n_restricted
    unevidenced = sum(1 for r in f.warnings() if r["field"] in NUMERIC_EVIDENCE_FACETS)
    numeric_facets = max(1, buildable * len(NUMERIC_EVIDENCE_FACETS))
    unevidenced_pct = 100.0 * unevidenced / numeric_facets

    if args.json:
        print(json.dumps({
            "catalogue": os.path.relpath(args.catalogue),
            "total": len(entries),
            "buildable": buildable,
            "restricted": n_restricted,
            "expected_total": EXPECTED_TOTAL,
            "unevidenced_numeric_pct": round(unevidenced_pct, 1),
            "coverage": [{"family": a, "label": b, "have": c, "expected": d}
                         for a, b, c, d in coverage],
            "findings": f.rows,
        }, indent=2))
        return 1 if f.errors() else 0

    print(f"CATALOGUE  {os.path.relpath(args.catalogue)}  "
          f"({len(sources)} shard{'s' if len(sources) != 1 else ''})")
    print(f"  {len(entries)} entries: {buildable} buildable, {n_restricted} restricted "
          f"(spec enumerates {EXPECTED_TOTAL})")
    print()
    if coverage:
        print("FAMILY COVERAGE")
        for fam, label, got, expected in coverage:
            mark = "ok " if got >= expected else ("EMPTY" if got == 0 else "thin ")
            print(f"  {mark} {fam}  {got:>2}/{expected:<2}  {label}")
        print()

    if f.errors():
        print(f"ERRORS ({len(f.errors())})")
        for r in f.errors():
            print(f"  {r['id']} :: {r['field']}")
            print(f"      {r['message']}")
        print()
    if f.warnings():
        print(f"WARNINGS ({len(f.warnings())})")
        for r in f.warnings()[:20]:
            print(f"  {r['id']} :: {r['field']} - {r['message']}")
        if len(f.warnings()) > 20:
            print(f"  ... and {len(f.warnings()) - 20} more")
        print()

    print(f"UNEVIDENCED NUMERIC FACETS: {unevidenced_pct:.1f}% "
          "(these clamp to the neutral midpoint at render time)")
    print("PASS" if not f.errors() else f"FAIL - {len(f.errors())} errors")
    return 1 if f.errors() else 0


if __name__ == "__main__":
    sys.exit(main())
