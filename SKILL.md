---
name: signal-lens
description: >-
  Use this whenever someone asks how to find leads, prospects or customers in
  public conversations; what buying signals or intent signals to watch for; how
  to do outbound, prospecting, lead gen or social listening; who is in-market or
  ready to buy; what keywords or search terms to monitor on Reddit, LinkedIn,
  forums or communities; where their buyers are actually talking; or who is
  complaining about a competitor - including when they only give a website and
  ask what to watch for. Works out which public conversations mean someone is
  about to buy from that specific seller, and who the lead actually is, which is
  often not the person who posted. Do not hand-write a keyword list or a signal
  list yourself, and never answer from the seller's own marketing words - run
  this skill first. For how buyers would react to a page or a price, use
  buyer-lens instead.
license: MIT
compatibility: >-
  Requires network access to fetch the seller's website. No third-party Python
  packages. Not usable where the runtime has no network.
metadata:
  version: "0.2.0"
  author: ujjwalks
  homepage: https://github.com/ujjwalks/signal-lens
---

# signal-lens

Derive the signals for one seller. The signals are not a list you pick from —
they fall out of who the seller is and how their buyers currently cope.

## The reframe that does the most work

**Stop looking for pain. Look for the structural failure of the workaround.**

Pain is the ambient condition of every market. Everyone in r/accounting hates
closing the books; that is the price of entry, not a signal, and ranking on it
surfaces students and venters first because they write the most vivid posts.

What discriminates is the moment the current arrangement *breaks*: the person
who maintained it leaves, the vendor sunsets, the renewal comes with an uplift,
the bottle runs out, the freelancer hits their ceiling, the req will not close.

So the highest-yield signals are about **the product or arrangement as an
object** — running out, out of stock, price rose, licence changed, brand died,
warranty ended, contract renews, maintainer left — rather than about the buyer's
feelings. Those are dated, checkable, cohort-forming, and safe to act on.

## Step 1 — Profile the seller, then derive five artifacts

Fetch the site. If it will not render, say so and work from the user's
description — do not infer pages that might plausibly exist.

**The test that governs all of it:** if a phrase you write could plausibly appear
on the seller's own website, it is not buyer language. Rewrite it. Real posts are
messy and specific, name tools and prices and hours wasted, and do not contain
category nouns the buyer has never heard.

Two ways this goes wrong that the test above will not catch:

- **The buyer's ask can be the opposite of the seller's promise.** An
  observability vendor sells "keep all your data at full fidelity"; the buyer is
  asking how to store *less*. Search the seller's language and you retrieve the
  happy half of the market. Check for this explicitly — it is the failure that
  looks like success.
- **Sometimes there is no gap.** Where the buyer is fluent — *MER*, *blended
  CAC*, *RFE on prong 2* — translate **posture** instead: the sound of someone
  auditing a decision they have already made. *"Am I being farmed"*, *"is this
  normal"*, *"talk me out of it"*.

Derive all five before writing a single signal. They are what everything
downstream is built from:

| | |
|---|---|
| **A. Workaround inventory** | For each way buyers cope: the **artifact** (a concrete noun they can see, open or photograph), the **verb** they perform on it weekly, its **failure mode** and **time to failure** |
| **B. Competitor set, three tiers** | Paid products · the free or manual substitute (usually the real incumbent) · **the person they pay to do it** — the CPA firm, the freelancer, the agency. Tier three never appears on a website and is a paid competitor in half of all cases |
| **C. The countable severity noun** | The one noun whose count decides whether a post is worth nothing or five figures — entities, GB/month, ad spend, doors, tonnage, priority date |
| **D. Vocabulary split** | The same complaint in the credentialed register and the lay register. If they share tokens, you have not found the lay one |
| **E. Prohibited bridge** | The most persuasive true sentence the seller could say — and whether they are allowed to say it |

Every inferred field carries what you inferred it from. An artifact you cannot
evidence is a guess, and guesses at this step propagate into every signal.

## Step 2 — Validate the problem before looking for signals

You now have the evidence to do this, because artifacts A and B *are* the
evidence. It costs a paragraph and it decides whether the rest is possible.

**A signal is someone already doing something about a problem.** So if nobody is
doing anything about it yet, there is nothing to find, and any list you produce
will be invented. That is the entire reason this step exists.

Grade the problem on what you can actually evidence — best first:

| | What it looks like |
|---|---|
| **Money already moving** | Someone is paid for this today: a tool, a firm, a freelancer, an internal hire |
| **Effort already spent** | A workaround exists — the spreadsheet, the manual process, the thing someone built |
| **A consequence with a number** | Hours lost, money leaked, incidents, a date missed |
| **Complaint only** | People say it is annoying. Nobody pays, nobody works around it |
| **The seller's word only** | The problem appears in their marketing and nowhere else |

The top three are past behaviour — what someone already did, paid for, or built.
The bottom two are opinion about a hypothetical, and **anything about the future
is an over-optimistic lie**. That distinction is the whole test.

Two traps in the seller's own copy:

- **A number the seller invented is not evidence.** "Teams waste 10 hours a week"
  with no source is a claim about a hypothetical average person. Ask where it
  came from; if nowhere, it is marketing.
- **Solution-shaped problems.** "Companies lack a unified view of X" describes the
  absence of the product, not a problem anyone had before it existed. Nobody
  wakes up lacking a unified view; they wake up to a number that is wrong.

**Refuse at the bottom two.** Say the problem is not yet evidenced outside their
own marketing, show which of the five rows you could and could not fill, and name
what would change your mind — someone paying for a workaround, a named
competitor, a complaint thread. Then stop.

