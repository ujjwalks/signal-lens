"""Step 1 carries two kinds of prose, and only one of them is load-bearing.

Most of what it used to say restated a rule `validate_profile.py` already refuses:
untranslated vocabulary, an uncountable severity noun, a workaround with no failure
condition, an empty third competitor tier, category-noun competitors, an unanswered
price, an absent prohibited_bridge, an unaskable question. All eight are deterministic
errors. Explaining them in prose as well is the delta rule's exact target — the model
does not need telling, because it will be stopped.

What remains is the part nothing else carries: things that are non-obvious AND cannot
be enforced, so if the prose goes, they go. This file exists because the next person
shortening step 1 will not be able to tell those two categories apart by reading, and
these four are exactly what a shortening pass deletes.
"""

import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STEP1 = os.path.join(ROOT, "references", "step-1-profile.md")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_profile.py")


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


class NonEnforceableDeltas(unittest.TestCase):
    """Each of these was learned from a real run and no script can check it."""

    def setUp(self):
        self.text = read(STEP1)

    def test_the_page_hunt_survives(self):
        """A homepage is a positioning document. Mister O1's prices were in
        per-location PDFs and nothing on the site was a price as text."""
        for path in ("/pricing", "/careers", "/sitemap.xml", "/compare"):
            self.assertIn(path, self.text, f"the page hunt lost {path}")

    def test_the_platform_is_the_finding_survives(self):
        """If ordering runs through Toast, Toast is a vendor they pay, a workaround,
        and a cohort shock — not an obstacle. Nothing produces this by default."""
        self.assertIn("Toast", self.text)
        self.assertRegex(self.text.lower(), r"not the obstacle|is the answer, not")

    def test_the_forcing_question_survives(self):
        """What does someone type BEFORE they know this category exists? The single
        line that makes buyer_language real rather than seller vocabulary reworded."""
        self.assertRegex(self.text.lower(), r"before they know (this|the) category")

    def test_the_fluent_buyer_exception_survives(self):
        """Some markets legitimately share the seller's vocabulary — immigration,
        performance marketing. The validator deliberately allows it, so only the prose
        says what to do instead: translate posture."""
        self.assertIn("posture", self.text)

    def test_named_not_category_competitors_survives(self):
        self.assertRegex(self.text.lower(), r"navigate to|generic bi tools")


class EnforcedRulesNeedNoProse(unittest.TestCase):
    """The counterpart. If step 1 grows back to explaining what the validator refuses,
    that is prose the delta rule says to cut — the error message already says it, at
    the moment it matters, to someone who has to act on it."""

    def test_every_hard_rule_is_enforced_somewhere(self):
        v = read(VALIDATOR)
        for needle in ("rearranged", "not countable", "fails_when",
                       "the_person_they_pay", "competitors.direct", "price_band",
                       "prohibited_bridge"):
            self.assertIn(needle, v,
                          f"{needle} is no longer enforced — if it moved to prose only, "
                          "the check got weaker, not the file shorter")

    def test_step_1_stays_short(self):
        """Not a style rule. Step 1 loads on every single run, and it grew to 2,300
        words by accreting explanations of things a script already refuses."""
        words = len(read(STEP1).split())
        self.assertLess(words, 1600,
                        f"step 1 is {words} words. Check what grew: if it restates a "
                        "validator rule, cut it; if it is a new non-enforceable delta, "
                        "add a test above and raise this bound deliberately.")


if __name__ == "__main__":
    unittest.main()
