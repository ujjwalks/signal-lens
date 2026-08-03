#!/usr/bin/env python3
"""Validate a seller profile produced by step 1.

Step 1 writes ./signal-lens/<domain>.json and then runs this. Every later step reads
that file instead of the website, so an error here propagates into every signal derived
afterwards — which is the argument for checking it at the point it is written rather
than noticing at the end that the whole plan was built on the seller's own vocabulary.

Structure comes from scripts/profile_schema.json, so there is one definition of the
shape. The checks below it are the semantic ones a schema cannot express, and each
corresponds to a way a profile can be well-formed and useless:

  - buyer_language that merely paraphrases seller_language. The translation is the
    whole skill; a profile that skips it produces searches nobody's post will match,
    and it looks completely fine until you read the output.
  - a severity noun that is not countable. "Time" and "complexity" cannot appear as an
    integer in a post, so no signal can carry the count the library requires.
  - a workaround with no stated failure condition. That condition IS the signal; a
    workaround without one contributes nothing downstream.

    python3 scripts/validate_profile.py signal-lens/example.com.json
    python3 scripts/validate_profile.py <file> --questions   # what to ask the user
    python3 scripts/validate_profile.py <file> --json

Exit codes: 0 valid, 1 invalid, 2 unreadable.
"""

import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "profile_schema.json")

# Nouns that cannot appear as an integer in somebody's post. A severity noun has to be
# countable or no signal can carry the count the signal library requires of all of them.
UNCOUNTABLE = {
    "time", "money", "effort", "pain", "complexity", "efficiency", "productivity",
    "overhead", "work", "hassle", "friction", "stress", "cost", "revenue", "growth",
    "accuracy", "visibility", "insight", "data", "information", "quality",
}

# Search filler. These attach to any query in any market and are not evidence that
# anyone translated anything. Without this set the whole check is defeated by adding one
# word: "reverse ETL" is caught, "looking for a reverse ETL tool" is not, and the second
# is what a model actually writes when it skips the translation.
FILLER = {
    "best", "top", "good", "great", "cheap", "cheapest", "free", "looking", "look",
    "tool", "tools", "software", "platform", "platforms", "solution", "solutions",
    "vendor", "vendors", "alternative", "alternatives", "option", "options",
    "pricing", "price", "cost", "costs", "review", "reviews", "compare", "comparison",
    "versus", "recommend", "recommendation", "recommendations", "help", "need",
    "want", "use", "using", "used", "anyone", "anybody", "someone", "people",
    "advice", "suggestions", "thoughts", "experience", "experiences", "worth",
    "system", "systems", "service", "services", "app", "apps", "stack",
}

# Words too generic to count as evidence that buyer language was actually derived.
STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with", "my", "our",
    "your", "is", "are", "it", "this", "that", "we", "i", "you", "how", "what", "do",
    "does", "can", "not", "no", "at", "by", "from", "up", "out", "if", "be", "have",
    "has", "get", "got", "am", "as", "was", "were", "than", "then", "too", "very",
}


def tokens(text):
    return {w for w in re.findall(r"[a-z0-9]+", str(text).lower())
            if w not in STOPWORDS and len(w) > 2}


# --------------------------------------------------------------------------- schema

def walk(node, schema, path, out):
    """A deliberately small JSON Schema subset: type, required, enum, minLength,
    minItems, properties, items. Enough for profile_schema.json and nothing more."""
    t = schema.get("type")
    if t == "object":
        if not isinstance(node, dict):
            out.append((path or "<root>", f"expected an object, got {type(node).__name__}"))
            return
        for key in schema.get("required", []):
            # Absent only. An empty value is a different defect with a better message —
            # minLength/minItems below say what is wrong with it, and `prohibited_bridge: []`
            # is a legitimate answer meaning "considered, nothing applies".
            if key not in node or node[key] is None:
                out.append((f"{path}.{key}".lstrip("."), "required key is absent"))
        for key, sub in schema.get("properties", {}).items():
            if key in node and node[key] is not None:
                walk(node[key], sub, f"{path}.{key}".lstrip("."), out)
    elif t == "array":
        if not isinstance(node, list):
            out.append((path, f"expected a list, got {type(node).__name__}"))
            return
        if len(node) < schema.get("minItems", 0):
            out.append((path, f"has {len(node)} entries, needs at least {schema['minItems']}"))
        for i, item in enumerate(node):
            walk(item, schema.get("items", {}), f"{path}[{i}]", out)
    elif t == "string":
        if not isinstance(node, str):
            out.append((path, f"expected a string, got {type(node).__name__}"))
            return
        if len(node.strip()) < schema.get("minLength", 0):
            out.append((path, f"is {len(node.strip())} chars, needs at least "
                              f"{schema['minLength']} — a placeholder, not an answer"))
        if "enum" in schema and node not in schema["enum"]:
            out.append((path, f"must be one of {schema['enum']}, got {node!r}"))