This will be unpopular and it is the most useful thing the skill can do. A
plausible list of keywords for a problem nobody has yet costs a company months.
If the evidence is thin but real — say, complaints exist but nobody pays —
continue, and mark every signal derived from it as unvalidated.

## Step 3 — Derive the signals

These are the types that recurred across ten unrelated businesses. Walk them; for
each, write the signal for this seller or record why it does not apply — a reason
about this business, never "I could not think of one".

**Arrangement breaking** — the highest-yield group, and the one a pain-shaped
search cannot see:

- **Clock on the incumbent arrangement** — renewal, trial expiry, replenishment,
  coverage cliff. The date is in their own words
- **Continuity break** — the person who maintained the workaround is leaving. The
  inheritor is the best lead shape there is: same problem, no attachment
- **Vendor death** — an EOL date, a shutdown, a rebrand, a warranty refused
- **Broadcast cohort shock** — a price change, recall, stockout or compliance date
  strands a whole population at once. Detect once, enumerate the cohort
- **Just churned off something** — decided to leave, not yet decided where to go
- **Unhappy with a named incumbent** — from any of the three competitor tiers

**Buyer in motion:**

- **Second opinion / pre-commitment** — one quote in hand, asking strangers to
  confirm or refute it. Latest-stage and cheapest to convert. **Discriminator is
  tense:** "wants $11,400" is live, "I paid $11,400" is over
- **Asking what it costs** · **Asking for a recommendation** (the asker is the
  lead; the replies tell you who you are against)
- **Counted failed attempt loop** — the workaround failing with an integer attached
- **Outgrown their setup** · **Doing it the hard way** (strong on pain, weak on budget)
- **Gatekeeper spec you cannot meet** — a third party names the exact capability
  gap in their own words

**Conditional:** unaware the category exists · new person in a buying role ·
building it themselves (works on a lag) · hiring for the pain (B2B only) ·
third-party-funded budget.

Read `references/signal-library.md` for the specimens, the doppelgängers, the
strengths, and what was deliberately cut and why.

Then extend. The library is a floor. Every industry has signals it does not
contain, and the ones you add are the most valuable part of the output.

**Every candidate signal must pass three gates.** A signal failing any of them is
not a signal:

1. **COUNT** — at least one number that would be awkward to invent, and it must
   count the *right* noun from artifact C. Venting has adjectives; intent has
   integers.
2. **CLOCK** — a date or decayable event extracted *from the text*, never the
   crawl timestamp. A 60-day grace-period post is strong on day two and dead on
   day fifty-five.
3. **SIDE AND ROLE** — the poster is on the demand side, and their relation to
   the money is known: payer, champion, user, proxy, channel, or anti-lead. In
   communities that are mostly practitioners, run this *before* scoring, not
   after.

## Step 4 — Give every signal a doppelgänger

A signal without a named doppelgänger is not finished.

Every signal has a twin that shares its vocabulary and inverts its meaning: the
supply-side actor, the student, the past-tense war story, the affiliate, the
vendor farming the thread, the person on the other side of the desk, the
post-purchase reassurance-seeker, the hobbyist who enjoys the manual work.

The discriminators that keep working:

- present tense vs past tense
- "we" plus a number vs "what do people generally use"
- a specific mechanic hit *this month* vs the general vibe of the category
- asking *how* to verify vs asserting verification is impossible
- a question mark at the end vs a screenshot at the end

## Step 5 — Name the lead, which is often not the poster

Getting this wrong wastes the signal even when detection is perfect.

- **The poster** — the default.
- **The employer, not the individual** — where a company pays for what a person
  needs. They post; someone else signs.
- **A third party in the thread** — the me-too commenter who volunteers their own
  scale under someone else's rant has self-selected into a pain description they
  did not have to write. A thread is a container of leads, not one lead.
- **The channel, not a buyer** — whoever keeps answering recommendation threads.
  Pitching them is the fastest way to lose them. Their doppelgänger is the paid
  affiliate: a link, a coupon code, or suspiciously consistent loyalty.
- **Nobody.** Some signals identify a company with no contactable person, and
  some identify a person you must not contact. **"No lead" is a valid outcome** —
  return it rather than manufacturing one.

## Step 6 — Run the prohibitions pass

Read `references/prohibitions.md` and check the finished list against it.

Public conversation is *more* exposed than first-party data, not less: you are
profiling a stranger from things they said for another purpose, on a platform
whose terms you are subject to. The two that end companies: **never join a
pseudonymous handle to a real identity**, and **exclude distress before scoring,
not after** — in several markets the highest-intent strings are crisis posts,
which is exactly why a naive relevance model ranks them first.

Anything matching goes into a **do not use** section with its reason.

Never tell the seller a signal is *permitted*, *allowed*, *fine* or *safe* — you
are not in a position to clear anyone, and they will act on it as though you
were. Where you found nothing to flag, say you found nothing and name who should
confirm it. Write that in your own words to the seller; do not recite a formula
about checks or findings, which reads as machinery and is not their language.

## Step 7 — Output

Lead with the **three signals to start with** and why those three. A list of
thirty is the artifact a busy person pays to escape.

Then the full table, then **do not use**, then — only if asked — the phrases.

- Every figure carries "(assumed)" and the check that would replace it. You have
  no data on this seller's conversion rate.
- Not every signal is a reply opportunity. The right action is sometimes to reply
  without mentioning the product, route to a different person, hold on a timer,
  or do nothing.
- Write for the seller. Never mention this skill, a library, a reference file, or
  a step number.
