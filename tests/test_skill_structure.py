"""The body must survive its references being unreachable.

Some harnesses block file reads. A router whose references cannot be loaded was
measured at -33 points against no skill at all — worse than nothing, because it
promises knowledge it never delivers. The body therefore carries a compressed floor,
and this file is what stops that floor silently drifting out of date as the step
files grow. It was checked by hand once; that does not survive the next change.
"""

import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REFS = os.path.join(ROOT, "references")


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as fh:
        return fh.read()


def keyed(phrase):
    """Content words only, so wording can differ between the floor and the step file."""
    return frozenset(w for w in re.findall(r"[a-z]{4,}", phrase.lower())
                     if w not in {"their", "them", "with", "that", "this", "from",
                                  "into", "over", "your", "have", "been", "what",
                                  "when", "where", "which", "some", "were", "they"})


class InlineFloor(unittest.TestCase):
    def setUp(self):
        self.body = read(ROOT, "SKILL.md")
        self.floor = self.body.split("If you cannot read the step files")[1]

    def test_the_floor_exists(self):
        self.assertIn("If you cannot read the step files", self.body,
                      "the inline floor is gone — a router with unreachable references "
                      "measured -33 against no skill at all")

    def test_the_floor_names_every_signal_type_step_3_requires(self):
        """The floor must be a superset. A type only in step 3 vanishes entirely
        whenever the references cannot be read."""
        s3 = read(REFS, "step-3-signals.md")
        types = re.findall(r"^- \*\*([^*]+)\*\*", s3, re.M)
        for block in re.findall(r"\*\*(?:Conditional|And the artifact forms[^:]*):\*\*(.+?)\n\n",
                                s3 + "\n\n", re.S):
            types += [c for c in re.split(r"·", block)]
        # Normalise before splitting, in this order, because each step broke the
        # previous attempt: collapse newlines (the floor is line-wrapped, so \n cut
        # "certification or / licence expiring" in half), strip **bold** (the lead-in
        # was glued to the first type in each list), then split on BOTH the separator
        # the floor uses and sentence ends — otherwise the whole 489-char preamble is
        # one fragment carrying the first type inside it.
        flat = re.sub(r"\s+", " ", self.floor)
        flat = re.sub(r"\*\*[^*]+\*\*", " ", flat)
        floor_keys = [keyed(f) for f in re.split(r"·|\. ", flat) if keyed(f)]
        missing = []
        for t in types:
            k = keyed(t)
            if not k:
                continue
            # Two shared content words, not one. One is met by accident: "registry
            # state" and "marketplace listing state" share "state" and nothing else,
            # so a 1-token threshold passes even after a type is deleted. Verified by
            # deleting one and watching this fail.
            need = 2 if len(k) > 1 else 1
            if not any(len(k & f) >= need for f in floor_keys):
                missing.append(t.strip()[:60])
        self.assertEqual(missing, [],
                         f"signal types in step 3 but absent from the inline floor: {missing}")

    def test_the_floor_keeps_the_two_hardest_prohibitions(self):
        for must in ("pseudonymous", "distress"):
            self.assertIn(must, self.floor.lower(),
                          f"the floor dropped the {must} prohibition")

    def test_the_floor_keeps_the_translation_test(self):
        self.assertRegex(self.floor.lower(), r"seller'?s own website|buyer language",
                         "the floor dropped the seller-vs-buyer translation test")


class Routing(unittest.TestCase):
    def test_the_router_names_every_reference_that_exists(self):
        """A reference nothing points at is dead weight; one the body does not name is
        reachable only through a chain, which is what audit.py warns about."""
        body = read(ROOT, "SKILL.md")
        named_anywhere = body + "".join(
            read(REFS, f) for f in os.listdir(REFS) if f.endswith(".md"))
        for fn in sorted(os.listdir(REFS)):
            if fn.endswith(".md"):
                self.assertIn(fn, named_anywhere, f"references/{fn} is never pointed at")

    def test_every_step_file_referenced_by_the_router_exists(self):
        body = read(ROOT, "SKILL.md")
        for ref in sorted(set(re.findall(r"references/([\w.-]+\.md)", body))):
            self.assertTrue(os.path.isfile(os.path.join(REFS, ref)),
                            f"SKILL.md routes to references/{ref}, which does not exist")


if __name__ == "__main__":
    unittest.main()
