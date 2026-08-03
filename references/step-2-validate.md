# Step 2 — Validate the problem before looking for signals

You have the evidence to do this now, because artifacts A and B in the profile
*are* the evidence. It costs a paragraph and it decides whether the rest is
possible.

**A signal is someone already doing something about a problem.** If nobody is doing
anything about it yet, there is nothing to find, and any list you produce will be
invented. That is the entire reason this step exists.

## Grade the problem on what you can evidence

Best first. Read it off `artifacts.workarounds` and `artifacts.competitors`.

| | What it looks like | Where it shows in the profile |
|---|---|---|
| **Money already moving** | Someone is paid for this today: a tool, a firm, a freelancer, an internal hire | `competitors.the_person_they_pay` is populated |
| **Effort already spent** | A workaround exists — the spreadsheet, the manual process, the thing someone built | `workarounds[]` with a named maintainer |
| **A consequence with a number** | Hours lost, money leaked, incidents, a date missed | `severity_noun.material_at` |
| **Complaint only** | People say it is annoying. Nobody pays, nobody works around it | workarounds thin or unmaintained |
| **The seller's word only** | The problem appears in their marketing and nowhere else | artifacts filled from the site alone |

The top three are **past behaviour** — what someone already did, paid for, or
built. The bottom two are opinion about a hypothetical, and anything about the
future is an over-optimistic lie. That distinction is the whole test.

## Two traps in the seller's own copy

- **A number the seller invented is not evidence.** "Teams waste 10 hours a week"
  with no source is a claim about a hypothetical average person. Ask where it came
  from; if nowhere, it is marketing.
- **Solution-shaped problems.** "Companies lack a unified view of X" describes the
  absence of the product, not a problem anyone had before it existed. Nobody wakes
  up lacking a unified view; they wake up to a number that is wrong.

## Say which row you reached

In one line, **even when the answer is obviously yes.** *"People already pay CPA
firms two to three thousand a month to do this by hand"* is the sentence that makes
everything after it credible. Skipping it because the answer is easy is how a plan
for a real problem reads exactly like a plan for an imaginary one.

## Refuse at the bottom two

Say the problem is not yet evidenced outside their own marketing, show which of the
five rows you could and could not fill, and name what would change your mind —
someone paying for a workaround, a named competitor, a complaint thread. Then stop.

This will be unpopular and it is the most useful thing the skill can do. A plausible
list of keywords for a problem nobody has yet costs a company months.

If the evidence is thin but real — complaints exist but nobody pays — continue, and
mark every signal derived from it as unvalidated.
