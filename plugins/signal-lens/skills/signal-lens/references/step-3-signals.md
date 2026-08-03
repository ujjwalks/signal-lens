# Step 3 — Derive the signals

Enumerate. Do not shortlist. Something downstream filters these by what can
actually be built; filtering recovers precision, but it can never recover a signal
you failed to list. A signal left out because it felt marginal is gone for good.

## Read these three first

1. `references/industry-signals.md` — look up every value in `seller.industry`.
   It tells you which types actually fire in that market, which are dead there, and
   what the channel surfaces are. The strengths in the library are cross-industry
   averages and are the wrong number for any specific seller.
2. `references/signal-library.md` — the specimens, the doppelgängers, the
   strengths, and what was deliberately cut and why.
3. `references/presence-signals.md` — signals visible with nobody having said
   anything: ratings, reviews, listings, certifications, profiles, content cadence,
   the competitor's own footprint.

## Two ways to observe, not two kinds of signal

Most of the library is built on **utterances** — somebody wrote something and you
match against it. That finds only people who write, ranks by vividness, and gives
you a crawl timestamp instead of the date the thing happened.

A **state** has none of those problems. A certificate expiring on 14 March is dated,
verifiable, identical for every observer, and forms a cohort for free.

Many signals have both forms. *Outgrown their setup* is a post; a bio-link page
carrying four disconnected tools is the same intent as an artifact, and the artifact
is the better evidence. **Where a signal has an artifact form, write the artifact
row too** — it is a different `where`, a different `detection`, and often a different
false positive, so it is a separate row, not a footnote on the utterance one.

## Walk every type

For each, write the signal for this seller or record why it does not apply — a
reason about *this business*, never "I could not think of one".

**Arrangement breaking** — highest-yield, and the group a pain-shaped search
cannot see:

- **Clock on the incumbent arrangement** — renewal, trial expiry, replenishment,
  coverage cliff. The date is in their own words
- **Continuity break** — the person who maintained the workaround is leaving. The
  inheritor is the best lead shape there is: same problem, no attachment. Read this
  straight off `workarounds[].who_maintains`
- **Vendor death** — an EOL date, a shutdown, a rebrand, a warranty refused
- **Broadcast cohort shock** — a price change, recall, stockout or compliance date
  strands a whole population at once. Detect once, enumerate the cohort.
  **The platform the seller sits on is an incumbent arrangement.** This is the one
  most often missed, because "incumbent" reads as "competitor". If the product
  attaches to QuickBooks, Shopify, Salesforce, HubSpot, an app store or a payment
  processor, then that platform's tier changes, limit changes, deprecations and
  fee rises strand every customer of the shape you sell to, on a dated day, at once
  — usually the highest-reach signal available to the business. A real finboard.ai
  run named QuickBooks six times in its own rows and never once watched Intuit
- **Just churned off something** — decided to leave, not yet decided where to go
- **Unhappy with a named incumbent** — from any of the three competitor tiers

**Failing slowly** — no break event, and the trace is the pain itself. Do not skip
this group; for most sellers it is larger than the one above:

- **Counted failed attempt loop** — the workaround failing with an integer attached
- **Outgrown their setup** — the arrangement was right at a smaller count of the
  severity noun and is not at this one
- **Doing it the hard way** — strong on pain, weak on budget. Qualify with a count
  before scoring it
- **Cost of the workaround surfacing** — someone totals up what the manual route
  actually costs, usually in a reply rather than a post

**Buyer in motion:**

- **Second opinion / pre-commitment** — one quote in hand, asking strangers to
  confirm or refute it. Latest-stage and cheapest to convert. **Discriminator is
  tense:** "wants $11,400" is live, "I paid $11,400" is over
- **Asking what it costs** · **Asking for a recommendation** (the asker is the lead;
  the replies tell you who you are against)
- **Gatekeeper spec you cannot meet** — a third party names the exact capability gap
  in their own words

**Presence and artifacts** — nobody said anything; something is observably in a
different state than it was. Full treatment in `references/presence-signals.md`:

- **Rating trajectory break** — the movement and its window, never the rating
- **Review content naming the workaround** — buyers describe the manual process in
  reviews, unprompted, and almost nobody reads them as evidence
- **Marketplace listing state** — listed · delisted · out of stock · suspended ·
  price moved · seller-of-record changed
- **Certification, licence or registry state** — obtained, expiring, lapsed. Dated by
  a third party and cohort-forming for free
- **Profile and link-stack fragmentation** — the workaround visible on the profile
- **Content cadence break** — continuity break seen from outside
- **Content role changing hands** — a byline change or a ghostwriter req means the
  in-house arrangement failed and somebody is now being paid
- **Public stack disclosure** — a tools page, an affiliate link, a job ad naming the
  incumbent by name
- **Competitor footprint movement** — their pricing page, status page, changelog or
  careers page changed, which strands *their* customers
- **Comment-section residue** · **directory or listicle presence**

Every row in this group must name **the baseline** in `detection`: what you compare
against and how often you would look. "They have a 3.9 rating" is a fact; "it fell
from 4.6 over sixty days" is a signal, and the difference is a snapshot you took
earlier. Where no baseline exists yet, say so — most of this group starts working in
month two, and that is worth telling the seller.

**Conditional:** unaware the category exists · new person in a buying role ·
building it themselves (works on a lag) · hiring for the pain (B2B only) ·
third-party-funded budget.

Then **extend**. The library and the industry file are a floor. Every business has
signals neither contains, and the ones you add are the most valuable part of the
output.

## Three gates

Every candidate must pass all three. A signal failing any of them is not a signal:

1. **COUNT** — at least one number that would be awkward to invent, counting the
   noun from `artifacts.severity_noun`. Venting has adjectives; intent has integers.
2. **CLOCK** — a date or decayable event extracted *from the text*, never the crawl
   timestamp. A 60-day grace-period post is strong on day two and dead on day
   fifty-five.
3. **SIDE AND ROLE** — the poster is on the demand side, and their relation to the
   money is known: payer, champion, user, proxy, channel, or anti-lead. In
   communities that are mostly practitioners, run this *before* scoring, not after.

## What each signal has to carry

| | |
|---|---|
| **Signal** | what the person is doing or saying |
| **What it sounds like** | a realistic post in their own voice, not a paraphrase |
| **Who the lead is** | often not the poster — step 5 |
| **Why it is intent** | the reasoning, so a human can disagree with it |
| **Strength** | strong / medium / weak, and say what makes it weak |
| **False positive** | what looks exactly like this and is not — step 4 |
| **What detecting it takes** | the surface it appears on, and what catching it would require: a keyword match, a profile compared against its earlier state, a public register, a date arriving, a thread watched over time |

That last column is not for the reader. It is what lets someone decide later which
of these can be built. Fill it even when the honest answer is "no practical way to
catch this today" — a signal that is real and uncatchable is worth knowing, and it
is the one most likely to become catchable.
