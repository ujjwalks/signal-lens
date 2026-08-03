#!/usr/bin/env python3
"""Sync the plugin mirror from the canonical skill at the repo root.

Why a mirror exists at all: the two install paths want different layouts. A plain
`git clone` into `~/.claude/skills/signal-lens` needs SKILL.md at the repo root. A plugin
marketplace needs a `skills/<name>/` directory it can point at. Rather than pick one and
break the other, the root is canonical and `plugins/signal-lens/` is generated.

What it deliberately does NOT copy: `data/` (a parked 92-entry catalogue this skill does
not use, ~862KB), `evals/`, `tests/`, `docs/`. An installed plugin should carry the skill
and nothing else.

`scripts/` is copied by explicit allowlist, not wholesale. Only the files the agent runs are part
of the skill: `check_output.py` (step 7), `validate_profile.py` and the
`profile_schema.json` it reads (step 1). The rest (`bump_version.py`, this file,
`validate_catalogue.py`) are repo machinery and would be noise in an install. A new script
does not ship until someone adds it to SCRIPTS below, which is the intended friction.

Run after editing SKILL.md or references/. `tests/test_plugin_mirror.py` fails if the
mirror drifts, so a stale mirror cannot ship quietly.

Usage:
    python3 scripts/sync_plugin.py [--check]
"""

import argparse
import filecmp
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NAME = "signal-lens"
MIRROR = os.path.join(ROOT, "plugins", NAME, "skills", NAME)

# (source, destination-relative-to-mirror). Order is cosmetic.
COPY = [("SKILL.md", "SKILL.md")]
COPY_DIRS = [("references", "references")]
# Scripts the agent runs. Allowlist — see the module docstring.
SCRIPTS = ["check_output.py", "validate_profile.py", "profile_schema.json",
           "validate_signals.py", "signals_schema.json"]


def sources():
    out = [(os.path.join(ROOT, s), os.path.join(MIRROR, d)) for s, d in COPY]
    for s, d in COPY_DIRS:
        src_dir = os.path.join(ROOT, s)
        if not os.path.isdir(src_dir):
            continue
        for fn in sorted(os.listdir(src_dir)):
            if fn.endswith(".md"):
                out.append((os.path.join(src_dir, fn), os.path.join(MIRROR, d, fn)))
    for fn in SCRIPTS:
        out.append((os.path.join(ROOT, "scripts", fn),
                    os.path.join(MIRROR, "scripts", fn)))
    return out


def expected_mirror_files():
    return {os.path.relpath(dst, MIRROR) for _, dst in sources()}


def actual_mirror_files():
    found = set()
    for base, _, files in os.walk(MIRROR):
        for fn in files:
            found.add(os.path.relpath(os.path.join(base, fn), MIRROR))
    return found


def check():
    """Return a list of human-readable drift descriptions."""
    if not os.path.isdir(MIRROR):
        return [f"mirror does not exist at {os.path.relpath(MIRROR, ROOT)}"]
    drift = []
    for src, dst in sources():
        if not os.path.exists(dst):
            drift.append(f"missing from mirror: {os.path.relpath(dst, ROOT)}")
        elif not filecmp.cmp(src, dst, shallow=False):
            drift.append(f"differs from source: {os.path.relpath(dst, ROOT)}")
    for extra in sorted(actual_mirror_files() - expected_mirror_files()):
        drift.append(f"stale file in mirror, no longer in source: {extra}")
    return drift


def sync():
    if os.path.isdir(MIRROR):
        shutil.rmtree(MIRROR)
    for src, dst in sources():
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return [os.path.relpath(d, ROOT) for _, d in sources()]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="report drift and exit non-zero; write nothing")
    args = ap.parse_args()

    if args.check:
        drift = check()
        if drift:
            print(f"MIRROR IS STALE ({len(drift)})")
            for d in drift:
                print(f"  {d}")
            print("\nRun: python3 scripts/sync_plugin.py")
            return 1
        print(f"mirror is in sync ({len(sources())} files)")
        return 0

    written = sync()
    print(f"synced {len(written)} files to plugins/{NAME}/skills/{NAME}/")
    for w in written:
        print(f"  {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
