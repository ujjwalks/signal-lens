"""Tests for the step 1 profile contract.

`profile-untranslated.json` is the case the validator exists for: every field present,
nothing obviously wrong on a read-through, and the buyer vocabulary is the seller's own
words rearranged. A profile like that produces searches that return the company's own
marketing and no buyer at all, and it looks fine until you read the finished plan.
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
VALIDATOR = os.path.join(ROOT, "scripts", "validate_profile.py")
GOOD = os.path.join(HERE, "fixtures", "profile-good.json")
BAD = os.path.join(HERE, "fixtures", "profile-untranslated.json")


def run(path, *extra):
    p = subprocess.run([sys.executable, VALIDATOR, path, *extra],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


class Fixtures(unittest.TestCase):
    def test_a_real_profile_validates(self):
        rc, out = run(GOOD)
        self.assertEqual(rc, 0, out)

    def test_the_untranslated_profile_is_rejected(self):
        rc, out = run(BAD)
        self.assertEqual(rc, 1, out)

    def test_it_names_the_vocabulary_failure_specifically(self):
        """The whole point. A generic 'invalid profile' would not tell anyone what to fix."""
        _, out = run(BAD)
        self.assertIn("buyer_language", out)
        self.assertIn("seller_language", out)

    def test_questions_mode_prints_the_unresolved_questions(self):
        rc, out = run(GOOD, "--questions")
        self.assertEqual(rc, 0)
        self.assertIn("?", out)

    def test_json_mode_is_machine_readable(self):
        rc, out = run(GOOD, "--json")
        self.assertEqual(rc, 0)
        self.assertTrue(json.loads(out)["valid"])


class Rules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = load(GOOD)

    def write(self, profile):
        p = os.path.join(self.tmp.name, "p.json")
        with io.open(p, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(profile))
        return p

    def mutate(self, fn):
        p = copy.deepcopy(self.base)
        fn(p)
        return run(self.write(p))

    def test_buyer_language_echoing_the_seller_fails(self):
        def break_it(p):
            p["artifacts"]["vocabulary"]["buyer_language"] = \
                p["artifacts"]["vocabulary"]["seller_language"] + ["multi-entity consolidation tool"]
        rc, out = self.mutate(break_it)
        self.assertEqual(rc, 1, out)
        self.assertIn("rearranged", out)

    def test_an_uncountable_severity_noun_fails(self):
        rc, out = self.mutate(lambda p: p["artifacts"]["severity_noun"].update({"noun": "complexity"}))
        self.assertEqual(rc, 1, out)
        self.assertIn("not countable", out)

    def test_a_countable_noun_passes(self):
        rc, out = self.mutate(lambda p: p["artifacts"]["severity_noun"].update({"noun": "locations"}))
        self.assertEqual(rc, 0, out)

    def test_a_workaround_without_a_failure_condition_fails(self):
        rc, out = self.mutate(lambda p: p["artifacts"]["workarounds"][0].update({"fails_when": ""}))
        self.assertEqual(rc, 1, out)
        self.assertIn("fails_when", out)

    def test_an_empty_third_competitor_tier_fails(self):
        rc, out = self.mutate(lambda p: p["artifacts"]["competitors"].update({"the_person_they_pay": []}))
        self.assertEqual(rc, 1, out)
        self.assertIn("the_person_they_pay", out)

    def test_an_empty_prohibited_bridge_is_valid_but_a_missing_one_is_not(self):
        """Considered-and-empty is a real answer. Absent means nobody asked."""
        rc, _ = self.mutate(lambda p: p["artifacts"].update({"prohibited_bridge": []}))
        self.assertEqual(rc, 0)
        rc, out = self.mutate(lambda p: p["artifacts"].pop("prohibited_bridge"))
        self.assertEqual(rc, 1, out)

    def test_each_defect_is_reported_once(self):
        """Structural and semantic layers both fire on the same field; the reader should
        see one problem, not three."""
        rc, out = self.mutate(lambda p: p["artifacts"]["workarounds"][0].update({"fails_when": ""}))
        self.assertEqual(out.count("artifacts.workarounds[0].fails_when"), 1, out)

    def test_a_missing_file_is_an_error_not_an_invalid_profile(self):
        rc, out = run(os.path.join(self.tmp.name, "nope.json"))
        self.assertEqual(rc, 2, out)

    def test_malformed_json_is_an_error_not_an_invalid_profile(self):
        p = os.path.join(self.tmp.name, "bad.json")
        with io.open(p, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        rc, out = run(p)
        self.assertEqual(rc, 2, out)



class VocabularyCheckCalibration(unittest.TestCase):
    """The check that matters most, and the two ways it can be wrong.

    It shipped defeated by a single filler word: `reverse ETL` was caught but
    `looking for a reverse ETL tool` was not, and the second is what actually gets
    written when the translation is skipped. Overcorrecting is the opposite risk —
    step 1 says explicitly that some markets have fluent buyers whose vocabulary
    legitimately overlaps the seller's, and rejecting those would contradict it.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = load(GOOD)

    def run_with_vocab(self, seller, buyer):
        p = copy.deepcopy(self.base)
        p["artifacts"]["vocabulary"]["seller_language"] = seller
        p["artifacts"]["vocabulary"]["buyer_language"] = buyer
        f = os.path.join(self.tmp.name, "v.json")
        with io.open(f, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(p))
        return run(f)

    SELLER = ["composable CDP", "data activation", "reverse ETL",
              "audience orchestration", "agentic marketing platform"]

    def test_seller_vocabulary_with_filler_is_rejected(self):
        rc, out = self.run_with_vocab(self.SELLER, [
            "looking for a reverse ETL tool",
            "best data activation platform",
            "composable CDP vs traditional CDP",
            "audience orchestration tools",
            "how to do data activation",
            "reverse ETL pricing",
        ])
        self.assertEqual(rc, 1, f"filler words defeated the check again\n{out}")

    def test_genuine_buyer_language_is_accepted(self):
        rc, out = self.run_with_vocab(self.SELLER, [
            "getting our warehouse data into facebook ads",
            "the python script that pushes to braze keeps breaking",
            "exporting a csv every week just to upload it again",
            "how do people sync snowflake to hubspot",
            "our segment bill got insane after we grew",
            "audiences are always stale by the time the campaign goes out",
        ])
        self.assertEqual(rc, 0, out)

    def test_a_fluent_buyer_market_is_not_rejected(self):
        """Immigration: applicants use the same procedural vocabulary as the firm.
        Step 1 says to translate posture instead, and calls this legitimate."""
        rc, out = self.run_with_vocab(
            ["EB-2 NIW petition", "RFE response", "priority date retrogression",
             "I-140 filing", "premium processing"],
            ["got an RFE on prong 2, is this normal",
             "my priority date retrogressed again",
             "is premium processing worth it for I-140",
             "am I being farmed by my attorney",
             "talk me out of refiling the NIW petition",
             "attorney wants $8k for the RFE response"])
        self.assertEqual(rc, 0, f"overcorrected — fluent-buyer markets are legitimate\n{out}")

