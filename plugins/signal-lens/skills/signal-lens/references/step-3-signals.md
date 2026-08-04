# Step 3 — Derive the signals

**Enumerate. Do not shortlist.** Filtering comes later and can only choose from what
was listed; a signal left out because it felt marginal is gone for good.

Read first:

1. `references/industry-signals.md` — look up every value in `seller.industry`. Says
   what fires in that market, what is dead there, and the surfaces. The library's
   strengths are cross-industry averages and are the wrong number for one seller.
2. `references/signal-library.md` — specimens, doppelgängers, what was cut and why.
3. `references/presence-signals.md` — what is visible with nobody having said anything.

## Walk every type

For each, write the signal for this seller or record why it does not apply — a reason
about *this business*, never "I could not think of one".

**Arrangement breaking:** clock on the incumbent arrangement · continuity break (the
person maintaining the workaround is leaving) · vendor death · broadcast cohort shock
· just churned off something · unhappy with a named incumbent.

**The platform the seller sits on is an incumbent arrangement.** If the product
attaches to QuickBooks, Shopify, Salesforce or an app store, that platform's tier
changes and deprecations strand every customer at once.

**Failing slowly:** counted failed attempt loop · outgrown their setup · doing it the
hard way · cost of the workaround surfacing.

**Buyer in motion:** second opinion with a quote in hand — *discriminator is tense*,
"wants $11,400" is live and "I paid $11,400" is over · asking what it costs · asking
for a recommendation · gatekeeper spec you cannot meet.

**Presence and artifacts:** rating trajectory break · review content naming the
workaround · marketplace listing state · certification or licence expiring · profile
and link-stack fragmentation · content cadence break · content role changing hands ·
public stack disclosure · competitor footprint movement · comment-section residue ·
directory presence. Each needs its **baseline** named in `detection`.

**Conditional:** unaware the category exists · new person in a buying role · building
it themselves (works on a lag) · hiring for the pain (B2B only) · third-party-funded
budget.

Where a signal has both an utterance form and an artifact form, write both rows — they
have a different `where`, a different `detection`, and often a different twin.

Then extend. The references are a floor, and what you add is the most valuable part.

## Three gates

A candidate failing any of these is not a signal:

1. **COUNT** — a number that would be awkward to invent, counting the noun from
   `artifacts.severity_noun`. Venting has adjectives; intent has integers.
2. **CLOCK** — a date extracted *from the text*, never the crawl timestamp.
3. **SIDE AND ROLE** — demand-side, and their relation to the money is known. In
   communities that are mostly practitioners, run this *before* scoring.

## What each signal carries

Signal · what it sounds like in their voice · who the lead is · why it is intent ·
strength · false positive · what detecting it would take.

Fill the last one even when the honest answer is "no practical way today" — a signal
that is real and uncatchable is worth knowing, and is the one most likely to become
catchable.