# ------------------------------------------------------------------------ semantics

def semantic_checks(p):
    """Returns (errors, warnings). Each is (path, message)."""
    errors, warnings = [], []
    arts = p.get("artifacts") or {}

    # --- the crux: did the seller->buyer translation actually happen? ---
    vocab = arts.get("vocabulary") or {}
    seller = vocab.get("seller_language") or []
    buyer = vocab.get("buyer_language") or []
    if seller and buyer:
        s_tok = set().union(*(tokens(x) for x in seller)) if seller else set()
        # A phrase counts as translated only if something specific survives removing the
        # seller's vocabulary AND generic search filler. "best <seller category> tool"
        # must not pass merely because "best" and "tool" are not on the seller's website.
        derived = [b for b in buyer if tokens(b) and not (tokens(b) - s_tok - FILLER)]
        if derived:
            ratio = len(derived) / len(buyer)
            msg = (f"{len(derived)} of {len(buyer)} buyer_language entries use only words "
                   f"already in seller_language ({', '.join(map(repr, derived[:3]))}). "
                   "That is the seller's vocabulary rearranged, not the buyer's. Nobody "
                   "with this problem types the seller's category name before they know "
                   "the category exists — they describe the symptom or name the workaround.")
            (errors if ratio >= 0.5 else warnings).append(("artifacts.vocabulary.buyer_language", msg))
        overlap = set().union(*(tokens(x) for x in buyer)) & s_tok if buyer else set()
        if len(buyer) >= 5 and len(overlap) > len(set().union(*(tokens(x) for x in buyer))) * 0.6:
            warnings.append(("artifacts.vocabulary",
                             "buyer_language shares most of its vocabulary with the seller's. "
                             "Check it against a real post before trusting it."))

    # --- severity noun has to be countable ---
    sev = arts.get("severity_noun") or {}
    noun = str(sev.get("noun", "")).strip().lower()
    if noun:
        head = re.sub(r"^(number of|count of|no\.? of)\s+", "", noun)
        if any(w in UNCOUNTABLE for w in head.split()):
            errors.append(("artifacts.severity_noun.noun",
                           f"{noun!r} is not countable. It cannot appear as an integer in "
                           "somebody's post, so no signal can carry the count every signal "
                           "is required to carry. Name the thing there are N of — entities, "
                           "locations, seats, SKUs, clients, spreadsheets, headcount."))
        elif not sev.get("material_at"):
            warnings.append(("artifacts.severity_noun.material_at",
                             "no threshold. Without one, a count in a post cannot be sorted "
                             "into worth-a-human and not."))

    # --- an unanswered price has to become a question ---
    # Most businesses keep price off the HTML: a PDF menu, a Toast or Square ordering
    # page, an image, quote-only. Recording "not stated" and moving on skips the field
    # rather than answering it, and price is what calibrates the severity noun and sets
    # the ceiling the buyer already pays. So a non-answer is allowed only if somebody
    # wrote down the question.
    band = str((p.get("seller") or {}).get("price_band", "")).strip().lower()
    NON_ANSWER = re.compile(
        r"^$|unknown|not stated|not disclosed|not published|not available|not listed|"
        r"^n/?a$|^tbd$|unclear|no pricing|none found")
    if NON_ANSWER.search(band):
        asked = any("price" in str(u.get("field", "")).lower()
                    or "price" in str(u.get("question", "")).lower()
                    or "cost" in str(u.get("question", "")).lower()
                    or "pay" in str(u.get("question", "")).lower()
                    for u in (p.get("unresolved") or []) if isinstance(u, dict))
        if not asked:
            errors.append(("seller.price_band",
                           f"{band or 'empty'!r}, and nothing in `unresolved` asks about it. "
                           "Price is rarely in the HTML — check for a PDF rate card or menu, a "
                           "third-party ordering or booking platform (Toast, Square, ChowNow, "
                           "Resy, Mindbody), an image, or a marketplace listing. If it is behind "
                           "a platform, that platform is a vendor they pay and belongs in "
                           "competitors, not just here. If it is genuinely unavailable, add the "
                           "question naming where you looked."))

    # --- workarounds need a failure condition, because that is the signal ---
    for i, w in enumerate(arts.get("workarounds") or []):
        if isinstance(w, dict):
            if len(str(w.get("fails_when", "")).strip()) < 10:
                errors.append((f"artifacts.workarounds[{i}].fails_when",
                               "missing. The condition under which the workaround breaks is "
                               "the signal — a workaround without one yields nothing later."))
            if not str(w.get("who_maintains", "")).strip():
                warnings.append((f"artifacts.workarounds[{i}].who_maintains",
                                 "unnamed. When that person leaves the workaround dies, and "
                                 "that departure is one of the highest-yield signals there is."))

    # --- the tier sellers forget ---
    comp = arts.get("competitors") or {}
    if not [c for c in (comp.get("the_person_they_pay") or []) if str(c).strip()]:
        errors.append(("artifacts.competitors.the_person_they_pay",
                       "empty. Someone is being paid to do this by hand today — a bookkeeper, "
                       "an agency, a VA, a contractor. Their rate is the price ceiling and "
                       "their departure is a signal. If genuinely nobody is, say so explicitly."))

    # --- prohibited bridge: absent is different from considered-and-empty ---
    if "prohibited_bridge" not in arts:
        errors.append(("artifacts.prohibited_bridge",
                       "absent. An empty list is a valid answer; a missing key means nobody "
                       "asked which inferences would be off-limits."))

    # --- unresolved questions must be askable ---
    for i, u in enumerate(p.get("unresolved") or []):
        if isinstance(u, dict) and "?" not in str(u.get("question", "")):
            warnings.append((f"unresolved[{i}].question",
                             "is not phrased as a question, so it cannot be put to the user."))
    return errors, warnings


