"""Step 1 is deliberately minimal, and stays that way until a run proves otherwise.

It reached 242 lines and 2,303 words by accretion. Every time a run produced a bad
profile, the correction went into the prose. That is writing a skill from imagination,
which the method this repo follows says not to do: start from observed failure, never
from what you predict will go wrong.

TWO THINGS MAKE THE SMALL VERSION SAFE.

First, profiling a company is something the model already knows how to do, so the role
framing activates existing capability rather than teaching anything. That is the delta
rule answering "yes, it would have done this anyway".

Second, and this is what makes stripping the prose defensible rather than reckless:
`validate_profile.py` refuses every hard failure deterministically. Untranslated
vocabulary, an uncountable severity noun, a workaround with no failure condition, an
empty third competitor tier, category-noun competitors, an unanswered price, an absent
prohibited_bridge, an unaskable question. The prose was explaining rules a script
already enforces, and the script explains them better: at the moment it matters, to
someone who has to act on it.

WHAT WAS REMOVED, AND WHAT WOULD BRING IT BACK.

These were in the long version. Each came from a real observation, but each was then
applied as a standing instruction to every seller in every industry, which is a much
larger claim than the evidence supports. They are parked here rather than deleted, so
the knowledge survives without pre-loading the file:

  page hunt        try /pricing, /careers, /sitemap.xml rather than waiting for a link
                   ← Mister O1: prices were per-location PDFs, nothing on the site was
                     a price as text
  platform finding a platform like Toast is a vendor they pay, a workaround, and a
                   cohort shock, not an obstacle
                   ← the same run
  forcing question what does someone type BEFORE they know the category exists
                   ← the buyer/seller vocabulary failure this whole skill exists for
  fluent buyer     immigration and performance marketing buyers legitimately share the
                   seller's vocabulary; translate posture instead
                   ← measured while calibrating the vocabulary check

RE-ADD ONE ONLY WHEN A RUN FAILS FOR WANT OF IT. Not when it seems likely to help.
The test to run first is this step alone, across several industries, reading the
validator output rather than the prose. Whatever it gets wrong is what belongs here,
and nothing else does.
"""

import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STEP1 = os.path.join(ROOT, "references", "step-1-profile.md")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_profile.py")


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


class StaysMinimal(unittest.TestCase):
    def test_step_1_is_short(self):
        """A bound, not a style rule. It grew to 2,300 words once and the growth was
        invisible: every addition looked reasonable on its own."""
        words = len(read(STEP1).split())
        self.assertLess(words, 500,
                        f"step 1 is {words} words. Something was added. If a run failed "
                        "for want of it, raise this bound in the same commit and say "
                        "which run. If it merely seemed useful, cut it.")

    def test_it_still_names_the_artifact_it_produces(self):
        text = read(STEP1)
        self.assertIn("signal-lens/<domain>.json", text)
        self.assertIn("profile_schema.json", text)

    def test_it_still_runs_the_validator(self):
        self.assertIn("validate_profile.py", read(STEP1))

    def test_it_does_not_restate_what_the_validator_refuses(self):
        """The failure mode to guard: prose creeping back to explain a rule the script
        already enforces with a better message."""
        low = read(STEP1).lower()
        for restatement in ("uncountable", "not countable", "rearranged",
                            "the_person_they_pay", "fails_when"):
            self.assertNotIn(restatement, low,
                             f"{restatement!r} is enforced by validate_profile.py; "
                             "prose repeating it is the accretion this file prevents")


class EveryStepStaysSmall(unittest.TestCase):
    """The same rule as step 1, applied to the rest. Steps 2-6 have no script
    enforcing them, so prose is all they have — but that is an argument for keeping
    the instruction, not for keeping the justification around it.

    What was cut everywhere: explanations of why a rule exists, the story of the run
    that produced it, and anything a checker already refuses. What was kept: the
    instruction itself, the lists that are the actual knowledge (signal types, the
    three gates, the lead shapes, the discriminators), and the contract.
    """

    # Generous bounds. They exist to make growth visible, not to force a rewrite.
    BOUNDS = {"step-1-profile.md": 500, "step-2-validate.md": 400,
              "step-3-signals.md": 800, "step-4-doppelgangers.md": 300,
              "step-5-lead.md": 400, "step-6-prohibitions.md": 300,
              "step-7-output.md": 400, "step-8-specify.md": 600}

    def test_no_step_has_grown_past_its_bound(self):
        over = []
        for name, limit in sorted(self.BOUNDS.items()):
            words = len(read(os.path.join(ROOT, "references", name)).split())
            if words > limit:
                over.append(f"{name} {words}>{limit}")
        self.assertEqual(over, [],
                         f"steps grew: {'; '.join(over)}. If a run failed for want of "
                         "the addition, raise the bound in the same commit and say "
                         "which run. If it merely seemed useful, cut it.")

    def test_the_steps_are_all_present(self):
        for name in self.BOUNDS:
            self.assertTrue(os.path.isfile(os.path.join(ROOT, "references", name)), name)


class TheSafetyNetIsIntact(unittest.TestCase):
    """Stripping the prose is only safe while the validator still refuses these. If a
    check is ever removed, the corresponding instruction has to come back."""

    def test_every_hard_rule_is_still_enforced(self):
        v = read(VALIDATOR)
        for needle in ("rearranged", "not countable", "fails_when",
                       "the_person_they_pay", "competitors.direct", "price_band",
                       "prohibited_bridge"):
            self.assertIn(needle, v,
                          f"{needle} is no longer enforced. Step 1 was shortened on the "
                          "assumption that it is — restore the check, or restore the "
                          "prose that covered it.")


if __name__ == "__main__":
    unittest.main()