class UnansweredPrice(unittest.TestCase):
    """Mister O1: the menus are per-location PDFs and the ordering sits behind a
    platform, so nothing on the site is a price. The skill recorded "not stated" and
    carried on, which is a skipped field wearing the costume of an answer. Price
    calibrates the severity noun and sets the ceiling the buyer already pays, so a
    non-answer is only acceptable when somebody wrote down the question."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = load(GOOD)

    def build(self, band, unresolved):
        p = copy.deepcopy(self.base)
        p["seller"]["price_band"] = band
        p["unresolved"] = unresolved
        f = os.path.join(self.tmp.name, "pb.json")
        with io.open(f, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(p))
        return run(f)

    ASKED = [{"field": "seller.price_band",
              "question": "What does a typical account pay? The menus are per-location PDFs.",
              "why_it_matters": "decides whether a signal is worth a human's time"}]

    def test_a_shrug_with_no_question_is_rejected(self):
        for band in ("not stated", "unknown", "n/a", "", "TBD", "not disclosed"):
            rc, out = self.build(band, [])
            self.assertEqual(rc, 1, f"{band!r} passed unchallenged\n{out}")

    def test_the_same_gap_with_the_question_recorded_passes(self):
        rc, out = self.build("not stated", self.ASKED)
        self.assertEqual(rc, 0, out)

    def test_the_message_names_where_price_actually_hides(self):
        """A bare 'missing price' would not tell anyone what to go and do."""
        _, out = self.build("not stated", [])
        for hint in ("PDF", "Toast", "competitors"):
            self.assertIn(hint, out)

    def test_a_real_price_band_needs_no_question(self):
        rc, out = self.build("mid four figures per year", [])
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main()


class NamedCompetitors(unittest.TestCase):
    """A real finboard.ai profile filled competitors.direct with category nouns —
    "Generic BI tools", "generic FP&A tools", "multi-entity consolidation software;
    exact named products were not established from the website" — and the 35-row plan
    built on it lost SIX signals. Every competitor-watching row came back n/a, because
    there is no changelog to poll, no pricing page to diff and no reviews to read for
    a category.

    The field looked filled in, so nothing flagged it, and the loss only showed up as
    six weak rows a reader would skim past.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = load(GOOD)

    def build(self, direct, unresolved=None):
        p = copy.deepcopy(self.base)
        p["artifacts"]["competitors"]["direct"] = direct
        if unresolved is not None:
            p["unresolved"] = unresolved
        f = os.path.join(self.tmp.name, "c.json")
        with io.open(f, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(p))
        return run(f)

    ASKED = [{"field": "artifacts.competitors.direct",
              "question": "Which named products do you actually lose deals to?",
              "why_it_matters": "an unnamed competitor set kills a whole signal group"}]

    def test_named_products_pass(self):
        rc, out = self.build(["Fathom", "LiveFlow", "Cube", "Vena"])
        self.assertEqual(rc, 0, out)

    def test_the_real_category_nouns_are_rejected(self):
        rc, out = self.build([
            "Generic BI tools", "generic FP&A tools",
            "multi-entity consolidation software; exact named products were not "
            "established from the website."])
        self.assertEqual(rc, 1, out)
        self.assertIn("competitors.direct", out)

    def test_one_real_name_among_categories_is_enough(self):
        """The check is 'did you find any', not 'is every entry perfect'."""
        rc, out = self.build(["Generic BI tools", "Fathom"])
        self.assertEqual(rc, 0, out)

    def test_recording_the_question_downgrades_it_to_a_warning(self):
        """Same rule as price_band: an honest gap you asked about is not a defect."""
        rc, out = self.build(["Generic BI tools"], unresolved=self.ASKED)
        self.assertEqual(rc, 0, out)
        self.assertIn("competitors.direct", out)

    def test_the_message_says_where_to_look(self):
        _, out = self.build(["various tools"])
        for hint in ("/compare", "alternatives", "switched from"):
            self.assertIn(hint, out)
