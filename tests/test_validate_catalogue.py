"""Adversarial tests for the catalogue contract.

Every test here corresponds to a real defect that shipped and was caught in review.
The point is not coverage for its own sake: it is that the publication-blocking rules
are the ones most likely to be quietly weakened by a future edit, and a rule nobody
tests is a rule that works until someone touches it.

Run: python3 -m unittest discover -s tests -v
Stdlib only, no dependencies.
"""

import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VALIDATOR = os.path.join(REPO, "scripts", "validate_catalogue.py")
FAMILIES = os.path.join(REPO, "data", "families")


def run(path, *extra):
    proc = subprocess.run(
        [sys.executable, VALIDATOR, path, *extra],
        capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def write_shard(tmpdir, name, signals):
    p = os.path.join(tmpdir, f"{name}.json")
    with io.open(p, "w", encoding="utf-8") as fh:
        json.dump({"shard": name, "catalogue_version": "0.1.0",
                   "as_of": "2026-08-01", "signals": signals}, fh, indent=2)
    return p


def load_entry(shard, entry_id):
    with open(os.path.join(FAMILIES, f"{shard}.json"), encoding="utf-8") as fh:
        for s in json.load(fh)["signals"]:
            if s["id"] == entry_id:
                return copy.deepcopy(s)
    raise LookupError(f"{entry_id} not in {shard}")


class ShippedCatalogue(unittest.TestCase):
    """The catalogue as committed must pass its own contract."""

    def test_full_catalogue_passes(self):
        rc, out = run(FAMILIES)
        self.assertEqual(rc, 0, out)
        self.assertIn("PASS", out)

    def test_every_family_is_populated(self):
        rc, out = run(FAMILIES)
        self.assertNotIn("EMPTY", out, "a family lost all its entries")
        self.assertNotIn("thin ", out, "a family fell below the spec's enumeration")

    def test_unevidenced_percentage_is_a_percentage(self):
        """It once printed 3200% on a restricted-only shard."""
        for target in (FAMILIES, os.path.join(FAMILIES, "restricted.json")):
            args = () if target == FAMILIES else ("--shard-only",)
            rc, out = run(target, *args)
            line = [l for l in out.splitlines() if "UNEVIDENCED" in l][0]
            pct = float(line.split(":")[1].strip().split("%")[0])
            self.assertGreaterEqual(pct, 0.0, line)
            self.assertLessEqual(pct, 100.0, line)


class RestrictedEntriesShipNoRecipe(unittest.TestCase):
    """Publication blocker: a prohibition must never carry an implementation path."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.prohibition = load_entry("restricted", "restricted.health_status_inference")

    def test_denied_field_on_restricted_entry_fails(self):
        bad = self.prohibition
        bad["capability_ladder"] = [{"rung": 1, "how": "join pageviews to the loyalty id"}]
        p = write_shard(self.tmp.name, "restricted", [bad])
        rc, out = run(p, "--shard-only")
        self.assertEqual(rc, 1, out)
        self.assertIn("capability_ladder", out)

    def test_off_schema_key_on_restricted_entry_fails(self):
        """The rule is an allow-list; a deny-list only blocks names thought of first."""
        bad = self.prohibition
        bad["detection_recipe"] = {"step1": "join the SKU list to the loyalty id"}
        bad["how_to_build"] = "score condition from basket contents"
        p = write_shard(self.tmp.name, "restricted", [bad])
        rc, out = run(p, "--shard-only")
        self.assertEqual(rc, 1, out)
        self.assertIn("detection_recipe", out)
        self.assertIn("how_to_build", out)

    def test_relabelling_does_not_smuggle_a_build_path(self):
        """sensitivity/availability are author-chosen, so semantics must also be checked."""
        bad = self.prohibition
        bad["id"] = "f12.clinical_journey_stage"
        bad["sensitivity"] = "high"
        bad["availability"] = "integration"
        bad.pop("prohibition_basis", None)
        bad["required_raw_fields"] = ["subject_id", "page_path", "timestamp"]
        bad["capability_ladder"] = [{"rung": 1, "how": "score journey stage from pageviews"}]
        p = write_shard(self.tmp.name, "F12", [bad])
        rc, out = run(p, "--shard-only")
        self.assertEqual(rc, 1, out)
        self.assertIn("prohibited class", out)

    def test_restricted_id_with_soft_facets_is_rejected(self):
        """A 'restricted.' id used to be classified buildable, which inverted the rule:
        the else-branch then DEMANDED the prohibition ship a capability ladder."""
        bad = self.prohibition
        bad["sensitivity"] = "high"
        bad["availability"] = "integration"
        p = write_shard(self.tmp.name, "restricted", [bad])
        rc, out = run(p, "--shard-only")
        self.assertEqual(rc, 1, out)
        self.assertIn("consistently", out)
        self.assertNotIn("must state the minimum fields needed", out,
                         "a prohibition was asked to supply required_raw_fields")


class LegalFacetsCannotBeOmitted(unittest.TestCase):
    """An absent legal block used to degrade to {} and buy silent clearance."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.entry = load_entry("F04", "f04.product_comparison")

    def test_missing_legal_block_fails(self):
        bad = self.entry
        bad.pop("legal")
        p = write_shard(self.tmp.name, "F04", [bad])
        rc, out = run(p, "--shard-only")
        self.assertEqual(rc, 1, out)
        self.assertIn("legal", out)

    def test_empty_legal_block_fails(self):
        bad = self.entry
        bad["legal"] = {}
        p = write_shard(self.tmp.name, "F04", [bad])
        rc, out = run(p, "--shard-only")
        self.assertEqual(rc, 1, out)

    def test_honest_entry_is_not_penalised_relative_to_silent_one(self):
        """The regression: declaring facets honestly failed while omitting them passed."""
        silent = copy.deepcopy(self.entry)
        silent.pop("legal")
        honest = copy.deepcopy(self.entry)
        honest["legal"]["terminal_equipment_access"] = True
        honest["permission_requirement"] = "notice"
        rc_silent, _ = run(write_shard(self.tmp.name, "a", [silent]), "--shard-only")
        rc_honest, _ = run(write_shard(self.tmp.name, "b", [honest]), "--shard-only")
        self.assertEqual(rc_silent, 1, "omitting the legal block must not pass")
        self.assertEqual(rc_honest, 0, "an honestly-declared entry must pass")


class PermissionCoherence(unittest.TestCase):
    """availability answers 'can it be obtained'; permission answers 'may it be'."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.entry = load_entry("F04", "f04.product_comparison")

    def _run_with(self, **patch):
        bad = copy.deepcopy(self.entry)
        legal = patch.pop("legal", {})
        bad.update(patch)
        bad["legal"].update(legal)
        return run(write_shard(self.tmp.name, "F04", [bad]), "--shard-only")

    def test_device_access_cannot_claim_no_permission(self):
        rc, out = self._run_with(permission_requirement="none",
                                 legal={"terminal_equipment_access": True})
        self.assertEqual(rc, 1, out)
        self.assertIn("terminal_equipment_access", out)

    def test_person_level_resolution_cannot_claim_no_permission(self):
        rc, out = self._run_with(permission_requirement="none",
                                 legal={"terminal_equipment_access": False,
                                        "person_level_resolution": True})
        self.assertEqual(rc, 1, out)
        self.assertIn("person_level_resolution", out)

    def test_free_does_not_imply_lawful(self):
        rc, out = self._run_with(availability="public_cost_free",
                                 permission_requirement="none",
                                 legal={"terminal_equipment_access": False,
                                        "person_level_resolution": True})
        self.assertEqual(rc, 1, out)


class ScalarAndReferenceIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.entry = load_entry("F04", "f04.product_comparison")

    def test_boolean_is_not_an_integer_score(self):
        """isinstance(True, int) is True, so `strength: true` silently meant 1."""
        bad = self.entry
        bad["strength"] = True
        p = write_shard(self.tmp.name, "F04", [bad])
        rc, out = run(p, "--shard-only")
        self.assertEqual(rc, 1, out)
        self.assertIn("strength", out)

    def test_duplicate_ids_are_caught_in_shard_only_mode(self):
        """Duplicates are shard-local, and --shard-only is the per-family workflow."""
        p = write_shard(self.tmp.name, "F04",
                        [self.entry, copy.deepcopy(self.entry)])
        rc, out = run(p, "--shard-only")
        self.assertEqual(rc, 1, out)
        self.assertIn("duplicate", out.lower())

    def test_buildable_entry_cannot_cite_a_prohibition_as_corroboration(self):
        buildable = self.entry
        buildable["confirmation_signals"] = ["restricted.health_status_inference"]
        prohibition = load_entry("restricted", "restricted.health_status_inference")
        p = write_shard(self.tmp.name, "mixed", [buildable, prohibition])
        rc, out = run(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("do-not-collect", out)


if __name__ == "__main__":
    unittest.main()
