"""Regression tests for the output contract.

Both fixtures are real. `plan-regression.md` is the answer the skill actually gave a user
for topmate.io — six signals in prose, where the body lists about fifteen types. It is
kept because it is the shape of the failure, and because a synthetic bad example would
have been easier to catch than the one that really happened.

`plan-good.md` is a real run after the CSV format was introduced: 38 rows.

Every rule below corresponds to a defect that shipped. None was found by an eval — all
were found by someone running the skill and reading the output.
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHECKER = os.path.join(ROOT, "evals", "check_output.py")
FIXTURES = os.path.join(HERE, "fixtures")

HEADER = ("signal,what_you_see,where,channel,why_it_matters,who_the_lead_is,"
          "strength,false_positive,detection")


def run(path, *extra):
    proc = subprocess.run([sys.executable, CHECKER, path, *extra],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def synth(tmp, rows, header=HEADER, tail="\n\nDo not use: distress posts.\n"):
    """Build a minimal conforming plan with n rows, then let callers break one thing."""
    lines = [header]
    for i in range(rows):
        lines.append(
            f"sig_{i},\"they said something specific\",post,r/example,"
            f"because the arrangement broke,the poster,strong,"
            f"looks the same but is a researcher,keyword match")
    p = os.path.join(tmp, "plan.md")
    with io.open(p, "w", encoding="utf-8") as fh:
        fh.write("```csv\n" + "\n".join(lines) + "\n```" + tail)
    return p


class RealFixtures(unittest.TestCase):
    def test_the_output_that_shipped_and_was_wrong_fails(self):
        rc, out = run(os.path.join(FIXTURES, "plan-regression.md"))
        self.assertEqual(rc, 1, out)
        self.assertIn("csv-present", out)

    def test_the_output_after_the_fix_passes(self):
        rc, out = run(os.path.join(FIXTURES, "plan-good.md"))
        self.assertEqual(rc, 0, out)

    def test_the_good_fixture_actually_enumerates(self):
        rc, out = run(os.path.join(FIXTURES, "plan-good.md"), "--json")
        self.assertGreaterEqual(json.loads(out)["rows"], 20)


class ContractRules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_a_conforming_plan_passes(self):
        rc, out = run(synth(self.tmp.name, 25))
        self.assertEqual(rc, 0, out)

    def test_summarising_below_the_floor_fails(self):
        """Six rows is what the real failure looked like."""
        rc, out = run(synth(self.tmp.name, 6))
        self.assertEqual(rc, 1, out)
        self.assertIn("row-count", out)

    def test_a_missing_required_column_fails(self):
        short = HEADER.replace(",detection", "")
        p = synth(self.tmp.name, 25, header=short)
        rc, out = run(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("detection", out)

    def test_empty_false_positive_fails(self):
        p = synth(self.tmp.name, 25)
        with open(p, encoding="utf-8") as fh:
            s = fh.read().replace("looks the same but is a researcher", "", 3)
        with io.open(p, "w", encoding="utf-8") as fh:
            fh.write(s)
        rc, out = run(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("false_positive", out)

    def test_missing_exclusions_fails(self):
        rc, out = run(synth(self.tmp.name, 25, tail="\n\nGood luck.\n"))
        self.assertEqual(rc, 1, out)
        self.assertIn("exclusions", out)

    def test_clearance_language_fails(self):
        """The skill is not in a position to clear anyone, and a seller reads
        clearance as permission."""
        p = synth(self.tmp.name, 25,
                  tail="\n\nDo not use: distress posts. Everything else is permitted.\n")
        rc, out = run(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("clearance", out)

    def test_tooling_leakage_is_flagged(self):
        p = synth(self.tmp.name, 25,
                  tail="\n\nDo not use: distress. The filter returned these in this run.\n")
        rc, out = run(p)
        self.assertIn("tooling-leakage", out)

    def test_unexplained_na_rows_are_flagged(self):
        p = synth(self.tmp.name, 25)
        with open(p, encoding="utf-8") as fh:
            s = fh.read().replace(
                'sig_0,"they said something specific",post,r/example,because the arrangement broke',
                'sig_0,n/a,post,r/example,no', 1)
        with io.open(p, "w", encoding="utf-8") as fh:
            fh.write(s)
        rc, out = run(p)
        self.assertIn("na-rows", out)

    def test_unreadable_input_is_an_error_not_a_failure(self):
        rc, out = run(os.path.join(self.tmp.name, "nope.md"))
        self.assertEqual(rc, 2, out)


if __name__ == "__main__":
    unittest.main()
