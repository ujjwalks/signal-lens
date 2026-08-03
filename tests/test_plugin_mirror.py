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
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NAME = "signal-lens"
MIRROR = os.path.join(ROOT, "plugins", NAME, "skills", NAME)


def _sync_plugin():
    """Import sync_plugin.py so the allowlist has exactly one definition."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "sync_plugin", os.path.join(ROOT, "scripts", "sync_plugin.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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

    def _mirror_files(self):
        found = set()
        for base, _, files in os.walk(MIRROR):
            for fn in files:
                found.add(os.path.relpath(os.path.join(base, fn), MIRROR))
        return found

    def test_mirror_carries_the_skill_and_nothing_else(self):
        """An installed plugin should not drag the parked catalogue, evals or tests."""
        found = self._mirror_files()
        self.assertIn("SKILL.md", found)
        self.assertTrue(any(f.startswith("references") for f in found))
        for unwanted in ("data", "evals", "tests", "docs"):
            self.assertFalse(
                any(f.startswith(unwanted) for f in found),
                f"{unwanted}/ leaked into the plugin mirror")

    def test_the_output_check_ships_to_the_agent(self):
        """SKILL.md step 7 runs this. A body that points at a script the install does
        not carry fails at the only moment it matters, and fails silently."""
        found = self._mirror_files()
        self.assertIn(os.path.join("scripts", "check_output.py"), found,
                      "step 7 invokes scripts/check_output.py but it is not in the mirror")

    def test_mirror_scripts_match_the_allowlist_exactly(self):
        """Nothing reaches an install except via SCRIPTS in sync_plugin.py."""
        allowed = {os.path.join("scripts", n) for n in _sync_plugin().SCRIPTS}
        shipped = {f for f in self._mirror_files() if f.startswith("scripts" + os.sep)}
        self.assertEqual(shipped, allowed,
                         "scripts/ in the mirror drifted from the sync_plugin allowlist")

    def test_repo_machinery_is_not_on_the_allowlist(self):
        """The allowlist is only a guard if someone cannot quietly widen it. Version
        bumping, the mirror sync and the parked catalogue validator are build tooling;
        an install has no use for any of them."""
        for name in ("bump_version.py", "sync_plugin.py", "validate_catalogue.py"):
            self.assertNotIn(name, _sync_plugin().SCRIPTS,
                             f"{name} is repo machinery and must not ship to users")

    def test_every_script_the_skill_invokes_is_shipped(self):
        """Scans SKILL.md *and* every reference, because the steps moved into
        references/ and that is where invocations now live. A body — or a step file —
        pointing at a script the install lacks fails at the only moment it matters,
        and fails silently."""
        sources = {"SKILL.md": os.path.join(ROOT, "SKILL.md")}
        ref_dir = os.path.join(ROOT, "references")
        for fn in sorted(os.listdir(ref_dir)):
            if fn.endswith(".md"):
                sources[f"references/{fn}"] = os.path.join(ref_dir, fn)

        shipped = self._mirror_files()
        invoked_anywhere = set()
        for label, path in sources.items():
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            # The trailing guard matters: without it `.js` matches inside `.json`, and
            # the test demands a `profile_schema.js` that was never meant to exist.
            pattern = r"scripts/([A-Za-z0-9_]+\.(?:py|sh|js))(?![A-Za-z0-9])"
            for name in sorted(set(re.findall(pattern, text))):
                invoked_anywhere.add(name)
                self.assertIn(os.path.join("scripts", name), shipped,
                              f"{label} invokes scripts/{name}, which the mirror lacks")
        self.assertTrue(invoked_anywhere,
                        "no script is invoked anywhere — the deterministic checks are unreachable")

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

    def test_versions_agree_across_manifests(self):
        versions = {
            "marketplace": load(".claude-plugin", "marketplace.json")["plugins"][0]["version"],
            "claude-plugin": load("plugins", NAME, ".claude-plugin", "plugin.json")["version"],
            "codex-plugin": load("plugins", NAME, ".codex-plugin", "plugin.json")["version"],
        }
        self.assertEqual(len(set(versions.values())), 1,
                         f"version drift across manifests: {versions}")

    def test_skill_frontmatter_carries_no_version(self):
        """The cache key comes from plugin.json. Measured on a real machine: 18 of 19
        cached plugins have no `metadata.version` and all resolve correctly. A copy here
        is a fourth thing to keep in sync that nothing reads."""
        with open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8") as fh:
            head = fh.read(2000)
        fm = head.split("---")[1] if head.count("---") >= 2 else head
        self.assertNotIn("version:", fm,
                         "SKILL.md frontmatter has re-grown a version field")


if __name__ == "__main__":
    unittest.main()
