---
name: signal-lens
description: >-
  Works out which public conversations mean someone is about to buy, for a
  specific seller. Given a website or product description, it translates what
  the seller says about itself into what their buyer would actually type in a
  post, then derives the signals to monitor and who the lead really is. Use this
  whenever the user wants to find leads or prospects in public conversations,
  asks what buying signals or intent signals to look for, wants to monitor
  Reddit, LinkedIn, forums, communities or social for people with a problem they
  solve, asks who is in-market or ready to buy, wants keywords or search terms
  for social listening or lead discovery, or points at a site and asks what to
  watch for. Do not hand-write a keyword list or a signal list yourself, and do
  not answer from the seller's own marketing words - run this skill first. For
  how buyers would react to a page or price, use buyer-lens instead.
license: MIT
compatibility: >-
  Requires network access to fetch the seller's website. No third-party Python
  packages. Not usable where the runtime has no network.
metadata:
  version: "0.1.0"
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

Fetch the site. If it will not render, work from the user's description and say
so rather than inventing pages.

Then read `references/translation.md` and derive all five before writing a single
signal. They are what everything downstream is built from:

| | |
|---|---|
| **A. Workaround inventory** | For each way buyers cope: the **artifact** (a concrete noun they can see, open or photograph), the **verb** they perform on it weekly, its **failure mode** and **time to failure** |
| **B. Competitor set, three tiers** | Paid products · the free or manual substitute (usually the real incumbent) · **the person they pay to do it** — the CPA firm, the freelancer, the agency. Tier three never appears on a website and is a paid competitor in half of all cases |
| **C. The countable severity noun** | The one noun whose count decides whether a post is worth nothing or five figures — entities, GB/month, ad spend, doors, tonnage, priority date |
| **D. Vocabulary split** | The same complaint in the credentialed register and the lay register. If they share tokens, you have not found the lay one |
| **E. Prohibited bridge** | The most persuasive true sentence the seller could say — and whether they are allowed to say it |

Ask at most one clarifying question, then proceed on a stated assumption.

## Step 2 — Derive the signals

Read `references/signal-library.md`. Walk the core types; for each, write the
signal for this seller or record why it does not apply — a reason about this
business, never "I could not think of one".

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

## Step 3 — Give every signal a doppelgänger

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

## Step 4 — Name the lead, which is often not the poster

Getting this wrong wastes the signal even when detection is perfect.

- **The poster** — the default.
- **The employer, not the individual** — where a company pays for what a person
  needs. They post; someone else signs.
- **A third party in the thread** — the me-too commenter who volunteers their own
  scale under someone else's rant has self-selected into a pain description they
  did not have to write. A thread is a container of leads, not one lead.
- **The channel, not a buyer** — whoever keeps answering recommendation threads.
  Pitching them is the fastest way to lose them.
- **Nobody.** Some signals identify a company with no contactable person, and
  some identify a person you must not contact. **"No lead" is a valid outcome** —
  return it rather than manufacturing one.

## Step 5 — Run the prohibitions pass

Read `references/prohibitions.md` and check the finished list against it.

Public conversation is *more* exposed than first-party data, not less: you are
profiling a stranger from things they said for another purpose, on a platform
whose terms you are subject to. The two that end companies: **never join a
pseudonymous handle to a real identity**, and **exclude distress before scoring,
not after** — in several markets the highest-intent strings are crisis posts,
which is exactly why a naive relevance model ranks them first.

Anything matching goes into a **do not use** section with its reason. Do not
write "permitted"; if nothing matched, say nothing matched.

## Step 6 — Output

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
