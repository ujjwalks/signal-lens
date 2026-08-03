# Step 1 — Profile the seller

Produces `./signal-lens/<domain>.json`, a validated profile that every later step
reads. Nothing downstream re-reads the website. An error here propagates into
every signal derived afterwards, which is why this step ends in a validator rather
than a judgement.

## Contents

- [The order of operations](#the-order-of-operations)
- [Reading the site](#reading-the-site)
- [The five artifacts](#the-five-artifacts)
- [The test that governs all of it](#the-test-that-governs-all-of-it)
- [Writing the profile](#writing-the-profile)
- [Validating, and asking](#validating-and-asking)

## The order of operations

**1. Look for an existing profile first.**

```
cat ./signal-lens/<domain>.json
```

If it exists, do not fetch the site and do not re-derive. Validate it, show the
user what it says in three or four lines, and ask whether anything has changed.
A profile is a claim about a company at a date; companies reposition. If
`fetched_at` is more than about two quarters old, say so.

If it does not exist, continue.

**2. Fetch the site.** If it will not render, say so and work from the user's
description — do not infer pages that might plausibly exist. A profile built from
imagined pages is worse than one built from a paragraph the user typed, because it
looks sourced.

**3. Derive the five artifacts** below.

**4. Write the JSON**, run the validator, fix what it names, ask what it could not
resolve.

## Reading the site

Read for what buyers *do*, not for what the company *says*. The useful pages are
usually not the homepage: pricing tells you the severity noun, customer stories
name the workaround, careers pages name the person currently doing it by hand, and
docs or changelogs tell you what breaks.

Every inferred field carries **the value, how sure you are, and where you saw it**.
An artifact you cannot point at is a guess. Where the site does not say, write that
it does not say and put it in `unresolved` — that is a finding about the site, not
a gap to fill with a plausible sentence.

## The five artifacts

| | |
|---|---|
| **A. Workaround inventory** → `artifacts.workarounds` | For each way buyers cope: the **artifact** (a concrete noun they can see, open or photograph), **who maintains it**, and the condition under which it **fails**. The failure condition is the signal — a workaround recorded without one contributes nothing to step 3 |
| **B. Competitor set, three tiers** → `artifacts.competitors` | Paid products · the free or manual substitute (usually the real incumbent) · **the person they pay to do it** — the CPA firm, the freelancer, the agency, the VA. Tier three never appears on a website, is a paid competitor in half of all cases, sets the price ceiling, and their departure is a signal |
| **C. The countable severity noun** → `artifacts.severity_noun` | The one noun whose count decides whether a post is worth nothing or five figures — entities, GB/month, ad spend, doors, tonnage, priority date. It must be countable: "complexity" and "time" cannot appear as an integer in somebody's post, so no signal could carry the count step 3 requires |
| **D. Vocabulary split** → `artifacts.vocabulary` | The same complaint in the seller's register and the buyer's. This is the crux of the whole skill, and the validator checks it mechanically because it fails silently |
| **E. Prohibited bridge** → `artifacts.prohibited_bridge` | Inferences that would reach this buyer through a protected characteristic, a distress disclosure, or a third party the poster exposed. Named so they can be excluded. An empty list is a valid answer; an absent one means nobody asked |

## The test that governs all of it

**If a phrase you write could plausibly appear on the seller's own website, it is
not buyer language. Rewrite it.** Real posts are messy and specific, name tools and
prices and hours wasted, and do not contain category nouns the buyer has never
heard.

Two ways this goes wrong that the test above will not catch:

- **The buyer's ask can be the opposite of the seller's promise.** An observability
  vendor sells "keep all your data at full fidelity"; the buyer is asking how to
  store *less*. Search the seller's language and you retrieve the happy half of the
  market. Check for this explicitly — it is the failure that looks like success.
- **Sometimes there is no gap.** Where the buyer is fluent — *MER*, *blended CAC*,
  *RFE on prong 2* — translate **posture** instead: the sound of someone auditing a
  decision they have already made. *"Am I being farmed"*, *"is this normal"*,
  *"talk me out of it"*.

A useful forcing question for `buyer_language`: what does someone type **before
they know this category exists**? That person is the largest uncontested segment
in any market and shares zero tokens with the seller's site.

## Writing the profile

Write `./signal-lens/<domain>.json` against `scripts/profile_schema.json`. Create
the directory if it is not there. The schema documents every field; the shape is:

```
domain, source, fetched_at
seller     { sells, category, motion, industry[], price_band, buyer[] }
artifacts  { workarounds[], competitors{}, severity_noun{}, vocabulary{},
             prohibited_bridge[] }
unresolved [ { field, question, why_it_matters } ]
```

`seller.industry` keys into `references/industry-signals.md` in step 3, so name the
**buyer's** industry, not the seller's. A company selling software to accountants
is in accounting, not in SaaS.

`seller.motion` decides who the lead is in step 5. `dual` means an individual's
complaint can be a lead for their employer.

Put everything the site did not answer into `unresolved`, each as a question you
could actually put to a person.

## Validating, and asking

```
python3 scripts/validate_profile.py ./signal-lens/<domain>.json
```

Exit 0 means continue. Non-zero means fix what it names and run it again — do not
proceed with a profile that failed, because every signal in step 3 inherits its
defects and they will not be visible in the output.

It checks the things that are computable and that fail quietly:

- **`buyer_language` that is only the seller's words rearranged.** The commonest
  and most expensive failure in this skill. It produces searches that return the
  company's own marketing and no buyer at all, and it reads as fine.
- **A severity noun that cannot be counted.**
- **A workaround with no failure condition**, or nobody named as maintaining it.
- **An empty third competitor tier.**

Then ask the user the unresolved questions:

```
python3 scripts/validate_profile.py ./signal-lens/<domain>.json --questions
```

Ask them in your own words, in one short block, and say why each matters. Do not
ask more than about four — pick the ones that change the output. If the user does
not know, record that in `unresolved` rather than deleting the entry, and mark
every signal that depended on it.

**A valid profile with unresolved questions is usable.** Proceed to step 2, and say
plainly which parts of the plan rest on an assumption.
