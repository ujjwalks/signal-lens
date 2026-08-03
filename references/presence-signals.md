# Presence and artifact signals

Signals that are visible **without anyone having said anything**. A rating that fell,
a listing that changed, a certificate about to lapse, a blog that stopped, a bio-link
page carrying four disconnected tools.

Step 3 reads this alongside `signal-library.md`. Everything here goes in the same CSV.

## Why this group exists

The rest of the library is built on **utterances** — somebody wrote a post, and you
match against what they wrote. That biases the whole output in three ways:

- It only finds people who write. Most buyers never post.
- It ranks by vividness, which correlates with having time to write.
- A post is undated in the way that matters. You get a crawl timestamp, not the
  moment the thing happened.

A **state** has none of those problems. A certification expiring on 14 March is
dated, checkable by anyone, identical for every observer, and forms a cohort
automatically. Nobody had to be feeling anything.

**Much of this is not a new signal. It is a second way to observe one you already
have.** "Outgrown their setup" is in the library as a post; a bio-link page showing
Calendly plus Stripe plus a separate storefront is the same intent as an artifact,
and the artifact is the better evidence. When you derive a signal here, say which
library type it is an artifact-shaped view of, or say that it is genuinely new.

## The discipline that keeps this honest

A state change is only a signal if you can answer **compared to what**. "They have a
3.9 rating" is a fact. "Their rating fell from 4.6 to 3.9 over sixty days" is a
signal, and the difference between the two is a stored earlier observation.

So every row in this group needs its `detection` column to name **the baseline**:
what you compare against, and how often you would have to look. A signal that
requires a snapshot you never took is not detectable today — record it anyway, and
say so. That is what the column is for.

## The types

### Rating trajectory break

Not the rating. The **movement**, and the window it moved in.

*A Google rating going 4.6 → 3.9 across a quarter; a marketplace seller rating
crossing the threshold that changes their placement; a review velocity that stopped.*

**Lead** — the business being rated, not the reviewer.
**Doppelgänger** — a seasonal dip; one viral review; a platform-wide scoring change
that moved everybody at once. Check whether competitors moved on the same date.
**Detection** — stored earlier rating, re-read on a schedule. Needs a baseline.

### Review content naming the workaround

Reviews are the most under-read source in this whole library, because everyone treats
them as reputation rather than as evidence. Buyers describe the manual process in
them, unprompted, in their own words: *"had to email three times to get the invoice"*,
*"they still take card details over the phone"*.

**Lead** — usually the business being reviewed. On a software review site the
reviewer's **employer** is the lead, and the reviewer is the champion inside it.
**Doppelgänger** — the competitor writing a fake review; the incentivised review; the
one-star that is actually about delivery.
**Detection** — keyword match against review text on a named surface. Available now,
which is unusual for a signal this good.

### Marketplace listing state

A listing is a public database row that changes. Newly listed · delisted · out of
stock · suspended · price moved · "sold by" changed · fulfilment method changed ·
variant count changed.

**Lead** — the seller behind the listing.
**Doppelgänger** — a seasonal delisting; a test listing; a platform-wide outage.
**Detection** — listing polled and compared against its earlier state.

### Certification, licence and registry state

Obtained · renewing · expiring · lapsed · revoked · upgraded.

The cleanest signals available anywhere: dated by a third party, verifiable, no
opinion involved, and **cohort-forming for free** — everyone whose certificate expires
in Q3 is a list somebody can already generate.

**Lead** — the certificate holder, or their employer where the employer paid for it.
**Doppelgänger** — a lapse that means they left the industry, not that they need help
renewing.
**Detection** — public register polled; an expiry date arriving. Often no baseline
needed, because the register publishes the date.

### Profile and link-stack fragmentation

The artifact is the profile itself. A bio-link page showing a booking tool, a separate
payment link, and a separate storefront is a visible statement that the workaround has
fragmented — written by the person, about themselves, with no intent to persuade you.

