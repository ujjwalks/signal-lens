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

Read for what buyers *do*, not for what the company *says*.

**A homepage is a positioning document. Almost nothing you need is on it.** It is
written to be liked, so it carries the seller's vocabulary and hides the price, the
workaround and the competitor. Fetching it and stopping is the single most common
way this step produces a profile that validates and is useless.

### Go and find the pages

Do not wait for the homepage to link them. Navigation is often JavaScript, or the
link is in a footer that did not render, or the page exists and is simply not
linked. **Try the conventional path directly.**

| Looking for | Try |
|---|---|
| Price, and the severity noun | `/pricing` `/plans` `/rates` `/menu` `/order` `/order-online` `/book` |
| The workaround, in a customer's own words | `/customers` `/case-studies` `/stories` `/testimonials` |
| **Who does it by hand today** — the best page on most sites | `/careers` `/jobs` `/about/careers` and any ATS link (Greenhouse, Lever, Ashby) |
| What breaks, and how often | `/docs` `/changelog` `/status` `/releases` `/integrations` |
| Scale, and whether *locations* is the severity noun | `/locations` `/stores` `/find-us` |
| Named competitors | `/compare` `/vs` `/alternatives` `/migrate` |
| Everything, enumerated | `/sitemap.xml` — the reliable way to see what exists. Also `/robots.txt`, which usually names the sitemap |

Reach for `/sitemap.xml` early when the homepage is thin. It is a list of every page
the site admits to having, and it costs one fetch.

A job posting is worth more than any marketing page. *"Senior Accountant —
multi-entity consolidation experience required"* names the pain, the count and the
budget in a document the company wrote about itself, with no intention of
persuading you.

Every inferred field carries **the value, how sure you are, and where you saw it**.
An artifact you cannot point at is a guess. Where the site does not say, write that
it does not say and put it in `unresolved` — that is a finding about the site, not
a gap to fill with a plausible sentence.

### When the price is not on the page

Most businesses do not put prices in HTML text, and the profile is wrong without
them: price calibrates the severity noun, and the tier-three competitor's rate is
the ceiling the buyer is already paying. `price_band: "not stated"` with nothing
else is a skipped field, not an answer.

Look in this order before giving up:

| Where it hides | What to do |
|---|---|
| **A PDF** — menu, rate card, price list, prospectus, often one per location or region | Fetch and read it. Look under `/uploads/`, `/wp-content/`, `/files/`, or linked from a *menu* / *pricing* / *rates* page |
| **A third-party ordering or booking platform** — Toast, Square, ChowNow, Olo, DoorDash, Resy, OpenTable, Mindbody, Calendly | Follow the link. The prices live on that platform, not on the site |
| **An image** — a photographed menu, a price table exported as PNG | Read it if the tooling allows; if not, say which image |
| **Quote-only** — "contact us", "request a demo", "get a quote" | Never invent a band. Quote-only is itself a finding about how they sell |
| **A marketplace or directory** — Amazon, G2, Capterra, Yelp, Angi, a franchise disclosure | Third parties routinely publish the number the vendor will not |

### The platform is not an obstacle. It is the finding.

This is the part worth getting right, because it inverts a dead end into the most
valuable thing on the page.

If a restaurant's ordering runs through Toast, Toast is not in your way. Toast is:

- a **vendor they pay**, which belongs in `competitors.direct` — a tier-one entry
  you would never have found in the copy
- a **workaround** in artifact A wherever the menu is a document someone maintains
  and re-uploads by hand
- a **broadcast cohort shock** waiting to happen: when a platform changes its fee
  structure, every business on it is stranded on the same day, which is among the
  highest-yield signals in the library

So write it into `artifacts`, not only into `unresolved`. *"I could not read the
price because it is on Toast"* is a sentence containing a vendor relationship, a
whole cohort, and a renewal date.

**Per-location price documents are a severity reading.** Fifteen location-specific
menu PDFs says the severity noun is probably *locations*, and that somebody
maintains fifteen documents by hand — artifact A, already written down for you.
Compare their upload paths: a menu under `/uploads/2019/` sitting beside a wine
list under `/uploads/2026/03/` suggests two things maintained on very different
cadences, and the stale one is the workaround that is failing. Treat that as a lead
to check with the user, not a proven fact — a file can be replaced in place without
its path ever changing.

**When you genuinely cannot read it**, put it in `unresolved` naming *the specific
place you looked and what you would need* — "the menu is a per-location PDF I could
not fetch; the Miami one is at `<url>`" — never a bare "pricing unknown". A specific
question gets an answer; a vague one gets a shrug.

### If a critical field is still empty, ask

Searching has a floor. When you have tried the paths above and a field the output
depends on is still empty, **stop and ask the user.** Do not infer it, do not write
a plausible sentence, and do not proceed quietly with a gap.

These are the fields worth interrupting for, because each one changes the answer:

| Field | What goes wrong without it |
|---|---|
| `seller.price_band` | No way to say whether a signal is worth a human's time or only worth a list |
| `artifacts.severity_noun` | Every signal fails the COUNT gate in step 3, because there is no right noun to count |
| `artifacts.workarounds[].fails_when` | The arrangement-breaking group — the highest-yield signals — cannot be derived at all |
| `competitors.the_person_they_pay` | No price ceiling, and you miss the tier that yields most |
| `competitors.direct` — **named products, not a category** | An entire signal group dies. You cannot poll a changelog, diff a pricing page, or read reviews of "generic BI tools". A real run filled this with category nouns and the plan built on it lost **six signals**, every one of them returning `n/a` |
| `seller.industry` | Step 3 cannot look up what actually fires in this market and falls back to averages |
| `seller.motion` | Step 5 names the wrong lead wherever employer and individual differ |

Ask them together, in one short block, in your own words, and say why each matters.
Cap it at about four — pick the ones that change the output most. Then write the
answers into the profile and re-run the validator.

If the user does not know either, keep the entry in `unresolved` rather than
deleting it, and mark every signal that depended on it as resting on an assumption.
**An assumption you named is a finding. An assumption you buried is a defect.**

## The five artifacts

| | |
|---|---|
| **A. Workaround inventory** → `artifacts.workarounds` | For each way buyers cope: the **artifact** (a concrete noun they can see, open or photograph), the **verb** they perform on it weekly (*re-key, paste, reconcile, chase*) — that verb is how you recognise them in a post — **who maintains it**, the condition under which it **fails**, and roughly **how long it holds first**. The failure condition is the signal and the horizon is what makes the clock derivable; a workaround recorded without either contributes nothing to step 3 |
| **B. Competitor set, three tiers** → `artifacts.competitors` | Paid products, **named** · the free or manual substitute (usually the real incumbent) · **the person they pay to do it** — the CPA firm, the freelancer, the agency, the VA. Tier three never appears on a website, is a paid competitor in half of all cases, sets the price ceiling, and their departure is a signal. Tier one must be products you could navigate to: try `/compare`, `/vs`, `/alternatives`, review-site category pages, and what customers say they switched from. "Generic BI tools" is a category, and there is no changelog to poll |
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
