#!/usr/bin/env python3
"""Bump the version in every place that has to agree.

Three JSON files carry the version and all three must match, because the Codex plugin
cache is keyed by version: `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/`.
Push without bumping and installed users see nothing — which happened once already,
silently, for three commits' worth of work.

The version deliberately does NOT live in SKILL.md frontmatter. The cache key comes from
plugin.json; measured across the 19 plugins cached on a real machine, 18 carry no
`metadata.version` at all and every one still resolves to a correct version directory.
A copy in SKILL.md is a fourth thing to keep in sync that nothing reads.

`tests/test_plugin_mirror.py` checks the three agree with each other. It cannot check that
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