**Lead** — the profile owner.
**Doppelgänger** — the deliberate multi-tool setup someone is happy with; an
aggregator page maintained by an agency, not the person.
**Detection** — profile parsed for known tool domains. Compare against earlier state to
catch the moment a third tool is added, which is when it stops being tolerable.

### Content cadence break

A blog that published weekly and stopped. A changelog that went quiet. A newsletter
that missed two months. A podcast with a four-month gap.

This is **continuity break, observed from outside.** Somebody was maintaining that
and is not any more — they left, they got overloaded, or the arrangement collapsed.

**Lead** — the business, not the author. Though see the next type.
**Doppelgänger** — a deliberate strategy change; a seasonal pause; a site migration
that moved the feed.
**Detection** — publication dates compared against the prior cadence. Needs a baseline
of what normal looked like.

### Content role changing hands

A byline that changed. A "guest post" appearing where staff used to write. An agency
credit in the footer. A ghostwriter or content-marketer req on the careers page. A
blog that switched from first-person to corporate voice.

Means the in-house arrangement failed and somebody is now paying for it — which makes
this an **artifact-shaped view of "the person they pay"**, tier three of the competitor
set, appearing in public.

**Lead** — the business. In B2B the hiring manager now, and the new hire on their start
date.
**Detection** — byline compared against earlier state; careers page polled.

### Public stack disclosure

A "tools I use" page. An affiliate link. A sponsorship disclosure. A conference talk
listing the architecture. A job posting naming the software by name.

Names the **incumbent vendor**, publicly, on the record. For a seller who displaces
that vendor this is the whole ballgame, and for dual-motion sellers an influencer's
disclosure names the incumbent for their entire audience at once.

**Lead** — depends on the seller, and this is the type where getting it wrong is most
expensive. The discloser might be the buyer, or a channel you must not pitch, or
neither. Resolve it in step 5 before scoring.
**Doppelgänger** — the paid affiliate whose disclosure is an ad; the outdated page
listing a tool they left two years ago.

### Competitor footprint movement

Watching the incumbent rather than the buyer. Their pricing page changed · their status
page shows a run of incidents · their changelog deprecated something · their careers
page stopped hiring · their docs marked a feature legacy.

Every one of those is a dated, public event that strands **their customers**, and their
customers are your cohort. This is `broadcast cohort shock` observed at the source
instead of waiting for the complaints.

**Lead** — never the competitor. The cohort using them, which you then have to
enumerate by another route — and if you cannot, say so.
**Detection** — competitor pages polled and diffed. Needs a baseline.

### Comment-section residue

Comments under a competitor's blog post, a marketplace listing's Q&A, a YouTube
tutorial for the workaround, a review response thread.

Lower average quality than a forum thread and far higher volume, and almost nobody
watches them. The good ones are people asking the exact question your product answers,
underneath content about the alternative.

**Lead** — the commenter, usually.
**Doppelgänger** — the vendor answering in their own comments; the spam reply.

### Directory and listicle presence

Appearing in, or disappearing from, a "best X" listicle, a category directory, a
comparison page, an app marketplace.

**Lead** — the listed business, where they are the buyer. Disappearing is the stronger
signal of the two.
**Detection** — directory polled; needs a baseline to see the disappearance.

## What this group is bad at

Say so in the output rather than overselling it.

- **Almost everything here needs a baseline you have not taken yet.** On day one you
  can read current state; you cannot see movement. Most of these signals start working
  in month two.
- **A state change tells you something happened, never why.** A rating fell — because
  of service, a competitor, a platform change, or one angry customer. The reason is
  usually in an utterance, which means the two groups work together rather than one
  replacing the other.
- **Presence is easy to observe and easy to over-read.** A quiet blog might mean the
  content person left, or that they stopped bothering. Without the count from the
  severity noun, this group produces a very tidy list of businesses that are merely
  small.
