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
  often not the person who posted.
compatibility: >-
  Requires network access to fetch the seller's website, and python3 (stdlib only)
  to validate the seller profile and check the output.
---

# signal-lens

Derive the signals for one seller. The signals are not a list you pick from —
they fall out of who the seller is and how their buyers currently cope.

## The reframe that does the most work

**Pain is necessary and never sufficient. Rank on evidence that the workaround is
failing.**

Everyone in r/accounting hates closing the books. That is the price of entry, not
a signal. Rank posts by how much pain they express and you rank by writing
vividness, which sorts students and venters to the top because they have the time
to write well.

What promotes pain to a signal is evidence that the arrangement containing it has
started to fail. That evidence takes two forms, and you need both in scope:

- **A break event** — the person who maintained the workaround leaves, the vendor
  sunsets, the renewal arrives with an uplift, the bottle runs out, the freelancer
  hits their ceiling, the req will not close. Highest-yield, because it is dated,
  checkable, cohort-forming and safe to act on.
- **Continuous degradation** — no discrete event, and the only trace is the pain
  itself, expressed with a count and a cost. *"Three days on reconciliation and we
  still can't close"* is a failing workaround. It has an integer.

So do not search for feelings, and do not discard them either. The discriminator
is not pain versus structure — it is **unqualified versus evidenced**. A complaint
carrying a count, an artifact, a date, or awareness that a category exists is a
signal. The same complaint without one is ambient.

Structural breaks are where most of the evidenced volume lives, so weight them
first. But a plan that contains only break events has silently dropped every buyer
whose arrangement is failing slowly, and that is usually the larger group.

## Read the request sideways

People rarely ask for this in the words it produces. They ask **"where can I find
buyers"**, **"who should we target"**, **"what's our ICP"**, **"how do I do
outbound"**, **"we need more leads, where do I look"**. Those are all this — they
are just phrased as targeting questions, and the honest answer to a targeting
question is what those people *say in public when they are about to buy*.

So answer the question they asked, with what this produces. Say so in one line —
*"the useful version of 'where do I find them' is 'what do they say right before
they buy', so here is that"* — and then run the steps.

**Two failure modes, and the first is the common one.** If you answer the
targeting question directly you will produce a list of filters, directories and
job boards: competent, generic, and available without this skill. That is the
default the model reaches for and it is what this exists to replace. And if the
user genuinely wants something else — a list of named companies, a positioning
doc, a cold-email sequence — say plainly that this does not produce that, rather
than producing a worse version of it.

## The steps

Read each step's file when you reach it. Each one is a page; none is optional.

| | Read | When |
|---|---|---|
| 1 | `references/step-1-profile.md` | First, always. Produces a validated seller profile JSON that every later step reads. **If `./signal-lens/<domain>.json` already exists, this step is a re-check, not a re-derivation.** Writes against `scripts/profile_schema.json`, validated by `scripts/validate_profile.py`. |
| 2 | `references/step-2-validate.md` | Before deriving any signal, to decide whether the problem is evidenced at all. This step can end the run. |
| 3 | `references/step-3-signals.md` | To enumerate. Also sends you to `references/signal-library.md` for specimens and to `references/industry-signals.md` for what actually fires in this seller's industry. |
| 4 | `references/step-4-doppelgangers.md` | Once signals exist, before scoring any of them. |
| 5 | `references/step-5-lead.md` | To decide who the lead is for each signal, which is often not the poster. |
| 6 | `references/step-6-prohibitions.md` | On the finished list, before writing anything for the seller. Sends you to `references/prohibitions.md`, which is the actual rule set. |
| 7 | `references/step-7-output.md` | To produce the CSV and run the check that gates it. |

## If you cannot read the step files

Some harnesses block file reads. A router whose references are unreachable was measured
at **−33 points against no skill at all** — worse than nothing, because it promises
knowledge it never delivers. So if the reads fail, do not stop and do not improvise:
work from this floor, and say in the reply that it is the compressed version.

**Translate first.** If a phrase could appear on the seller's own website, it is not
buyer language. Rewrite it as what someone types *before they know the category exists*.

**Walk every type, write a row for each, `n/a` with a business reason where it does not
apply.** Clock on the incumbent arrangement · continuity break (the maintainer leaves) ·
vendor death · broadcast cohort shock · just churned · unhappy with a named incumbent ·
counted failed-attempt loop · outgrown their setup · doing it the hard way · cost of the
workaround surfacing · second opinion with a quote in hand · asking what it costs ·
asking for a recommendation · gatekeeper spec you cannot meet · unaware the category
exists · new person in a buying role · building it themselves · hiring for the pain ·
third-party-funded budget.

**Three gates:** a count of the seller's severity noun · a date from the text, never the
crawl · the poster is demand-side and their relation to the money is known.

**Two prohibitions that end companies:** never join a pseudonymous handle to a real
identity, and exclude distress *before* scoring rather than after.

**Output the CSV** with the header in step 7, several dozen rows, then a do-not-use
section.

## Non-negotiable, everywhere

- **Write for the seller.** Never mention this skill, a library, a reference file,
  a script, or a step number. They asked a business question.
- **Every figure carries "(assumed)"** and the check that would replace it. You
  have no data on this seller's conversion rate.
- **Never say a signal is permitted, allowed, fine or safe.** You are not in a
  position to clear anyone and they will act as though you were.
- **Not every signal is a reply opportunity.** The right action is sometimes to
  reply without mentioning the product, route to a different person, hold on a
  timer, or do nothing.