def validate(profile):
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        schema = json.load(fh)
    structural = []
    walk(profile, schema, "", structural)
    sem_err, warns = semantic_checks(profile)

    # One message per path. Where both layers fired, the semantic message wins: it says
    # why the field matters downstream, which is what the reader has to act on. Reporting
    # the same defect three times reads as three defects.
    semantic_by_path = dict(sem_err)
    merged, seen = [], set()
    for path, msg in structural:
        if path in seen:
            continue
        seen.add(path)
        merged.append((path, semantic_by_path.get(path, msg)))
    for path, msg in sem_err:
        if path not in seen:
            seen.add(path)
            merged.append((path, msg))
    return merged, warns


# ----------------------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("profile", help="path to signal-lens/<domain>.json, or - for stdin")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--questions", action="store_true",
                    help="print only the unresolved questions, one per line, and exit 0")
    args = ap.parse_args()

    try:
        if args.profile == "-":
            name, raw = "(stdin)", sys.stdin.read()
        else:
            name = os.path.basename(args.profile)
            with io.open(args.profile, encoding="utf-8") as fh:
                raw = fh.read()
        profile = json.loads(raw)
    except FileNotFoundError:
        print(f"NO PROFILE: {args.profile}\n"
              "Step 1 has not run for this seller. Read the site and write it.", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"NOT VALID JSON: {args.profile}\n  {exc}", file=sys.stderr)
        return 2

    if args.questions:
        for u in profile.get("unresolved") or []:
            q = u.get("question", "").strip()
            if q:
                why = u.get("why_it_matters", "").strip()
                print(f"{q}" + (f"  ({why})" if why else ""))
        return 0

    errors, warnings = validate(profile)

    if args.json:
        print(json.dumps({
            "profile": name,
            "valid": not errors,
            "errors": [{"path": p, "message": m} for p, m in errors],
            "warnings": [{"path": p, "message": m} for p, m in warnings],
            "unresolved": len(profile.get("unresolved") or []),
        }, indent=2))
        return 1 if errors else 0

    print(f"PROFILE  {name}")
    print()
    for group, label in ((errors, "ERRORS"), (warnings, "WARNINGS")):
        if group:
            print(f"{label} ({len(group)})")
            for path, msg in group:
                print(f"  {path}")
                print(f"      {msg}")
            print()
    pending = profile.get("unresolved") or []
    if pending:
        print(f"UNRESOLVED ({len(pending)}) — ask the user before deriving signals:")
        for u in pending:
            print(f"  - {u.get('question', '(no question written)')}")
        print()
    if errors:
        print(f"INVALID — {len(errors)} problem(s). Fix the profile and run again. "
              "Signals derived from it would inherit every one of these.")
    else:
        print("VALID" + (f" — {len(warnings)} warning(s) worth reading." if warnings else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
