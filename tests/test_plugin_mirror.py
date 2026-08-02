"""The plugin mirror must not drift from the canonical skill.

Two install paths want different layouts: a plain `git clone` needs SKILL.md at the repo
root, a plugin marketplace needs a `skills/<name>/` directory. The root is canonical and
the mirror is generated, which means the mirror can silently go stale — and a stale mirror
ships a different skill to plugin users than the one in the README. This test is what
stops that.

It also pins the manifest shapes, because both bugs it checks for are live in a sibling
repo and were copied from there.
"""

import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NAME = "signal-lens"
MIRROR = os.path.join(ROOT, "plugins", NAME, "skills", NAME)


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return json.load(fh)


class Mirror(unittest.TestCase):
    def test_mirror_is_in_sync(self):
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "sync_plugin.py"), "--check"],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0,
                         f"run `python3 scripts/sync_plugin.py`\n{proc.stdout}{proc.stderr}")

    def test_mirror_carries_the_skill_and_nothing_else(self):
        """An installed plugin should not drag the parked catalogue, evals or tests."""
        found = set()
        for base, _, files in os.walk(MIRROR):
            for fn in files:
                found.add(os.path.relpath(os.path.join(base, fn), MIRROR))
        self.assertIn("SKILL.md", found)
        self.assertTrue(any(f.startswith("references") for f in found))
        for unwanted in ("data", "evals", "tests", "docs", "scripts"):
            self.assertFalse(
                any(f.startswith(unwanted) for f in found),
                f"{unwanted}/ leaked into the plugin mirror")

    def test_mirror_is_small(self):
        """A guard on the 862KB parked catalogue reappearing by accident."""
        total = sum(os.path.getsize(os.path.join(b, f))
                    for b, _, fs in os.walk(MIRROR) for f in fs)
        self.assertLess(total, 200_000, f"mirror is {total} bytes — something large got in")


class Manifests(unittest.TestCase):
    def test_marketplace_points_at_the_plugin_directory(self):
        mk = load(".claude-plugin", "marketplace.json")
        plugin = mk["plugins"][0]
        self.assertEqual(plugin["name"], NAME)
        self.assertEqual(plugin["source"], f"./plugins/{NAME}")
        self.assertTrue(os.path.isdir(os.path.join(ROOT, "plugins", NAME)))

    def test_agents_marketplace_uses_local_source_not_url(self):
        """repo-lens ships {"source":"url","url":"./plugins/..."}. `url` is for remote git
        URLs; a relative path under it is not a documented combination."""
        src = load(".agents", "plugins", "marketplace.json")["plugins"][0]["source"]
        self.assertEqual(src["source"], "local")
        self.assertIn("path", src)
        self.assertNotIn("url", src)

    def test_authentication_is_on_use_not_on_install(self):
        """This skill needs no credential at install time; ON_INSTALL prompts for one."""
        policy = load(".agents", "plugins", "marketplace.json")["plugins"][0]["policy"]
        self.assertEqual(policy["authentication"], "ON_USE")

    def test_plugin_manifests_point_at_the_skills_directory(self):
        for parts in ((".claude-plugin",), (".codex-plugin",)):
            manifest = load("plugins", NAME, *parts, "plugin.json")
            self.assertEqual(manifest["name"], NAME)
            self.assertTrue(manifest["skills"].rstrip("/").endswith("skills"),
                            f"{parts[0]} does not point at ./skills")

    def test_versions_agree_across_manifests_and_the_skill(self):
        versions = {
            "marketplace": load(".claude-plugin", "marketplace.json")["plugins"][0]["version"],
            "claude-plugin": load("plugins", NAME, ".claude-plugin", "plugin.json")["version"],
            "codex-plugin": load("plugins", NAME, ".codex-plugin", "plugin.json")["version"],
        }
        with open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8") as fh:
            head = fh.read(2000)
        for line in head.splitlines():
            if line.strip().startswith("version:"):
                versions["SKILL.md"] = line.split(":", 1)[1].strip().strip('"')
                break
        self.assertEqual(len(set(versions.values())), 1,
                         f"version drift across manifests: {versions}")


if __name__ == "__main__":
    unittest.main()
