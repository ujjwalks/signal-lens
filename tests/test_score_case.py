"""Tests for the evaluation scorer.

The scorer's job is to be harder to fool than a human skimming a plan. These tests
pin the two properties that matter: recalling only the obvious signals must not look
like a good score, and recommending an excluded signal must fail outright rather than
cost points.
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCORER = os.path.join(REPO, "evals", "score_case.py")

CASE = {
    "case_id": "unit-durable",
    "company": "Test Durable Co",
    "must_include_signals": [
        {"id": "f04.product_comparison", "why": "shortlisting", "how_obvious": "obvious"},
        {"id": "f06.quote_request", "why": "priced enquiry", "how_obvious": "earned"},
        {"id": "f12.declared_relocation", "why": "the strongest trigger", "how_obvious": "hard"},
        {"id": "f14.household_coordination", "why": "two-person decision", "how_obvious": "hard"},
    ],
    "must_exclude_signals": [
        {"id": "f11.replenishment_due", "why": "durables are not consumables",
         "failure_mode": "treating a durable retailer as a subscription box"},
    ],
    "must_flag_restricted": [
        {"id": "restricted.household_composition_inference", "why": "inferring children"},
    ],
    "families_expected": ["F04", "F06", "F12", "F14"],
}


def write(tmp, name, payload):
    p = os.path.join(tmp, name)
    with io.open(p, "w", encoding="utf-8") as fh:
        fh.write(payload if isinstance(payload, str) else json.dumps(payload))
    return p


def run(case_path, plan_path, *extra):
    proc = subprocess.run([sys.executable, SCORER, case_path, plan_path, *extra],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


class Scoring(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.case = write(self.tmp.name, "case.json", CASE)

    def _json_score(self, plan):
        p = write(self.tmp.name, "plan.json", plan)
        rc, out = run(self.case, p, "--json")
        return rc, json.loads(out)

    def test_obvious_only_answer_scores_far_below_its_raw_hit_rate(self):
        """The whole point of the weighting: naming what the baseline already names
        must not look like success."""
        rc, r = self._json_score({"signals": ["f04.product_comparison"]})
        self.assertEqual(r["unweighted_recall"], 25.0)
        self.assertLess(r["weighted_recall"], r["unweighted_recall"])
        self.assertAlmostEqual(r["weighted_recall"], 11.1, places=1)

    def test_hard_signals_carry_the_score(self):
        rc, r = self._json_score({"signals": ["f12.declared_relocation",
                                              "f14.household_coordination"]})
        self.assertEqual(r["unweighted_recall"], 50.0)
        self.assertGreater(r["weighted_recall"], r["unweighted_recall"])

    def test_excluded_signal_fails_outright(self):
        """Not a deduction. A customer would act on this."""
        rc, r = self._json_score({"signals": [
            "f04.product_comparison", "f06.quote_request",
            "f12.declared_relocation", "f14.household_coordination",
            "f11.replenishment_due"]})
        self.assertEqual(rc, 1)
        self.assertFalse(r["passed"])
        self.assertEqual(r["weighted_recall"], 100.0,
                         "recall is still perfect - the failure is separate from the score")
        self.assertEqual(len(r["exclusion_violations"]), 1)

    def test_unsurfaced_prohibition_is_reported(self):
        rc, r = self._json_score({"signals": ["f04.product_comparison"]})
        self.assertEqual([x["id"] for x in r["restricted_not_named"]],
                         ["restricted.household_composition_inference"])

    def test_prose_plans_are_scorable(self):
        """Early evaluation is 'run the skill, save what it said'."""
        p = write(self.tmp.name, "plan.md",
                  "We recommend f04.product_comparison and f12.declared_relocation. "
                  "Families: F04, F12.")
        rc, out = run(self.case, p)
        self.assertEqual(rc, 0, out)
        self.assertIn("prose", out)
        self.assertIn("F06", out, "missing families should be named")

    def test_empty_plan_is_an_error_not_a_zero(self):
        """A plan with no ids means the harness broke, which must not read as 0%."""
        p = write(self.tmp.name, "plan.md", "No signals were identified.")
        rc, out = run(self.case, p)
        self.assertEqual(rc, 2, out)
        self.assertIn("CANNOT SCORE", out)


if __name__ == "__main__":
    unittest.main()
