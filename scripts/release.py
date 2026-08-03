#!/usr/bin/env python3
"""Tag and release the current version, refusing when something is not ready.

This exists because of a specific failure. PR #2 fixed a real defect — a vocabulary
check defeated by adding one filler word — and shipped it without bumping the version.
So `1.2.0` named two materially different states of main, and anyone who installed
during the earlier window had the broken one with no way to tell. `bump_version.py`
was already there. Nobody ran it.

So this refuses rather than reminds. Every check below corresponds to a way a release
has actually gone wrong in this repo:

  dirty tree          the tag would point at something that is not what you tested
  not on main         tagging a branch produces a version nobody can install
  versions disagree   the Codex cache is keyed by plugin.json; drift means the wrong
                      thing ships, silently
  mirror stale        the plugin carries a different skill from the repo
  tests failing       obvious, and cheap to check
  tag exists          a version means one commit, or it means nothing
  version unchanged   THE 1.2.0 FAILURE. Commits since the last tag with no bump means
                      two different states share a version. This is the check the
                      others existed without.

    python3 scripts/release.py              # dry run: report and exit
    python3 scripts/release.py --notes-from HEAD
    python3 scripts/release.py --go         # tag, push, create the GitHub release

Exit codes: 0 ready or released, 1 refused, 2 could not determine.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def sh(*args, check=False):
    p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError(f"{' '.join(args)}\n{p.stdout}{p.stderr}")
    return p.returncode, (p.stdout + p.stderr).strip()


def current_version():
    with open(os.path.join(ROOT, "plugins", "signal-lens", ".codex-plugin",
                           "plugin.json"), encoding="utf-8") as fh:
        return json.load(fh)["version"]


def last_tag():
    rc, out = sh("git", "describe", "--tags", "--abbrev=0")
    return out if rc == 0 else None


def checks(version):
    """Returns a list of (ok, name, detail)."""
    out = []

    rc, dirty = sh("git", "status", "--porcelain")
    out.append((not dirty, "clean tree",
                "uncommitted changes — the tag would not point at what you tested"
                if dirty else "nothing uncommitted"))

    _, branch = sh("git", "rev-parse", "--abbrev-ref", "HEAD")
    out.append((branch == "main", "on main",
                f"on {branch!r}; a tag on a branch is a version nobody can install"
                if branch != "main" else "main"))

    rc, ver = sh(sys.executable, os.path.join(HERE, "bump_version.py"), "--show")
    out.append((rc == 0, "versions agree",
                "version drift across manifests — the cache key is plugin.json, so the "
                "wrong thing ships silently" if rc else f"all at {version}"))

    rc, _ = sh(sys.executable, os.path.join(HERE, "sync_plugin.py"), "--check")
    out.append((rc == 0, "mirror in sync",
                "run scripts/sync_plugin.py — the plugin carries a different skill "
                "from the repo" if rc else "generated files match source"))

    rc, _ = sh(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q")
    out.append((rc == 0, "tests pass", "test failures" if rc else "all green"))

    tag = f"v{version}"
    rc, _ = sh("git", "rev-parse", "--verify", f"refs/tags/{tag}")
    out.append((rc != 0, "tag is free",
                f"{tag} already exists — a version means one commit, or it means nothing"
                if rc == 0 else f"{tag} is unused"))

    # The one that would have caught 1.2.0.
    prev = last_tag()
    if prev:
        rc, commits = sh("git", "log", "--oneline", f"{prev}..HEAD")
        n = len([l for l in commits.splitlines() if l.strip()])
        bumped = prev.lstrip("v") != version
        out.append((n == 0 or bumped, "version was bumped",
                    f"{n} commit(s) since {prev} and the version is still {version}. "
                    "Two different states would share one version — this is exactly how "
                    "1.2.0 shipped both a broken vocabulary check and its fix. Run "
                    "scripts/bump_version.py first"
                    if n and not bumped else
                    f"{version} is new since {prev}" if bumped else "nothing since " + prev))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--go", action="store_true", help="actually tag, push and release")
    ap.add_argument("--notes-from", default="HEAD",
                    help="commit whose message becomes the release notes (default HEAD)")
    args = ap.parse_args()

    try:
        version = current_version()
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"could not read the version: {exc}", file=sys.stderr)
        return 2

    print(f"RELEASE  signal-lens {version}\n")
    results = checks(version)
    for ok, name, detail in results:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name:<18} {detail}")
    blocked = [n for ok, n, _ in results if not ok]
    print()

    if blocked:
        print(f"REFUSED — {len(blocked)} check(s) failed: {', '.join(blocked)}")
        return 1

    if not args.go:
        print(f"Ready. Run with --go to tag v{version}, push it, and create the release.")
        return 0

    _, subject = sh("git", "log", "-1", "--format=%s", args.notes_from)
    _, body = sh("git", "log", "-1", "--format=%b", args.notes_from)
    tag = f"v{version}"

    sh("git", "tag", "-a", tag, "-m", f"signal-lens {version}", "-m", body or subject,
       check=True)
    sh("git", "push", "origin", tag, check=True)
    rc, out = sh("gh", "release", "create", tag, "--title", version, "--latest",
                 "--notes", body or subject)
    if rc:
        print(f"tag pushed, but the GitHub release failed:\n{out}")
        return 1
    print(f"released {tag}\n{out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
