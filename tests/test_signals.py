"""Tests for the phase 2 detection-spec contract.

The specs are synthetic here, unlike the phase 1 fixtures. There is no real phase 2 run
to keep yet, and inventing one and calling it real is worse than saying so.

The rules under test all exist because of something already learned in this repo: a
model asserting a strength is unfalsifiable, a bare platform name is not a place anyone
can look, a signal without a named lookalike was never stress-tested, and a state
comparison without a stored baseline is a reading rather than a signal.
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
ROOT = os.path.dirname(HERE)
VALIDATOR = os.path.join(ROOT, "scripts", "validate_signals.py")
PROFILE = os.path.join(HERE, "fixtures", "profile-good.json")


def run(path, *extra):
    p = subprocess.run([sys.executable, VALIDATOR, path, *extra],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def one(name, **kw):
    d = {
        "signal": name,
        "surface": ["r/Accounting"],
        "observable": "post_body",
        "method": "keyword",
        "query": {"any_of": ["consolidating six files"], "near": ["Fathom"]},
        "must_also_have": {"count_of": "legal entities", "date_from_text": False,
                           "demand_side": True},
        "disqualifiers": ["a ProAdvisor answering on someone else's behalf"],
        "baseline": {"required": False},
        "freshness_days": 45,
        "yields": {"entity": "the poster's employer", "contactable": "sometimes"},
        "rank": {"stage": 2, "evidence_density": 2, "separability": 2, "reach": 0},
    }
    d.update(kw)
    return d


def doc(signals=None, n=20):
    sigs = list(signals or [])
    sigs += [one(f"filler {i}") for i in range(max(0, n - len(sigs)))]
    return {"domain": "finboard.ai", "signals": sigs}


class Contract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, d):
        p = os.path.join(self.tmp.name, "s.json")
        with io.open(p, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(d))
        return p

    def check(self, d, *extra):
        return run(self.write(d), *extra)

    def test_a_conforming_set_validates(self):
        rc, out = self.check(doc())
        self.assertEqual(rc, 0, out)

    def test_the_twenty_floor_carries_over_from_phase_1(self):
        """Phase 2 cannot recover a signal phase 1 failed to list, so the floor holds."""
        rc, out = self.check(doc(n=6))
        self.assertEqual(rc, 1, out)

    def test_a_bare_platform_is_not_a_surface(self):
        rc, out = self.check(doc([one("named signal", surface=["LinkedIn"])]))
        self.assertEqual(rc, 1, out)
        self.assertIn("platform, not a surface", out)

    def test_state_diff_without_a_baseline_is_rejected(self):
        rc, out = self.check(doc([one("named signal", method="state_diff",
                                      baseline={"required": False})]))
        self.assertEqual(rc, 1, out)
        self.assertIn("baseline", out)

    def test_none_known_needs_a_reason(self):
        rc, out = self.check(doc([one("named signal", method="none_known", observable="none",
                                      query=None)]))
        self.assertEqual(rc, 1, out)
        self.assertIn("unspecifiable_because", out)

    def test_none_known_with_a_reason_is_kept_not_dropped(self):
        """The whole point: an undetectable signal stays in the set."""
        s = one("no public trace", method="none_known", observable="none",
                unspecifiable_because="leaves no public trace until the close slips",
                disqualifiers=[],
                # nothing is detected, so nothing is required: density must be 0
                rank={"stage": 3, "evidence_density": 0, "separability": 0, "reach": 0})
        s.pop("query")
        rc, out = self.check(doc([s]))
        self.assertEqual(rc, 0, out)
        rc, out = self.check(doc([s]), "--json")
        self.assertEqual(len(json.loads(out)["ranked"]), 20)

    def test_a_method_with_no_query_is_rejected(self):
        s = one("named signal")
        s.pop("query")
        rc, out = self.check(doc([s]))
        self.assertEqual(rc, 1, out)

    def test_duplicate_signal_names_are_rejected(self):
        rc, out = self.check(doc([one("same"), one("same")]))
        self.assertEqual(rc, 1, out)
        self.assertIn("duplicate", out)

    def test_an_empty_disqualifier_list_warns(self):
        rc, out = self.check(doc([one("named signal", disqualifiers=[])]))
        self.assertEqual(rc, 0, out)
        self.assertIn("precision is unknown", out)


class Ranking(unittest.TestCase):
    """The rank is derived from stated components so it cannot be asserted."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, d):
        p = os.path.join(self.tmp.name, "r.json")
        with io.open(p, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(d))
        return p

    def test_the_score_is_deterministic(self):
        d = doc()
        a = run(self.write(d), "--json")[1]
        b = run(self.write(copy.deepcopy(d)), "--json")[1]
        self.assertEqual(json.loads(a)["ranked"], json.loads(b)["ranked"])

    def test_later_stage_outranks_earlier_all_else_equal(self):
        late = one("quote in hand", rank={"stage": 4, "evidence_density": 2,
                                          "separability": 2, "reach": 0})
        early = one("vaguely annoyed", rank={"stage": 0, "evidence_density": 2,
                                             "separability": 2, "reach": 0})
        rc, out = run(self.write(doc([late, early])), "--json")
        order = [r["signal"] for r in json.loads(out)["ranked"]]
        self.assertLess(order.index("quote in hand"), order.index("vaguely annoyed"))

    def test_an_inflated_component_is_rejected(self):
        """Claiming evidence_density 3 when the spec requires one thing is how a rank
        becomes an assertion again."""
        s = one("named signal", rank={"stage": 2, "evidence_density": 3, "separability": 2,
                           "reach": 0},
                must_also_have={"count_of": "legal entities", "date_from_text": False,
                                "demand_side": True},
                query={"any_of": ["something"]})
        rc, out = run(self.write(doc([s])))
        self.assertEqual(rc, 1, out)
        self.assertIn("evidence_density", out)

    def test_undetectable_signals_are_ranked_and_flagged(self):
        s = one("high value, no method", method="none_known", observable="none",
                unspecifiable_because="no public trace exists",
                disqualifiers=[],
                rank={"stage": 4, "evidence_density": 0, "separability": 0, "reach": 0})
        s.pop("query")
        rc, out = run(self.write(doc([s])), "--ranked")
        self.assertEqual(rc, 0, out)
        self.assertIn("argument for what to build next", out)

    def test_the_ranking_output_states_it_is_not_backtested(self):
        rc, out = run(self.write(doc()), "--ranked")
        self.assertIn("backtested", out)


class CrossChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_counting_the_wrong_noun_warns_against_the_profile(self):
        s = one("named signal", must_also_have={"count_of": "employees", "date_from_text": False,
                                     "demand_side": True})
        p = os.path.join(self.tmp.name, "c.json")
        with io.open(p, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(doc([s])))
        rc, out = run(p, "--profile", PROFILE)
        self.assertIn("severity noun", out)


if __name__ == "__main__":
    unittest.main()
