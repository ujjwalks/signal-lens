#!/usr/bin/env python3
"""Bump the version in every place that has to agree.

Four files carry the version and all four must match, because the Codex plugin cache is
keyed by version: `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/`. Push without
bumping and installed users see nothing — which happened once already, silently, for three
commits' worth of work.

`tests/test_plugin_mirror.py` checks the four agree with each other. It cannot check that
you remembered to bump, so this exists to make forgetting harder than remembering.

Usage:
    python3 scripts/bump_version.py 0.3.0
    python3 scripts/bump_version.py --show
"""

import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NAME = "signal-lens"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

JSON_TARGETS = [
    (os.path.join(ROOT, ".claude-plugin", "marketplace.json"),
     [("metadata", "version"), ("plugins", 0, "version")]),
    (os.path.join(ROOT, "plugins", NAME, ".claude-plugin", "plugin.json"), [("version",)]),
    (os.path.join(ROOT, "plugins", NAME, ".codex-plugin", "plugin.json"), [("version",)]),
]
SKILL = os.path.join(ROOT, "SKILL.md")
SKILL_RE = re.compile(r'(^\s*version:\s*)"[^"]+"', re.M)


def get(obj, path):
    for k in path:
        obj = obj[k]
    return obj


def put(obj, path, value):
    for k in path[:-1]:
        obj = obj[k]
    obj[path[-1]] = value


def current():
    found = {}
    m = SKILL_RE.search(open(SKILL, encoding="utf-8").read())
    found["SKILL.md"] = m.group(0).split('"')[1] if m else None
    for path, keys in JSON_TARGETS:
        d = json.load(open(path, encoding="utf-8"))
        for kp in keys:
            found[f"{os.path.relpath(path, ROOT)}:{'.'.join(str(k) for k in kp)}"] = get(d, kp)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version", nargs="?", help="new semver, e.g. 0.3.0")
    ap.add_argument("--show", action="store_true", help="print current versions and exit")
    args = ap.parse_args()

    now = current()
    if args.show or not args.version:
        for k, v in now.items():
            print(f"  {v}  {k}")
        distinct = set(now.values())
        print(("in sync" if len(distinct) == 1 else f"DRIFT: {distinct}"))
        return 0 if len(distinct) == 1 else 1

    new = args.version
    if not SEMVER.match(new):
        print(f"not a semver: {new}", file=sys.stderr)
        return 2
    if new in set(now.values()) and len(set(now.values())) == 1:
        print(f"already at {new} — nothing to do", file=sys.stderr)
        return 2

    raw = open(SKILL, encoding="utf-8").read()
    raw, n = SKILL_RE.subn(lambda m: f'{m.group(1)}"{new}"', raw, count=1)
    if not n:
        print("could not find `version:` in SKILL.md frontmatter", file=sys.stderr)
        return 2
    io.open(SKILL, "w", encoding="utf-8").write(raw)

    for path, keys in JSON_TARGETS:
        d = json.load(open(path, encoding="utf-8"))
        for kp in keys:
            put(d, kp, new)
        with io.open(path, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

    print(f"bumped to {new} in {1 + sum(len(k) for _, k in JSON_TARGETS)} places")
    print("next: python3 scripts/sync_plugin.py && python3 -m unittest discover -s tests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
